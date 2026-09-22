"""Servicio de lógica de negocio del inventario de insumos (alimentos).

Administra los tipos de alimento, su stock, el ingreso de nuevos kilos y
las operaciones de suspender o eliminar. Cada acción que modifica datos
genera un evento de trazabilidad.
"""

from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.feed_stock import FeedStockMovement, FeedType
from app.models.feeding import FeedingRecord
from app.repositories.feed_stock_repository import FeedStockRepository
from app.schemas.feed_stock import (
    FeedStockAddStock,
    FeedStockCreate,
    FeedStockUpdate,
)
from app.services.traceability_service import TraceabilityService


class FeedStockService:
    """Lógica de negocio del inventario de alimentos.

    Attributes:
        repository: Repositorio del inventario usado para la persistencia.
    """

    def __init__(self, db: Session):
        self.db = db
        self.repository = FeedStockRepository(db)
        self.traceability = TraceabilityService(db)

    def list_feed_types(self, search: str | None = None) -> list[FeedType]:
        """Lista los tipos de alimento, opcionalmente filtrados por búsqueda.

        Args:
            search: Texto de búsqueda por nombre (opcional).

        Returns:
            Lista de tipos de alimento.
        """
        feed_types = self.repository.get_all()
        if not search or not search.strip():
            return feed_types
        term = search.strip().lower()
        return [ft for ft in feed_types if term in ft.name.lower()]

    def create_feed_type(
        self, data: FeedStockCreate, user_id: int
    ) -> FeedType:
        """Crea un tipo de alimento con su stock inicial.

        Args:
            data: Datos validados del nuevo alimento.
            user_id: Usuario que ejecuta la acción.

        Returns:
            El tipo de alimento creado.

        Raises:
            HTTPException 400: Si ya existe un alimento con ese nombre.
        """
        if self.repository.get_by_name(data.name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un alimento con ese nombre",
            )

        entry_date = data.entry_date or date.today()
        feed_type = FeedType(
            name=data.name.strip(),
            stock_kg=data.stock_kg,
            min_stock_kg=data.min_stock_kg,
            cost_per_kilo=data.cost_per_kilo,
            last_stock_date=entry_date if data.stock_kg > 0 else None,
        )
        feed_type = self.repository.create(feed_type)

        if data.stock_kg > 0:
            self.repository.create_movement(
                FeedStockMovement(
                    feed_type_id=feed_type.id,
                    kilos_added=data.stock_kg,
                    cost_per_kilo=data.cost_per_kilo,
                    entry_date=entry_date,
                )
            )

        self.traceability.log_event(
            "FeedType",
            feed_type.id,
            "CREATE",
            user_id,
            changes={
                "name": feed_type.name,
                "stock_kg": feed_type.stock_kg,
                "cost_per_kilo": feed_type.cost_per_kilo,
            },
        )
        return feed_type

    def update_feed_type(
        self, feed_type_id: int, data: FeedStockUpdate, user_id: int
    ) -> FeedType:
        """Actualiza el nombre y el stock mínimo de un tipo de alimento.

        Args:
            feed_type_id: Identificador del tipo de alimento.
            data: Campos a actualizar.
            user_id: Usuario que ejecuta la acción.

        Returns:
            El tipo de alimento actualizado.

        Raises:
            HTTPException 404: Si el alimento no existe.
            HTTPException 400: Si el nuevo nombre ya está en uso.
        """
        feed_type = self.repository.get(feed_type_id)
        if feed_type is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El tipo de alimento no existe",
            )

        changes: dict = {}
        if data.name is not None and data.name.strip() != feed_type.name:
            existing = self.repository.get_by_name(data.name.strip())
            if existing is not None and existing.id != feed_type_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ya existe un alimento con ese nombre",
                )
            feed_type.name = data.name.strip()
            changes["name"] = feed_type.name
        if data.min_stock_kg is not None:
            feed_type.min_stock_kg = data.min_stock_kg
            changes["min_stock_kg"] = feed_type.min_stock_kg

        feed_type = self.repository.update(feed_type)
        if changes:
            self.traceability.log_event(
                "FeedType", feed_type.id, "UPDATE", user_id, changes=changes
            )
        return feed_type

    def add_stock(
        self, feed_type_id: int, data: FeedStockAddStock, user_id: int
    ) -> FeedType:
        """Añade kilos al stock de un tipo de alimento.

        Si `price_option` es "new" se actualiza el costo por kilo con el
        valor enviado; si es "same" se conserva el último precio.

        Args:
            feed_type_id: Identificador del tipo de alimento.
            data: Datos del ingreso de stock.
            user_id: Usuario que ejecuta la acción.

        Returns:
            El tipo de alimento actualizado.

        Raises:
            HTTPException 404: Si el alimento no existe.
            HTTPException 400: Si se requiere un nuevo precio y no se envía.
        """
        feed_type = self.repository.get(feed_type_id)
        if feed_type is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El tipo de alimento no existe",
            )

        entry_date = data.entry_date or date.today()
        cost_per_kilo = feed_type.cost_per_kilo
        if data.price_option == "new":
            if data.cost_per_kilo is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Debes indicar el nuevo costo por kilo",
                )
            cost_per_kilo = data.cost_per_kilo

        feed_type.stock_kg = round(feed_type.stock_kg + data.kilos_added, 2)
        feed_type.cost_per_kilo = cost_per_kilo
        feed_type.last_stock_date = entry_date
        feed_type = self.repository.update(feed_type)

        self.repository.create_movement(
            FeedStockMovement(
                feed_type_id=feed_type.id,
                kilos_added=data.kilos_added,
                cost_per_kilo=cost_per_kilo,
                entry_date=entry_date,
            )
        )

        self.traceability.log_event(
            "FeedType",
            feed_type.id,
            "UPDATE",
            user_id,
            changes={
                "kilos_added": data.kilos_added,
                "stock_kg": feed_type.stock_kg,
                "cost_per_kilo": cost_per_kilo,
            },
        )
        return feed_type

    def toggle_suspend(self, feed_type_id: int, user_id: int) -> FeedType:
        """Suspende o reactiva un tipo de alimento.

        Args:
            feed_type_id: Identificador del tipo de alimento.
            user_id: Usuario que ejecuta la acción.

        Returns:
            El tipo de alimento actualizado.

        Raises:
            HTTPException 404: Si el alimento no existe.
        """
        feed_type = self.repository.get(feed_type_id)
        if feed_type is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El tipo de alimento no existe",
            )

        feed_type.is_active = not feed_type.is_active
        feed_type = self.repository.update(feed_type)
        self.traceability.log_event(
            "FeedType",
            feed_type.id,
            "UPDATE",
            user_id,
            changes={"is_active": feed_type.is_active},
        )
        return feed_type

    def delete_feed_type(self, feed_type_id: int, user_id: int) -> None:
        """Elimina un tipo de alimento del inventario.

        Los registros históricos de alimentación que lo referencian quedan
        con `feed_type_id` nulo pero conservan el nombre del alimento, de
        modo que el historial sigue mostrando qué producto se suministró.

        Args:
            feed_type_id: Identificador del tipo de alimento.
            user_id: Usuario que ejecuta la acción.

        Raises:
            HTTPException 404: Si el alimento no existe.
        """
        feed_type = self.repository.get(feed_type_id)
        if feed_type is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El tipo de alimento no existe",
            )

        name = feed_type.name
        self.traceability.log_event(
            "FeedType",
            feed_type_id,
            "DELETE",
            user_id,
            changes={"name": name},
        )

        (
            self.db.query(FeedingRecord)
            .filter(FeedingRecord.feed_type_id == feed_type_id)
            .update({FeedingRecord.feed_type_id: None})
        )
        self.db.commit()
        self.repository.delete(feed_type)

    def get_movements(self, feed_type_id: int) -> list[FeedStockMovement]:
        """Lista los movimientos de ingreso de stock de un alimento.

        Args:
            feed_type_id: Identificador del tipo de alimento.

        Returns:
            Lista de movimientos del alimento en orden cronológico inverso.
        """
        feed_type = self.repository.get(feed_type_id)
        if feed_type is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El tipo de alimento no existe",
            )
        return (
            self.db.query(FeedStockMovement)
            .filter(FeedStockMovement.feed_type_id == feed_type_id)
            .order_by(FeedStockMovement.created_at.desc())
            .all()
        )
