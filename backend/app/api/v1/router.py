"""Routers de la versión 1 de la API.

Agrupa todos los sub-routers bajo el prefijo `/api/v1`.
"""

from fastapi import APIRouter

from app.api.v1 import (
    auth,
    feed_stock,
    feeding,
    health,
    iot,
    lots,
    production,
    system,
    traceability,
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(system.router, tags=["system"])
api_router.include_router(lots.router, prefix="/lots", tags=["lots"])
api_router.include_router(production.router, prefix="/lots", tags=["production"])
api_router.include_router(feeding.router, prefix="/lots", tags=["feeding"])
api_router.include_router(feed_stock.router, prefix="/feed-stock", tags=["feed-stock"])
api_router.include_router(health.router, prefix="/lots", tags=["health"])
api_router.include_router(
    traceability.router, prefix="/traceability", tags=["traceability"]
)
api_router.include_router(iot.router, prefix="/iot", tags=["iot"])
