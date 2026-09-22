"""Configuración de la base de datos.

Este módulo crea el engine de SQLAlchemy, la sesión y la clase base `Base`
para los modelos ORM. Además define el generador `get_db` usado como
dependencia de FastAPI para inyectar la sesión en cada request.

Attributes:
    engine (Engine): Engine de SQLAlchemy conectado a la base de datos.
    SessionLocal (sessionmaker): Fábrica de sesiones de la aplicación.
    Base (DeclarativeBase): Clase base para todos los modelos ORM.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

# SQLite requiere check_same_thread=False cuando se comparte la conexión
# entre el hilo de la app y el de los tests.
_connect_args = (
    {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
)

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=_connect_args,
    echo=settings.DEBUG,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Clase base declarativa de SQLAlchemy para todos los modelos."""


def get_db():
    """Generador de sesiones de base de datos.

    Cede una sesión a la dependencia de FastAPI y garantiza que se cierre
    correctamente al terminar el request.

    Yields:
        Session: Sesión de SQLAlchemy para el request actual.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
