"""
OCR Service for invoice/receipt data extraction
Supports PDF and image files (JPG, PNG)
"""
import os
import re
import logging
from typing import Dict, Optional, List, Tuple
from datetime import datetime
from pathlib import Path
import tempfile

logger = logging.getLogger(__name__)

try:
    import pytesseract
    from PIL import Image
    import cv2
    import numpy as np
    from pdf2image import convert_from_path
    from pypdf import PdfReader
    OCR_AVAILABLE = True
except ImportError as e:
    logger.warning(f"OCR dependencies not installed: {e}")
    logger.warning("Install with: pip install pytesseract Pillow opencv-python pdf2image pypdf")
    OCR_AVAILABLE = False


class OCRService:
    """Service for extracting invoice data from images and PDFs using OCR"""
    
    SUPPORTED_IMAGE_FORMATS = ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']
    SUPPORTED_PDF_FORMAT = ['.pdf']
    
    def __init__(self):
        """Initialize OCR service with configuration"""
        self.tesseract_config = '--oem 3 --psm 6'
        
        if OCR_AVAILABLE:
            try:
                pytesseract.get_tesseract_version()
                logger.info("Tesseract OCR initialized successfully")
            except Exception as e:
                logger.error(f"Tesseract not found in system: {e}")
                logger.error("Install tesseract-ocr: sudo apt-get install tesseract-ocr")
    
    def is_available(self) -> bool:
        """Check if OCR dependencies are available"""
        return OCR_AVAILABLE
    
    def extract_invoice_data(self, file_path: str, filename: str) -> Dict:
        """
        Main method to extract invoice data from file
        
        Args:
            file_path: Path to the file
            filename: Original filename
            
        Returns:
            Dictionary with extracted data
        """
        if not OCR_AVAILABLE:
            return self._mock_extraction(filename)
        
        try:
            file_ext = Path(filename).suffix.lower()
            
            if file_ext in self.SUPPORTED_IMAGE_FORMATS:
                text = self._extract_text_from_image(file_path)
            elif file_ext in self.SUPPORTED_PDF_FORMAT:
                text = self._extract_text_from_pdf(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")
            
            extracted_data = self._parse_invoice_text(text, filename)
            extracted_data['raw_text'] = text
            extracted_data['file_format'] = file_ext
            
            return extracted_data
            
        except Exception as e:
            logger.error(f"Error extracting invoice data: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'tipo': None,
                'numero': None,
                'fecha_emision': None,
                'total': None,
                'cuit_emisor': None,
                'razon_social': None
            }
    
    def _extract_text_from_image(self, image_path: str) -> str:
        """Extract text from image file using OCR"""
        try:
            img = cv2.imread(image_path)
            
            if img is None:
                raise ValueError("Could not read image file")
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
            
            _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            text = pytesseract.image_to_string(thresh, config=self.tesseract_config, lang='spa')
            
            return text
            
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            pil_image = Image.open(image_path)
            text = pytesseract.image_to_string(pil_image, config=self.tesseract_config, lang='spa')
            return text
    
    def _extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF file"""
        try:
            reader = PdfReader(pdf_path)
            text_parts = []
            
            for page in reader.pages:
                text_parts.append(page.extract_text())
            
            text = '\n'.join(text_parts)
            
            if len(text.strip()) < 50:
                logger.info("PDF has little text, using OCR on images")
                images = convert_from_path(pdf_path, dpi=300)
                
                text_parts = []
                for i, image in enumerate(images):
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                        image.save(tmp.name)
                        page_text = self._extract_text_from_image(tmp.name)
                        text_parts.append(page_text)
                        os.unlink(tmp.name)
                
                text = '\n'.join(text_parts)
            
            return text
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise
    
    def _parse_invoice_text(self, text: str, filename: str) -> Dict:
        """
        Parse extracted text to find invoice fields
        
        Returns:
            Dictionary with parsed fields
        """
        data = {
            'success': True,
            'tipo': self._detect_document_type(text, filename),
            'numero': self._extract_invoice_number(text),
            'fecha_emision': self._extract_date(text),
            'total': self._extract_total(text),
            'cuit_emisor': self._extract_cuit(text),
            'razon_social': self._extract_company_name(text),
            'subtotal': self._extract_subtotal(text),
            'iva': self._extract_iva(text),
            'confidence': self._calculate_confidence(text)
        }
        
        return data
    
    def _detect_document_type(self, text: str, filename: str) -> str:
        """Detect document type from text and filename"""
        text_lower = text.lower()
        filename_lower = filename.lower()
        
        patterns = {
            'factura_a': ['factura a', 'fac a', 'factura "a"'],
            'factura_b': ['factura b', 'fac b', 'factura "b"'],
            'factura_c': ['factura c', 'fac c', 'factura "c"'],
            'nota_credito': ['nota de crédito', 'nota credito', 'n/c'],
            'nota_debito': ['nota de débito', 'nota debito', 'n/d'],
            'recibo': ['recibo', 'receipt'],
            'presupuesto': ['presupuesto', 'cotización', 'cotizacion', 'budget']
        }
        
        for tipo, keywords in patterns.items():
            for keyword in keywords:
                if keyword in text_lower or keyword in filename_lower:
                    return tipo
        
        return 'recibo'
    
    def _extract_invoice_number(self, text: str) -> Optional[str]:
        """Extract invoice number from text"""
        patterns = [
            r'n[úu]mero[:\s]+(\d{4}-\d{8})',
            r'n[°º][:\s]+(\d{4}-\d{8})',
            r'factura[:\s]+n[°º]?\s*(\d{4}-\d{8})',
            r'comprobante[:\s]+n[°º]?\s*(\d{4}-\d{8})',
            r'(\d{4}-\d{8})',
            r'n[°º]\s*(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_date(self, text: str) -> Optional[str]:
        """Extract emission date from text"""
        patterns = [
            r'fecha[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'fecha de emisión[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{4})',
            r'(\d{1,2}/\d{1,2}/\d{2})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_str = match.group(1)
                return self._normalize_date(date_str)
        
        return None
    
    def _normalize_date(self, date_str: str) -> str:
        """Convert date string to ISO format"""
        try:
            date_str = date_str.replace('-', '/')
            parts = date_str.split('/')
            
            if len(parts[2]) == 2:
                parts[2] = '20' + parts[2]
            
            day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
            date_obj = datetime(year, month, day)
            return date_obj.isoformat()
            
        except Exception:
            return date_str
    
    def _extract_total(self, text: str) -> Optional[float]:
        """Extract total amount from text"""
        patterns = [
            r'total[:\s]+\$?\s*([\d,.]+)',
            r'importe total[:\s]+\$?\s*([\d,.]+)',
            r'total a pagar[:\s]+\$?\s*([\d,.]+)',
            r'monto total[:\s]+\$?\s*([\d,.]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '.')
                try:
                    return float(amount_str)
                except ValueError:
                    continue
        
        numbers = re.findall(r'\$?\s*([\d,.]+)', text)
        if numbers:
            try:
                return float(numbers[-1].replace(',', '.'))
            except ValueError:
                pass
        
        return None
    
    def _extract_subtotal(self, text: str) -> Optional[float]:
        """Extract subtotal amount from text"""
        patterns = [
            r'subtotal[:\s]+\$?\s*([\d,.]+)',
            r'neto[:\s]+\$?\s*([\d,.]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '.')
                try:
                    return float(amount_str)
                except ValueError:
                    continue
        
        return None
    
    def _extract_iva(self, text: str) -> Optional[float]:
        """Extract IVA amount from text"""
        patterns = [
            r'iva[:\s]+\$?\s*([\d,.]+)',
            r'i\.v\.a[:\s]+\$?\s*([\d,.]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '.')
                try:
                    return float(amount_str)
                except ValueError:
                    continue
        
        return None
    
    def _extract_cuit(self, text: str) -> Optional[str]:
        """Extract CUIT from text"""
        patterns = [
            r'cuit[:\s]+(\d{2}[-\s]?\d{8}[-\s]?\d{1})',
            r'c\.u\.i\.t[:\s]+(\d{2}[-\s]?\d{8}[-\s]?\d{1})',
            r'(\d{2}[-\s]?\d{8}[-\s]?\d{1})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                cuit = match.group(1).replace('-', '').replace(' ', '')
                if len(cuit) == 11:
                    return cuit
        
        return None
    
    def _extract_company_name(self, text: str) -> Optional[str]:
        """Extract company name from text"""
        lines = text.split('\n')
        for i, line in enumerate(lines[:10]):
            line = line.strip()
            if len(line) > 5 and any(keyword in line.lower() for keyword in ['s.a.', 's.r.l.', 'sa', 'srl', 'empresa', 'compañía']):
                return line
            
            if i == 0 and len(line) > 5:
                return line
        
        return None
    
    def _calculate_confidence(self, text: str) -> float:
        """Calculate confidence score based on extracted data"""
        score = 0.0
        
        if len(text) > 100:
            score += 0.2
        
        if self._extract_invoice_number(text):
            score += 0.25
        if self._extract_date(text):
            score += 0.25
        if self._extract_total(text):
            score += 0.20
        if self._extract_cuit(text):
            score += 0.10
        
        return round(score, 2)
    
    def _mock_extraction(self, filename: str) -> Dict:
        """Return mock data when OCR is not available"""
        logger.warning("OCR not available, returning mock data")
        return {
            'success': False,
            'mock': True,
            'message': 'OCR dependencies not installed',
            'tipo': 'factura_b',
            'numero': '0001-00000001',
            'fecha_emision': datetime.now().isoformat(),
            'total': 1000.0,
            'subtotal': 826.45,
            'iva': 173.55,
            'cuit_emisor': '20123456789',
            'razon_social': 'Empresa Mock SA',
            'confidence': 0.0,
            'file_format': Path(filename).suffix.lower()
        }


ocr_service = OCRService()
