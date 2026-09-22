"""Endpoints del inventario de insumos (alimentos).

Expone el CRUD de los tipos de alimento, el ingreso de stock, la suspensión,
la eliminación y el listado de movimientos.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.feed_stock import (
    FeedStockAddStock,
    FeedStockCreate,
    FeedStockMovementOut,
    FeedStockOut,
    FeedStockUpdate,
)
from app.services.feed_stock_service import FeedStockService

router = APIRouter()


@router.get(
    "",
    response_model=list[FeedStockOut],
    summary="Listar tipos de alimento",
)
def list_feed_stock(
    search: str | None = None,
    db: Session = Depends(get_db),
    _: object = Depends(get_current_user),
) -> list[FeedStockOut]:
    """Lista los tipos de alimento del inventario.

    Args:
        search: Texto de búsqueda por nombre (opcional).
        db: Sesión de base de datos inyectada por FastAPI.

    Returns:
        Lista de tipos de alimento.
    """
    service = FeedStockService(db)
    return [FeedStockOut.model_validate(ft) for ft in service.list_feed_types(search)]


@router.post(
    "",
    response_model=FeedStockOut,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un tipo de alimento",
)
def create_feed_stock(
    payload: FeedStockCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FeedStockOut:
    """Crea un tipo de alimento con su stock inicial.

    Args:
        payload: Datos del nuevo alimento.
        db: Sesión de base de datos inyectada por FastAPI.
        current_user: Usuario autenticado.

    Returns:
        El tipo de alimento creado.
    """
    service = FeedStockService(db)
    feed_type = service.create_feed_type(payload, current_user.id)
    return FeedStockOut.model_validate(feed_type)


@router.put(
    "/{feed_type_id}",
    response_model=FeedStockOut,
    summary="Actualizar un tipo de alimento",
)
def update_feed_stock(
    feed_type_id: int,
    payload: FeedStockUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FeedStockOut:
    """Actualiza el nombre y el stock mínimo de un tipo de alimento.

    Args:
        feed_type_id: Identificador del tipo de alimento.
        payload: Campos a actualizar.
        db: Sesión de base de datos inyectada por FastAPI.
        current_user: Usuario autenticado.

    Returns:
        El tipo de alimento actualizado.
    """
    service = FeedStockService(db)
    feed_type = service.update_feed_type(feed_type_id, payload, current_user.id)
    return FeedStockOut.model_validate(feed_type)


@router.post(
    "/{feed_type_id}/stock",
    response_model=FeedStockOut,
    summary="Añadir stock a un tipo de alimento",
)
def add_feed_stock(
    feed_type_id: int,
    payload: FeedStockAddStock,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FeedStockOut:
    """Añade kilos al stock de un tipo de alimento.

    Args:
        feed_type_id: Identificador del tipo de alimento.
        payload: Datos del ingreso de stock.
        db: Sesión de base de datos inyectada por FastAPI.
        current_user: Usuario autenticado.

    Returns:
        El tipo de alimento actualizado.
    """
    service = FeedStockService(db)
    feed_type = service.add_stock(feed_type_id, payload, current_user.id)
    return FeedStockOut.model_validate(feed_type)


@router.post(
    "/{feed_type_id}/suspend",
    response_model=FeedStockOut,
    summary="Suspender o reactivar un tipo de alimento",
)
def suspend_feed_stock(
    feed_type_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FeedStockOut:
    """Suspende o reactiva un tipo de alimento.

    Args:
        feed_type_id: Identificador del tipo de alimento.
        db: Sesión de base de datos inyectada por FastAPI.
        current_user: Usuario autenticado.

    Returns:
        El tipo de alimento actualizado.
    """
    service = FeedStockService(db)
    feed_type = service.toggle_suspend(feed_type_id, current_user.id)
    return FeedStockOut.model_validate(feed_type)


@router.delete(
    "/{feed_type_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un tipo de alimento",
)
def delete_feed_stock(
    feed_type_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Elimina un tipo de alimento del inventario.

    Los registros históricos de alimentación conservan el nombre del
    alimento con `feed_type_id` nulo.

    Args:
        feed_type_id: Identificador del tipo de alimento.
        db: Sesión de base de datos inyectada por FastAPI.
        current_user: Usuario autenticado.
    """
    service = FeedStockService(db)
    service.delete_feed_type(feed_type_id, current_user.id)


@router.get(
    "/{feed_type_id}/movements",
    response_model=list[FeedStockMovementOut],
    summary="Listar movimientos de stock de un tipo de alimento",
)
def list_feed_stock_movements(
    feed_type_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(get_current_user),
) -> list[FeedStockMovementOut]:
    """Lista los movimientos de ingreso de stock de un alimento.

    Args:
        feed_type_id: Identificador del tipo de alimento.
        db: Sesión de base de datos inyectada por FastAPI.

    Returns:
        Lista de movimientos del alimento.
    """
    service = FeedStockService(db)
    return [
        FeedStockMovementOut.model_validate(m)
        for m in service.get_movements(feed_type_id)
    ]
