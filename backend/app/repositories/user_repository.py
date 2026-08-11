"""Repositorio de acceso a datos para usuarios.

Encapsula las consultas a la tabla `users` mediante SQLAlchemy, de modo que
la capa de servicios no conozca los detalles de la persistencia.
"""

from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate


class UserRepository:
    """Acceso a datos de la entidad `User`."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_username(self, username: str) -> User | None:
        """Busca un usuario por su nombre de usuario.

        Args:
            username: Nombre de usuario a buscar.

        Returns:
            El usuario encontrado o None si no existe.
        """
        return self.db.query(User).filter(User.username == username).first()

    def get_by_email(self, email: str) -> User | None:
        """Busca un usuario por su correo electrónico.

        Args:
            email: Correo electrónico a buscar.

        Returns:
            El usuario encontrado o None si no existe.
        """
        return self.db.query(User).filter(User.email == email).first()

    def create(self, user_data: UserCreate, hashed_password: str) -> User:
        """Crea y persiste un nuevo usuario.

        Args:
            user_data: Datos validados del nuevo usuario.
            hashed_password: Hash bcrypt de la contraseña.

        Returns:
            El usuario recién creado.
        """
        user = User(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
