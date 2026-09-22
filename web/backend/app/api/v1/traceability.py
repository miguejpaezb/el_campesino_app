"""Endpoints de trazabilidad (blockchain simulado).

Expone el historial de auditoría de una entidad y la verificación de
integridad de su cadena de hash.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.schemas.audit_log import AuditLogOut, ChainVerifyResult
from app.services.traceability_service import TraceabilityService

router = APIRouter()


@router.get(
    "/{entity_type}/{entity_id}",
    response_model=list[AuditLogOut],
    summary="Historial de trazabilidad de una entidad",
    description="Devuelve el historial de auditoría (cadena de hash) de una "
    "entidad. Ej.: /api/v1/traceability/BirdLot/1",
)
def get_history(
    entity_type: str,
    entity_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(get_current_user),
) -> list[AuditLogOut]:
    """Devuelve el historial de auditoría de una entidad.

    Args:
        entity_type: Tipo de entidad (BirdLot, EggProduction, etc.).
        entity_id: Identificador de la entidad.
        db: Sesión de base de datos inyectada por FastAPI.

    Returns:
        Lista de registros de auditoría en orden cronológico.
    """
    service = TraceabilityService(db)
    logs = service.get_history(entity_type, entity_id)
    return [AuditLogOut.model_validate(log) for log in logs]


@router.post(
    "/verify/{entity_type}/{entity_id}",
    response_model=ChainVerifyResult,
    summary="Verificar la integridad de la cadena",
    description="Recalcula los hash de la cadena y verifica que no hubo "
    "alteraciones.",
)
def verify_chain(
    entity_type: str,
    entity_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(get_current_user),
) -> ChainVerifyResult:
    """Verifica la integridad de la cadena de hash de una entidad.

    Args:
        entity_type: Tipo de entidad.
        entity_id: Identificador de la entidad.
        db: Sesión de base de datos inyectada por FastAPI.

    Returns:
        Resultado de la verificación de la cadena.
    """
    service = TraceabilityService(db)
    return service.verify_chain(entity_type, entity_id)
