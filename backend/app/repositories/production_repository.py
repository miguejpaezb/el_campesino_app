"""Repositorio de acceso a datos para la producción diaria.

Encapsula las consultas a la tabla `egg_production` mediante SQLAlchemy,
abstrayendo a la capa de servicios de los detalles de persistencia.
"""

from datetime import date

from sqlalchemy.orm import Session

from app.models.egg_production import EggProduction


class ProductionRepository:
    """Acceso a datos de la entidad `EggProduction`."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_lot(
        self,
        lot_id: int,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[EggProduction]:
        """Lista los registros de producción de un lote.

        Args:
            lot_id: Identificador del lote.
            start_date: Fecha inicial del filtro (inclusive).
            end_date: Fecha final del filtro (inclusive).

        Returns:
            Lista con los registros encontrados.
        """
        query = self.db.query(EggProduction).filter(EggProduction.lot_id == lot_id)
        if start_date is not None:
            query = query.filter(EggProduction.collection_date >= start_date)
        if end_date is not None:
            query = query.filter(EggProduction.collection_date <= end_date)
        return query.all()

    def create(self, production: EggProduction) -> EggProduction:
        """Persiste un nuevo registro de producción.

        Args:
            production: Instancia de `EggProduction` a crear.

        Returns:
            El registro recién creado.
        """
        self.db.add(production)
        self.db.commit()
        self.db.refresh(production)
        return production
