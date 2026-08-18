"""Repositorio de acceso a datos del inventario de insumos.

Encapsula las consultas a las tablas `feed_types` y `feed_stock_movements`
mediante SQLAlchemy, abstrayendo a la capa de servicios de los detalles de
persistencia.
"""

from sqlalchemy.orm import Session

from app.models.feed_stock import FeedStockMovement, FeedType


class FeedStockRepository:
    """Acceso a datos de los tipos de alimento y sus movimientos."""

    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[FeedType]:
        """Lista todos los tipos de alimento.

        Returns:
            Lista con los tipos de alimento en orden alfabético.
        """
        return self.db.query(FeedType).order_by(FeedType.name).all()

    def get(self, feed_type_id: int) -> FeedType | None:
        """Busca un tipo de alimento por su identificador.

        Args:
            feed_type_id: Identificador del tipo de alimento.

        Returns:
            El tipo de alimento encontrado o None si no existe.
        """
        return self.db.get(FeedType, feed_type_id)

    def get_by_name(self, name: str) -> FeedType | None:
        """Busca un tipo de alimento por su nombre (insensible a mayúsculas).

        Args:
            name: Nombre del alimento.

        Returns:
            El tipo de alimento encontrado o None si no existe.
        """
        return (
            self.db.query(FeedType)
            .filter(FeedType.name.ilike(name))
            .first()
        )

    def create(self, feed_type: FeedType) -> FeedType:
        """Persiste un nuevo tipo de alimento.

        Args:
            feed_type: Instancia de `FeedType` a crear.

        Returns:
            El tipo de alimento recién creado.
        """
        self.db.add(feed_type)
        self.db.commit()
        self.db.refresh(feed_type)
        return feed_type

    def update(self, feed_type: FeedType) -> FeedType:
        """Persiste los cambios de un tipo de alimento existente.

        Args:
            feed_type: Instancia de `FeedType` con los cambios aplicados.

        Returns:
            El tipo de alimento actualizado.
        """
        self.db.commit()
        self.db.refresh(feed_type)
        return feed_type

    def delete(self, feed_type: FeedType) -> None:
        """Elimina un tipo de alimento de la base de datos.

        Args:
            feed_type: Instancia de `FeedType` a eliminar.
        """
        self.db.delete(feed_type)
        self.db.commit()

    def create_movement(self, movement: FeedStockMovement) -> FeedStockMovement:
        """Persiste un nuevo movimiento de ingreso de stock.

        Args:
            movement: Instancia de `FeedStockMovement` a crear.

        Returns:
            El movimiento recién creado.
        """
        self.db.add(movement)
        self.db.commit()
        self.db.refresh(movement)
        return movement
