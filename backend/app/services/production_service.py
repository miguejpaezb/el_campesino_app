"""Servicio de lógica de negocio de la producción diaria de huevos.

Adapta `registrar_postura`, `total_huevos`, `calcular_promedio_postura_semanal`
y `calcular_porcentaje_postura` del ejercicio en clase
(`docs/ejercicio_en_clase/domain/lote.py`).
"""

from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.constants import CicloProductivo
from app.models.egg_production import EggProduction
from app.repositories.production_repository import ProductionRepository
from app.schemas.egg_production import EggProductionCreate
from app.services.lot_service import LotService
from app.services.traceability_service import TraceabilityService


class ProductionService:
    """Lógica de negocio de la producción diaria de huevos.

    Attributes:
        repository: Repositorio de producción usado para la persistencia.
        lot_service: Servicio de lotes para validar el lote propietario.
    """

    def __init__(self, db: Session):
        self.db = db
        self.repository = ProductionRepository(db)
        self.lot_service = LotService(db)

    def register_eggs(
        self, lot_id: int, data: EggProductionCreate, user_id: int
    ) -> EggProduction:
        """Registra la producción diaria de huevos de un lote.

        Aplica las reglas de negocio del ejercicio en clase:
          - El lote debe existir y estar activo.
          - La semana actual del lote debe ser >= SEMANA_DE_POSTURA.

        Args:
            lot_id: Identificador del lote.
            data: Datos validados del registro.
            user_id: Usuario que ejecuta la acción.

        Returns:
            El registro de producción creado.

        Raises:
            HTTPException 404: Si el lote no existe.
            HTTPException 400: Si el lote está inactivo o aún no está en
                etapa de postura.
        """
        lot = self.lot_service.get_lot(lot_id)

        if not lot.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El lote está inactivo, no se puede registrar producción",
            )

        if lot.current_week < CicloProductivo.SEMANA_DE_POSTURA:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"El lote no está en etapa de postura "
                    f"(semana #{CicloProductivo.SEMANA_DE_POSTURA})"
                ),
            )

        production = EggProduction(
            lot_id=lot.id,
            week=data.week if data.week is not None else lot.current_week,
            collection_date=data.collection_date or date.today(),
            egg_count=data.egg_count,
            avg_weight_grams=data.avg_weight_grams,
            broken_eggs=data.broken_eggs,
            observations=data.observations,
        )
        production = self.repository.create(production)
        TraceabilityService(self.db).log_event(
            "EggProduction",
            production.id,
            "CREATE",
            user_id,
            changes={
                "lot_id": production.lot_id,
                "week": production.week,
                "egg_count": production.egg_count,
            },
        )
        return production

    def get_production_by_lot(
        self,
        lot_id: int,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[EggProduction]:
        """Lista los registros de producción de un lote.

        Args:
            lot_id: Identificador del lote.
            start_date: Fecha inicial del filtro.
            end_date: Fecha final del filtro.

        Returns:
            Lista de registros de producción del lote.

        Raises:
            HTTPException 404: Si el lote no existe.
        """
        lot = self.lot_service.get_lot(lot_id)
        return self.repository.get_by_lot(lot.id, start_date, end_date)

    def get_total_eggs(self, lot_id: int) -> int:
        """Calcula el total de huevos producidos por un lote.

        Equivale a `total_huevos()` del ejercicio en clase.

        Args:
            lot_id: Identificador del lote.

        Returns:
            Total de huevos recolectados.

        Raises:
            HTTPException 404: Si el lote no existe.
        """
        self.lot_service.get_lot(lot_id)
        productions = self.repository.get_by_lot(lot_id)
        return sum(p.egg_count for p in productions)

    def get_avg_weekly_production(self, lot_id: int) -> float:
        """Calcula el promedio de postura semanal de un lote.

        Equivale a `calcular_promedio_postura_semanal()` del ejercicio.

        Args:
            lot_id: Identificador del lote.

        Returns:
            Promedio de huevos por semana registrada.

        Raises:
            HTTPException 404: Si el lote no existe.
        """
        self.lot_service.get_lot(lot_id)
        productions = self.repository.get_by_lot(lot_id)

        if not productions:
            return 0.0

        total = sum(p.egg_count for p in productions)
        return round(total / len(productions), 2)

    def get_laying_percentage(self, lot_id: int) -> float:
        """Calcula el porcentaje de postura de un lote.

        Equivale a `calcular_porcentaje_postura()` del ejercicio. La lógica
        está centralizada en `LotService.calculate_laying_percentage`.

        Args:
            lot_id: Identificador del lote.

        Returns:
            Porcentaje de postura redondeado a 2 decimales.

        Raises:
            HTTPException 404: Si el lote no existe.
        """
        lot = self.lot_service.get_lot(lot_id)
        return self.lot_service.calculate_laying_percentage(lot)
