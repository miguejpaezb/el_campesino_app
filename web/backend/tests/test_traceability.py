"""Pruebas de integración del módulo de trazabilidad.

Cubre la generación de registros de auditoría con hash encadenado, la
verificación de integridad y la detección de alteraciones en la cadena.
"""

from app.models.audit_log import AuditLog

LOT_PAYLOAD = {
    "lot_code": "LOTE-TRACE",
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


def _get_history(client, auth_headers, entity_type, entity_id):
    """Consulta el historial de trazabilidad de una entidad.

    Args:
        client: Cliente de pruebas.
        auth_headers: Headers de autenticación.
        entity_type: Tipo de entidad.
        entity_id: Identificador de la entidad.

    Returns:
        Lista de registros de auditoría.
    """
    response = client.get(
        f"/api/v1/traceability/{entity_type}/{entity_id}", headers=auth_headers
    )
    assert response.status_code == 200
    return response.json()


def test_create_lot_generates_create_log(client, auth_headers):
    """Crear un lote debe generar un registro de auditoría CREATE.

    Escenario:
        - Se crea un lote.
        - El historial debe tener un registro con acción CREATE y hashes.
    """
    lot = _create_lot(client, auth_headers)

    history = _get_history(client, auth_headers, "BirdLot", lot["id"])
    assert len(history) == 1
    entry = history[0]
    assert entry["action"] == "CREATE"
    assert entry["entity_type"] == "BirdLot"
    assert entry["entity_id"] == lot["id"]
    assert entry["previous_hash"] == "0" * 64
    assert entry["current_hash"]
    assert entry["current_hash"] != entry["previous_hash"]


def test_history_chains_hashes(client, auth_headers):
    """El historial debe encadenar los hash entre registros.

    Escenario:
        - Se crea un lote y se avanza una semana.
        - El segundo registro debe tener previous_hash igual al current_hash
          del primer registro.
    """
    lot = _create_lot(client, auth_headers)
    client.post(
        f"/api/v1/lots/{lot['id']}/advance-week", headers=auth_headers
    )

    history = _get_history(client, auth_headers, "BirdLot", lot["id"])
    assert len(history) == 2
    assert history[1]["previous_hash"] == history[0]["current_hash"]


def test_verify_chain_is_valid(client, auth_headers):
    """Verificar una cadena sin alteraciones debe ser válida.

    Escenario:
        - Se crea un lote y se avanza una semana.
        - La verificación debe devolver valid=True con 2 registros.
    """
    lot = _create_lot(client, auth_headers)
    client.post(
        f"/api/v1/lots/{lot['id']}/advance-week", headers=auth_headers
    )

    response = client.post(
        f"/api/v1/traceability/verify/BirdLot/{lot['id']}", headers=auth_headers
    )
    assert response.status_code == 200
    body = response.json()
    assert body["valid"] is True
    assert body["entries"] == 2
    assert "íntegra" in body["detail"]


def test_verify_chain_detects_tampering(client, auth_headers, db_session):
    """Verificar una cadena alterada debe detectar la manipulación.

    Escenario:
        - Se crea un lote (genera un registro de auditoría).
        - Se modifica el campo changes del registro directamente en la BD.
        - La verificación debe devolver valid=False.
    """
    lot = _create_lot(client, auth_headers)

    log = (
        db_session.query(AuditLog)
        .filter(AuditLog.entity_type == "BirdLot", AuditLog.entity_id == lot["id"])
        .first()
    )
    log.changes = '{"tampered": true}'
    db_session.commit()

    response = client.post(
        f"/api/v1/traceability/verify/BirdLot/{lot['id']}", headers=auth_headers
    )
    assert response.status_code == 200
    body = response.json()
    assert body["valid"] is False
    assert "alteración" in body["detail"]


def test_verify_chain_for_unknown_entity_is_valid(client, auth_headers):
    """Verificar una entidad sin registros debe ser válida (cadena vacía).

    Escenario:
        - Se verifica una entidad que nunca fue auditada.
        - Debe devolver valid=True con entries=0.
    """
    response = client.post(
        "/api/v1/traceability/verify/BirdLot/999", headers=auth_headers
    )
    assert response.status_code == 200
    body = response.json()
    assert body["valid"] is True
    assert body["entries"] == 0


def test_traceability_requires_auth(client):
    """Consultar trazabilidad sin token debe devolver HTTP 401.

    Escenario:
        - No se envía el header Authorization.
        - La API debe rechazar la consulta con 401.
    """
    response = client.get("/api/v1/traceability/BirdLot/1")
    assert response.status_code == 401
