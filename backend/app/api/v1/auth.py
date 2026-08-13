"""Endpoints de autenticación y gestión de usuarios.

Expone las rutas `/register`, `/login` y `/me` para el módulo de auth.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_current_user, get_db
from app.models.user import User
from app.schemas.user import TokenResponse, UserCreate, UserLogin, UserOut
from app.services.auth_service import AuthService

router = APIRouter()


@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo usuario (solo admin)",
)
def register(
    payload: UserCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
) -> UserOut:
    """Crea un usuario en el sistema.

    Solo un usuario autenticado con rol admin puede crear cuentas.

    Args:
        payload: Datos del usuario a registrar.
        db: Sesión de base de datos inyectada por FastAPI.

    Returns:
        Los datos públicos del usuario recién creado.

    Raises:
        HTTPException 401: Si no hay sesión iniciada.
        HTTPException 403: Si el usuario autenticado no es admin.
        HTTPException 409: Si el username o el correo ya existen.
    """
    service = AuthService(db)
    user = service.register(payload)
    return UserOut.model_validate(user)


@router.get(
    "/users",
    response_model=list[UserOut],
    summary="Listar usuarios (solo admin)",
)
def list_users(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
) -> list[UserOut]:
    """Devuelve todos los usuarios registrados.

    Args:
        db: Sesión de base de datos inyectada por FastAPI.

    Returns:
        Lista con los datos públicos de todos los usuarios.
    """
    service = AuthService(db)
    return service.list_users()


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Iniciar sesión",
    description="Autentica al usuario y devuelve un token JWT de acceso.",
)
def login(payload: UserLogin, db: Session = Depends(get_db)) -> TokenResponse:
    """Autentica las credenciales y emite un token JWT.

    Args:
        payload: Nombre de usuario y contraseña.
        db: Sesión de base de datos inyectada por FastAPI.

    Returns:
        Token JWT de acceso.

    Raises:
        HTTPException 401: Si las credenciales son inválidas.
    """
    service = AuthService(db)
    return service.authenticate(payload)


@router.get(
    "/me",
    response_model=UserOut,
    summary="Obtener el usuario autenticado",
)
def get_me(current_user: User = Depends(get_current_user)) -> UserOut:
    """Devuelve los datos del usuario identificado por el token.

    Args:
        current_user: Usuario autenticado inyectado por la dependencia.

    Returns:
        Datos públicos del usuario autenticado.
    """
    return UserOut.model_validate(current_user)
