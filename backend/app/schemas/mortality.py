"""Schemas Pydantic para el registro de mortalidad.

Define los DTOs de creación y salida del módulo de mortalidad.
"""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class MortalityCreate(BaseModel):
    """Datos necesarios para registrar la mortalidad de un lote.

    Attributes:
        week: Semana del ciclo. Si se omite, se usa la semana actual del lote.
        event_date: Fecha del evento. Si se omite, se usa hoy.
        quantity: Cantidad de aves muertas (mayor a 0).
        cause: Causa de la mortalidad (1-200 caracteres).
        observations: Observaciones del registro (opcional).
    """

    week: int | None = None
    event_date: date | None = None
    quantity: int = Field(gt=0)
    cause: str = Field(min_length=1, max_length=200)
    observations: str | None = Field(default=None, max_length=500)


class MortalityOut(BaseModel):
    """Datos de un registro de mortalidad para la respuesta de la API.

    Attributes:
        id: Identificador del registro.
        lot_id: Identificador del lote.
        week: Semana del ciclo del registro.
        event_date: Fecha del evento.
        quantity: Cantidad de aves muertas.
        cause: Causa de la mortalidad.
        observations: Observaciones del registro.
        created_at: Fecha de creación del registro.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    lot_id: int
    week: int
    event_date: date
    quantity: int
    cause: str
    observations: str | None
    created_at: datetime
