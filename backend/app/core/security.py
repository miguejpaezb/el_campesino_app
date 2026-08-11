"""Seguridad y autenticación de la aplicación.

Provee utilidades para el hashing de contraseñas, generación y validación de
tokens JWT, y la dependencia de FastAPI `get_current_user` que protege los
endpoints sensibles.

Attributes:
    pwd_context (CryptContext): Contexto de hashing de contraseñas (bcrypt).
"""

from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def hash_password(password: str) -> str:
    """Genera el hash bcrypt de una contraseña en texto plano.

    Args:
        password: Contraseña en texto plano.

    Returns:
        Cadena con el hash bcrypt de la contraseña.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica que una contraseña en texto plano coincida con su hash.

    Args:
        plain_password: Contraseña en texto plano.
        hashed_password: Hash bcrypt almacenado.

    Returns:
        True si la contraseña coincide con el hash, False en caso contrario.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    data: dict[str, Any], expires_minutes: int | None = None
) -> str:
    """Crea un token JWT con los datos indicados.

    Args:
        data: Datos que se incluirán dentro del payload del token.
        expires_minutes: Minutos de validez del token. Si es None, se usa el
            valor de `settings.JWT_EXPIRATION_MINUTES`.

    Returns:
        Token JWT codificado como cadena.
    """
    to_encode = data.copy()
    expire_minutes = expires_minutes or settings.JWT_EXPIRATION_MINUTES
    expire = datetime.now(UTC) + timedelta(minutes=expire_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any] | None:
    """Decodifica y valida un token JWT.

    Args:
        token: Token JWT a decodificar.

    Returns:
        El payload del token si es válido, o None si no pudo decodificarse.
    """
    try:
        return jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
    except JWTError:
        return None


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Dependencia que devuelve el usuario autenticado a partir del token.

    Args:
        token: Token JWT extraído del header Authorization.
        db: Sesión de base de datos inyectada por FastAPI.

    Returns:
        El modelo `User` del usuario autenticado.

    Raises:
        HTTPException: Si el token es inválido, ha expirado o el usuario
            no existe o está inactivo.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    username: str | None = payload.get("sub")
    if username is None:
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if user is None or not user.is_active:
        raise credentials_exception

    return user
