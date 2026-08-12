"""Modelo ORM del registro de vacunas.

Adapta `RegistroVacuna` del ejercicio en clase
(`docs/ejercicio_en_clase/domain/lote.py`) a SQLAlchemy 2.0.
"""

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.bird_lot import BirdLot


class Vaccination(Base):
    """Representa una vacuna aplicada a un lote.

    Attributes:
        id: Identificador único del registro.
        lot_id: Identificador del lote al que pertenece.
        week: Semana del ciclo en la que se aplicó (antes semana).
        application_date: Fecha de aplicación de la vacuna.
        vaccine_name: Nombre de la vacuna (antes nombre_vacuna).
        dosage: Dosis aplicada (antes dosis).
        batch_number: Número de lote del biológico.
        next_application_date: Fecha de la próxima aplicación (refuerzo).
        created_at: Fecha de creación del registro.
        lot: Relación con el lote propietario.
    """

    __tablename__ = "vaccinations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    lot_id: Mapped[int] = mapped_column(ForeignKey("bird_lots.id"), index=True)
    week: Mapped[int] = mapped_column(Integer, nullable=False)
    application_date: Mapped[date] = mapped_column(Date, default=date.today)
    vaccine_name: Mapped[str] = mapped_column(String(100), nullable=False)
    dosage: Mapped[str] = mapped_column(String(50), nullable=False)
    batch_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    next_application_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    lot: Mapped["BirdLot"] = relationship(back_populates="vaccinations")
