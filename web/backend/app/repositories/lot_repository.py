"""Repositorio de acceso a datos para los lotes de aves.

Encapsula las consultas a la tabla `bird_lots` mediante SQLAlchemy,
abstrayendo a la capa de servicios de los detalles de persistencia.
"""

from sqlalchemy.orm import Session

from app.models.bird_lot import BirdLot


class LotRepository:
    """Acceso a datos de la entidad `BirdLot`."""

    def __init__(self, db: Session):
        self.db = db

    def get_all(self, active_only: bool = False) -> list[BirdLot]:
        """Lista los lotes registrados.

        Args:
            active_only: Si es True, solo devuelve lotes activos.

        Returns:
            Lista con los lotes encontrados.
        """
        query = self.db.query(BirdLot)
        if active_only:
            query = query.filter(BirdLot.is_active.is_(True))
        return query.all()

    def get_by_id(self, lot_id: int) -> BirdLot | None:
        """Busca un lote por su identificador.

        Args:
            lot_id: Identificador del lote.

        Returns:
            El lote encontrado o None si no existe.
        """
        return self.db.get(BirdLot, lot_id)

    def get_by_code(self, lot_code: str) -> BirdLot | None:
        """Busca un lote por su código.

        Args:
            lot_code: Código único del lote.

        Returns:
            El lote encontrado o None si no existe.
        """
        return (
            self.db.query(BirdLot).filter(BirdLot.lot_code == lot_code).first()
        )

    def create(self, lot: BirdLot) -> BirdLot:
        """Persiste un nuevo lote.

        Args:
            lot: Instancia de `BirdLot` a crear.

        Returns:
            El lote recién creado.
        """
        self.db.add(lot)
        self.db.commit()
        self.db.refresh(lot)
        return lot

    def update(self, lot: BirdLot) -> BirdLot:
        """Persiste los cambios de un lote existente.

        Args:
            lot: Instancia de `BirdLot` con los cambios aplicados.

        Returns:
            El lote actualizado.
        """
        self.db.commit()
        self.db.refresh(lot)
        return lot

    def delete(self, lot_id: int) -> bool:
        """Elimina físicamente un lote.

        Args:
            lot_id: Identificador del lote a eliminar.

        Returns:
            True si se eliminó, False si no existía.
        """
        lot = self.get_by_id(lot_id)
        if lot is None:
            return False
        self.db.delete(lot)
        self.db.commit()
        return True
