"""Servicio de autenticación y gestión de usuarios.

Contiene la lógica de registro, autenticación y obtención del usuario actual.
Desacoplado de FastAPI y de la base de datos (usa el repositorio inyectado).
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import TokenResponse, UserCreate, UserLogin, UserOut


class AuthService:
    """Lógica de negocio para el registro y la autenticación de usuarios.

    Attributes:
        repository: Repositorio de usuarios usado para la persistencia.
    """

    def __init__(self, db: Session):
        self.repository = UserRepository(db)

    def register(
        self, user_data: UserCreate, role: str | None = None
    ) -> User:
        """Registra un nuevo usuario en el sistema.

        Args:
            user_data: Datos validados del usuario a crear.
            role: Rol opcional que sobreescribe el valor de `user_data.role`.

        Returns:
            El usuario creado.

        Raises:
            HTTPException: Si el nombre de usuario o el correo ya existen.
        """
        if self.repository.get_by_username(user_data.username):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El nombre de usuario ya está registrado",
            )
        if self.repository.get_by_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El correo electrónico ya está registrado",
            )

        hashed = hash_password(user_data.password)
        return self.repository.create(user_data, hashed, role=role)

    def authenticate(self, credentials: UserLogin) -> TokenResponse:
        """Autentica a un usuario y devuelve un token JWT.

        Args:
            credentials: Nombre de usuario y contraseña.

        Returns:
            Un objeto `TokenResponse` con el token de acceso.

        Raises:
            HTTPException: Si las credenciales son inválidas.
        """
        user = self.repository.get_by_username(credentials.username)
        valid = user is not None and verify_password(
            credentials.password, user.hashed_password
        )
        if not valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = create_access_token(data={"sub": user.username})
        return TokenResponse(access_token=token)

    def get_me(self, current_user: User) -> UserOut:
        """Devuelve los datos públicos del usuario autenticado.

        Args:
            current_user: Usuario inyectado por la dependencia de seguridad.

        Returns:
            Los datos públicos del usuario.
        """
        return UserOut.model_validate(current_user)

    def list_users(self) -> list[UserOut]:
        """Lista todos los usuarios del sistema.

        Returns:
            Lista con los datos públicos de todos los usuarios.
        """
        return [
            UserOut.model_validate(user) for user in self.repository.get_all()
        ]
