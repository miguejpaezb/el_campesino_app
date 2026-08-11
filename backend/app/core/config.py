"""Configuración de la aplicación.

Carga las variables de entorno desde un archivo `.env` y expone la instancia
global `settings` con todos los valores de configuración del sistema.

Attributes:
    settings (Settings): Instancia única de configuración de la aplicación.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración central de la aplicación.

    Lee los valores desde variables de entorno o desde el archivo `.env`.
    Todos los valores sensibles deben definirse en el entorno, nunca en el
    código fuente.

    Attributes:
        APP_NAME: Nombre de la aplicación.
        APP_ENV: Entorno de ejecución (development, production, testing).
        DEBUG: Habilita o deshabilita el modo depuración.
        DATABASE_URL: Cadena de conexión de la base de datos.
        SECRET_KEY: Llave secreta para firmar tokens JWT.
        JWT_ALGORITHM: Algoritmo usado para firmar los tokens JWT.
        JWT_EXPIRATION_MINUTES: Minutos de validez de un token JWT.
        HOST: Host de escucha del servidor.
        PORT: Puerto de escucha del servidor.
        FRONTEND_URL: Origen permitido para CORS.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    APP_NAME: str = "ElCampesino"
    APP_ENV: str = "development"
    DEBUG: bool = True

    DATABASE_URL: str = "sqlite:///./el_campesino.db"

    SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60

    HOST: str = "0.0.0.0"
    PORT: int = 8000

    FRONTEND_URL: str = "http://localhost:3000"


settings = Settings()
