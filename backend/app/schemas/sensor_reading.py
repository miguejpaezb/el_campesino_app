"""Schemas Pydantic para las lecturas de sensores IoT.

Define los DTOs de entrada y salida del módulo de monitoreo IoT.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

SensorType = Literal["temperature", "humidity", "ammonia"]


class SensorReadingCreate(BaseModel):
    """Datos necesarios para registrar una lectura de sensor.

    Attributes:
        sensor_id: Identificador del sensor (1-50 caracteres).
        sensor_type: Tipo de sensor (temperature, humidity, ammonia).
        lot_id: Identificador del lote asociado (opcional).
        value: Valor medido por el sensor.
    """

    sensor_id: str = Field(min_length=1, max_length=50)
    sensor_type: SensorType
    lot_id: int | None = None
    value: float


class SensorReadingOut(BaseModel):
    """Datos de una lectura de sensor para la respuesta de la API.

    Attributes:
        id: Identificador de la lectura.
        sensor_id: Identificador del sensor.
        sensor_type: Tipo de sensor.
        lot_id: Identificador del lote asociado.
        value: Valor medido.
        unit: Unidad de medida.
        reading_timestamp: Fecha y hora de la lectura.
        is_alert: Indica si el valor está fuera del rango seguro.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    sensor_id: str
    sensor_type: str
    lot_id: int | None
    value: float
    unit: str
    reading_timestamp: datetime
    is_alert: bool
