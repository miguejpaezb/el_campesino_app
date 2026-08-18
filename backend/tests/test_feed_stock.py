"""Pruebas de integración del inventario de insumos (alimentos).

Cubre el CRUD de tipos de alimento, el ingreso de stock (mismo/nuevo
precio), la suspensión, la eliminación con desvinculación del historial y
la integración con el registro de alimentación (descuento de stock).
"""

LOT_PAYLOAD = {
    "lot_code": "LOTE-FEEDSTOCK",
    "breed": "Ross 308",
    "initial_quantity": 1000,
}

FEED_PAYLOAD = {
    "name": "Concentrado",
    "stock_kg": 500,
    "cost_per_kilo": 2.5,
    "min_stock_kg": 50,
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


def _create_feed(client, auth_headers, **overrides):
    """Crea un tipo de alimento de prueba a través de la API.

    Args:
        client: Cliente de pruebas.
        auth_headers: Headers de autenticación.
        overrides: Campos adicionales del payload.

    Returns:
        Respuesta HTTP de la creación.
    """
    payload = {**FEED_PAYLOAD, **overrides}
    return client.post("/api/v1/feed-stock", json=payload, headers=auth_headers)


def test_create_feed_type_success(client, auth_headers):
    """Crear un tipo de alimento debe devolver HTTP 201.

    Escenario:
        - Se crea "Concentrado" con 500 kg y costo 2.5.
        - El stock inicial debe ser 500 y last_stock_date debe estar fijado.
    """
    response = _create_feed(client, auth_headers)
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Concentrado"
    assert body["stock_kg"] == 500
    assert body["cost_per_kilo"] == 2.5
    assert body["min_stock_kg"] == 50
    assert body["is_active"] is True
    assert body["is_low_stock"] is False
    assert body["last_stock_date"] is not None


def test_create_feed_type_duplicate_name_returns_400(client, auth_headers):
    """Un nombre de alimento duplicado debe ser rechazado.

    Escenario:
        - Se crea "Concentrado" y se intenta crear otro con el mismo nombre.
        - El servicio debe responder 400.
    """
    _create_feed(client, auth_headers)
    response = _create_feed(client, auth_headers)
    assert response.status_code == 400


def test_list_feed_types_with_search(client, auth_headers):
    """El listado debe soportar búsqueda por nombre.

    Escenario:
        - Se crean "Concentrado" y "Maíz".
        - La búsqueda "ma" debe devolver solo "Maíz".
    """
    _create_feed(client, auth_headers)
    _create_feed(client, auth_headers, name="Maíz")

    response = client.get(
        "/api/v1/feed-stock", params={"search": "ma"}, headers=auth_headers
    )
    assert response.status_code == 200
    names = [item["name"] for item in response.json()]
    assert names == ["Maíz"]


def test_update_feed_type_changes_name_and_min_stock(client, auth_headers):
    """Actualizar debe cambiar el nombre y el stock mínimo.

    Escenario:
        - Se actualiza "Concentrado" a "Concentrado Premium" y min 80.
        - La respuesta debe reflejar ambos cambios.
    """
    created = _create_feed(client, auth_headers).json()
    response = client.put(
        f"/api/v1/feed-stock/{created['id']}",
        json={"name": "Concentrado Premium", "min_stock_kg": 80},
        headers=auth_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Concentrado Premium"
    assert body["min_stock_kg"] == 80


def test_update_feed_type_duplicate_name_returns_400(client, auth_headers):
    """Renombrar a un nombre ya usado debe ser rechazado.

    Escenario:
        - Se crean "Concentrado" y "Maíz".
        - Renombrar "Maíz" a "Concentrado" debe responder 400.
    """
    _create_feed(client, auth_headers)
    maiz = _create_feed(client, auth_headers, name="Maíz").json()
    response = client.put(
        f"/api/v1/feed-stock/{maiz['id']}",
        json={"name": "Concentrado"},
        headers=auth_headers,
    )
    assert response.status_code == 400


def test_add_stock_same_price_keeps_cost(client, auth_headers):
    """Añadir stock con mismo precio conserva el costo por kilo.

    Escenario:
        - Se añaden 200 kg con price_option "same".
        - El stock debe subir a 700 y el costo seguir en 2.5.
    """
    created = _create_feed(client, auth_headers).json()
    response = client.post(
        f"/api/v1/feed-stock/{created['id']}/stock",
        json={"kilos_added": 200, "price_option": "same"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["stock_kg"] == 700
    assert body["cost_per_kilo"] == 2.5


def test_add_stock_new_price_updates_cost(client, auth_headers):
    """Añadir stock con nuevo precio actualiza el costo por kilo.

    Escenario:
        - Se añaden 100 kg con price_option "new" y costo 3.0.
        - El stock debe subir a 600 y el costo a 3.0.
    """
    created = _create_feed(client, auth_headers).json()
    response = client.post(
        f"/api/v1/feed-stock/{created['id']}/stock",
        json={"kilos_added": 100, "price_option": "new", "cost_per_kilo": 3.0},
        headers=auth_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["stock_kg"] == 600
    assert body["cost_per_kilo"] == 3.0


def test_add_stock_new_price_without_cost_returns_400(client, auth_headers):
    """Añadir stock con precio nuevo sin costo debe responder 400.

    Escenario:
        - price_option "new" sin cost_per_kilo.
        - El servicio debe rechazar la solicitud.
    """
    created = _create_feed(client, auth_headers).json()
    response = client.post(
        f"/api/v1/feed-stock/{created['id']}/stock",
        json={"kilos_added": 100, "price_option": "new"},
        headers=auth_headers,
    )
    assert response.status_code == 400


def test_toggle_suspend_feed_type(client, auth_headers):
    """Suspender y reactivar debe alternar el estado activo.

    Escenario:
        - Tras suspender, is_active debe ser False.
        - Tras suspender de nuevo, is_active debe volver a True.
    """
    created = _create_feed(client, auth_headers).json()
    response = client.post(
        f"/api/v1/feed-stock/{created['id']}/suspend", headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["is_active"] is False

    response = client.post(
        f"/api/v1/feed-stock/{created['id']}/suspend", headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["is_active"] is True


def test_delete_feed_type_unlinks_historical_records(client, auth_headers):
    """Eliminar un alimento conserva el nombre en los registros históricos.

    Escenario:
        - Se registra alimentación con feed_type_id.
        - Se elimina el alimento (204).
        - El registro histórico conserva feed_type y feed_type_id es None.
    """
    lot = _create_lot(client, auth_headers)
    feed = _create_feed(client, auth_headers).json()

    register = client.post(
        f"/api/v1/lots/{lot['id']}/feeding",
        json={"feed_type_id": feed["id"], "kilos": 100},
        headers=auth_headers,
    )
    assert register.status_code == 201
    record = register.json()

    response = client.delete(
        f"/api/v1/feed-stock/{feed['id']}", headers=auth_headers
    )
    assert response.status_code == 204

    listing = client.get(
        f"/api/v1/lots/{lot['id']}/feeding", headers=auth_headers
    ).json()
    assert len(listing) == 1
    assert listing[0]["id"] == record["id"]
    assert listing[0]["feed_type"] == "Concentrado"
    assert listing[0]["feed_type_id"] is None


def test_register_feeding_with_feed_type_deducts_stock(client, auth_headers):
    """Registrar alimentación con alimento del inventario descuenta stock.

    Escenario:
        - Alimento con 500 kg a $2.5.
        - Se registran 100 kg; el stock debe quedar en 400.
        - El registro debe guardar el costo del inventario (total_cost 250).
    """
    lot = _create_lot(client, auth_headers)
    feed = _create_feed(client, auth_headers).json()

    response = client.post(
        f"/api/v1/lots/{lot['id']}/feeding",
        json={"feed_type_id": feed["id"], "kilos": 100},
        headers=auth_headers,
    )
    assert response.status_code == 201
    body = response.json()
    assert body["feed_type"] == "Concentrado"
    assert body["feed_type_id"] == feed["id"]
    assert body["cost_per_kilo"] == 2.5
    assert body["total_cost"] == 250.0

    feed_after = client.get("/api/v1/feed-stock", headers=auth_headers).json()[0]
    assert feed_after["stock_kg"] == 400


def test_register_feeding_insufficient_stock_returns_400(client, auth_headers):
    """Registrar más kilos que el stock disponible debe responder 400.

    Escenario:
        - Alimento con 500 kg.
        - Se intenta registrar 600 kg.
        - El servicio debe rechazar con 400 y no crear el registro.
    """
    lot = _create_lot(client, auth_headers)
    feed = _create_feed(client, auth_headers).json()

    response = client.post(
        f"/api/v1/lots/{lot['id']}/feeding",
        json={"feed_type_id": feed["id"], "kilos": 600},
        headers=auth_headers,
    )
    assert response.status_code == 400
    assert "Stock insuficiente" in response.json()["detail"]

    listing = client.get(
        f"/api/v1/lots/{lot['id']}/feeding", headers=auth_headers
    ).json()
    assert listing == []


def test_register_feeding_suspended_feed_returns_400(client, auth_headers):
    """Registrar alimentación con alimento suspendido debe responder 400.

    Escenario:
        - Se suspende "Concentrado".
        - Registrar alimentación con ese alimento debe ser rechazado.
    """
    lot = _create_lot(client, auth_headers)
    feed = _create_feed(client, auth_headers).json()
    client.post(f"/api/v1/feed-stock/{feed['id']}/suspend", headers=auth_headers)

    response = client.post(
        f"/api/v1/lots/{lot['id']}/feeding",
        json={"feed_type_id": feed["id"], "kilos": 10},
        headers=auth_headers,
    )
    assert response.status_code == 400
    assert "suspendido" in response.json()["detail"]
