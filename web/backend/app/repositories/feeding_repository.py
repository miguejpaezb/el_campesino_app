"""Repositorio de acceso a datos para la alimentación.

Encapsula las consultas a la tabla `feeding_records` mediante SQLAlchemy,
abstrayendo a la capa de servicios de los detalles de persistencia.
"""

from sqlalchemy.orm import Session

from app.models.feeding import FeedingRecord


class FeedingRepository:
    """Acceso a datos de la entidad `FeedingRecord`."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_lot(self, lot_id: int) -> list[FeedingRecord]:
        """Lista los registros de alimentación de un lote.

        Args:
            lot_id: Identificador del lote.

        Returns:
            Lista con los registros encontrados.
        """
        return (
            self.db.query(FeedingRecord)
            .filter(FeedingRecord.lot_id == lot_id)
            .all()
        )

    def create(self, record: FeedingRecord) -> FeedingRecord:
        """Persiste un nuevo registro de alimentación.

        Args:
            record: Instancia de `FeedingRecord` a crear.

        Returns:
            El registro recién creado.
        """
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record
