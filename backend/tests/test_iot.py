"""Pruebas de integración del módulo de monitoreo IoT.

Cubre el registro de lecturas de sensores, la detección de alertas según el
rango seguro y las consultas con filtros.
"""

LOT_PAYLOAD = {
    "lot_code": "LOTE-IOT",
    "breed": "Ross 308",
    "initial_quantity": 1000,
}


def _create_lot(client, auth_headers, **overrides):
    """Crea un lote de prueba y devuelve su cuerpo de respuesta.

    Args:
        client: Cliente de pruebas.
        auth_headers: Headers de autenticación.
        overrides: Campos a sobreescribir en el payload.

    Returns:
        Diccionario con el lote creado.
    """
    payload = {**LOT_PAYLOAD, **overrides}
    response = client.post("/api/v1/lots/", json=payload, headers=auth_headers)
    return response.json()


def _post_reading(client, auth_headers, sensor_type, value, **overrides):
    """Registra una lectura de sensor a través de la API.

    Args:
        client: Cliente de pruebas.
        auth_headers: Headers de autenticación.
        sensor_type: Tipo de sensor.
        value: Valor medido.
        overrides: Campos adicionales del payload.

    Returns:
        Respuesta HTTP del registro.
    """
    payload = {"sensor_id": "SENS-1", "sensor_type": sensor_type, "value": value}
    payload.update(overrides)
    return client.post("/api/v1/iot/readings", json=payload, headers=auth_headers)


def test_create_reading_success_returns_201(client, auth_headers):
    """Registrar una lectura válida debe devolver HTTP 201.

    Escenario:
        - Se registra una temperatura de 25 °C (rango seguro).
        - La respuesta debe incluir la unidad, sin alerta.
    """
    response = _post_reading(client, auth_headers, "temperature", 25.0)
    assert response.status_code == 201
    body = response.json()
    assert body["sensor_type"] == "temperature"
    assert body["value"] == 25.0
    assert body["unit"] == "°C"
    assert body["is_alert"] is False


def test_create_reading_generates_alert_out_of_range(client, auth_headers):
    """Valores fuera del rango seguro deben marcarse como alerta.

    Escenario:
        - Temperatura 35 °C (máximo 30) debe generar alerta.
        - Humedad 20% (mínimo 40) debe generar alerta.
        - Amoníaco 30 ppm (máximo 25) debe generar alerta.
    """
    temp = _post_reading(client, auth_headers, "temperature", 35.0).json()
    humidity = _post_reading(client, auth_headers, "humidity", 20.0).json()
    ammonia = _post_reading(client, auth_headers, "ammonia", 30.0).json()

    assert temp["is_alert"] is True
    assert humidity["is_alert"] is True
    assert ammonia["is_alert"] is True


def test_create_reading_within_range_no_alert(client, auth_headers):
    """Valores dentro del rango seguro no deben marcar alerta.

    Escenario:
        - Humedad 55% (rango 40-70) no debe generar alerta.
    """
    response = _post_reading(client, auth_headers, "humidity", 55.0)
    assert response.json()["is_alert"] is False


def test_create_reading_invalid_sensor_type_returns_422(client, auth_headers):
    """Un tipo de sensor no válido debe ser rechazado.

    Escenario:
        - Se envía sensor_type="co2" que no está en los permitidos.
        - FastAPI debe devolver HTTP 422.
    """
    response = _post_reading(client, auth_headers, "co2", 10.0)
    assert response.status_code == 422


def test_create_reading_nonexistent_lot_returns_404(client, auth_headers):
    """Una lectura con un lote inexistente debe devolver HTTP 404.

    Escenario:
        - Se envía lot_id=999 que no existe.
        - La API debe devolver 404.
    """
    response = _post_reading(
        client, auth_headers, "temperature", 25.0, lot_id=999
    )
    assert response.status_code == 404


def test_create_reading_with_lot(client, auth_headers):
    """Una lectura asociada a un lote válido debe registrarse.

    Escenario:
        - Se crea un lote y se registra una lectura con su lot_id.
        - La respuesta debe incluir el lot_id.
    """
    lot = _create_lot(client, auth_headers)
    response = _post_reading(
        client, auth_headers, "temperature", 24.0, lot_id=lot["id"]
    )
    assert response.status_code == 201
    assert response.json()["lot_id"] == lot["id"]


def test_list_readings_filtered(client, auth_headers):
    """El listado debe aplicar los filtros por tipo y lote.

    Escenario:
        - Se registran lecturas de temperatura y humedad para dos lotes.
        - Filtrando por sensor_type=temperature y lot_id del primer lote,
          solo debe aparecer esa lectura.
    """
    lot_a = _create_lot(client, auth_headers)
    lot_b = _create_lot(client, auth_headers, lot_code="LOTE-IOT-B")

    _post_reading(client, auth_headers, "temperature", 25.0, lot_id=lot_a["id"])
    _post_reading(client, auth_headers, "humidity", 55.0, lot_id=lot_a["id"])
    _post_reading(client, auth_headers, "temperature", 26.0, lot_id=lot_b["id"])

    response = client.get(
        f"/api/v1/iot/readings?lot_id={lot_a['id']}&sensor_type=temperature",
        headers=auth_headers,
    )
    assert response.status_code == 200
    bodies = response.json()
    assert len(bodies) == 1
    assert bodies[0]["value"] == 25.0


def test_list_alerts_returns_only_alerts(client, auth_headers):
    """El listado de alertas solo debe incluir lecturas con alerta.

    Escenario:
        - Se registra una temperatura normal y una fuera de rango.
        - El endpoint /alerts solo debe devolver la lectura con alerta.
    """
    _post_reading(client, auth_headers, "temperature", 25.0)
    _post_reading(client, auth_headers, "temperature", 40.0)

    response = client.get("/api/v1/iot/alerts", headers=auth_headers)
    assert response.status_code == 200
    bodies = response.json()
    assert len(bodies) == 1
    assert bodies[0]["value"] == 40.0
    assert bodies[0]["is_alert"] is True
