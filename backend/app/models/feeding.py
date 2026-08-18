"""Modelo ORM del registro de alimentación.

Adapta `RegistroAlimentacion` del ejercicio en clase
(`docs/ejercicio_en_clase/domain/lote.py`) a SQLAlchemy 2.0.
"""

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.bird_lot import BirdLot
    from app.models.feed_stock import FeedType


class FeedingRecord(Base):
    """Representa un registro de alimentación de un lote.

    Attributes:
        id: Identificador único del registro.
        lot_id: Identificador del lote al que pertenece.
        feed_type_id: Identificador del tipo de alimento del inventario
            (si el registro proviene del inventario; se anula al eliminar
            el alimento).
        week: Semana del ciclo en la que se registró (antes semana).
        feed_date: Fecha del suministro de alimento.
        feed_type: Nombre del alimento suministrado (snapshot del nombre).
        kilos: Cantidad de alimento en kilos (antes kilos).
        cost_per_kilo: Costo por kilo del alimento.
        observations: Observaciones del registro.
        created_at: Fecha de creación del registro.
        lot: Relación con el lote propietario.
        feed_type_rel: Relación con el tipo de alimento del inventario.
    """

    __tablename__ = "feeding_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    lot_id: Mapped[int] = mapped_column(ForeignKey("bird_lots.id"), index=True)
    feed_type_id: Mapped[int | None] = mapped_column(
        ForeignKey("feed_types.id"), nullable=True, index=True
    )
    week: Mapped[int] = mapped_column(Integer, nullable=False)
    feed_date: Mapped[date] = mapped_column(Date, default=date.today)
    feed_type: Mapped[str] = mapped_column(String(50), nullable=False)
    kilos: Mapped[float] = mapped_column(Float, nullable=False)
    cost_per_kilo: Mapped[float | None] = mapped_column(Float, nullable=True)
    observations: Mapped[str | None] = mapped_column(String(300), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    lot: Mapped["BirdLot"] = relationship(back_populates="feeding_records")
    feed_type_rel: Mapped["FeedType | None"] = relationship(
        back_populates="feeding_records"
    )

    @property
    def total_cost(self) -> float | None:
        """Costo total del registro (kilos x costo por kilo).

        Returns:
            Costo total redondeado a 2 decimales, o None si no hay costo.
        """
        if self.cost_per_kilo is None:
            return None
        return round(self.kilos * self.cost_per_kilo, 2)
