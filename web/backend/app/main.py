"""Punto de entrada de la aplicación FastAPI.

Configura la aplicación, el CORS, incluye los routers de la API y crea
las tablas de la base de datos al iniciar (solo en entornos con SQLite).
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import inspect, text

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import Base, engine

STATIC_DIR = Path(__file__).parent / "static"


def _run_lightweight_migrations() -> None:
    """Aplica migraciones ligeras a bases SQLite existentes.

    `create_all` solo crea tablas nuevas; las columnas agregadas a tablas
    existentes se añaden aquí mediante `ALTER TABLE`.
    """
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())

    if "feeding_records" in tables:
        columns = {
            column["name"] for column in inspector.get_columns("feeding_records")
        }
        if "feed_type_id" not in columns:
            with engine.begin() as connection:
                connection.execute(
                    text(
                        "ALTER TABLE feeding_records "
                        "ADD COLUMN feed_type_id INTEGER"
                    )
                )


def create_app() -> FastAPI:
    """Crea y configura la instancia de la aplicación FastAPI.

    Returns:
        La aplicación FastAPI configurada con CORS y routers.
    """
    app = FastAPI(
        title=settings.APP_NAME,
        description="Sistema de gestión avícola El Campesino - Backend API",
        version="1.0.0",
        docs_url=None,
    )

    if settings.DATABASE_URL.startswith("sqlite"):
        Base.metadata.create_all(bind=engine)
        _run_lightweight_migrations()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.FRONTEND_URL],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @app.get("/docs", include_in_schema=False)
    async def custom_docs() -> FileResponse:
        """Devuelve la página de documentación personalizada.

        Returns:
            El archivo HTML de la documentación.
        """
        return FileResponse(STATIC_DIR / "docs" / "index.html")

    app.include_router(api_router, prefix="/api/v1")

    return app


app = create_app()
