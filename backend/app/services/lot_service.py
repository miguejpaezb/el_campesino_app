"""Servicio de lógica de negocio de los lotes de aves.

Adapta el `LoteService` del ejercicio en clase
(`docs/ejercicio_en_clase/services/lote_service.py`) y los cálculos de
`LoteGallinas` a SQLAlchemy y la arquitectura del backend.

Contiene las reglas de dominio: creación, actualización, descarte, avance
de semana, evaluación del ciclo productivo y resumen del lote.
"""

from datetime import datetime, time

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.constants import CicloProductivo
from app.models.bird_lot import BirdLot
from app.repositories.lot_repository import LotRepository
from app.schemas.bird_lot import (
    BirdLotCreate,
    BirdLotDiscard,
    BirdLotSummary,
    BirdLotUpdate,
)
from app.services.traceability_service import TraceabilityService


class LotService:
    """Lógica de negocio de los lotes de aves.

    Attributes:
        repository: Repositorio de lotes usado para la persistencia.
    """

    def __init__(self, db: Session):
        self.db = db
        self.repository = LotRepository(db)

    def create_lot(self, data: BirdLotCreate, user_id: int) -> BirdLot:
        """Crea un nuevo lote de aves.

        La cantidad inicial y actual coinciden al momento de la creación y la
        semana arranca en `SEMANA_COMPRA` (constante del ciclo productivo).

        Args:
            data: Datos validados del lote.
            user_id: Usuario que ejecuta la acción.

        Returns:
            El lote recién creado.

        Raises:
            HTTPException 409: Si el código del lote ya existe.
        """
        if self.repository.get_by_code(data.lot_code):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El código de lote ya existe",
            )

        lot = BirdLot(
            lot_code=data.lot_code,
            breed=data.breed,
            initial_quantity=data.initial_quantity,
            current_quantity=data.initial_quantity,
            current_week=CicloProductivo.SEMANA_COMPRA,
            observations=data.observations,
        )
        if data.entry_date is not None:
            lot.entry_date = datetime.combine(data.entry_date, time.min)

        lot = self.repository.create(lot)
        TraceabilityService(self.db).log_event(
            "BirdLot",
            lot.id,
            "CREATE",
            user_id,
            changes={
                "lot_code": lot.lot_code,
                "breed": lot.breed,
                "initial_quantity": lot.initial_quantity,
            },
        )
        return lot

    def get_lot(self, lot_id: int) -> BirdLot:
        """Obtiene un lote por su identificador.

        Args:
            lot_id: Identificador del lote.

        Returns:
            El lote encontrado.

        Raises:
            HTTPException 404: Si el lote no existe.
        """
        lot = self.repository.get_by_id(lot_id)
        if lot is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lote no encontrado",
            )
        return lot

    def list_lots(self, active_only: bool = False) -> list[BirdLot]:
        """Lista los lotes registrados.

        Args:
            active_only: Si es True, solo se devuelven lotes activos.

        Returns:
            Lista con los lotes encontrados.
        """
        return self.repository.get_all(active_only=active_only)

    def update_lot(self, lot_id: int, data: BirdLotUpdate, user_id: int) -> BirdLot:
        """Actualiza los campos indicados de un lote.

        Args:
            lot_id: Identificador del lote.
            data: Campos a actualizar (solo los enviados).
            user_id: Usuario que ejecuta la acción.

        Returns:
            El lote actualizado.

        Raises:
            HTTPException 404: Si el lote no existe.
        """
        lot = self.get_lot(lot_id)
        changes = data.model_dump(exclude_unset=True)
        for field, value in changes.items():
            setattr(lot, field, value)
        lot = self.repository.update(lot)
        TraceabilityService(self.db).log_event(
            "BirdLot", lot.id, "UPDATE", user_id, changes=changes
        )
        return lot

    def discard_lot(
        self, lot_id: int, data: BirdLotDiscard, user_id: int
    ) -> BirdLot:
        """Desactiva un lote indicando la razón de descarte.

        Equivale a `desactivar_lote` del ejercicio en clase.

        Args:
            lot_id: Identificador del lote.
            data: Razón del descarte.
            user_id: Usuario que ejecuta la acción.

        Returns:
            El lote desactivado.

        Raises:
            HTTPException 404: Si el lote no existe.
        """
        lot = self.get_lot(lot_id)
        lot.is_active = False
        lot.discard_reason = data.reason
        lot = self.repository.update(lot)
        TraceabilityService(self.db).log_event(
            "BirdLot",
            lot.id,
            "DELETE",
            user_id,
            changes={"reason": data.reason},
        )
        return lot

    def advance_week(self, lot_id: int, user_id: int) -> BirdLot:
        """Avanza una semana el ciclo productivo del lote.

        Equivale a `avanzar_semana` del ejercicio en clase.

        Args:
            lot_id: Identificador del lote.
            user_id: Usuario que ejecuta la acción.

        Returns:
            El lote con la semana incrementada.

        Raises:
            HTTPException 404: Si el lote no existe.
        """
        lot = self.get_lot(lot_id)
        lot.current_week += 1
        lot = self.repository.update(lot)
        TraceabilityService(self.db).log_event(
            "BirdLot",
            lot.id,
            "UPDATE",
            user_id,
            changes={"current_week": lot.current_week},
        )
        return lot

    def save_lot(self, lot: BirdLot) -> BirdLot:
        """Persiste los cambios de un lote ya modificado en memoria.

        Permite que otros servicios (p. ej. sanidad) actualicen el lote
        sin conocer el repositorio. Equivale a `guardar_lote` del ejercicio.

        Args:
            lot: Instancia de `BirdLot` con los cambios aplicados.

        Returns:
            El lote persistido.
        """
        return self.repository.update(lot)

    def evaluate_lot(self, lot_id: int, user_id: int) -> dict[str, bool | str]:
        """Evalúa el rendimiento productivo del lote.

        Equivale a `evaluar_lote` del ejercicio en clase:
          - Si aún no es la semana de evaluación, no hace nada.
          - Si el porcentaje de postura es menor al mínimo, descarta el lote.
          - En caso contrario, extiende el ciclo `EXTENSION_SEMANAS` semanas.

        Args:
            lot_id: Identificador del lote.
            user_id: Usuario que ejecuta la acción.

        Returns:
            Diccionario con el mensaje resultante y el nuevo estado.

        Raises:
            HTTPException 404: Si el lote no existe.
        """
        lot = self.get_lot(lot_id)

        if lot.current_week < CicloProductivo.SEMANA_DE_EVALUACION:
            message = (
                f"Aún no es la semana de evaluación "
                f"(semana #{CicloProductivo.SEMANA_DE_EVALUACION})."
            )
            return {"message": message, "is_active": lot.is_active}

        percentage = self.calculate_laying_percentage(lot)

        if percentage < CicloProductivo.PORCENTAJE_MINIMO_POSTURA:
            lot.is_active = False
            lot.discard_reason = "Desempeño por debajo del esperado."
            self.repository.update(lot)
            TraceabilityService(self.db).log_event(
                "BirdLot",
                lot.id,
                "UPDATE",
                user_id,
                changes={
                    "action": "evaluate",
                    "message": lot.discard_reason,
                },
            )
            return {"message": lot.discard_reason, "is_active": False}

        lot.current_week += CicloProductivo.EXTENSION_SEMANAS
        self.repository.update(lot)
        TraceabilityService(self.db).log_event(
            "BirdLot",
            lot.id,
            "UPDATE",
            user_id,
            changes={
                "action": "evaluate",
                "message": "Lote aprobado por eficiencia.",
                "current_week": lot.current_week,
            },
        )
        return {"message": "Lote aprobado por eficiencia.", "is_active": True}

    def get_summary(self, lot_id: int) -> BirdLotSummary:
        """Genera el resumen productivo de un lote.

        Los indicadores de producción, alimentación, sanidad y mortalidad se
        calculan a partir de las tablas relacionadas. Si aún no existen
        registros (módulos de fases posteriores), los indicadores son 0.

        Args:
            lot_id: Identificador del lote.

        Returns:
            Un `BirdLotSummary` con los indicadores del lote.

        Raises:
            HTTPException 404: Si el lote no existe.
        """
        lot = self.get_lot(lot_id)

        productions = getattr(lot, "egg_productions", None) or []
        vaccinations = getattr(lot, "vaccinations", None) or []
        mortalities = getattr(lot, "mortalities", None) or []
        feedings = getattr(lot, "feeding_records", None) or []

        total_eggs = sum(p.egg_count for p in productions)
        total_mortality = sum(m.quantity for m in mortalities)
        total_feed = sum(f.kilos for f in feedings)

        productive_weeks = len(productions)
        average_weekly = (
            round(total_eggs / productive_weeks, 2) if productive_weeks else 0
        )
        max_eggs = lot.initial_quantity * 7 * productive_weeks
        laying_percentage = (
            round((total_eggs / max_eggs) * 100, 2) if max_eggs else 0.0
        )
        mortality_percentage = (
            round((total_mortality / lot.initial_quantity) * 100, 2)
            if lot.initial_quantity
            else 0.0
        )
        survival_percentage = (
            round((lot.current_quantity / lot.initial_quantity) * 100, 2)
            if lot.initial_quantity
            else 0.0
        )

        return BirdLotSummary(
            id=lot.id,
            lot_code=lot.lot_code,
            breed=lot.breed,
            current_week=lot.current_week,
            initial_quantity=lot.initial_quantity,
            current_quantity=lot.current_quantity,
            total_eggs=total_eggs,
            average_weekly_production=average_weekly,
            laying_percentage=laying_percentage,
            total_feed=total_feed,
            total_mortality=total_mortality,
            mortality_percentage=mortality_percentage,
            survival_percentage=survival_percentage,
            vaccination_count=len(vaccinations),
            is_active=lot.is_active,
            discard_reason=lot.discard_reason,
        )

    def calculate_laying_percentage(self, lot: BirdLot) -> float:
        """Calcula el porcentaje de postura del lote.

        Equivale a `calcular_porcentaje_postura` del ejercicio: relación entre
        los huevos recolectados y el máximo teórico (aves iniciales x 7 días
        por semana productiva).

        Args:
            lot: Instancia del lote a evaluar.

        Returns:
            Porcentaje de postura redondeado a 2 decimales.
        """
        productions = getattr(lot, "egg_productions", None) or []
        productive_weeks = len(productions)

        if not productive_weeks:
            return 0.0

        total_eggs = sum(p.egg_count for p in productions)
        max_eggs = lot.initial_quantity * 7 * productive_weeks
        if max_eggs == 0:
            return 0.0

        return round((total_eggs / max_eggs) * 100, 2)
