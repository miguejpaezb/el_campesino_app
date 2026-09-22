"""Endpoints de alimentación.

Expone el registro y la consulta de alimentación por lote, más los
indicadores de total de kilos y costo total.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.feeding import FeedingCreate, FeedingOut
from app.services.feeding_service import FeedingService

router = APIRouter()


@router.get(
    "/{lot_id}/feeding",
    response_model=list[FeedingOut],
    summary="Listar registros de alimentación",
)
def list_feeding(
    lot_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(get_current_user),
) -> list[FeedingOut]:
    """Lista los registros de alimentación de un lote.

    Args:
        lot_id: Identificador del lote.
        db: Sesión de base de datos inyectada por FastAPI.

    Returns:
        Lista de registros de alimentación del lote.
    """
    service = FeedingService(db)
    records = service.get_feeding_by_lot(lot_id)
    return [FeedingOut.model_validate(r) for r in records]


@router.post(
    "/{lot_id}/feeding",
    response_model=FeedingOut,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar alimentación",
)
def register_feeding(
    lot_id: int,
    payload: FeedingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FeedingOut:
    """Registra el suministro de alimento de un lote.

    Args:
        lot_id: Identificador del lote.
        payload: Datos del registro de alimentación.
        db: Sesión de base de datos inyectada por FastAPI.
        current_user: Usuario autenticado.

    Returns:
        El registro de alimentación creado.

    Raises:
        HTTPException 404: Si el lote no existe.
        HTTPException 400: Si el lote está inactivo.
    """
    service = FeedingService(db)
    record = service.register_feeding(lot_id, payload, current_user.id)
    return FeedingOut.model_validate(record)


@router.get(
    "/{lot_id}/feeding/total",
    summary="Total de kilos de alimento",
)
def total_feed(
    lot_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(get_current_user),
) -> dict[str, float]:
    """Devuelve el total de kilos de alimento consumidos por el lote.

    Args:
        lot_id: Identificador del lote.
        db: Sesión de base de datos inyectada por FastAPI.

    Returns:
        Total de kilos consumidos del lote.
    """
    service = FeedingService(db)
    return {"lot_id": lot_id, "total_feed_kg": service.get_total_feed(lot_id)}


@router.get(
    "/{lot_id}/feeding/cost",
    summary="Costo total de alimentación",
)
def total_feed_cost(
    lot_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(get_current_user),
) -> dict[str, float]:
    """Devuelve el costo total de alimentación del lote.

    Args:
        lot_id: Identificador del lote.
        db: Sesión de base de datos inyectada por FastAPI.

    Returns:
        Costo total de alimentación del lote.
    """
    service = FeedingService(db)
    return {"lot_id": lot_id, "total_feed_cost": service.get_total_feed_cost(lot_id)}
