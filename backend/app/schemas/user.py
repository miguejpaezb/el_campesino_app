"""Schemas Pydantic para la autenticación y los usuarios.

Define los DTOs de entrada y salida para el módulo de usuarios: creación,
login, respuesta de token y datos públicos del usuario.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

UserRole = Literal["admin", "operario", "veterinario"]


class UserCreate(BaseModel):
    """Datos necesarios para registrar un nuevo usuario.

    Attributes:
        username: Nombre de usuario (3-50 caracteres).
        email: Correo electrónico válido.
        password: Contraseña en texto plano (mínimo 8 caracteres).
        full_name: Nombre completo del usuario.
        role: Rol asignado al usuario (admin, operario, veterinario).
    """

    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str = Field(min_length=1, max_length=100)
    role: UserRole = "operario"


class UserLogin(BaseModel):
    """Credenciales para iniciar sesión.

    Attributes:
        username: Nombre de usuario.
        password: Contraseña en texto plano.
    """

    username: str
    password: str


class UserOut(BaseModel):
    """Datos públicos de un usuario (nunca incluye el hash de contraseña).

    Attributes:
        id: Identificador del usuario.
        username: Nombre de usuario.
        email: Correo electrónico.
        full_name: Nombre completo.
        role: Rol asignado.
        is_active: Si la cuenta está habilitada.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    full_name: str
    role: str
    is_active: bool


class TokenResponse(BaseModel):
    """Respuesta de autenticación con el token JWT.

    Attributes:
        access_token: Token JWT de acceso.
        token_type: Tipo de token (Bearer).
    """

    access_token: str
    token_type: str = "bearer"
