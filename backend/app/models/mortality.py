"""Modelo ORM del registro de mortalidad.

Adapta `RegistroMortalidad` del ejercicio en clase
(`docs/ejercicio_en_clase/domain/lote.py`) a SQLAlchemy 2.0.
"""

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.bird_lot import BirdLot


class Mortality(Base):
    """Representa un registro de mortalidad de un lote.

    Attributes:
        id: Identificador único del registro.
        lot_id: Identificador del lote al que pertenece.
        week: Semana del ciclo en la que ocurrió (antes semana).
        event_date: Fecha del evento.
        quantity: Cantidad de aves muertas (antes cantidad).
        cause: Causa de la mortalidad (antes causa).
        observations: Observaciones del registro.
        created_at: Fecha de creación del registro.
        lot: Relación con el lote propietario.
    """

    __tablename__ = "mortality"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    lot_id: Mapped[int] = mapped_column(ForeignKey("bird_lots.id"), index=True)
    week: Mapped[int] = mapped_column(Integer, nullable=False)
    event_date: Mapped[date] = mapped_column(Date, default=date.today)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    cause: Mapped[str] = mapped_column(String(200), nullable=False)
    observations: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    lot: Mapped["BirdLot"] = relationship(back_populates="mortalities")
