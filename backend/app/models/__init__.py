"""Modelos ORM de la aplicación.

Importar aquí cada modelo garantiza que SQLAlchemy lo registre en el
metadata de `Base` (necesario para `create_all` y las migraciones).
"""

from app.models.bird_lot import BirdLot
from app.models.egg_production import EggProduction
from app.models.feeding import FeedingRecord
from app.models.user import User

__all__ = ["BirdLot", "EggProduction", "FeedingRecord", "User"]
