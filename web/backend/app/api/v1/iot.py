"""Endpoints de monitoreo IoT.

Expone el registro y la consulta de lecturas de sensores ambientales, y las
alertas generadas por valores fuera del rango seguro.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.schemas.sensor_reading import SensorReadingCreate, SensorReadingOut
from app.services.iot_service import IotService

router = APIRouter()


@router.get(
    "/readings",
    response_model=list[SensorReadingOut],
    summary="Listar lecturas de sensores",
    description="Devuelve las lecturas registradas. Filtrar con `?lot_id=` y "
    "`?sensor_type=`. Ordenadas de la más reciente a la más antigua.",
)
def list_readings(
    lot_id: int | None = None,
    sensor_type: str | None = None,
    db: Session = Depends(get_db),
    _: object = Depends(get_current_user),
) -> list[SensorReadingOut]:
    """Lista las lecturas de sensores con filtros opcionales.

    Args:
        lot_id: Filtra por lote asociado.
        sensor_type: Filtra por tipo de sensor.
        db: Sesión de base de datos inyectada por FastAPI.

    Returns:
        Lista de lecturas de sensores.
    """
    service = IotService(db)
    readings = service.get_readings(lot_id=lot_id, sensor_type=sensor_type)
    return [SensorReadingOut.model_validate(r) for r in readings]


@router.post(
    "/readings",
    response_model=SensorReadingOut,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar una lectura de sensor",
    description="Registra una lectura y calcula automáticamente si genera "
    "alerta según el rango seguro del tipo de sensor.",
)
def create_reading(
    payload: SensorReadingCreate,
    db: Session = Depends(get_db),
    _: object = Depends(get_current_user),
) -> SensorReadingOut:
    """Registra una lectura de sensor y determina si es alerta.

    Args:
        payload: Datos de la lectura.
        db: Sesión de base de datos inyectada por FastAPI.

    Returns:
        La lectura registrada.

    Raises:
        HTTPException 404: Si el lote asociado no existe.
    """
    service = IotService(db)
    reading = service.create_reading(payload)
    return SensorReadingOut.model_validate(reading)


@router.get(
    "/alerts",
    response_model=list[SensorReadingOut],
    summary="Listar alertas activas",
    description="Devuelve las lecturas marcadas como alerta (valores fuera "
    "del rango seguro).",
)
def list_alerts(
    db: Session = Depends(get_db),
    _: object = Depends(get_current_user),
) -> list[SensorReadingOut]:
    """Lista las lecturas marcadas como alerta.

    Args:
        db: Sesión de base de datos inyectada por FastAPI.

    Returns:
        Lista de lecturas de alerta.
    """
    service = IotService(db)
    alerts = service.get_alerts()
    return [SensorReadingOut.model_validate(r) for r in alerts]
