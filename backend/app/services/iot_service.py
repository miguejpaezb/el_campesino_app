"""Servicio de lógica de negocio del monitoreo IoT.

Registra y consulta las lecturas de los sensores ambientales, determinando
automáticamente si un valor está fuera del rango seguro (alerta).
"""

from sqlalchemy.orm import Session

from app.core.constants import SensorThresholds, SensorUnits
from app.models.sensor_reading import SensorReading
from app.repositories.iot_repository import IotRepository
from app.schemas.sensor_reading import SensorReadingCreate, SensorType
from app.services.lot_service import LotService

_UNITS_BY_SENSOR: dict[SensorType, str] = {
    "temperature": SensorUnits.TEMPERATURE,
    "humidity": SensorUnits.HUMIDITY,
    "ammonia": SensorUnits.AMMONIA,
}


class IotService:
    """Lógica de negocio de las lecturas de sensores.

    Attributes:
        repository: Repositorio IoT usado para la persistencia.
        lot_service: Servicio de lotes para validar el lote asociado.
    """

    def __init__(self, db: Session):
        self.repository = IotRepository(db)
        self.lot_service = LotService(db)

    @staticmethod
    def _compute_alert(sensor_type: str, value: float) -> bool:
        """Determina si un valor está fuera del rango seguro.

        Args:
            sensor_type: Tipo de sensor.
            value: Valor medido.

        Returns:
            True si el valor está fuera del rango seguro.
        """
        if sensor_type == "temperature":
            return value < SensorThresholds.TEMPERATURE_MIN or (
                value > SensorThresholds.TEMPERATURE_MAX
            )
        if sensor_type == "humidity":
            return value < SensorThresholds.HUMIDITY_MIN or (
                value > SensorThresholds.HUMIDITY_MAX
            )
        if sensor_type == "ammonia":
            return value >= SensorThresholds.AMMONIA_MAX
        return False

    def create_reading(self, data: SensorReadingCreate) -> SensorReading:
        """Registra una lectura de sensor y calcula si genera alerta.

        Args:
            data: Datos validados de la lectura.

        Returns:
            La lectura registrada.

        Raises:
            HTTPException 404: Si el lote asociado no existe.
        """
        if data.lot_id is not None:
            self.lot_service.get_lot(data.lot_id)

        reading = SensorReading(
            sensor_id=data.sensor_id,
            sensor_type=data.sensor_type,
            lot_id=data.lot_id,
            value=data.value,
            unit=_UNITS_BY_SENSOR[data.sensor_type],
            is_alert=self._compute_alert(data.sensor_type, data.value),
        )
        return self.repository.create(reading)

    def get_readings(
        self,
        lot_id: int | None = None,
        sensor_type: str | None = None,
    ) -> list[SensorReading]:
        """Lista las lecturas de sensores con filtros opcionales.

        Args:
            lot_id: Filtra por lote asociado.
            sensor_type: Filtra por tipo de sensor.

        Returns:
            Lista de lecturas, ordenadas de la más reciente a la más antigua.
        """
        return self.repository.get_all(lot_id=lot_id, sensor_type=sensor_type)

    def get_alerts(self) -> list[SensorReading]:
        """Lista las lecturas marcadas como alerta.

        Returns:
            Lista de lecturas de alerta.
        """
        return self.repository.get_alerts()
