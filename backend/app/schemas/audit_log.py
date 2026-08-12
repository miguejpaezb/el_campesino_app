"""Schemas Pydantic para la trazabilidad (auditoría).

Define el DTO de salida de los registros de auditoría y la respuesta de
verificación de la cadena de hash.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuditLogOut(BaseModel):
    """Datos de un registro de auditoría para la respuesta de la API.

    Attributes:
        id: Identificador del registro.
        entity_type: Tipo de entidad auditada.
        entity_id: Identificador de la entidad.
        action: Acción registrada.
        user_id: Usuario que ejecutó la acción.
        previous_hash: Hash del registro anterior.
        current_hash: Hash del registro actual.
        changes: Cambios realizados (JSON).
        timestamp: Fecha y hora del evento.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    entity_type: str
    entity_id: int
    action: str
    user_id: int
    previous_hash: str
    current_hash: str
    changes: str | None
    timestamp: datetime


class ChainVerifyResult(BaseModel):
    """Resultado de la verificación de integridad de la cadena.

    Attributes:
        entity_type: Tipo de entidad verificada.
        entity_id: Identificador de la entidad.
        valid: True si la cadena de hash es íntegra.
        entries: Cantidad de registros en la cadena.
        detail: Detalle del resultado de la verificación.
    """

    entity_type: str
    entity_id: int
    valid: bool
    entries: int
    detail: str
