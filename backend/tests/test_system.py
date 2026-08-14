"""Pruebas de integración del módulo del sistema.

Cubre el chequeo de salud público de la API.
"""


def test_system_health_returns_ok(client):
    """El endpoint de salud debe responder 200 con estado ok.

    Escenario:
        - Se solicita GET /api/v1/health sin autenticación.
        - La respuesta debe ser 200 y contener status "ok".
    """
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
