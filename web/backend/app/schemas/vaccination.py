"""Schemas Pydantic para el registro de vacunas.

Define los DTOs de creación y salida del módulo de vacunación.
"""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class VaccinationCreate(BaseModel):
    """Datos necesarios para registrar una vacuna aplicada a un lote.

    Attributes:
        week: Semana del ciclo. Si se omite, se usa la semana actual del lote.
        application_date: Fecha de aplicación. Si se omite, se usa hoy.
        vaccine_name: Nombre de la vacuna (1-100 caracteres).
        dosage: Dosis aplicada (1-50 caracteres).
        batch_number: Número de lote del biológico (opcional).
        next_application_date: Fecha del refuerzo (opcional).
    """

    week: int | None = None
    application_date: date | None = None
    vaccine_name: str = Field(min_length=1, max_length=100)
    dosage: str = Field(min_length=1, max_length=50)
    batch_number: str | None = Field(default=None, max_length=50)
    next_application_date: date | None = None


class VaccinationOut(BaseModel):
    """Datos de un registro de vacunación para la respuesta de la API.

    Attributes:
        id: Identificador del registro.
        lot_id: Identificador del lote.
        week: Semana del ciclo del registro.
        application_date: Fecha de aplicación.
        vaccine_name: Nombre de la vacuna.
        dosage: Dosis aplicada.
        batch_number: Número de lote del biológico.
        next_application_date: Fecha del refuerzo.
        created_at: Fecha de creación del registro.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    lot_id: int
    week: int
    application_date: date
    vaccine_name: str
    dosage: str
    batch_number: str | None
    next_application_date: date | None
    created_at: datetime
