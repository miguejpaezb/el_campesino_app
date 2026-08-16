"""Pruebas de integración del módulo de producción diaria de huevos.

Cubre el registro de producción, las consultas por fechas, los indicadores
(total, promedio, porcentaje) y la evaluación del lote con buen rendimiento
(escenario diferido de la Fase 2).
"""

from datetime import date, datetime, timedelta

import pytest

from app.core.constants import CicloProductivo

LOT_PAYLOAD = {
    "lot_code": "LOTE-PROD",
    "breed": "Ross 308",
    "initial_quantity": 1000,
}


def _yesterday_iso():
    """Devuelve la fecha de ayer en formato ISO.

    Returns:
        Fecha de ayer como cadena `AAAA-MM-DD`.
    """
    return (date.today() - timedelta(days=1)).isoformat()


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
        - Se registra producción ayer y hoy.
        - Filtrando desde hoy solo debe aparecer el registro de hoy.
    """
    lot = _create_lot(client, auth_headers)
    _advance_to(client, auth_headers, lot["id"], CicloProductivo.SEMANA_DE_POSTURA)
    _register_eggs(
        client, auth_headers, lot["id"], 100, collection_date=_yesterday_iso()
    )
    _register_eggs(
        client,
        auth_headers,
        lot["id"],
        200,
        collection_date=date.today().isoformat(),
    )

    response = client.get(
        f"/api/v1/lots/{lot['id']}/production?from={date.today().isoformat()}",
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


def test_register_production_with_both_zero_returns_422(client, auth_headers):
    """Aptos y no aptos en 0 debe ser rechazado.

    Escenario:
        - Se envía egg_count=0 y broken_eggs=0.
        - La validación debe devolver HTTP 422.
    """
    lot = _create_lot(client, auth_headers)
    _advance_to(client, auth_headers, lot["id"], CicloProductivo.SEMANA_DE_POSTURA)
    response = _register_eggs(
        client, auth_headers, lot["id"], 0, broken_eggs=0
    )
    assert response.status_code == 422


def test_register_production_with_only_broken_returns_201(client, auth_headers):
    """Solo huevos no aptos debe ser un registro válido.

    Escenario:
        - egg_count=0 y broken_eggs=5.
        - La validación debe aceptarlo y devolver HTTP 201.
    """
    lot = _create_lot(client, auth_headers)
    _advance_to(client, auth_headers, lot["id"], CicloProductivo.SEMANA_DE_POSTURA)
    response = _register_eggs(
        client, auth_headers, lot["id"], 0, broken_eggs=5
    )
    assert response.status_code == 201
    assert response.json()["broken_eggs"] == 5


def test_register_production_future_date_returns_400(client, auth_headers):
    """Una fecha de recolección futura debe ser rechazada.

    Escenario:
        - Se envía collection_date = 9999-01-01.
        - El servicio debe devolver HTTP 400.
    """
    lot = _create_lot(client, auth_headers)
    _advance_to(client, auth_headers, lot["id"], CicloProductivo.SEMANA_DE_POSTURA)
    response = _register_eggs(
        client, auth_headers, lot["id"], 100, collection_date="9999-01-01"
    )
    assert response.status_code == 400
    assert "futura" in response.json()["detail"]


def test_register_production_old_date_returns_400(client, auth_headers):
    """Una fecha anterior al día previo debe ser rechazada.

    Escenario:
        - Se envía collection_date = 2000-01-01.
        - El servicio debe devolver HTTP 400.
    """
    lot = _create_lot(client, auth_headers)
    _advance_to(client, auth_headers, lot["id"], CicloProductivo.SEMANA_DE_POSTURA)
    response = _register_eggs(
        client, auth_headers, lot["id"], 100, collection_date="2000-01-01"
    )
    assert response.status_code == 400
    assert "anterior" in response.json()["detail"]


def test_register_production_future_time_returns_400(client, auth_headers):
    """Una hora futura (con fecha de hoy) debe ser rechazada.

    Escenario:
        - Se envía collection_date = hoy y una hora posterior a la actual.
        - El servicio debe devolver HTTP 400.
    """
    now = datetime.now()
    future = now + timedelta(minutes=5)
    if future.date() != now.date():
        pytest.skip("Demasiado cerca de la medianoche para probar hora futura")
    future_time = future.time().strftime("%H:%M:%S")

    lot = _create_lot(client, auth_headers)
    _advance_to(client, auth_headers, lot["id"], CicloProductivo.SEMANA_DE_POSTURA)
    response = _register_eggs(
        client,
        auth_headers,
        lot["id"],
        100,
        collection_time=future_time,
    )
    assert response.status_code == 400
    assert "hora" in response.json()["detail"]


def test_multiple_records_same_day_returns_201(client, auth_headers):
    """Varios registros el mismo día en horas distintas deben guardarse.

    Escenario:
        - Se registran huevos a las 06:00 y a las 07:00 de ayer.
        - Ambos registros deben existir y sumar 300.
    """
    lot = _create_lot(client, auth_headers)
    _advance_to(client, auth_headers, lot["id"], CicloProductivo.SEMANA_DE_POSTURA)
    _register_eggs(
        client,
        auth_headers,
        lot["id"],
        100,
        collection_date=_yesterday_iso(),
        collection_time="06:00:00",
    )
    _register_eggs(
        client,
        auth_headers,
        lot["id"],
        200,
        collection_date=_yesterday_iso(),
        collection_time="07:00:00",
    )

    response = client.get(
        f"/api/v1/lots/{lot['id']}/production/total", headers=auth_headers
    )
    assert response.json()["total_eggs"] == 300


def test_duplicate_datetime_returns_409(client, auth_headers):
    """Un registro con la misma fecha y hora debe devolver HTTP 409.

    Escenario:
        - Se registran 100 huevos ayer a las 06:00.
        - Se intenta registrar 50 huevos a la misma fecha y hora.
        - La API debe responder 409 con el registro existente.
    """
    lot = _create_lot(client, auth_headers)
    _advance_to(client, auth_headers, lot["id"], CicloProductivo.SEMANA_DE_POSTURA)
    first = _register_eggs(
        client,
        auth_headers,
        lot["id"],
        100,
        collection_date=_yesterday_iso(),
        collection_time="06:00:00",
    )
    assert first.status_code == 201

    response = _register_eggs(
        client,
        auth_headers,
        lot["id"],
        50,
        collection_date=_yesterday_iso(),
        collection_time="06:00:00",
    )
    assert response.status_code == 409
    body = response.json()
    assert body["detail"]["existing"]["egg_count"] == 100


def test_merge_sums_quantities(client, auth_headers):
    """Con merge=true las cantidades deben sumarse al registro existente.

    Escenario:
        - Se registran 100 huevos ayer a las 06:00.
        - Se suma con merge=true otros 50 huevos y 5 no aptos.
        - El registro debe quedar con 150 aptos y 5 no aptos.
    """
    lot = _create_lot(client, auth_headers)
    _advance_to(client, auth_headers, lot["id"], CicloProductivo.SEMANA_DE_POSTURA)
    _register_eggs(
        client,
        auth_headers,
        lot["id"],
        100,
        collection_date=_yesterday_iso(),
        collection_time="06:00:00",
    )

    response = client.post(
        f"/api/v1/lots/{lot['id']}/production?merge=true",
        json={
            "egg_count": 50,
            "broken_eggs": 5,
            "collection_date": _yesterday_iso(),
            "collection_time": "06:00:00",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    body = response.json()
    assert body["egg_count"] == 150
    assert body["broken_eggs"] == 5

    total = client.get(
        f"/api/v1/lots/{lot['id']}/production/total", headers=auth_headers
    )
    assert total.json()["total_eggs"] == 150
