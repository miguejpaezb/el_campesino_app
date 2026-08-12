"""Modelo ORM de enfermedades de los lotes.

Módulo nuevo que no existía en el ejercicio en clase. Amplía el control
sanitario con el registro de enfermedades, síntomas y tratamientos.
"""

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.bird_lot import BirdLot


class Disease(Base):
    """Representa una enfermedad diagnosticada en un lote.

    Attributes:
        id: Identificador único del registro.
        lot_id: Identificador del lote al que pertenece.
        diagnosis_date: Fecha del diagnóstico.
        disease_name: Nombre de la enfermedad.
        affected_quantity: Cantidad de aves afectadas.
        symptoms: Síntomas observados.
        treatment: Tratamiento aplicado.
        treatment_start_date: Fecha de inicio del tratamiento.
        treatment_end_date: Fecha de finalización del tratamiento.
        is_resolved: Indica si la enfermedad fue resuelta.
        created_at: Fecha de creación del registro.
        lot: Relación con el lote propietario.
    """

    __tablename__ = "diseases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    lot_id: Mapped[int] = mapped_column(ForeignKey("bird_lots.id"), index=True)
    diagnosis_date: Mapped[date] = mapped_column(Date, default=date.today)
    disease_name: Mapped[str] = mapped_column(String(100), nullable=False)
    affected_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    symptoms: Mapped[str | None] = mapped_column(String(500), nullable=True)
    treatment: Mapped[str | None] = mapped_column(String(500), nullable=True)
    treatment_start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    treatment_end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_resolved: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    lot: Mapped["BirdLot"] = relationship(back_populates="diseases")
