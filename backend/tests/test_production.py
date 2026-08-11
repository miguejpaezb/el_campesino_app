"""Pruebas de integración del módulo de producción diaria de huevos.

Cubre el registro de producción, las consultas por fechas, los indicadores
(total, promedio, porcentaje) y la evaluación del lote con buen rendimiento
(escenario diferido de la Fase 2).
"""

from app.core.constants import CicloProductivo

LOT_PAYLOAD = {
    "lot_code": "LOTE-PROD",
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


def _advance_weeks(client, auth_headers, lot_id, weeks):
    """Avanza una cantidad de semanas a un lote.

    Args:
        client: Cliente de pruebas.
        auth_headers: Headers de autenticación.
        lot_id: Identificador del lote.
        weeks: Cantidad de semanas a avanzar.
    """
    for _ in range(weeks):
        client.post(f"/api/v1/lots/{lot_id}/advance-week", headers=auth_headers)


def _advance_to(client, auth_headers, lot_id, target_week):
    """Avanza el lote hasta una semana objetivo.

    Args:
        client: Cliente de pruebas.
        auth_headers: Headers de autenticación.
        lot_id: Identificador del lote.
        target_week: Semana a la que se quiere llegar.
    """
    weeks = target_week - CicloProductivo.SEMANA_COMPRA
    _advance_weeks(client, auth_headers, lot_id, weeks)


def _register_eggs(client, auth_headers, lot_id, egg_count, **overrides):
    """Registra producción a través de la API.

    Args:
        client: Cliente de pruebas.
        auth_headers: Headers de autenticación.
        lot_id: Identificador del lote.
        egg_count: Cantidad de huevos.
        overrides: Campos adicionales del payload.

    Returns:
        Respuesta HTTP del registro.
    """
    payload = {"egg_count": egg_count, **overrides}
    return client.post(
        f"/api/v1/lots/{lot_id}/production", json=payload, headers=auth_headers
    )


def test_register_production_success_returns_201(client, auth_headers):
    """Registrar producción en un lote en postura debe devolver HTTP 201.

    Escenario:
        - Se avanza el lote hasta la semana de postura (28).
        - Se registran 500 huevos.
        - La semana del registro debe ser la semana actual del lote.
    """
    lot = _create_lot(client, auth_headers)
    _advance_to(client, auth_headers, lot["id"], CicloProductivo.SEMANA_DE_POSTURA)

    response = _register_eggs(client, auth_headers, lot["id"], 500)
    assert response.status_code == 201
    body = response.json()
    assert body["lot_id"] == lot["id"]
    assert body["egg_count"] == 500
    assert body["week"] == CicloProductivo.SEMANA_DE_POSTURA


def test_register_production_before_postura_returns_400(client, auth_headers):
    """Registrar producción antes de la semana 28 debe devolver HTTP 400.

    Escenario:
        - El lote se crea en la semana 16 (antes de la postura).
        - El servicio debe rechazar el registro con 400.
    """
    lot = _create_lot(client, auth_headers)
    response = _register_eggs(client, auth_headers, lot["id"], 100)
    assert response.status_code == 400


def test_register_production_inactive_lot_returns_400(client, auth_headers):
    """Registrar producción en un lote inactivo debe devolver HTTP 400.

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
    response = _register_eggs(client, auth_headers, lot["id"], 100)
    assert response.status_code == 400


def test_register_production_negative_count_returns_422(client, auth_headers):
    """Una cantidad de huevos negativa debe ser rechazada.

    Escenario:
        - Se envía egg_count = -5.
        - FastAPI debe devolver HTTP 422 por validación de Pydantic.
    """
    lot = _create_lot(client, auth_headers)
    _advance_to(client, auth_headers, lot["id"], CicloProductivo.SEMANA_DE_POSTURA)
    response = _register_eggs(client, auth_headers, lot["id"], -5)
    assert response.status_code == 422


def test_list_production_returns_records(client, auth_headers):
    """Listar la producción debe devolver los registros del lote.

    Escenario:
        - Se registran dos producciones.
        - La lista debe contener ambos registros.
    """
    lot = _create_lot(client, auth_headers)
    _advance_to(client, auth_headers, lot["id"], CicloProductivo.SEMANA_DE_POSTURA)
    _register_eggs(client, auth_headers, lot["id"], 100)
    _register_eggs(client, auth_headers, lot["id"], 200)

    response = client.get(
        f"/api/v1/lots/{lot['id']}/production", headers=auth_headers
    )
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_list_production_filtered_by_date(client, auth_headers):
    """El filtro por fechas debe limitar los registros devueltos.

    Escenario:
        - Se registra producción el 10-01-2026 y el 10-02-2026.
        - Filtrando desde febrero solo debe aparecer el segundo registro.
    """
    lot = _create_lot(client, auth_headers)
    _advance_to(client, auth_headers, lot["id"], CicloProductivo.SEMANA_DE_POSTURA)
    _register_eggs(
        client, auth_headers, lot["id"], 100, collection_date="2026-01-10"
    )
    _register_eggs(
        client, auth_headers, lot["id"], 200, collection_date="2026-02-10"
    )

    response = client.get(
        f"/api/v1/lots/{lot['id']}/production?from=2026-02-01",
        headers=auth_headers,
    )
    assert response.status_code == 200
    bodies = response.json()
    assert len(bodies) == 1
    assert bodies[0]["egg_count"] == 200


def test_total_eggs_returns_sum(client, auth_headers):
    """El total de huevos debe ser la suma de los registros.

    Escenario:
        - Se registran 300 y 500 huevos.
        - El total debe ser 800.
    """
    lot = _create_lot(client, auth_headers)
    _advance_to(client, auth_headers, lot["id"], CicloProductivo.SEMANA_DE_POSTURA)
    _register_eggs(client, auth_headers, lot["id"], 300)
    _register_eggs(client, auth_headers, lot["id"], 500)

    response = client.get(
        f"/api/v1/lots/{lot['id']}/production/total", headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["total_eggs"] == 800


def test_average_weekly_production(client, auth_headers):
    """El promedio semanal debe ser total / número de registros.

    Escenario:
        - Se registran 100 y 200 huevos.
        - El promedio debe ser 150.0.
    """
    lot = _create_lot(client, auth_headers)
    _advance_to(client, auth_headers, lot["id"], CicloProductivo.SEMANA_DE_POSTURA)
    _register_eggs(client, auth_headers, lot["id"], 100)
    _register_eggs(client, auth_headers, lot["id"], 200)

    response = client.get(
        f"/api/v1/lots/{lot['id']}/production/average", headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["average_weekly_production"] == 150.0


def test_laying_percentage(client, auth_headers):
    """El porcentaje de postura debe calcularse contra el máximo teórico.

    Escenario:
        - Lote de 1000 aves con 2 registros de 500 huevos cada uno.
        - Máximo teórico = 1000 x 7 x 2 = 14000, porcentaje = 1000/14000 = 7.14%.
    """
    lot = _create_lot(client, auth_headers)
    _advance_to(client, auth_headers, lot["id"], CicloProductivo.SEMANA_DE_POSTURA)
    _register_eggs(client, auth_headers, lot["id"], 500)
    _register_eggs(client, auth_headers, lot["id"], 500)

    response = client.get(
        f"/api/v1/lots/{lot['id']}/production/percentage", headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["laying_percentage"] == 7.14


def test_evaluate_good_performance_extends_weeks(client, auth_headers):
    """Evaluar un lote con buen rendimiento debe extender el ciclo 30 semanas.

    Escenario:
        - Lote de 1000 aves avanzado hasta la semana 90.
        - Se registran 7 producciones de 5600 huevos (80% de postura).
        - La evaluación debe aprobar el lote y extender a la semana 120.
    """
    lot = _create_lot(client, auth_headers)
    _advance_to(client, auth_headers, lot["id"], CicloProductivo.SEMANA_DE_EVALUACION)

    for _ in range(7):
        _register_eggs(client, auth_headers, lot["id"], 5600)

    response = client.post(
        f"/api/v1/lots/{lot['id']}/evaluate", headers=auth_headers
    )
    assert response.status_code == 200
    body = response.json()
    assert "aprobado por eficiencia" in body["message"]
    assert body["is_active"] is True

    detail = client.get(f"/api/v1/lots/{lot['id']}", headers=auth_headers).json()
    assert (
        detail["current_week"]
        == CicloProductivo.SEMANA_DE_EVALUACION + CicloProductivo.EXTENSION_SEMANAS
    )


def test_summary_includes_eggs_after_production(client, auth_headers):
    """El resumen debe reflejar la producción registrada.

    Escenario:
        - Lote en postura con 2 registros de 100 huevos.
        - El resumen debe mostrar total_eggs=200 y promedio=100.0.
    """
    lot = _create_lot(client, auth_headers)
    _advance_to(client, auth_headers, lot["id"], CicloProductivo.SEMANA_DE_POSTURA)
    _register_eggs(client, auth_headers, lot["id"], 100)
    _register_eggs(client, auth_headers, lot["id"], 100)

    response = client.get(
        f"/api/v1/lots/{lot['id']}/summary", headers=auth_headers
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total_eggs"] == 200
    assert body["average_weekly_production"] == 100.0
