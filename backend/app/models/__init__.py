"""Modelos ORM de la aplicación.

Importar aquí cada modelo garantiza que SQLAlchemy lo registre en el
metadata de `Base` (necesario para `create_all` y las migraciones).
"""

from app.models.audit_log import AuditLog
from app.models.bird_lot import BirdLot
from app.models.disease import Disease
from app.models.egg_production import EggProduction
from app.models.feed_stock import FeedStockMovement, FeedType
from app.models.feeding import FeedingRecord
from app.models.mortality import Mortality
from app.models.sensor_reading import SensorReading
from app.models.user import User
from app.models.vaccination import Vaccination

__all__ = [
    "AuditLog",
    "BirdLot",
    "Disease",
    "EggProduction",
    "FeedStockMovement",
    "FeedType",
    "FeedingRecord",
    "Mortality",
    "SensorReading",
    "User",
    "Vaccination",
]
