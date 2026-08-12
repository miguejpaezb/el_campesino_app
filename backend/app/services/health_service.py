"""Servicio de lógica de negocio del módulo de sanidad.

Adapta `registrar_vacuna`, `registrar_mortalidad`, `calcular_porcentaje_
mortalidad` y `calcular_porcentaje_supervivencia` del ejercicio en clase
(`docs/ejercicio_en_clase/domain/lote.py`). Incluye el módulo nuevo de
enfermedades.
"""

from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.disease import Disease
from app.models.mortality import Mortality
from app.models.vaccination import Vaccination
from app.repositories.health_repository import HealthRepository
from app.schemas.disease import DiseaseCreate, DiseaseUpdate
from app.schemas.mortality import MortalityCreate
from app.schemas.vaccination import VaccinationCreate
from app.services.lot_service import LotService
from app.services.traceability_service import TraceabilityService


class HealthService:
    """Lógica de negocio de vacunas, mortalidad y enfermedades.

    Attributes:
        repository: Repositorio de sanidad usado para la persistencia.
        lot_service: Servicio de lotes para validar el lote propietario.
    """

    def __init__(self, db: Session):
        self.db = db
        self.repository = HealthRepository(db)
        self.lot_service = LotService(db)

    # ============================ Vacunas ============================

    def register_vaccine(
        self, lot_id: int, data: VaccinationCreate, user_id: int
    ) -> Vaccination:
        """Registra una vacuna aplicada a un lote.

        Aplica la regla de negocio del ejercicio en clase: el lote debe
        existir y estar activo.

        Args:
            lot_id: Identificador del lote.
            data: Datos validados de la vacuna.
            user_id: Usuario que ejecuta la acción.

        Returns:
            La vacuna registrada.

        Raises:
            HTTPException 404: Si el lote no existe.
            HTTPException 400: Si el lote está inactivo.
        """
        lot = self.lot_service.get_lot(lot_id)

        if not lot.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El lote está inactivo, no se puede registrar vacuna",
            )

        record = Vaccination(
            lot_id=lot.id,
            week=data.week if data.week is not None else lot.current_week,
            application_date=data.application_date or date.today(),
            vaccine_name=data.vaccine_name,
            dosage=data.dosage,
            batch_number=data.batch_number,
            next_application_date=data.next_application_date,
        )
        record = self.repository.create_vaccination(record)
        TraceabilityService(self.db).log_event(
            "Vaccination",
            record.id,
            "CREATE",
            user_id,
            changes={
                "lot_id": record.lot_id,
                "week": record.week,
                "vaccine_name": record.vaccine_name,
                "dosage": record.dosage,
            },
        )
        return record

    def get_vaccinations(self, lot_id: int) -> list[Vaccination]:
        """Lista las vacunas aplicadas a un lote.

        Args:
            lot_id: Identificador del lote.

        Returns:
            Lista de vacunas del lote.

        Raises:
            HTTPException 404: Si el lote no existe.
        """
        lot = self.lot_service.get_lot(lot_id)
        return self.repository.get_vaccinations(lot.id)

    # ============================ Mortalidad ============================

    def register_mortality(
        self, lot_id: int, data: MortalityCreate, user_id: int
    ) -> Mortality:
        """Registra la mortalidad de un lote y actualiza sus aves.

        Aplica las reglas de negocio del ejercicio en clase:
          - El lote debe existir y estar activo.
          - La cantidad muerta no puede exceder las aves actuales.
          - Si el lote queda sin aves, se desactiva con la razón
            "Muerte de todas las gallinas".

        Args:
            lot_id: Identificador del lote.
            data: Datos validados del registro.
            user_id: Usuario que ejecuta la acción.

        Returns:
            El registro de mortalidad creado.

        Raises:
            HTTPException 404: Si el lote no existe.
            HTTPException 400: Si el lote está inactivo o la cantidad
                excede las aves actuales.
        """
        lot = self.lot_service.get_lot(lot_id)

        if not lot.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El lote está inactivo, no se puede registrar mortalidad",
            )

        if data.quantity > lot.current_quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "La cantidad de aves muertas excede las aves actuales "
                    f"({lot.current_quantity})"
                ),
            )

        record = Mortality(
            lot_id=lot.id,
            week=data.week if data.week is not None else lot.current_week,
            event_date=data.event_date or date.today(),
            quantity=data.quantity,
            cause=data.cause,
            observations=data.observations,
        )
        self.repository.create_mortality(record)
        TraceabilityService(self.db).log_event(
            "Mortality",
            record.id,
            "CREATE",
            user_id,
            changes={
                "lot_id": record.lot_id,
                "week": record.week,
                "quantity": record.quantity,
                "cause": record.cause,
            },
        )

        lot.current_quantity -= data.quantity
        if lot.current_quantity <= 0:
            lot.current_quantity = 0
            lot.is_active = False
            lot.discard_reason = "Muerte de todas las gallinas"
        self.lot_service.save_lot(lot)

        return record

    def get_mortalities(self, lot_id: int) -> list[Mortality]:
        """Lista los registros de mortalidad de un lote.

        Args:
            lot_id: Identificador del lote.

        Returns:
            Lista de registros de mortalidad del lote.

        Raises:
            HTTPException 404: Si el lote no existe.
        """
        lot = self.lot_service.get_lot(lot_id)
        return self.repository.get_mortalities(lot.id)

    def get_total_mortality(self, lot_id: int) -> int:
        """Calcula el total de aves muertas de un lote.

        Equivale a `total_mortalidad()` del ejercicio en clase.

        Args:
            lot_id: Identificador del lote.

        Returns:
            Total de aves muertas del lote.

        Raises:
            HTTPException 404: Si el lote no existe.
        """
        self.lot_service.get_lot(lot_id)
        records = self.repository.get_mortalities(lot_id)
        return sum(r.quantity for r in records)

    def get_mortality_percentage(self, lot_id: int) -> float:
        """Calcula el porcentaje de mortalidad de un lote.

        Equivale a `calcular_porcentaje_mortalidad()` del ejercicio.

        Args:
            lot_id: Identificador del lote.

        Returns:
            Porcentaje de mortalidad redondeado a 2 decimales.

        Raises:
            HTTPException 404: Si el lote no existe.
        """
        lot = self.lot_service.get_lot(lot_id)
        if lot.initial_quantity == 0:
            return 0.0

        total = self.get_total_mortality(lot_id)
        return round((total / lot.initial_quantity) * 100, 2)

    def get_survival_percentage(self, lot_id: int) -> float:
        """Calcula el porcentaje de supervivencia de un lote.

        Equivale a `calcular_porcentaje_supervivencia()` del ejercicio.

        Args:
            lot_id: Identificador del lote.

        Returns:
            Porcentaje de supervivencia redondeado a 2 decimales.

        Raises:
            HTTPException 404: Si el lote no existe.
        """
        lot = self.lot_service.get_lot(lot_id)
        if lot.initial_quantity == 0:
            return 0.0

        return round((lot.current_quantity / lot.initial_quantity) * 100, 2)

    # ============================ Enfermedades ============================

    def register_disease(
        self, lot_id: int, data: DiseaseCreate, user_id: int
    ) -> Disease:
        """Registra una enfermedad diagnosticada en un lote.

        Args:
            lot_id: Identificador del lote.
            data: Datos validados de la enfermedad.
            user_id: Usuario que ejecuta la acción.

        Returns:
            La enfermedad registrada.

        Raises:
            HTTPException 404: Si el lote no existe.
        """
        lot = self.lot_service.get_lot(lot_id)

        record = Disease(
            lot_id=lot.id,
            diagnosis_date=data.diagnosis_date or date.today(),
            disease_name=data.disease_name,
            affected_quantity=data.affected_quantity,
            symptoms=data.symptoms,
            treatment=data.treatment,
            treatment_start_date=data.treatment_start_date,
            treatment_end_date=data.treatment_end_date,
            is_resolved=data.is_resolved,
        )
        record = self.repository.create_disease(record)
        TraceabilityService(self.db).log_event(
            "Disease",
            record.id,
            "CREATE",
            user_id,
            changes={
                "lot_id": record.lot_id,
                "disease_name": record.disease_name,
                "affected_quantity": record.affected_quantity,
            },
        )
        return record

    def get_diseases(self, lot_id: int) -> list[Disease]:
        """Lista las enfermedades de un lote.

        Args:
            lot_id: Identificador del lote.

        Returns:
            Lista de enfermedades del lote.

        Raises:
            HTTPException 404: Si el lote no existe.
        """
        lot = self.lot_service.get_lot(lot_id)
        return self.repository.get_diseases(lot.id)

    def _get_lot_disease(self, lot_id: int, disease_id: int) -> Disease:
        """Obtiene una enfermedad validando que pertenezca al lote.

        Args:
            lot_id: Identificador del lote.
            disease_id: Identificador de la enfermedad.

        Returns:
            La enfermedad del lote.

        Raises:
            HTTPException 404: Si la enfermedad no existe o no pertenece
                al lote indicado.
        """
        self.lot_service.get_lot(lot_id)
        disease = self.repository.get_disease(disease_id)
        if disease is None or disease.lot_id != lot_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Enfermedad no encontrada",
            )
        return disease

    def update_treatment(
        self, lot_id: int, disease_id: int, data: DiseaseUpdate
    ) -> Disease:
        """Actualiza el tratamiento y estado de una enfermedad.

        Args:
            lot_id: Identificador del lote.
            disease_id: Identificador de la enfermedad.
            data: Campos a actualizar (solo los enviados).

        Returns:
            La enfermedad actualizada.

        Raises:
            HTTPException 404: Si la enfermedad no existe.
        """
        disease = self._get_lot_disease(lot_id, disease_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(disease, field, value)
        return self.repository.update_disease(disease)

    def resolve_disease(self, lot_id: int, disease_id: int) -> Disease:
        """Marca una enfermedad como resuelta.

        Args:
            lot_id: Identificador del lote.
            disease_id: Identificador de la enfermedad.

        Returns:
            La enfermedad resuelta.

        Raises:
            HTTPException 404: Si la enfermedad no existe.
        """
        disease = self._get_lot_disease(lot_id, disease_id)
        disease.is_resolved = True
        return self.repository.update_disease(disease)
