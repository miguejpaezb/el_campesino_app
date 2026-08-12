"""Schemas Pydantic para las enfermedades de los lotes.

Define los DTOs de creación, actualización y salida del módulo de sanidad.
"""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class DiseaseCreate(BaseModel):
    """Datos necesarios para registrar una enfermedad en un lote.

    Attributes:
        diagnosis_date: Fecha del diagnóstico. Si se omite, se usa hoy.
        disease_name: Nombre de la enfermedad (1-100 caracteres).
        affected_quantity: Cantidad de aves afectadas (mayor a 0).
        symptoms: Síntomas observados (opcional).
        treatment: Tratamiento aplicado (opcional).
        treatment_start_date: Fecha de inicio del tratamiento (opcional).
        treatment_end_date: Fecha de finalización del tratamiento (opcional).
        is_resolved: Indica si la enfermedad fue resuelta (opcional).
    """

    diagnosis_date: date | None = None
    disease_name: str = Field(min_length=1, max_length=100)
    affected_quantity: int = Field(gt=0)
    symptoms: str | None = Field(default=None, max_length=500)
    treatment: str | None = Field(default=None, max_length=500)
    treatment_start_date: date | None = None
    treatment_end_date: date | None = None
    is_resolved: bool = False


class DiseaseUpdate(BaseModel):
    """Campos actualizables de una enfermedad existente.

    Attributes:
        symptoms: Síntomas actualizados (opcional).
        treatment: Tratamiento actualizado (opcional).
        treatment_start_date: Fecha de inicio del tratamiento (opcional).
        treatment_end_date: Fecha de finalización del tratamiento (opcional).
        is_resolved: Nuevo estado de resolución (opcional).
    """

    symptoms: str | None = Field(default=None, max_length=500)
    treatment: str | None = Field(default=None, max_length=500)
    treatment_start_date: date | None = None
    treatment_end_date: date | None = None
    is_resolved: bool | None = None


class DiseaseOut(BaseModel):
    """Datos de una enfermedad para la respuesta de la API.

    Attributes:
        id: Identificador del registro.
        lot_id: Identificador del lote.
        diagnosis_date: Fecha del diagnóstico.
        disease_name: Nombre de la enfermedad.
        affected_quantity: Cantidad de aves afectadas.
        symptoms: Síntomas observados.
        treatment: Tratamiento aplicado.
        treatment_start_date: Fecha de inicio del tratamiento.
        treatment_end_date: Fecha de finalización del tratamiento.
        is_resolved: Si la enfermedad fue resuelta.
        created_at: Fecha de creación del registro.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    lot_id: int
    diagnosis_date: date
    disease_name: str
    affected_quantity: int
    symptoms: str | None
    treatment: str | None
    treatment_start_date: date | None
    treatment_end_date: date | None
    is_resolved: bool
    created_at: datetime
