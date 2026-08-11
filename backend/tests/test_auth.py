"""Pruebas de integración del módulo de autenticación.

Cubre el registro de usuarios, el login y el acceso al endpoint protegido
`/me` con distintos escenarios de credenciales.
"""


def test_register_success_returns_201_and_user_data(client):
    """El registro de un usuario válido debe devolver HTTP 201 con sus datos.

    Escenario:
        - Se envían datos de usuario válidos a /api/v1/auth/register.
        - La respuesta debe ser 201 y contener los datos públicos.
        - La respuesta no debe incluir el hash de la contraseña.
    """
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "nuevo_usuario",
            "email": "nuevo@example.com",
            "password": "Password123",
            "full_name": "Nuevo Usuario",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["username"] == "nuevo_usuario"
    assert body["email"] == "nuevo@example.com"
    assert body["full_name"] == "Nuevo Usuario"
    assert "hashed_password" not in body
    assert "password" not in body


def test_register_with_short_password_returns_422(client):
    """Una contraseña de menos de 8 caracteres debe ser rechazada.

    Escenario:
        - Se envía una contraseña de 6 caracteres.
        - FastAPI debe devolver HTTP 422 por validación de Pydantic.
    """
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "usuario_corto",
            "email": "corto@example.com",
            "password": "123456",
            "full_name": "Usuario Corto",
        },
    )
    assert response.status_code == 422


def test_register_with_invalid_email_returns_422(client):
    """Un correo mal formado debe ser rechazado por validación.

    Escenario:
        - Se envía un correo sin formato válido.
        - FastAPI debe devolver HTTP 422.
    """
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "usuario_correo",
            "email": "no-es-un-correo",
            "password": "Password123",
            "full_name": "Usuario Correo",
        },
    )
    assert response.status_code == 422


def test_register_with_duplicate_username_returns_409(client, test_user):
    """Registrar un username existente debe devolver HTTP 409.

    Escenario:
        - Ya existe un usuario con username "testuser".
        - Se intenta registrar otro usuario con el mismo username.
        - El servicio debe devolver conflicto 409.
    """
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser",
            "email": "otro@example.com",
            "password": "Password123",
            "full_name": "Otro Usuario",
        },
    )
    assert response.status_code == 409


def test_register_with_duplicate_email_returns_409(client, test_user):
    """Registrar un correo existente debe devolver HTTP 409.

    Escenario:
        - Ya existe un usuario con email "test@example.com".
        - Se intenta registrar otro usuario con el mismo correo.
        - El servicio debe devolver conflicto 409.
    """
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "otro_usuario",
            "email": "test@example.com",
            "password": "Password123",
            "full_name": "Otro Usuario",
        },
    )
    assert response.status_code == 409


def test_login_success_returns_token(client, test_user):
    """El login con credenciales válidas debe devolver un token JWT.

    Escenario:
        - Se envían las credenciales correctas del usuario de prueba.
        - La respuesta debe ser 200 y contener access_token y bearer.
    """
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "password": "Testpass123"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["access_token"]
    assert body["token_type"] == "bearer"


def test_login_with_wrong_password_returns_401(client, test_user):
    """El login con contraseña incorrecta debe devolver HTTP 401.

    Escenario:
        - Se envía la contraseña equivocada.
        - La API debe rechazar la autenticación con 401.
    """
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "password": "Wrongpass123"},
    )
    assert response.status_code == 401


def test_login_with_unknown_user_returns_401(client):
    """El login de un usuario inexistente debe devolver HTTP 401.

    Escenario:
        - Se envía un username que no existe en la base de datos.
        - La API debe rechazar la autenticación con 401.
    """
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "no_existe", "password": "Password123"},
    )
    assert response.status_code == 401


def test_me_with_valid_token_returns_user(client, auth_headers, test_user):
    """El endpoint /me con token válido debe devolver los datos del usuario.

    Escenario:
        - Se envía el header Authorization con el token del usuario de prueba.
        - La respuesta debe ser 200 con los datos públicos del usuario.
    """
    response = client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["username"] == "testuser"
    assert body["email"] == "test@example.com"


def test_me_without_token_returns_401(client):
    """El endpoint /me sin token debe devolver HTTP 401.

    Escenario:
        - No se envía el header Authorization.
        - La API debe rechazar el acceso con 401.
    """
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_me_with_invalid_token_returns_401(client):
    """El endpoint /me con un token inválido debe devolver HTTP 401.

    Escenario:
        - Se envía un token JWT aleatorio o corrupto.
        - La API debe rechazar el acceso con 401.
    """
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer token-invalido"},
    )
    assert response.status_code == 401
