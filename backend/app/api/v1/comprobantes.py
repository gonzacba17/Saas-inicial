from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.core.config import settings
from app.db.db import get_db, User, ComprobanteCRUD, ComprobanteStatus
from app.schemas import (
    Comprobante, ComprobanteCreate, ComprobanteUpdate,
    ComprobanteStatusEnum, ComprobanteTypeEnum
)
from app.api.v1.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=Comprobante, status_code=status.HTTP_201_CREATED)
async def create_comprobante(
    comprobante: ComprobanteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crear un nuevo comprobante (factura, nota de crédito, recibo, etc.).
    
    - **tipo**: Tipo de comprobante (factura_a, factura_b, factura_c, nota_credito, etc.)
    - **numero**: Número del comprobante
    - **fecha_emision**: Fecha de emisión del comprobante
    - **total**: Monto total del comprobante
    """
    try:
        comprobante_data = comprobante.model_dump()
        comprobante_data['user_id'] = current_user.id
        
        db_comprobante = ComprobanteCRUD.create(db, comprobante_data)
        
        try:
            from app.tasks.notification_tasks import send_comprobante_notification_task
            
            comprobante_dict = {
                "id": str(db_comprobante.id),
                "tipo": db_comprobante.tipo.value,
                "numero": db_comprobante.numero,
                "total": db_comprobante.total,
                "fecha_emision": db_comprobante.fecha_emision.isoformat()
            }
            
            send_comprobante_notification_task.delay(
                comprobante=comprobante_dict,
                user_email=current_user.email,
                user_id=str(current_user.id),
                user_name=current_user.username
            )
        except Exception as notif_error:
            pass
        
        return db_comprobante
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al crear comprobante: {str(e)}"
        )

@router.get("/", response_model=List[Comprobante])
def list_comprobantes(
    business_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status_filter: Optional[ComprobanteStatusEnum] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Listar todos los comprobantes de un negocio.
    
    - **business_id**: ID del negocio
    - **skip**: Número de registros a saltar (paginación)
    - **limit**: Número máximo de registros a devolver
    - **status_filter**: Filtrar por estado (pendiente, procesado, validado, rechazado, archivado)
    """
    try:
        if status_filter:
            comprobantes = ComprobanteCRUD.get_by_status(
                db, business_id, ComprobanteStatus[status_filter.value.upper()], skip, limit
            )
        else:
            comprobantes = ComprobanteCRUD.get_by_business(db, business_id, skip, limit)
        return comprobantes
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener comprobantes: {str(e)}"
        )

@router.get("/{comprobante_id}", response_model=Comprobante)
def get_comprobante(
    comprobante_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener un comprobante por su ID.
    """
    comprobante = ComprobanteCRUD.get_by_id(db, comprobante_id)
    if not comprobante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comprobante no encontrado"
        )
    return comprobante

@router.get("/business/{business_id}/numero/{numero}", response_model=Comprobante)
def get_comprobante_by_numero(
    business_id: UUID,
    numero: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener un comprobante por su número dentro de un negocio.
    """
    comprobante = ComprobanteCRUD.get_by_numero(db, business_id, numero)
    if not comprobante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Comprobante número {numero} no encontrado"
        )
    return comprobante

@router.get("/business/{business_id}/date-range", response_model=List[Comprobante])
def get_comprobantes_by_date_range(
    business_id: UUID,
    fecha_inicio: datetime,
    fecha_fin: datetime,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener comprobantes de un negocio dentro de un rango de fechas.
    
    - **fecha_inicio**: Fecha inicial (formato ISO: 2024-01-01T00:00:00)
    - **fecha_fin**: Fecha final
    """
    try:
        comprobantes = ComprobanteCRUD.get_by_date_range(
            db, business_id, fecha_inicio, fecha_fin, skip, limit
        )
        return comprobantes
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener comprobantes: {str(e)}"
        )

@router.put("/{comprobante_id}", response_model=Comprobante)
def update_comprobante(
    comprobante_id: UUID,
    comprobante_update: ComprobanteUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Actualizar un comprobante existente.
    """
    db_comprobante = ComprobanteCRUD.get_by_id(db, comprobante_id)
    if not db_comprobante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comprobante no encontrado"
        )
    
    try:
        update_data = comprobante_update.model_dump(exclude_unset=True)
        updated_comprobante = ComprobanteCRUD.update(db, comprobante_id, update_data)
        return updated_comprobante
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al actualizar comprobante: {str(e)}"
        )

@router.patch("/{comprobante_id}/status", response_model=Comprobante)
def update_comprobante_status(
    comprobante_id: UUID,
    new_status: ComprobanteStatusEnum,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Actualizar solo el estado de un comprobante.
    
    - **new_status**: Nuevo estado (pendiente, procesado, validado, rechazado, archivado)
    """
    db_comprobante = ComprobanteCRUD.get_by_id(db, comprobante_id)
    if not db_comprobante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comprobante no encontrado"
        )
    
    try:
        updated_comprobante = ComprobanteCRUD.update_status(
            db, comprobante_id, ComprobanteStatus[new_status.value.upper()]
        )
        return updated_comprobante
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al actualizar estado: {str(e)}"
        )

@router.delete("/{comprobante_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comprobante(
    comprobante_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Eliminar un comprobante.
    
    **ADVERTENCIA:** Esta acción es irreversible.
    """
    db_comprobante = ComprobanteCRUD.get_by_id(db, comprobante_id)
    if not db_comprobante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comprobante no encontrado"
        )
    
    try:
        ComprobanteCRUD.delete(db, comprobante_id)
        return None
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar comprobante: {str(e)}"
        )
