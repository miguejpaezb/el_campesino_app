"""Modelo ORM de la producción diaria de huevos.

Adapta `RegistroPosturas` del ejercicio en clase
(`docs/ejercicio_en_clase/domain/lote.py`) a SQLAlchemy 2.0.
"""

from datetime import date, datetime, time
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, Time, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.bird_lot import BirdLot


class EggProduction(Base):
    """Representa un registro de producción diaria de huevos.

    Attributes:
        id: Identificador único del registro.
        lot_id: Identificador del lote al que pertenece.
        week: Semana del ciclo en la que se registró (antes semana).
        collection_date: Fecha de recolección de los huevos.
        collection_time: Hora de recolección de los huevos.
        egg_count: Cantidad de huevos recolectados (antes cantidad_huevos).
        avg_weight_grams: Peso promedio por huevo en gramos.
        broken_eggs: Cantidad de huevos rotos en la recolección.
        observations: Observaciones del registro.
        created_at: Fecha de creación del registro.
        lot: Relación con el lote propietario.
    """

    __tablename__ = "egg_production"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    lot_id: Mapped[int] = mapped_column(ForeignKey("bird_lots.id"), index=True)
    week: Mapped[int] = mapped_column(Integer, nullable=False)
    collection_date: Mapped[date] = mapped_column(Date, default=date.today)
    collection_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    egg_count: Mapped[int] = mapped_column(Integer, nullable=False)
    avg_weight_grams: Mapped[float | None] = mapped_column(Float, nullable=True)
    broken_eggs: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    observations: Mapped[str | None] = mapped_column(String(300), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    lot: Mapped["BirdLot"] = relationship(back_populates="egg_productions")
