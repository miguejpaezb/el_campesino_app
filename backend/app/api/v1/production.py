"""Endpoints de producción diaria de huevos.

Expone el registro y la consulta de producción diaria por lote, más los
indicadores de total, promedio semanal y porcentaje de postura.
"""

from datetime import date

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.egg_production import EggProductionCreate, EggProductionOut
from app.services.production_service import ProductionService

router = APIRouter()


@router.get(
    "/{lot_id}/production",
    response_model=list[EggProductionOut],
    summary="Listar producción de un lote",
    description="Devuelve los registros de producción del lote. Filtrar con "
    "`?from=AAAA-MM-DD` y `?to=AAAA-MM-DD` por fecha de recolección.",
)
def list_production(
    lot_id: int,
    from_date: date | None = Query(default=None, alias="from"),
    to_date: date | None = Query(default=None, alias="to"),
    db: Session = Depends(get_db),
    _: object = Depends(get_current_user),
) -> list[EggProductionOut]:
    """Lista los registros de producción de un lote.

    Args:
        lot_id: Identificador del lote.
        from_date: Fecha inicial del filtro (alias `from`).
        to_date: Fecha final del filtro (alias `to`).
        db: Sesión de base de datos inyectada por FastAPI.

    Returns:
        Lista de registros de producción.
    """
    service = ProductionService(db)
    records = service.get_production_by_lot(lot_id, from_date, to_date)
    return [EggProductionOut.model_validate(r) for r in records]


@router.post(
    "/{lot_id}/production",
    response_model=EggProductionOut,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar producción diaria",
    description="Registra la producción diaria de huevos de un lote. Si ya "
    "existe un registro con la misma fecha y hora devuelve HTTP 409 con el "
    "registro existente; usa `?merge=true` para sumar las cantidades al "
    "registro existente.",
)
def register_production(
    lot_id: int,
    payload: EggProductionCreate,
    merge: bool = Query(default=False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EggProductionOut:
    """Registra la producción diaria de huevos de un lote.

    Args:
        lot_id: Identificador del lote.
        payload: Datos del registro de producción.
        merge: Si True, suma cantidades al registro existente con la misma
            fecha y hora.
        db: Sesión de base de datos inyectada por FastAPI.
        current_user: Usuario autenticado.

    Returns:
        El registro de producción creado o actualizado.

    Raises:
        HTTPException 404: Si el lote no existe.
        HTTPException 400: Si el lote está inactivo, no está en postura o la
            fecha/hora no es válida.
        HTTPException 409: Si ya existe un registro con la misma fecha y hora
            y `merge` es False.
    """
    service = ProductionService(db)
    production = service.register_eggs(lot_id, payload, current_user.id, merge)
    return EggProductionOut.model_validate(production)


@router.get(
    "/{lot_id}/production/total",
    summary="Total de huevos del lote",
)
def total_eggs(
    lot_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(get_current_user),
) -> dict[str, int]:
    """Devuelve el total de huevos recolectados del lote.

    Args:
        lot_id: Identificador del lote.
        db: Sesión de base de datos inyectada por FastAPI.

    Returns:
        Total de huevos del lote.
    """
    service = ProductionService(db)
    return {"lot_id": lot_id, "total_eggs": service.get_total_eggs(lot_id)}


@router.get(
    "/{lot_id}/production/average",
    summary="Promedio semanal de postura",
)
def average_weekly(
    lot_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(get_current_user),
) -> dict[str, float]:
    """Devuelve el promedio semanal de postura del lote.

    Args:
        lot_id: Identificador del lote.
        db: Sesión de base de datos inyectada por FastAPI.

    Returns:
        Promedio semanal de postura del lote.
    """
    service = ProductionService(db)
    return {
        "lot_id": lot_id,
        "average_weekly_production": service.get_avg_weekly_production(lot_id),
    }


@router.get(
    "/{lot_id}/production/percentage",
    summary="Porcentaje de postura",
)
def laying_percentage(
    lot_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(get_current_user),
) -> dict[str, float]:
    """Devuelve el porcentaje de postura del lote.

    Args:
        lot_id: Identificador del lote.
        db: Sesión de base de datos inyectada por FastAPI.

    Returns:
        Porcentaje de postura del lote.
    """
    service = ProductionService(db)
    return {
        "lot_id": lot_id,
        "laying_percentage": service.get_laying_percentage(lot_id),
    }
