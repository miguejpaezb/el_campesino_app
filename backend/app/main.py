"""Punto de entrada de la aplicación FastAPI.

Configura la aplicación, el CORS, incluye los routers de la API y crea
las tablas de la base de datos al iniciar (solo en entornos con SQLite).
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import Base, engine


def create_app() -> FastAPI:
    """Crea y configura la instancia de la aplicación FastAPI.

    Returns:
        La aplicación FastAPI configurada con CORS y routers.
    """
    app = FastAPI(
        title=settings.APP_NAME,
        description="Sistema de gestión avícola El Campesino - Backend API",
        version="1.0.0",
    )

    if settings.DATABASE_URL.startswith("sqlite"):
        Base.metadata.create_all(bind=engine)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.FRONTEND_URL],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix="/api/v1")

    return app


app = create_app()
