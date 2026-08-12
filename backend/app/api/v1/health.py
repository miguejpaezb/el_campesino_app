"""Endpoints del módulo de sanidad.

Expone las vacunas, la mortalidad (con sus porcentajes) y las enfermedades
de cada lote.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.disease import DiseaseCreate, DiseaseOut, DiseaseUpdate
from app.schemas.mortality import MortalityCreate, MortalityOut
from app.schemas.vaccination import VaccinationCreate, VaccinationOut
from app.services.health_service import HealthService

router = APIRouter()


# ============================ Vacunas ============================


@router.get(
    "/{lot_id}/vaccinations",
    response_model=list[VaccinationOut],
    summary="Listar vacunas de un lote",
)
def list_vaccinations(
    lot_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(get_current_user),
) -> list[VaccinationOut]:
    """Lista las vacunas aplicadas a un lote.

    Args:
        lot_id: Identificador del lote.
        db: Sesión de base de datos inyectada por FastAPI.

    Returns:
        Lista de vacunas del lote.
    """
    service = HealthService(db)
    records = service.get_vaccinations(lot_id)
    return [VaccinationOut.model_validate(r) for r in records]


@router.post(
    "/{lot_id}/vaccinations",
    response_model=VaccinationOut,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar una vacuna",
)
def register_vaccination(
    lot_id: int,
    payload: VaccinationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> VaccinationOut:
    """Registra una vacuna aplicada a un lote.

    Args:
        lot_id: Identificador del lote.
        payload: Datos de la vacuna.
        db: Sesión de base de datos inyectada por FastAPI.
        current_user: Usuario autenticado.

    Returns:
        La vacuna registrada.
    """
    service = HealthService(db)
    record = service.register_vaccine(lot_id, payload, current_user.id)
    return VaccinationOut.model_validate(record)


# ============================ Mortalidad ============================


@router.get(
    "/{lot_id}/mortality",
    response_model=list[MortalityOut],
    summary="Listar mortalidad de un lote",
)
def list_mortality(
    lot_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(get_current_user),
) -> list[MortalityOut]:
    """Lista los registros de mortalidad de un lote.

    Args:
        lot_id: Identificador del lote.
        db: Sesión de base de datos inyectada por FastAPI.

    Returns:
        Lista de registros de mortalidad del lote.
    """
    service = HealthService(db)
    records = service.get_mortalities(lot_id)
    return [MortalityOut.model_validate(r) for r in records]


@router.post(
    "/{lot_id}/mortality",
    response_model=MortalityOut,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar mortalidad",
    description="Registra mortalidad y actualiza la cantidad de aves del lote. "
    "Si el lote queda sin aves, se desactiva automáticamente.",
)
def register_mortality(
    lot_id: int,
    payload: MortalityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MortalityOut:
    """Registra la mortalidad de un lote y ajusta sus aves.

    Args:
        lot_id: Identificador del lote.
        payload: Datos del registro.
        db: Sesión de base de datos inyectada por FastAPI.
        current_user: Usuario autenticado.

    Returns:
        El registro de mortalidad creado.
    """
    service = HealthService(db)
    record = service.register_mortality(lot_id, payload, current_user.id)
    return MortalityOut.model_validate(record)


@router.get(
    "/{lot_id}/mortality/stats",
    summary="Porcentajes de mortalidad y supervivencia",
)
def mortality_stats(
    lot_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(get_current_user),
) -> dict[str, float]:
    """Devuelve los porcentajes de mortalidad y supervivencia del lote.

    Args:
        lot_id: Identificador del lote.
        db: Sesión de base de datos inyectada por FastAPI.

    Returns:
        Diccionario con ambos porcentajes.
    """
    service = HealthService(db)
    return {
        "lot_id": lot_id,
        "mortality_percentage": service.get_mortality_percentage(lot_id),
        "survival_percentage": service.get_survival_percentage(lot_id),
    }


# ============================ Enfermedades ============================


@router.get(
    "/{lot_id}/diseases",
    response_model=list[DiseaseOut],
    summary="Listar enfermedades de un lote",
)
def list_diseases(
    lot_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(get_current_user),
) -> list[DiseaseOut]:
    """Lista las enfermedades diagnosticadas en un lote.

    Args:
        lot_id: Identificador del lote.
        db: Sesión de base de datos inyectada por FastAPI.

    Returns:
        Lista de enfermedades del lote.
    """
    service = HealthService(db)
    records = service.get_diseases(lot_id)
    return [DiseaseOut.model_validate(r) for r in records]


@router.post(
    "/{lot_id}/diseases",
    response_model=DiseaseOut,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar una enfermedad",
)
def register_disease(
    lot_id: int,
    payload: DiseaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DiseaseOut:
    """Registra una enfermedad diagnosticada en un lote.

    Args:
        lot_id: Identificador del lote.
        payload: Datos de la enfermedad.
        db: Sesión de base de datos inyectada por FastAPI.
        current_user: Usuario autenticado.

    Returns:
        La enfermedad registrada.
    """
    service = HealthService(db)
    record = service.register_disease(lot_id, payload, current_user.id)
    return DiseaseOut.model_validate(record)


@router.put(
    "/{lot_id}/diseases/{disease_id}",
    response_model=DiseaseOut,
    summary="Actualizar tratamiento de una enfermedad",
)
def update_disease(
    lot_id: int,
    disease_id: int,
    payload: DiseaseUpdate,
    db: Session = Depends(get_db),
    _: object = Depends(get_current_user),
) -> DiseaseOut:
    """Actualiza el tratamiento y estado de una enfermedad.

    Args:
        lot_id: Identificador del lote.
        disease_id: Identificador de la enfermedad.
        payload: Campos a actualizar.
        db: Sesión de base de datos inyectada por FastAPI.

    Returns:
        La enfermedad actualizada.
    """
    service = HealthService(db)
    record = service.update_treatment(lot_id, disease_id, payload)
    return DiseaseOut.model_validate(record)


@router.post(
    "/{lot_id}/diseases/{disease_id}/resolve",
    response_model=DiseaseOut,
    summary="Marcar una enfermedad como resuelta",
)
def resolve_disease(
    lot_id: int,
    disease_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(get_current_user),
) -> DiseaseOut:
    """Marca una enfermedad como resuelta.

    Args:
        lot_id: Identificador del lote.
        disease_id: Identificador de la enfermedad.
        db: Sesión de base de datos inyectada por FastAPI.

    Returns:
        La enfermedad resuelta.
    """
    service = HealthService(db)
    record = service.resolve_disease(lot_id, disease_id)
    return DiseaseOut.model_validate(record)
