"""Schemas Pydantic del inventario de insumos (alimentos).

Define los DTOs de creación, actualización, ingreso de stock y salida de
los tipos de alimento y sus movimientos.
"""

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class FeedStockCreate(BaseModel):
    """Datos para crear un tipo de alimento en el inventario.

    Attributes:
        name: Nombre del alimento (1-50 caracteres).
        stock_kg: Cantidad inicial de stock en kilos (mayor o igual a 0).
        cost_per_kilo: Costo por kilo del alimento (opcional).
        min_stock_kg: Cantidad mínima para notificar stock bajo.
        entry_date: Fecha del ingreso inicial. Si se omite, se usa hoy.
    """

    name: str = Field(min_length=1, max_length=50)
    stock_kg: float = Field(default=0, ge=0)
    cost_per_kilo: float | None = Field(default=None, gt=0)
    min_stock_kg: float = Field(default=0, ge=0)
    entry_date: date | None = None


class FeedStockUpdate(BaseModel):
    """Campos actualizables de un tipo de alimento existente.

    Attributes:
        name: Nuevo nombre del alimento (opcional).
        min_stock_kg: Nuevo stock mínimo para notificar (opcional).
    """

    name: str | None = Field(default=None, min_length=1, max_length=50)
    min_stock_kg: float | None = Field(default=None, ge=0)


class FeedStockAddStock(BaseModel):
    """Datos para añadir stock a un tipo de alimento.

    Attributes:
        kilos_added: Cantidad de kilos a ingresar (mayor a 0).
        price_option: "same" si el kilo costó lo mismo que la última vez,
            "new" si cambió el precio.
        cost_per_kilo: Costo por kilo del ingreso (obligatorio si
            price_option == "new").
        entry_date: Fecha del ingreso. Si se omite, se usa hoy.
    """

    kilos_added: float = Field(gt=0)
    price_option: Literal["same", "new"] = "same"
    cost_per_kilo: float | None = Field(default=None, gt=0)
    entry_date: date | None = None


class FeedStockOut(BaseModel):
    """Datos completos de un tipo de alimento para la respuesta.

    Attributes:
        id: Identificador del tipo de alimento.
        name: Nombre del alimento.
        stock_kg: Cantidad actual de stock en kilos.
        min_stock_kg: Cantidad mínima para notificar stock bajo.
        cost_per_kilo: Costo por kilo del último ingreso.
        is_active: Si el alimento está activo.
        last_stock_date: Fecha del último ingreso de stock.
        is_low_stock: True si el stock está por debajo o igual al mínimo.
        created_at: Fecha de creación del registro.
        updated_at: Fecha de la última modificación.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    stock_kg: float
    min_stock_kg: float
    cost_per_kilo: float | None
    is_active: bool
    last_stock_date: date | None
    is_low_stock: bool
    created_at: datetime
    updated_at: datetime


class FeedStockMovementOut(BaseModel):
    """Datos de un movimiento de ingreso de stock para la respuesta.

    Attributes:
        id: Identificador del movimiento.
        feed_type_id: Identificador del tipo de alimento.
        kilos_added: Cantidad de kilos ingresados.
        cost_per_kilo: Costo por kilo del ingreso.
        total_cost: Costo total del ingreso (kilos x costo por kilo).
        entry_date: Fecha del ingreso de stock.
        created_at: Fecha de creación del registro.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    feed_type_id: int
    kilos_added: float
    cost_per_kilo: float | None
    total_cost: float | None
    entry_date: date
    created_at: datetime
