"""Dependencias compartidas por los routers de la API.

Re-exporta las dependencias de base de datos y seguridad para que los
routers las importen de forma limpia y consistente.
"""

from app.core.database import get_db
from app.core.security import get_current_admin, get_current_user, oauth2_scheme

__all__ = ["get_current_admin", "get_current_user", "get_db", "oauth2_scheme"]
