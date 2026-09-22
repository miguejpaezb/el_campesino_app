"""Servicio de trazabilidad con blockchain simulado.

Genera una cadena de hash SHA-256 para el historial de auditoría de cada
entidad. Cada registro incluye el hash del registro anterior (`previous_hash`)
y su propio hash (`current_hash`), lo que garantiza que cualquier alteración
de un registro rompe la cadena y es detectable en la verificación.
"""

import hashlib
import json
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.repositories.traceability_repository import TraceabilityRepository
from app.schemas.audit_log import ChainVerifyResult

GENESIS_HASH = "0" * 64


class TraceabilityService:
    """Lógica de negocio de la trazabilidad de las entidades.

    Attributes:
        repository: Repositorio de auditoría usado para la persistencia.
    """

    def __init__(self, db: Session):
        self.repository = TraceabilityRepository(db)

    @staticmethod
    def _build_payload(log: AuditLog) -> str:
        """Construye el string canónico que se firma con el hash.

        Args:
            log: Registro de auditoría.

        Returns:
            String concatenado con los campos que forman el hash.
        """
        return (
            f"{log.previous_hash}|{log.entity_type}|{log.entity_id}|"
            f"{log.action}|{log.user_id}|{log.changes or ''}|"
            f"{log.timestamp.isoformat()}"
        )

    def _compute_hash(self, log: AuditLog) -> str:
        """Calcula el hash SHA-256 de un registro de auditoría.

        Args:
            log: Registro de auditoría.

        Returns:
            Hash hexadecimal del registro.
        """
        return hashlib.sha256(
            self._build_payload(log).encode("utf-8")
        ).hexdigest()

    def log_event(
        self,
        entity_type: str,
        entity_id: int,
        action: str,
        user_id: int,
        changes: dict | None = None,
    ) -> AuditLog:
        """Registra un evento de auditoría encadenando el hash.

        Args:
            entity_type: Tipo de entidad auditada.
            entity_id: Identificador de la entidad.
            action: Acción registrada ("CREATE", "UPDATE", "DELETE").
            user_id: Usuario que ejecutó la acción.
            changes: Diccionario con los cambios (se serializa a JSON).

        Returns:
            El registro de auditoría creado.
        """
        previous = self.repository.get_last(entity_type, entity_id)
        previous_hash = previous.current_hash if previous else GENESIS_HASH

        changes_json = (
            json.dumps(changes, ensure_ascii=False, sort_keys=True)
            if changes is not None
            else None
        )
        # Timestamp naive en UTC para que el formato sobreviva el round-trip
        # con SQLite y la verificación pueda reproducir el mismo hash.
        timestamp = datetime.now(UTC).replace(tzinfo=None)

        log = AuditLog(
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            user_id=user_id,
            changes=changes_json,
            previous_hash=previous_hash,
            current_hash="",
            timestamp=timestamp,
        )
        log.current_hash = self._compute_hash(log)
        return self.repository.create(log)

    def get_history(self, entity_type: str, entity_id: int) -> list[AuditLog]:
        """Devuelve el historial de auditoría de una entidad.

        Args:
            entity_type: Tipo de entidad.
            entity_id: Identificador de la entidad.

        Returns:
            Lista con los registros de auditoría en orden cronológico.
        """
        return self.repository.get_history(entity_type, entity_id)

    def verify_chain(self, entity_type: str, entity_id: int) -> ChainVerifyResult:
        """Verifica la integridad de la cadena de hash de una entidad.

        Recalcula el hash de cada registro y comprueba que cada
        `previous_hash` coincida con el `current_hash` del registro anterior.

        Args:
            entity_type: Tipo de entidad.
            entity_id: Identificador de la entidad.

        Returns:
            Un `ChainVerifyResult` con el resultado de la verificación.
        """
        logs = self.repository.get_history(entity_type, entity_id)

        if not logs:
            return ChainVerifyResult(
                entity_type=entity_type,
                entity_id=entity_id,
                valid=True,
                entries=0,
                detail="La entidad no tiene registros de auditoría",
            )

        previous_hash = GENESIS_HASH
        valid = True
        tampered_index = None

        for index, log in enumerate(logs):
            if log.previous_hash != previous_hash:
                valid = False
                tampered_index = index
                break
            if self._compute_hash(log) != log.current_hash:
                valid = False
                tampered_index = index
                break
            previous_hash = log.current_hash

        if valid:
            detail = f"La cadena es íntegra ({len(logs)} registros verificados)."
        else:
            detail = f"Se detectó una alteración en el registro #{tampered_index + 1}."

        return ChainVerifyResult(
            entity_type=entity_type,
            entity_id=entity_id,
            valid=valid,
            entries=len(logs),
            detail=detail,
        )
