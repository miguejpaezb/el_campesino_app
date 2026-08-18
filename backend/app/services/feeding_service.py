"""Servicio de lógica de negocio de la alimentación.

Adapta `registrar_alimentacion` y `total_alimento` del ejercicio en clase
(`docs/ejercicio_en_clase/domain/lote.py`) a SQLAlchemy y la arquitectura
del backend.
"""

from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.feeding import FeedingRecord
from app.repositories.feed_stock_repository import FeedStockRepository
from app.repositories.feeding_repository import FeedingRepository
from app.schemas.feeding import FeedingCreate
from app.services.lot_service import LotService
from app.services.traceability_service import TraceabilityService


class FeedingService:
    """Lógica de negocio de la alimentación de los lotes.

    Attributes:
        repository: Repositorio de alimentación usado para la persistencia.
        lot_service: Servicio de lotes para validar el lote propietario.
    """

    def __init__(self, db: Session):
        self.db = db
        self.repository = FeedingRepository(db)
        self.feed_stock_repository = FeedStockRepository(db)
        self.lot_service = LotService(db)

    def register_feeding(
        self, lot_id: int, data: FeedingCreate, user_id: int
    ) -> FeedingRecord:
        """Registra el suministro de alimento de un lote.

        Aplica la regla de negocio del ejercicio en clase: el lote debe
        existir y estar activo. Si se indica `feed_type_id`, el alimento
        debe existir, estar activo y tener stock suficiente; se descuenta
        el stock y el costo se toma del inventario.

        Args:
            lot_id: Identificador del lote.
            data: Datos validados del registro.
            user_id: Usuario que ejecuta la acción.

        Returns:
            El registro de alimentación creado.

        Raises:
            HTTPException 404: Si el lote no existe.
            HTTPException 400: Si el lote está inactivo, el alimento no
                existe, está suspendido o no hay stock suficiente.
        """
        lot = self.lot_service.get_lot(lot_id)

        if not lot.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El lote está inactivo, no se puede registrar alimentación",
            )

        feed_type = None
        if data.feed_type_id is not None:
            feed_type = self.feed_stock_repository.get(data.feed_type_id)
            if feed_type is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="El tipo de alimento no existe",
                )
            if not feed_type.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El tipo de alimento está suspendido",
                )
            if feed_type.stock_kg < data.kilos:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "Stock insuficiente: hay "
                        f"{feed_type.stock_kg} kg de {feed_type.name}"
                    ),
                )

        feed_type_name = None
        if data.feed_type:
            feed_type_name = data.feed_type
        elif feed_type is not None:
            feed_type_name = feed_type.name
        if not feed_type_name:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Debes indicar el tipo de alimento",
            )

        cost_per_kilo = (
            feed_type.cost_per_kilo if feed_type is not None else data.cost_per_kilo
        )

        record = FeedingRecord(
            lot_id=lot.id,
            feed_type_id=feed_type.id if feed_type is not None else None,
            week=data.week if data.week is not None else lot.current_week,
            feed_date=data.feed_date or date.today(),
            feed_type=feed_type_name,
            kilos=data.kilos,
            cost_per_kilo=cost_per_kilo,
            observations=data.observations,
        )
        record = self.repository.create(record)

        if feed_type is not None:
            feed_type.stock_kg = round(feed_type.stock_kg - data.kilos, 2)
            self.feed_stock_repository.update(feed_type)

        TraceabilityService(self.db).log_event(
            "FeedingRecord",
            record.id,
            "CREATE",
            user_id,
            changes={
                "lot_id": record.lot_id,
                "week": record.week,
                "feed_type": record.feed_type,
                "feed_type_id": record.feed_type_id,
                "kilos": record.kilos,
            },
        )
        return record

    def get_feeding_by_lot(self, lot_id: int) -> list[FeedingRecord]:
        """Lista los registros de alimentación de un lote.

        Args:
            lot_id: Identificador del lote.

        Returns:
            Lista de registros de alimentación del lote.

        Raises:
            HTTPException 404: Si el lote no existe.
        """
        lot = self.lot_service.get_lot(lot_id)
        return self.repository.get_by_lot(lot.id)

    def get_total_feed(self, lot_id: int) -> float:
        """Calcula el total de alimento consumido por un lote.

        Equivale a `total_alimento()` del ejercicio en clase.

        Args:
            lot_id: Identificador del lote.

        Returns:
            Total de kilos de alimento consumidos.

        Raises:
            HTTPException 404: Si el lote no existe.
        """
        self.lot_service.get_lot(lot_id)
        records = self.repository.get_by_lot(lot_id)
        return round(sum(r.kilos for r in records), 2)

    def get_total_feed_cost(self, lot_id: int) -> float:
        """Calcula el costo total de alimentación de un lote.

        Suma `kilos x cost_per_kilo` de los registros que tienen costo.
        Este indicador no existía en el ejercicio en clase.

        Args:
            lot_id: Identificador del lote.

        Returns:
            Costo total de la alimentación del lote.

        Raises:
            HTTPException 404: Si el lote no existe.
        """
        self.lot_service.get_lot(lot_id)
        records = self.repository.get_by_lot(lot_id)
        total = sum(
            r.kilos * r.cost_per_kilo for r in records if r.cost_per_kilo is not None
        )
        return round(total, 2)
