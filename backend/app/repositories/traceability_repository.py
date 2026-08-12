"""Repositorio de acceso a datos para la trazabilidad.

Encapsula las consultas a la tabla `audit_logs` mediante SQLAlchemy,
abstrayendo a la capa de servicios de los detalles de persistencia.
"""

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


class TraceabilityRepository:
    """Acceso a datos de la entidad `AuditLog`."""

    def __init__(self, db: Session):
        self.db = db

    def get_history(self, entity_type: str, entity_id: int) -> list[AuditLog]:
        """Lista el historial de auditoría de una entidad en orden cronológico.

        Args:
            entity_type: Tipo de entidad.
            entity_id: Identificador de la entidad.

        Returns:
            Lista con los registros de auditoría de la entidad.
        """
        return (
            self.db.query(AuditLog)
            .filter(
                AuditLog.entity_type == entity_type,
                AuditLog.entity_id == entity_id,
            )
            .order_by(AuditLog.id)
            .all()
        )

    def get_last(self, entity_type: str, entity_id: int) -> AuditLog | None:
        """Obtiene el último registro de auditoría de una entidad.

        Args:
            entity_type: Tipo de entidad.
            entity_id: Identificador de la entidad.

        Returns:
            El último registro o None si no existe ninguno.
        """
        return (
            self.db.query(AuditLog)
            .filter(
                AuditLog.entity_type == entity_type,
                AuditLog.entity_id == entity_id,
            )
            .order_by(AuditLog.id.desc())
            .first()
        )

    def create(self, log: AuditLog) -> AuditLog:
        """Persiste un nuevo registro de auditoría.

        Args:
            log: Instancia de `AuditLog` a crear.

        Returns:
            El registro recién creado.
        """
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log
