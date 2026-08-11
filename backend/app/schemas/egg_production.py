"""Schemas Pydantic para la producción diaria de huevos.

Define los DTOs de creación y salida del módulo de producción diaria.
"""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class EggProductionCreate(BaseModel):
    """Datos necesarios para registrar la producción diaria de un lote.

    Attributes:
        week: Semana del ciclo. Si se omite, se usa la semana actual del lote.
        collection_date: Fecha de recolección. Si se omite, se usa hoy.
        egg_count: Cantidad de huevos recolectados (mayor o igual a 0).
        avg_weight_grams: Peso promedio por huevo en gramos (opcional).
        broken_eggs: Cantidad de huevos rotos (mayor o igual a 0).
        observations: Observaciones del registro (opcional).
    """

    week: int | None = None
    collection_date: date | None = None
    egg_count: int = Field(ge=0)
    avg_weight_grams: float | None = Field(default=None, gt=0)
    broken_eggs: int = Field(default=0, ge=0)
    observations: str | None = Field(default=None, max_length=300)


class EggProductionOut(BaseModel):
    """Datos de un registro de producción para la respuesta de la API.

    Attributes:
        id: Identificador del registro.
        lot_id: Identificador del lote.
        week: Semana del ciclo del registro.
        collection_date: Fecha de recolección.
        egg_count: Cantidad de huevos recolectados.
        avg_weight_grams: Peso promedio por huevo en gramos.
        broken_eggs: Cantidad de huevos rotos.
        observations: Observaciones del registro.
        created_at: Fecha de creación del registro.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    lot_id: int
    week: int
    collection_date: date
    egg_count: int
    avg_weight_grams: float | None
    broken_eggs: int
    observations: str | None
    created_at: datetime
