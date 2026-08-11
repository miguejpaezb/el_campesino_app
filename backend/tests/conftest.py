"""Fixture principal de la suite de pruebas.

Provee la aplicación FastAPI con una base de datos SQLite en memoria,
un cliente de pruebas y utilidades para crear usuarios de prueba.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.schemas.user import UserCreate
from app.services.auth_service import AuthService


@pytest.fixture
def db_session():
    """Crea una base de datos SQLite en memoria para cada prueba.

    Yields:
        Session: Sesión de SQLAlchemy con las tablas creadas.
    """
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture
def client(db_session):
    """Cliente de pruebas con la sesión de la base en memoria.

    Override la dependencia `get_db` para usar la sesión de prueba.

    Yields:
        TestClient: Cliente HTTP de FastAPI para ejecutar los tests.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """Crea un usuario de prueba activo en la base de datos.

    Args:
        db_session: Sesión de la base en memoria.

    Returns:
        El usuario creado.
    """
    service = AuthService(db_session)
    user_data = UserCreate(
        username="testuser",
        email="test@example.com",
        password="Testpass123",
        full_name="Usuario de Prueba",
    )
    return service.register(user_data)


@pytest.fixture
def auth_headers(client, test_user):
    """Headers de autorización para un usuario autenticado.

    Realiza login con el usuario de prueba y devuelve los headers Bearer.

    Args:
        client: Cliente de pruebas.
        test_user: Usuario de prueba registrado.

    Returns:
        Diccionario con el header Authorization.
    """
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "password": "Testpass123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
