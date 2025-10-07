"""
OCR API endpoints for invoice/receipt data extraction
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
import time
import os
import tempfile
from pathlib import Path

from app.core.config import settings
from app.db.db import get_db, User, ComprobanteCRUD, ComprobanteType, ComprobanteStatus
from app.schemas import OCRResponse, OCRExtractedData, OCRUploadResponse
from app.api.v1.auth import get_current_user
from app.services_directory.ocr_service import ocr_service

router = APIRouter()

UPLOAD_DIR = Path("uploads/ocr")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {'.pdf', '.jpg', '.jpeg', '.png', '.tiff', '.bmp'}
MAX_FILE_SIZE = 10 * 1024 * 1024


@router.post("/upload", response_model=OCRUploadResponse, status_code=status.HTTP_200_OK)
async def upload_and_extract(
    file: UploadFile = File(...),
    business_id: Optional[str] = Form(None),
    auto_save: bool = Form(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload invoice/receipt image or PDF and extract data using OCR.
    
    - **file**: Image (JPG, PNG, TIFF, BMP) or PDF file
    - **business_id**: Optional business ID to associate the comprobante
    - **auto_save**: If True, automatically save extracted data as Comprobante
    
    Returns:
        - Extracted data (tipo, numero, fecha, total, CUIT, etc.)
        - Confidence score
        - Option to save as Comprobante
    """
    start_time = time.time()
    
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided"
        )
    
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not supported. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    file_size = 0
    temp_path = None
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
            temp_path = tmp.name
            content = await file.read()
            file_size = len(content)
            
            if file_size > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"File too large. Max size: {MAX_FILE_SIZE / 1024 / 1024}MB"
                )
            
            tmp.write(content)
        
        extracted_data_dict = ocr_service.extract_invoice_data(temp_path, file.filename)
        
        extracted_data = OCRExtractedData(**extracted_data_dict)
        
        processing_time = time.time() - start_time
        
        comprobante_id = None
        saved_to_comprobante = False
        
        if auto_save and extracted_data.success and business_id:
            try:
                comprobante_data = {
                    'business_id': UUID(business_id),
                    'user_id': current_user.id,
                    'tipo': ComprobanteType[extracted_data.tipo.upper()] if extracted_data.tipo else ComprobanteType.RECIBO,
                    'numero': extracted_data.numero or f"OCR-{int(time.time())}",
                    'fecha_emision': extracted_data.fecha_emision or time.strftime('%Y-%m-%dT%H:%M:%S'),
                    'cuit_emisor': extracted_data.cuit_emisor,
                    'razon_social_emisor': extracted_data.razon_social,
                    'subtotal': extracted_data.subtotal or 0.0,
                    'iva': extracted_data.iva or 0.0,
                    'total': extracted_data.total or 0.0,
                    'moneda': 'ARS',
                    'status': ComprobanteStatus.PROCESADO,
                    'ocr_data': extracted_data.raw_text or '',
                    'file_path': str(temp_path),
                    'notas': f"Extraído automáticamente via OCR (Confidence: {extracted_data.confidence})"
                }
                
                saved_file_path = UPLOAD_DIR / f"{current_user.id}_{int(time.time())}{file_ext}"
                os.rename(temp_path, saved_file_path)
                comprobante_data['file_path'] = str(saved_file_path)
                temp_path = None
                
                db_comprobante = ComprobanteCRUD.create(db, comprobante_data)
                comprobante_id = str(db_comprobante.id)
                saved_to_comprobante = True
                
            except Exception as e:
                logger_error = f"Error saving to comprobante: {str(e)}"
                import logging
                logging.error(logger_error)
        
        ocr_response = OCRResponse(
            success=extracted_data.success,
            filename=file.filename,
            file_size=file_size,
            processing_time=round(processing_time, 2),
            data=extracted_data,
            saved_to_comprobante=saved_to_comprobante,
            comprobante_id=comprobante_id
        )
        
        return OCRUploadResponse(
            message="OCR processing completed successfully",
            ocr_result=ocr_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(e)}"
        )
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except Exception:
                pass


@router.get("/status", response_model=dict)
def ocr_status(current_user: User = Depends(get_current_user)):
    """
    Check OCR service status and availability.
    """
    return {
        "ocr_available": ocr_service.is_available(),
        "supported_formats": list(ALLOWED_EXTENSIONS),
        "max_file_size_mb": MAX_FILE_SIZE / 1024 / 1024,
        "message": "OCR service is ready" if ocr_service.is_available() else "OCR dependencies not installed"
    }


@router.post("/extract-text", response_model=dict)
async def extract_text_only(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Extract raw text from image/PDF without parsing invoice data.
    Useful for debugging OCR quality.
    """
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not supported. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
            content = await file.read()
            tmp.write(content)
            temp_path = tmp.name
        
        extracted_data = ocr_service.extract_invoice_data(temp_path, file.filename)
        
        os.unlink(temp_path)
        
        return {
            "filename": file.filename,
            "raw_text": extracted_data.get('raw_text', ''),
            "text_length": len(extracted_data.get('raw_text', '')),
            "success": extracted_data.get('success', False)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error extracting text: {str(e)}"
        )
