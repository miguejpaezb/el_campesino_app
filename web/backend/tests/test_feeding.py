"""Pruebas de integración del módulo de alimentación.

Cubre el registro de alimentación, el listado, el total de kilos, el costo
total y la integración con el resumen del lote.
"""

from app.core.constants import CicloProductivo

LOT_PAYLOAD = {
    "lot_code": "LOTE-FEED",
    "breed": "Ross 308",
    "initial_quantity": 1000,
}


def _create_lot(client, auth_headers):
    """Crea un lote de prueba y devuelve su cuerpo de respuesta.

    Args:
        client: Cliente de pruebas.
        auth_headers: Headers de autenticación.

    Returns:
        Diccionario con el lote creado.
    """
    response = client.post("/api/v1/lots/", json=LOT_PAYLOAD, headers=auth_headers)
    return response.json()


def _register_feeding(client, auth_headers, lot_id, kilos, **overrides):
    """Registra alimentación a través de la API.

    Args:
        client: Cliente de pruebas.
        auth_headers: Headers de autenticación.
        lot_id: Identificador del lote.
        kilos: Cantidad de alimento en kilos.
        overrides: Campos adicionales del payload.

    Returns:
        Respuesta HTTP del registro.
    """
    payload = {"feed_type": "Concentrado", "kilos": kilos, **overrides}
    return client.post(
        f"/api/v1/lots/{lot_id}/feeding", json=payload, headers=auth_headers
    )


def test_register_feeding_success_returns_201(client, auth_headers):
    """Registrar alimentación en un lote activo debe devolver HTTP 201.

    Escenario:
        - Se crea un lote y se registran 150 kg de alimento.
        - La semana del registro debe ser la semana actual del lote.
    """
    lot = _create_lot(client, auth_headers)

    response = _register_feeding(client, auth_headers, lot["id"], 150)
    assert response.status_code == 201
    body = response.json()
    assert body["lot_id"] == lot["id"]
    assert body["kilos"] == 150
    assert body["feed_type"] == "Concentrado"
    assert body["week"] == CicloProductivo.SEMANA_COMPRA
    assert body["total_cost"] is None


def test_register_feeding_with_cost_computes_total_cost(client, auth_headers):
    """El registro con costo debe calcular el total_cost en la respuesta.

    Escenario:
        - Se registran 100 kg a $2.5 por kilo.
        - total_cost debe ser 250.0.
    """
    lot = _create_lot(client, auth_headers)

    response = _register_feeding(
        client, auth_headers, lot["id"], 100, cost_per_kilo=2.5
    )
    assert response.status_code == 201
    assert response.json()["total_cost"] == 250.0


def test_register_feeding_inactive_lot_returns_400(client, auth_headers):
    """Registrar alimentación en un lote inactivo debe devolver HTTP 400.

    Escenario:
        - Se crea un lote y se descarta.
        - El servicio debe rechazar el registro con 400.
    """
    lot = _create_lot(client, auth_headers)
    client.request(
        "DELETE",
        f"/api/v1/lots/{lot['id']}",
        json={"reason": "Descarte de prueba"},
        headers=auth_headers,
    )
    response = _register_feeding(client, auth_headers, lot["id"], 50)
    assert response.status_code == 400


def test_register_feeding_negative_kilos_returns_422(client, auth_headers):
    """Una cantidad de kilos negativa o cero debe ser rechazada.

    Escenario:
        - Se envía kilos = 0.
        - FastAPI debe devolver HTTP 422 por validación de Pydantic.
    """
    lot = _create_lot(client, auth_headers)
    response = _register_feeding(client, auth_headers, lot["id"], 0)
    assert response.status_code == 422


def test_list_feeding_returns_records(client, auth_headers):
    """Listar la alimentación debe devolver los registros del lote.

    Escenario:
        - Se registran dos suministros de alimento.
        - La lista debe contener ambos registros.
    """
    lot = _create_lot(client, auth_headers)
    _register_feeding(client, auth_headers, lot["id"], 100)
    _register_feeding(client, auth_headers, lot["id"], 200)

    response = client.get(
        f"/api/v1/lots/{lot['id']}/feeding", headers=auth_headers
    )
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_total_feed_returns_sum(client, auth_headers):
    """El total de kilos debe ser la suma de los registros.

    Escenario:
        - Se registran 100.5 y 50 kg.
        - El total debe ser 150.5.
    """
    lot = _create_lot(client, auth_headers)
    _register_feeding(client, auth_headers, lot["id"], 100.5)
    _register_feeding(client, auth_headers, lot["id"], 50)

    response = client.get(
        f"/api/v1/lots/{lot['id']}/feeding/total", headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["total_feed_kg"] == 150.5


def test_total_feed_cost_sums_only_records_with_cost(client, auth_headers):
    """El costo total solo debe considerar registros con costo por kilo.

    Escenario:
        - Se registran 100 kg a $2 (costo 200) y 50 kg sin costo.
        - El costo total debe ser 200.0.
    """
    lot = _create_lot(client, auth_headers)
    _register_feeding(client, auth_headers, lot["id"], 100, cost_per_kilo=2)
    _register_feeding(client, auth_headers, lot["id"], 50)

    response = client.get(
        f"/api/v1/lots/{lot['id']}/feeding/cost", headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["total_feed_cost"] == 200.0


def test_summary_includes_feed_after_registration(client, auth_headers):
    """El resumen debe reflejar la alimentación registrada.

    Escenario:
        - Lote con 2 registros de 100 kg cada uno.
        - El resumen debe mostrar total_feed=200.0.
    """
    lot = _create_lot(client, auth_headers)
    _register_feeding(client, auth_headers, lot["id"], 100)
    _register_feeding(client, auth_headers, lot["id"], 100)

    response = client.get(
        f"/api/v1/lots/{lot['id']}/summary", headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["total_feed"] == 200.0
