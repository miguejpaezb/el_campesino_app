"""Endpoints del sistema.

Expone un chequeo de salud público para verificar que la API
está corriendo correctamente.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get(
    "/health",
    summary="Estado de salud del sistema",
    description="Indica si la API está operativa.",
)
def system_health() -> dict[str, str]:
    """Devuelve el estado operativo de la API.

    Returns:
        Diccionario con el estado del sistema.
    """
    return {"status": "ok"}
