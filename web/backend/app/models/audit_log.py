"""Modelo ORM del registro de auditoría (trazabilidad).

Implementa una cadena de hash SHA-256 simulando blockchain para garantizar
la integridad e inmutabilidad del historial de cambios de cada entidad.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class AuditLog(Base):
    """Representa un evento de auditoría de una entidad.

    Attributes:
        id: Identificador único del registro.
        entity_type: Tipo de entidad auditada ("BirdLot", "EggProduction", etc.).
        entity_id: Identificador de la entidad auditada.
        action: Acción registrada ("CREATE", "UPDATE", "DELETE").
        user_id: Usuario que ejecutó la acción.
        previous_hash: Hash del registro anterior de la misma entidad.
        current_hash: Hash del registro actual (encadena el historial).
        changes: JSON con los cambios realizados.
        timestamp: Fecha y hora del evento.
        user: Relación con el usuario que ejecutó la acción.
    """

    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entity_type: Mapped[str] = mapped_column(String(50), index=True)
    entity_id: Mapped[int] = mapped_column(Integer, index=True)
    action: Mapped[str] = mapped_column(String(20))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    previous_hash: Mapped[str] = mapped_column(String(64))
    current_hash: Mapped[str] = mapped_column(String(64))
    changes: Mapped[str | None] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    user: Mapped["User"] = relationship()
