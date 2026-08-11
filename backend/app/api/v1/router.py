"""Routers de la versión 1 de la API.

Agrupa todos los sub-routers bajo el prefijo `/api/v1`.
"""

from fastapi import APIRouter

from app.api.v1 import auth, feeding, lots, production

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(lots.router, prefix="/lots", tags=["lots"])
api_router.include_router(production.router, prefix="/lots", tags=["production"])
api_router.include_router(feeding.router, prefix="/lots", tags=["feeding"])
