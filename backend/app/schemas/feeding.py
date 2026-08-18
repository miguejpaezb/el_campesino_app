"""Schemas Pydantic para el registro de alimentación.

Define los DTOs de creación y salida del módulo de alimentación.
"""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class FeedingCreate(BaseModel):
    """Datos necesarios para registrar alimentación de un lote.

    Attributes:
        week: Semana del ciclo. Si se omite, se usa la semana actual del lote.
        feed_date: Fecha del suministro. Si se omite, se usa hoy.
        feed_type: Tipo de alimento suministrado (1-50 caracteres).
            Si se envía `feed_type_id`, se usa como respaldo para compatibilidad.
        feed_type_id: Identificador del tipo de alimento del inventario.
            Al usarlo, el costo y el nombre se toman del inventario y se
            descuenta el stock.
        kilos: Cantidad de alimento en kilos (mayor a 0).
        cost_per_kilo: Costo por kilo del alimento (mayor a 0, opcional).
        observations: Observaciones del registro (opcional).
    """

    week: int | None = None
    feed_date: date | None = None
    feed_type: str | None = Field(default=None, min_length=1, max_length=50)
    feed_type_id: int | None = None
    kilos: float = Field(gt=0)
    cost_per_kilo: float | None = Field(default=None, gt=0)
    observations: str | None = Field(default=None, max_length=300)


class FeedingOut(BaseModel):
    """Datos de un registro de alimentación para la respuesta de la API.

    Attributes:
        id: Identificador del registro.
        lot_id: Identificador del lote.
        feed_type_id: Identificador del tipo de alimento del inventario
            (si aplica).
        week: Semana del ciclo del registro.
        feed_date: Fecha del suministro.
        feed_type: Tipo de alimento.
        kilos: Cantidad de alimento en kilos.
        cost_per_kilo: Costo por kilo del alimento.
        total_cost: Costo total del registro (kilos x costo por kilo).
        observations: Observaciones del registro.
        created_at: Fecha de creación del registro.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    lot_id: int
    feed_type_id: int | None
    week: int
    feed_date: date
    feed_type: str
    kilos: float
    cost_per_kilo: float | None
    total_cost: float | None
    observations: str | None
    created_at: datetime
