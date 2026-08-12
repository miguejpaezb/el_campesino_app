"""Pruebas de integración del módulo de sanidad.

Cubre vacunas, mortalidad (incluida la desactivación del lote al quedar sin
aves) y enfermedades.
"""

from app.core.constants import CicloProductivo

LOT_PAYLOAD = {
    "lot_code": "LOTE-HEALTH",
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


def _get_lot(client, auth_headers, lot_id):
    """Consulta un lote por su id.

    Args:
        client: Cliente de pruebas.
        auth_headers: Headers de autenticación.
        lot_id: Identificador del lote.

    Returns:
        Cuerpo de la respuesta con el lote.
    """
    return client.get(f"/api/v1/lots/{lot_id}", headers=auth_headers).json()


# ============================ Vacunas ============================


def test_register_vaccination_success_returns_201(client, auth_headers):
    """Registrar una vacuna en un lote activo debe devolver HTTP 201.

    Escenario:
        - Se crea un lote y se registra una vacuna.
        - La semana del registro debe ser la semana actual del lote.
    """
    lot = _create_lot(client, auth_headers)

    response = client.post(
        f"/api/v1/lots/{lot['id']}/vaccinations",
        json={"vaccine_name": "Newcastle", "dosage": "2 ml"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    body = response.json()
    assert body["lot_id"] == lot["id"]
    assert body["vaccine_name"] == "Newcastle"
    assert body["dosage"] == "2 ml"
    assert body["week"] == CicloProductivo.SEMANA_COMPRA


def test_register_vaccination_inactive_lot_returns_400(client, auth_headers):
    """Registrar vacuna en un lote inactivo debe devolver HTTP 400.

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
    response = client.post(
        f"/api/v1/lots/{lot['id']}/vaccinations",
        json={"vaccine_name": "Newcastle", "dosage": "2 ml"},
        headers=auth_headers,
    )
    assert response.status_code == 400


def test_list_vaccinations_returns_records(client, auth_headers):
    """Listar las vacunas debe devolver los registros del lote.

    Escenario:
        - Se registran dos vacunas.
        - La lista debe contener ambos registros.
    """
    lot = _create_lot(client, auth_headers)
    client.post(
        f"/api/v1/lots/{lot['id']}/vaccinations",
        json={"vaccine_name": "Newcastle", "dosage": "2 ml"},
        headers=auth_headers,
    )
    client.post(
        f"/api/v1/lots/{lot['id']}/vaccinations",
        json={"vaccine_name": "Gumboro", "dosage": "1 ml"},
        headers=auth_headers,
    )

    response = client.get(
        f"/api/v1/lots/{lot['id']}/vaccinations", headers=auth_headers
    )
    assert response.status_code == 200
    assert len(response.json()) == 2


# ============================ Mortalidad ============================


def test_register_mortality_updates_current_quantity(client, auth_headers):
    """Registrar mortalidad debe restar aves al lote.

    Escenario:
        - Lote con 1000 aves y se registran 40 muertes.
        - El lote debe quedar con 960 aves y el registro con la causa.
    """
    lot = _create_lot(client, auth_headers)

    response = client.post(
        f"/api/v1/lots/{lot['id']}/mortality",
        json={"quantity": 40, "cause": "Bronquitis"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    assert response.json()["cause"] == "Bronquitis"

    detail = _get_lot(client, auth_headers, lot["id"])
    assert detail["current_quantity"] == 960
    assert detail["is_active"] is True


def test_register_mortality_exceeding_quantity_returns_400(client, auth_headers):
    """Mortalidad mayor a las aves actuales debe devolver HTTP 400.

    Escenario:
        - Lote con 1000 aves y se registran 1500 muertes.
        - El servicio debe rechazar el registro con 400.
    """
    lot = _create_lot(client, auth_headers)

    response = client.post(
        f"/api/v1/lots/{lot['id']}/mortality",
        json={"quantity": 1500, "cause": "Accidente"},
        headers=auth_headers,
    )
    assert response.status_code == 400


def test_register_mortality_all_birds_discards_lot(client, auth_headers):
    """Si mueren todas las aves, el lote debe desactivarse.

    Escenario:
        - Lote con 1000 aves y se registran 1000 muertes.
        - El lote debe quedar inactivo con razón "Muerte de todas las gallinas".
    """
    lot = _create_lot(client, auth_headers)

    response = client.post(
        f"/api/v1/lots/{lot['id']}/mortality",
        json={"quantity": 1000, "cause": "Epidemia"},
        headers=auth_headers,
    )
    assert response.status_code == 201

    detail = _get_lot(client, auth_headers, lot["id"])
    assert detail["current_quantity"] == 0
    assert detail["is_active"] is False
    assert detail["discard_reason"] == "Muerte de todas las gallinas"


def test_mortality_stats_returns_percentages(client, auth_headers):
    """Los stats de mortalidad deben calcular ambos porcentajes.

    Escenario:
        - Lote con 1000 aves y se registran 100 muertes.
        - Mortalidad 10% y supervivencia 90%.
    """
    lot = _create_lot(client, auth_headers)
    client.post(
        f"/api/v1/lots/{lot['id']}/mortality",
        json={"quantity": 100, "cause": "Colibacilosis"},
        headers=auth_headers,
    )

    response = client.get(
        f"/api/v1/lots/{lot['id']}/mortality/stats", headers=auth_headers
    )
    assert response.status_code == 200
    body = response.json()
    assert body["mortality_percentage"] == 10.0
    assert body["survival_percentage"] == 90.0


def test_summary_includes_mortality(client, auth_headers):
    """El resumen debe reflejar la mortalidad registrada.

    Escenario:
        - Lote con 1000 aves y se registran 100 muertes.
        - El resumen debe mostrar total_mortality=100 y mortalidad 10%.
    """
    lot = _create_lot(client, auth_headers)
    client.post(
        f"/api/v1/lots/{lot['id']}/mortality",
        json={"quantity": 100, "cause": "Colibacilosis"},
        headers=auth_headers,
    )

    response = client.get(
        f"/api/v1/lots/{lot['id']}/summary", headers=auth_headers
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total_mortality"] == 100
    assert body["mortality_percentage"] == 10.0
    assert body["survival_percentage"] == 90.0


# ============================ Enfermedades ============================


def test_register_disease_success_returns_201(client, auth_headers):
    """Registrar una enfermedad debe devolver HTTP 201.

    Escenario:
        - Se registra una enfermedad con 50 aves afectadas.
        - La respuesta debe contener los datos de la enfermedad.
    """
    lot = _create_lot(client, auth_headers)

    response = client.post(
        f"/api/v1/lots/{lot['id']}/diseases",
        json={"disease_name": "Newcastle", "affected_quantity": 50},
        headers=auth_headers,
    )
    assert response.status_code == 201
    body = response.json()
    assert body["lot_id"] == lot["id"]
    assert body["disease_name"] == "Newcastle"
    assert body["affected_quantity"] == 50
    assert body["is_resolved"] is False


def test_list_diseases_returns_records(client, auth_headers):
    """Listar las enfermedades debe devolver los registros del lote.

    Escenario:
        - Se registran dos enfermedades.
        - La lista debe contener ambos registros.
    """
    lot = _create_lot(client, auth_headers)
    client.post(
        f"/api/v1/lots/{lot['id']}/diseases",
        json={"disease_name": "Newcastle", "affected_quantity": 10},
        headers=auth_headers,
    )
    client.post(
        f"/api/v1/lots/{lot['id']}/diseases",
        json={"disease_name": "Gumboro", "affected_quantity": 5},
        headers=auth_headers,
    )

    response = client.get(
        f"/api/v1/lots/{lot['id']}/diseases", headers=auth_headers
    )
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_update_disease_treatment(client, auth_headers):
    """Actualizar el tratamiento debe aplicar los cambios.

    Escenario:
        - Se registra una enfermedad y se actualiza su tratamiento.
        - La respuesta debe reflejar el nuevo tratamiento.
    """
    lot = _create_lot(client, auth_headers)
    disease = client.post(
        f"/api/v1/lots/{lot['id']}/diseases",
        json={"disease_name": "Newcastle", "affected_quantity": 10},
        headers=auth_headers,
    ).json()

    response = client.put(
        f"/api/v1/lots/{lot['id']}/diseases/{disease['id']}",
        json={"treatment": "Antibiótico en agua"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["treatment"] == "Antibiótico en agua"


def test_resolve_disease_sets_resolved(client, auth_headers):
    """Marcar como resuelta debe cambiar el estado de la enfermedad.

    Escenario:
        - Se registra una enfermedad y se marca como resuelta.
        - La respuesta debe tener is_resolved=True.
    """
    lot = _create_lot(client, auth_headers)
    disease = client.post(
        f"/api/v1/lots/{lot['id']}/diseases",
        json={"disease_name": "Newcastle", "affected_quantity": 10},
        headers=auth_headers,
    ).json()

    response = client.post(
        f"/api/v1/lots/{lot['id']}/diseases/{disease['id']}/resolve",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["is_resolved"] is True


def test_update_disease_of_other_lot_returns_404(client, auth_headers):
    """Actualizar una enfermedad de otro lote debe devolver HTTP 404.

    Escenario:
        - Se crean dos lotes y una enfermedad en el primero.
        - Se intenta actualizarla usando el id del segundo lote.
        - El servicio debe devolver 404.
    """
    lot_a = _create_lot(client, auth_headers)
    lot_b = _create_lot(
        client, auth_headers, lot_code="LOTE-HEALTH-B"
    )
    disease = client.post(
        f"/api/v1/lots/{lot_a['id']}/diseases",
        json={"disease_name": "Newcastle", "affected_quantity": 10},
        headers=auth_headers,
    ).json()

    response = client.put(
        f"/api/v1/lots/{lot_b['id']}/diseases/{disease['id']}",
        json={"treatment": "Nuevo tratamiento"},
        headers=auth_headers,
    )
    assert response.status_code == 404
