"""Modelo ORM de los lotes de aves.

Adapta la entidad `LoteGallinas` del ejercicio en clase
(`docs/ejercicio_en_clase/domain/lote.py`) a SQLAlchemy 2.0. La lógica de
dominio (cálculos y evaluaciones) vive en `app/services/lot_service.py`.
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.constants import CicloProductivo
from app.core.database import Base


class BirdLot(Base):
    """Representa un lote de aves dentro de la granja.

    Attributes:
        id: Identificador único del lote.
        lot_code: Código único del lote (antes id_lote).
        breed: Raza de las aves del lote.
        initial_quantity: Cantidad inicial de aves (cantidad_gallinas_iniciales).
        current_quantity: Cantidad actual de aves (cantidad_gallinas).
        current_week: Semana actual del ciclo (semana_actual).
        entry_date: Fecha de ingreso del lote.
        created_at: Fecha de creación del registro.
        updated_at: Fecha de la última modificación.
        is_active: Si el lote está activo (activo).
        discard_reason: Razón de descarte (razon_descarte).
        observations: Observaciones generales del lote.
    """

    __tablename__ = "bird_lots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    lot_code: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False, index=True
    )
    breed: Mapped[str] = mapped_column(String(50), nullable=False)
    initial_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    current_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    current_week: Mapped[int] = mapped_column(
        Integer, nullable=False, default=CicloProductivo.SEMANA_COMPRA
    )
    entry_date: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    discard_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    observations: Mapped[str | None] = mapped_column(String(500), nullable=True)
