"""Pruebas de integración del módulo de inventario de aves (lotes).

Cubre el CRUD de lotes, el avance de semana y la evaluación del ciclo
productivo, incluyendo los escenarios heredados del ejercicio en clase.
"""

from app.core.constants import CicloProductivo

LOT_PAYLOAD = {
    "lot_code": "LOTE-001",
    "breed": "Ross 308",
    "initial_quantity": 1000,
}


def _create_lot(client, auth_headers, **overrides):
    """Crea un lote a través de la API y devuelve la respuesta.

    Args:
        client: Cliente de pruebas.
        auth_headers: Headers de autenticación.
        overrides: Campos a sobreescribir en el payload.

    Returns:
        Respuesta HTTP de la creación.
    """
    payload = {**LOT_PAYLOAD, **overrides}
    return client.post("/api/v1/lots/", json=payload, headers=auth_headers)


def _advance_weeks(client, auth_headers, lot_id, weeks):
    """Avanza varias semanas a un lote a través de la API.

    Args:
        client: Cliente de pruebas.
        auth_headers: Headers de autenticación.
        lot_id: Identificador del lote.
        weeks: Cantidad de semanas a avanzar.

    Returns:
        La respuesta HTTP de la última operación.
    """
    response = None
    for _ in range(weeks):
        response = client.post(
            f"/api/v1/lots/{lot_id}/advance-week", headers=auth_headers
        )
    return response


def test_create_lot_success_returns_201(client, auth_headers):
    """La creación de un lote válido debe devolver HTTP 201.

    Escenario:
        - Se envía un payload válido con cantidad inicial.
        - La respuesta debe contener el lote con la semana inicial y
          la cantidad actual igual a la inicial.
    """
    response = _create_lot(client, auth_headers)
    assert response.status_code == 201
    body = response.json()
    assert body["lot_code"] == "LOTE-001"
    assert body["breed"] == "Ross 308"
    assert body["initial_quantity"] == 1000
    assert body["current_quantity"] == 1000
    assert body["current_week"] == CicloProductivo.SEMANA_COMPRA
    assert body["is_active"] is True


def test_create_lot_duplicate_code_returns_409(client, auth_headers):
    """Crear un lote con código duplicado debe devolver HTTP 409.

    Escenario:
        - Se crea un lote con código LOTE-001.
        - Se intenta crear otro lote con el mismo código.
        - El servicio debe devolver conflicto.
    """
    _create_lot(client, auth_headers)
    response = _create_lot(client, auth_headers, lot_code="LOTE-001")
    assert response.status_code == 409


def test_create_lot_with_negative_quantity_returns_422(client, auth_headers):
    """Una cantidad inicial negativa o cero debe ser rechazada.

    Escenario:
        - Se envía initial_quantity = 0.
        - FastAPI debe devolver HTTP 422 por validación de Pydantic.
    """
    response = _create_lot(client, auth_headers, initial_quantity=0)
    assert response.status_code == 422


def test_create_lot_without_auth_returns_401(client):
    """Crear un lote sin token debe devolver HTTP 401.

    Escenario:
        - No se envía el header Authorization.
        - La API debe rechazar la operación con 401.
    """
    response = client.post("/api/v1/lots/", json=LOT_PAYLOAD)
    assert response.status_code == 401


def test_list_lots_empty_returns_empty_list(client, auth_headers):
    """Listar lotes sin registros debe devolver una lista vacía.

    Escenario:
        - No hay lotes en la base de datos.
        - La respuesta debe ser 200 con una lista vacía.
    """
    response = client.get("/api/v1/lots/", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_list_lots_with_active_filter(client, auth_headers):
    """El filtro `active=true` debe devolver solo lotes activos.

    Escenario:
        - Se crean dos lotes y se descarta uno.
        - Con active=true solo debe aparecer el lote activo.
    """
    active = _create_lot(client, auth_headers).json()
    discarded = _create_lot(
        client, auth_headers, lot_code="LOTE-002"
    ).json()

    client.request(
        "DELETE",
        f"/api/v1/lots/{discarded['id']}",
        json={"reason": "Prueba de descarte"},
        headers=auth_headers,
    )

    response = client.get("/api/v1/lots/?active=true", headers=auth_headers)
    assert response.status_code == 200
    bodies = response.json()
    assert len(bodies) == 1
    assert bodies[0]["id"] == active["id"]


def test_get_lot_success(client, auth_headers):
    """Obtener un lote existente debe devolver HTTP 200.

    Escenario:
        - Se crea un lote.
        - Se consulta por su id y se devuelven sus datos.
    """
    created = _create_lot(client, auth_headers).json()
    response = client.get(f"/api/v1/lots/{created['id']}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["lot_code"] == "LOTE-001"


def test_get_lot_not_found_returns_404(client, auth_headers):
    """Obtener un lote inexistente debe devolver HTTP 404.

    Escenario:
        - Se consulta un id que no existe.
        - La API debe devolver 404.
    """
    response = client.get("/api/v1/lots/9999", headers=auth_headers)
    assert response.status_code == 404


def test_update_lot_success(client, auth_headers):
    """Actualizar un lote debe aplicar los cambios enviados.

    Escenario:
        - Se crea un lote y se actualiza su raza.
        - La respuesta debe reflejar la nueva raza.
    """
    created = _create_lot(client, auth_headers).json()
    response = client.put(
        f"/api/v1/lots/{created['id']}",
        json={"breed": "Lohmann Brown"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["breed"] == "Lohmann Brown"


def test_discard_lot_success(client, auth_headers):
    """Descartar un lote debe desactivarlo y guardar la razón.

    Escenario:
        - Se crea un lote y se descarta con una razón.
        - El lote debe quedar inactivo con la razón registrada.
    """
    created = _create_lot(client, auth_headers).json()
    response = client.request(
        "DELETE",
        f"/api/v1/lots/{created['id']}",
        json={"reason": "Fallo de postura"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["is_active"] is False
    assert body["discard_reason"] == "Fallo de postura"


def test_advance_week_increments_current_week(client, auth_headers):
    """Avanzar una semana debe incrementar la semana actual en 1.

    Escenario:
        - Se crea un lote en la semana 16.
        - Se avanza una semana y la semana actual debe ser 17.
    """
    created = _create_lot(client, auth_headers).json()
    response = client.post(
        f"/api/v1/lots/{created['id']}/advance-week", headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["current_week"] == CicloProductivo.SEMANA_COMPRA + 1


def test_evaluate_before_week_90_returns_waiting_message(client, auth_headers):
    """Evaluar antes de la semana 90 debe indicar que aún no aplica.

    Escenario:
        - Se crea un lote en la semana 16 y se evalúa.
        - La API debe responder que aún no es la semana de evaluación
          y el lote debe seguir activo.
    """
    created = _create_lot(client, auth_headers).json()
    response = client.post(
        f"/api/v1/lots/{created['id']}/evaluate", headers=auth_headers
    )
    assert response.status_code == 200
    body = response.json()
    assert "no es la semana de evaluación" in body["message"]
    assert body["is_active"] is True


def test_evaluate_at_week_90_without_production_discards_lot(client, auth_headers):
    """Evaluar en la semana 90 sin producción debe descartar el lote.

    Escenario:
        - Se avanza el lote hasta la semana 90.
        - No hay registros de postura, por lo que el porcentaje es 0
          (por debajo del mínimo del 80%).
        - La evaluación debe desactivar el lote.
    """
    created = _create_lot(client, auth_headers).json()
    weeks = CicloProductivo.SEMANA_DE_EVALUACION - CicloProductivo.SEMANA_COMPRA
    _advance_weeks(client, auth_headers, created["id"], weeks)

    response = client.post(
        f"/api/v1/lots/{created['id']}/evaluate", headers=auth_headers
    )
    assert response.status_code == 200
    body = response.json()
    assert body["is_active"] is False
    assert "Desempeño por debajo" in body["message"]

    detail = client.get(
        f"/api/v1/lots/{created['id']}", headers=auth_headers
    ).json()
    assert detail["is_active"] is False


def test_lot_summary_returns_indicators(client, auth_headers):
    """El resumen de un lote debe devolver sus indicadores.

    Escenario:
        - Se crea un lote y se solicita su resumen.
        - La respuesta debe incluir los indicadores con valores iniciales.
    """
    created = _create_lot(client, auth_headers).json()
    response = client.get(
        f"/api/v1/lots/{created['id']}/summary", headers=auth_headers
    )
    assert response.status_code == 200
    body = response.json()
    assert body["lot_code"] == "LOTE-001"
    assert body["initial_quantity"] == 1000
    assert body["current_quantity"] == 1000
    assert body["survival_percentage"] == 100.0
    assert body["total_eggs"] == 0
