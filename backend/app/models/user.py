"""Modelo ORM de usuarios del sistema.

Define la tabla `users` que almacena las cuentas de acceso al sistema.
Las contraseñas siempre se guardan como hash bcrypt, nunca en texto plano.
"""

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class User(Base):
    """Representa un usuario del sistema.

    Attributes:
        id: Identificador único del usuario.
        username: Nombre de usuario único para el login.
        email: Correo electrónico único del usuario.
        hashed_password: Hash bcrypt de la contraseña.
        full_name: Nombre completo del usuario.
        is_active: Indica si la cuenta se encuentra habilitada.
        role: Rol del usuario (admin, operario, veterinario).
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    role: Mapped[str] = mapped_column(String(20), default="operario")
