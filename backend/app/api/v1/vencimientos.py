from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.core.config import settings
from app.db.db import get_db, User, VencimientoCRUD, VencimientoStatus
from app.schemas import (
    Vencimiento, VencimientoCreate, VencimientoUpdate,
    VencimientoStatusEnum, VencimientoTypeEnum
)
from app.api.v1.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=Vencimiento, status_code=status.HTTP_201_CREATED)
def create_vencimiento(
    vencimiento: VencimientoCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crear un nuevo vencimiento.
    
    - **tipo**: Tipo de vencimiento (impuesto, servicio, alquiler, proveedor, etc.)
    - **descripcion**: Descripción del vencimiento
    - **monto**: Monto a pagar
    - **fecha_vencimiento**: Fecha de vencimiento
    - **recordatorio_dias_antes**: Días antes para enviar recordatorio (default: 7)
    """
    try:
        vencimiento_data = vencimiento.model_dump()
        db_vencimiento = VencimientoCRUD.create(db, vencimiento_data)
        return db_vencimiento
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al crear vencimiento: {str(e)}"
        )

@router.get("/", response_model=List[Vencimiento])
def list_vencimientos(
    business_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status_filter: Optional[VencimientoStatusEnum] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Listar todos los vencimientos de un negocio.
    
    - **business_id**: ID del negocio
    - **skip**: Número de registros a saltar (paginación)
    - **limit**: Número máximo de registros a devolver
    - **status_filter**: Filtrar por estado (pendiente, pagado, vencido, cancelado)
    """
    try:
        if status_filter:
            vencimientos = VencimientoCRUD.get_by_status(
                db, business_id, VencimientoStatus[status_filter.value.upper()], skip, limit
            )
        else:
            vencimientos = VencimientoCRUD.get_by_business(db, business_id, skip, limit)
        return vencimientos
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener vencimientos: {str(e)}"
        )

@router.get("/{vencimiento_id}", response_model=Vencimiento)
def get_vencimiento(
    vencimiento_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener un vencimiento por su ID.
    """
    vencimiento = VencimientoCRUD.get_by_id(db, vencimiento_id)
    if not vencimiento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vencimiento no encontrado"
        )
    return vencimiento

@router.get("/business/{business_id}/proximos", response_model=List[Vencimiento])
def get_vencimientos_proximos(
    business_id: UUID,
    dias: int = Query(30, ge=1, le=365, description="Días hacia adelante"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener vencimientos próximos de un negocio.
    
    - **dias**: Número de días hacia adelante (default: 30)
    
    Devuelve todos los vencimientos pendientes en los próximos N días.
    """
    try:
        vencimientos = VencimientoCRUD.get_proximos(db, business_id, dias)
        return vencimientos
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener vencimientos próximos: {str(e)}"
        )

@router.get("/business/{business_id}/vencidos", response_model=List[Vencimiento])
def get_vencimientos_vencidos(
    business_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener vencimientos vencidos de un negocio.
    
    Devuelve todos los vencimientos pendientes cuya fecha de vencimiento ya pasó.
    """
    try:
        vencimientos = VencimientoCRUD.get_vencidos(db, business_id)
        return vencimientos
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener vencimientos vencidos: {str(e)}"
        )

@router.get("/business/{business_id}/date-range", response_model=List[Vencimiento])
def get_vencimientos_by_date_range(
    business_id: UUID,
    fecha_inicio: datetime,
    fecha_fin: datetime,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener vencimientos de un negocio dentro de un rango de fechas.
    
    - **fecha_inicio**: Fecha inicial (formato ISO: 2024-01-01T00:00:00)
    - **fecha_fin**: Fecha final
    """
    try:
        vencimientos = VencimientoCRUD.get_by_date_range(
            db, business_id, fecha_inicio, fecha_fin, skip, limit
        )
        return vencimientos
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener vencimientos: {str(e)}"
        )

@router.put("/{vencimiento_id}", response_model=Vencimiento)
def update_vencimiento(
    vencimiento_id: UUID,
    vencimiento_update: VencimientoUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Actualizar un vencimiento existente.
    """
    db_vencimiento = VencimientoCRUD.get_by_id(db, vencimiento_id)
    if not db_vencimiento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vencimiento no encontrado"
        )
    
    try:
        update_data = vencimiento_update.model_dump(exclude_unset=True)
        updated_vencimiento = VencimientoCRUD.update(db, vencimiento_id, update_data)
        return updated_vencimiento
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al actualizar vencimiento: {str(e)}"
        )

@router.patch("/{vencimiento_id}/marcar-pagado", response_model=Vencimiento)
def marcar_vencimiento_pagado(
    vencimiento_id: UUID,
    fecha_pago: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Marcar un vencimiento como pagado.
    
    - **fecha_pago**: Fecha de pago (opcional, si no se envía se usa la fecha actual)
    """
    db_vencimiento = VencimientoCRUD.get_by_id(db, vencimiento_id)
    if not db_vencimiento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vencimiento no encontrado"
        )
    
    try:
        updated_vencimiento = VencimientoCRUD.marcar_pagado(db, vencimiento_id, fecha_pago)
        return updated_vencimiento
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al marcar como pagado: {str(e)}"
        )

@router.delete("/{vencimiento_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vencimiento(
    vencimiento_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Eliminar un vencimiento.
    
    **ADVERTENCIA:** Esta acción es irreversible.
    """
    db_vencimiento = VencimientoCRUD.get_by_id(db, vencimiento_id)
    if not db_vencimiento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vencimiento no encontrado"
        )
    
    try:
        VencimientoCRUD.delete(db, vencimiento_id)
        return None
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar vencimiento: {str(e)}"
        )
