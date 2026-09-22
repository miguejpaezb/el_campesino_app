"""Modelos ORM del inventario de insumos (alimentos).

Define `FeedType` (tipos de alimento con su stock) y `FeedStockMovement`
(movimientos de ingreso de stock), que permiten controlar la disponibilidad
de alimento, notificar stock bajo y llevar el historial de precios.
"""

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.feeding import FeedingRecord


class FeedType(Base):
    """Representa un tipo de alimento con su stock actual.

    Attributes:
        id: Identificador único del tipo de alimento.
        name: Nombre del alimento (único).
        stock_kg: Cantidad actual de stock en kilos.
        min_stock_kg: Cantidad mínima para notificar stock bajo.
        cost_per_kilo: Costo por kilo del último ingreso.
        is_active: Si el alimento está activo (no suspendido).
        last_stock_date: Fecha del último ingreso de stock.
        created_at: Fecha de creación del registro.
        updated_at: Fecha de la última modificación.
        feeding_records: Registros de alimentación vinculados al alimento.
        movements: Movimientos de ingreso de stock del alimento.
    """

    __tablename__ = "feed_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    stock_kg: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    min_stock_kg: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    cost_per_kilo: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    last_stock_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )

    feeding_records: Mapped[list["FeedingRecord"]] = relationship(
        back_populates="feed_type_rel"
    )
    movements: Mapped[list["FeedStockMovement"]] = relationship(
        back_populates="feed_type", cascade="all, delete-orphan"
    )

    @property
    def is_low_stock(self) -> bool:
        """Indica si el stock está por debajo o igual al mínimo configurado.

        Returns:
            True si el stock no supera el mínimo, False en caso contrario.
        """
        return self.stock_kg <= self.min_stock_kg


class FeedStockMovement(Base):
    """Representa un ingreso de stock de un tipo de alimento.

    Attributes:
        id: Identificador único del movimiento.
        feed_type_id: Identificador del tipo de alimento.
        kilos_added: Cantidad de kilos ingresados.
        cost_per_kilo: Costo por kilo del ingreso (None si no se registró).
        total_cost: Costo total del ingreso (kilos x costo por kilo).
        entry_date: Fecha del ingreso de stock.
        created_at: Fecha de creación del registro.
        feed_type: Relación con el tipo de alimento.
    """

    __tablename__ = "feed_stock_movements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    feed_type_id: Mapped[int] = mapped_column(
        ForeignKey("feed_types.id"), index=True
    )
    kilos_added: Mapped[float] = mapped_column(Float, nullable=False)
    cost_per_kilo: Mapped[float | None] = mapped_column(Float, nullable=True)
    entry_date: Mapped[date] = mapped_column(Date, default=date.today)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    feed_type: Mapped["FeedType"] = relationship(back_populates="movements")

    @property
    def total_cost(self) -> float | None:
        """Costo total del ingreso (kilos x costo por kilo).

        Returns:
            Costo total redondeado a 2 decimales, o None si no hay costo.
        """
        if self.cost_per_kilo is None:
            return None
        return round(self.kilos_added * self.cost_per_kilo, 2)
