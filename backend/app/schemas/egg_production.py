"""Schemas Pydantic para la producción diaria de huevos.

Define los DTOs de creación y salida del módulo de producción diaria.
"""

from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict, Field, model_validator


class EggProductionCreate(BaseModel):
    """Datos necesarios para registrar la producción diaria de un lote.

    Attributes:
        week: Semana del ciclo. Si se omite, se usa la semana actual del lote.
        collection_date: Fecha de recolección. Si se omite, se usa hoy.
        collection_time: Hora de recolección. Si se omite, se usa la actual.
        egg_count: Cantidad de huevos aptos recolectados (mayor o igual a 0).
        avg_weight_grams: Peso promedio por huevo en gramos (opcional).
        broken_eggs: Cantidad de huevos no aptos/rotos (mayor o igual a 0).
        observations: Observaciones del registro (opcional).
    """

    week: int | None = None
    collection_date: date | None = None
    collection_time: time | None = None
    egg_count: int = Field(ge=0)
    avg_weight_grams: float | None = Field(default=None, gt=0)
    broken_eggs: int = Field(default=0, ge=0)
    observations: str | None = Field(default=None, max_length=300)

    @model_validator(mode="after")
    def _at_least_one_quantity(self):
        """Al menos una de las cantidades (aptos o no aptos) debe ser > 0.

        Raises:
            ValueError: Si ambas cantidades son 0.
        """
        if self.egg_count == 0 and self.broken_eggs == 0:
            raise ValueError(
                "Al menos una de las cantidades (aptos o no aptos) debe ser mayor a 0"
            )
        return self


class EggProductionOut(BaseModel):
    """Datos de un registro de producción para la respuesta de la API.

    Attributes:
        id: Identificador del registro.
        lot_id: Identificador del lote.
        week: Semana del ciclo del registro.
        collection_date: Fecha de recolección.
        collection_time: Hora de recolección.
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
    collection_time: time | None
    egg_count: int
    avg_weight_grams: float | None
    broken_eggs: int
    observations: str | None
    created_at: datetime
