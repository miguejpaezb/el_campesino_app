"""Schemas Pydantic para los lotes de aves.

Define los DTOs de creación, actualización, descarte, salida y resumen del
módulo de inventario de aves.
"""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class BirdLotCreate(BaseModel):
    """Datos necesarios para crear un lote de aves.

    Attributes:
        lot_code: Código único del lote (1-20 caracteres).
        breed: Raza de las aves.
        initial_quantity: Cantidad inicial de aves (mayor a 0).
        entry_date: Fecha de ingreso. Si se omite, se usa la fecha actual.
        observations: Observaciones generales (opcional).
    """

    lot_code: str = Field(min_length=1, max_length=20)
    breed: str = Field(min_length=1, max_length=50)
    initial_quantity: int = Field(gt=0)
    entry_date: date | None = None
    observations: str | None = Field(default=None, max_length=500)


class BirdLotUpdate(BaseModel):
    """Campos actualizables de un lote existente.

    Attributes:
        breed: Nueva raza (opcional).
        observations: Nuevas observaciones (opcional).
        is_active: Nuevo estado del lote (opcional).
    """

    breed: str | None = Field(default=None, min_length=1, max_length=50)
    observations: str | None = Field(default=None, max_length=500)
    is_active: bool | None = None


class BirdLotDiscard(BaseModel):
    """Razón de descarte de un lote.

    Attributes:
        reason: Motivo del descarte (1-500 caracteres).
    """

    reason: str = Field(min_length=1, max_length=500)


class BirdLotOut(BaseModel):
    """Datos completos de un lote para la respuesta de la API.

    Attributes:
        id: Identificador del lote.
        lot_code: Código único del lote.
        breed: Raza de las aves.
        initial_quantity: Cantidad inicial de aves.
        current_quantity: Cantidad actual de aves.
        current_week: Semana actual del ciclo.
        entry_date: Fecha de ingreso del lote.
        is_active: Si el lote está activo.
        discard_reason: Razón de descarte (si existe).
        observations: Observaciones del lote.
        created_at: Fecha de creación del registro.
        updated_at: Fecha de la última modificación.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    lot_code: str
    breed: str
    initial_quantity: int
    current_quantity: int
    current_week: int
    entry_date: datetime
    is_active: bool
    discard_reason: str | None
    observations: str | None
    created_at: datetime
    updated_at: datetime


class BirdLotSummary(BaseModel):
    """Resumen productivo de un lote.

    Adapta el diccionario del método `resumen()` del ejercicio en clase.

    Attributes:
        id: Identificador del lote.
        lot_code: Código único del lote.
        breed: Raza de las aves.
        current_week: Semana actual del ciclo.
        initial_quantity: Cantidad inicial de aves.
        current_quantity: Cantidad actual de aves.
        total_eggs: Total de huevos producidos.
        average_weekly_production: Promedio de postura semanal.
        laying_percentage: Porcentaje de postura.
        total_feed: Total de alimento consumido (kg).
        total_mortality: Total de aves muertas.
        mortality_percentage: Porcentaje de mortalidad.
        survival_percentage: Porcentaje de supervivencia.
        vaccination_count: Cantidad de vacunas aplicadas.
        is_active: Si el lote está activo.
        discard_reason: Razón de descarte (si existe).
    """

    id: int
    lot_code: str
    breed: str
    current_week: int
    initial_quantity: int
    current_quantity: int
    total_eggs: int
    average_weekly_production: float
    laying_percentage: float
    total_feed: float
    total_mortality: int
    mortality_percentage: float
    survival_percentage: float
    vaccination_count: int
    is_active: bool
    discard_reason: str | None
