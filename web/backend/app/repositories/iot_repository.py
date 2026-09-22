"""Repositorio de acceso a datos para el monitoreo IoT.

Encapsula las consultas a la tabla `sensor_readings` mediante SQLAlchemy,
abstrayendo a la capa de servicios de los detalles de persistencia.
"""

from sqlalchemy.orm import Session

from app.models.sensor_reading import SensorReading


class IotRepository:
    """Acceso a datos de la entidad `SensorReading`."""

    def __init__(self, db: Session):
        self.db = db

    def get_all(
        self,
        lot_id: int | None = None,
        sensor_type: str | None = None,
    ) -> list[SensorReading]:
        """Lista las lecturas de sensores con filtros opcionales.

        Args:
            lot_id: Filtra por lote asociado.
            sensor_type: Filtra por tipo de sensor.

        Returns:
            Lista con las lecturas encontradas.
        """
        query = self.db.query(SensorReading)
        if lot_id is not None:
            query = query.filter(SensorReading.lot_id == lot_id)
        if sensor_type is not None:
            query = query.filter(SensorReading.sensor_type == sensor_type)
        return query.order_by(SensorReading.reading_timestamp.desc()).all()

    def get_alerts(self) -> list[SensorReading]:
        """Lista las lecturas marcadas como alerta.

        Returns:
            Lista con las lecturas de alerta.
        """
        return (
            self.db.query(SensorReading)
            .filter(SensorReading.is_alert.is_(True))
            .order_by(SensorReading.reading_timestamp.desc())
            .all()
        )

    def create(self, reading: SensorReading) -> SensorReading:
        """Persiste una nueva lectura de sensor.

        Args:
            reading: Instancia de `SensorReading` a crear.

        Returns:
            La lectura recién creada.
        """
        self.db.add(reading)
        self.db.commit()
        self.db.refresh(reading)
        return reading
