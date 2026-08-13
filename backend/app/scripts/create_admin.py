"""Script CLI para crear el primer usuario administrador.

Uso:
    python -m app.scripts.create_admin \\
        --username admin --email admin@example.com --password Cambiame123
"""

import argparse

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

import app.models  # noqa: F401  (registra los modelos en el metadata de Base)
from app.core.database import Base, SessionLocal, engine
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate
from app.services.auth_service import AuthService


def main() -> None:
    """Ejecuta la creación del usuario administrador inicial."""
    parser = argparse.ArgumentParser(
        description="Crea el primer usuario administrador del sistema."
    )
    parser.add_argument("--username", required=True, help="Nombre de usuario del admin")
    parser.add_argument("--email", required=True, help="Correo electrónico del admin")
    parser.add_argument("--password", required=True, help="Contraseña del admin")
    parser.add_argument(
        "--full-name", default="Administrador", help="Nombre completo del admin"
    )
    args = parser.parse_args()

    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        repository = UserRepository(db)
        existing = repository.get_by_username(args.username) or repository.get_by_email(
            args.email
        )
        if existing is not None:
            raise SystemExit(
                "Ya existe un usuario con ese nombre de usuario o correo. "
                "El admin inicial solo se crea si no hay cuentas previas."
            )

        user_data = UserCreate(
            username=args.username,
            email=args.email,
            password=args.password,
            full_name=args.full_name,
            role="admin",
        )
        try:
            service = AuthService(db)
            user = service.register(user_data, role="admin")
        except HTTPException as exc:
            raise SystemExit(
                f"No se pudo crear el usuario: {exc.detail}"
            ) from exc
        except IntegrityError as exc:
            raise SystemExit(
                "No se pudo crear el usuario: nombre o correo duplicado."
            ) from exc

        print(
            f"Usuario admin '{user.username}' ({user.full_name}) "
            f"con rol '{user.role}' creado correctamente."
        )


if __name__ == "__main__":
    main()
