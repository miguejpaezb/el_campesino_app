"""Modelo ORM de las lecturas de sensores IoT.

Almacena las lecturas ambientales registradas por los sensores de la granja
(temperatura, humedad, amoníaco) asociadas opcionalmente a un lote.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.bird_lot import BirdLot


class SensorReading(Base):
    """Representa una lectura registrada por un sensor IoT.

    Attributes:
        id: Identificador único de la lectura.
        sensor_id: Identificador del sensor que emitió la lectura.
        sensor_type: Tipo de sensor ("temperature", "humidity", "ammonia").
        lot_id: Identificador del lote asociado (opcional).
        value: Valor medido por el sensor.
        unit: Unidad de medida de la lectura.
        reading_timestamp: Fecha y hora de la lectura.
        is_alert: Indica si el valor está fuera del rango seguro.
        lot: Relación con el lote asociado.
    """

    __tablename__ = "sensor_readings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sensor_id: Mapped[str] = mapped_column(String(50), index=True)
    sensor_type: Mapped[str] = mapped_column(String(30), index=True)
    lot_id: Mapped[int | None] = mapped_column(
        ForeignKey("bird_lots.id"), nullable=True
    )
    value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(10), nullable=False)
    reading_timestamp: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    is_alert: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    lot: Mapped["BirdLot | None"] = relationship()
