"""Endpoints de inventario de aves (lotes).

Expone el CRUD de lotes y las operaciones de ciclo productivo: avance de
semana, evaluación y resumen.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.bird_lot import (
    BirdLotCreate,
    BirdLotDiscard,
    BirdLotOut,
    BirdLotSummary,
    BirdLotUpdate,
)
from app.services.lot_service import LotService

router = APIRouter()


@router.get(
    "/",
    response_model=list[BirdLotOut],
    summary="Listar lotes de aves",
    description="Devuelve todos los lotes. Usar `?active=true` para solo activos.",
)
def list_lots(
    active: bool = False,
    db: Session = Depends(get_db),
    _: object = Depends(get_current_user),
) -> list[BirdLotOut]:
    """Lista los lotes registrados, con filtro opcional por estado.

    Args:
        active: Si es True, solo se devuelven lotes activos.
        db: Sesión de base de datos inyectada por FastAPI.

    Returns:
        Lista de lotes.
    """
    service = LotService(db)
    return [
        BirdLotOut.model_validate(lot) for lot in service.list_lots(active_only=active)
    ]


@router.post(
    "/",
    response_model=BirdLotOut,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un lote de aves",
)
def create_lot(
    payload: BirdLotCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BirdLotOut:
    """Crea un nuevo lote con la cantidad inicial de aves.

    Args:
        payload: Datos del lote a crear.
        db: Sesión de base de datos inyectada por FastAPI.
        current_user: Usuario autenticado.

    Returns:
        El lote recién creado.

    Raises:
        HTTPException 409: Si el código de lote ya existe.
    """
    service = LotService(db)
    lot = service.create_lot(payload, current_user.id)
    return BirdLotOut.model_validate(lot)


@router.get(
    "/{lot_id}",
    response_model=BirdLotOut,
    summary="Obtener un lote por ID",
)
def get_lot(
    lot_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(get_current_user),
) -> BirdLotOut:
    """Devuelve el lote con el identificador indicado.

    Args:
        lot_id: Identificador del lote.
        db: Sesión de base de datos inyectada por FastAPI.

    Returns:
        El lote encontrado.

    Raises:
        HTTPException 404: Si el lote no existe.
    """
    service = LotService(db)
    return BirdLotOut.model_validate(service.get_lot(lot_id))


@router.put(
    "/{lot_id}",
    response_model=BirdLotOut,
    summary="Actualizar un lote",
)
def update_lot(
    lot_id: int,
    payload: BirdLotUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BirdLotOut:
    """Actualiza los campos enviados de un lote.

    Args:
        lot_id: Identificador del lote.
        payload: Campos a actualizar.
        db: Sesión de base de datos inyectada por FastAPI.
        current_user: Usuario autenticado.

    Returns:
        El lote actualizado.
    """
    service = LotService(db)
    lot = service.update_lot(lot_id, payload, current_user.id)
    return BirdLotOut.model_validate(lot)


@router.delete(
    "/{lot_id}",
    response_model=BirdLotOut,
    summary="Descartar un lote",
    description="Desactiva el lote indicando la razón del descarte.",
)
def discard_lot(
    lot_id: int,
    payload: BirdLotDiscard,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BirdLotOut:
    """Desactiva un lote con la razón de descarte indicada.

    Args:
        lot_id: Identificador del lote.
        payload: Razón del descarte.
        db: Sesión de base de datos inyectada por FastAPI.
        current_user: Usuario autenticado.

    Returns:
        El lote desactivado.
    """
    service = LotService(db)
    lot = service.discard_lot(lot_id, payload, current_user.id)
    return BirdLotOut.model_validate(lot)


@router.post(
    "/{lot_id}/advance-week",
    response_model=BirdLotOut,
    summary="Avanzar una semana al lote",
)
def advance_week(
    lot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BirdLotOut:
    """Incrementa la semana actual del ciclo productivo del lote.

    Args:
        lot_id: Identificador del lote.
        db: Sesión de base de datos inyectada por FastAPI.
        current_user: Usuario autenticado.

    Returns:
        El lote con la semana incrementada.
    """
    service = LotService(db)
    lot = service.advance_week(lot_id, current_user.id)
    return BirdLotOut.model_validate(lot)


@router.post(
    "/{lot_id}/evaluate",
    summary="Evaluar el lote",
    description="Evalúa el rendimiento del lote en la semana de evaluación.",
)
def evaluate_lot(
    lot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, bool | str]:
    """Evalúa el lote y aplica la regla del ciclo productivo.

    Args:
        lot_id: Identificador del lote.
        db: Sesión de base de datos inyectada por FastAPI.
        current_user: Usuario autenticado.

    Returns:
        Mensaje con el resultado de la evaluación y el estado del lote.
    """
    service = LotService(db)
    return service.evaluate_lot(lot_id, current_user.id)


@router.get(
    "/{lot_id}/summary",
    response_model=BirdLotSummary,
    summary="Resumen productivo del lote",
)
def lot_summary(
    lot_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(get_current_user),
) -> BirdLotSummary:
    """Devuelve el resumen con los indicadores productivos del lote.

    Args:
        lot_id: Identificador del lote.
        db: Sesión de base de datos inyectada por FastAPI.

    Returns:
        Resumen del lote.
    """
    service = LotService(db)
    return service.get_summary(lot_id)
