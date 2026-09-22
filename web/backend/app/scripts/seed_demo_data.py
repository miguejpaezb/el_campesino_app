"""Script de datos de demostración para el lote lote001.

Simula un lote con historial completo para la evidencia GA7-220501096-AA3-EV02:
- Lote creado hace exactamente 35 semanas (2025-12-15).
- Inicia con 100 aves y llega a hoy (2026-08-17) con 97 (3 muertes).
- Semana actual 51 (SEMANA_COMPRA=16 + 35 semanas).
- Vacunas, alimentación diaria, mortalidad y enfermedades.
- Producción semanal (semanas 28-50) y registros diarios en los últimos 7
  días para que el gráfico del dashboard se vea completo.

Ejecutar desde la carpeta `backend`:

    python -m app.scripts.seed_demo_data
"""

from datetime import date, datetime, time, timedelta

import app.models  # noqa: F401  (registra los modelos en el metadata de Base)
from app.core.database import Base, SessionLocal, engine
from app.models.bird_lot import BirdLot
from app.models.disease import Disease
from app.models.egg_production import EggProduction
from app.models.feeding import FeedingRecord
from app.models.mortality import Mortality
from app.models.vaccination import Vaccination
from app.services.traceability_service import TraceabilityService

LOT_CODE = "lote001"
TODAY = date(2026, 8, 17)
ENTRY_DATE = TODAY - timedelta(weeks=35)  # 2025-12-15
SEMANA_COMPRA = 16
SEMANA_POSTURA = 28
WEEKS_OF_HISTORY = 35
INITIAL_BIRDS = 100
CURRENT_BIRDS = 97


def week_start(week: int) -> date:
    """Devuelve la fecha de inicio (lunes) de una semana del ciclo.

    Args:
        week: Semana del ciclo productivo (>= SEMANA_COMPRA).

    Returns:
        La fecha correspondiente al lunes de esa semana.
    """
    return ENTRY_DATE + timedelta(weeks=week - SEMANA_COMPRA)


def birds_on(day: date, deaths: list[tuple[int, int]]) -> int:
    """Cantidad de aves vivas en una fecha según las muertes acumuladas.

    Args:
        day: Fecha a consultar.
        deaths: Lista de tuplas (semana, cantidad_muerta).

    Returns:
        Número de aves vivas en esa fecha.
    """
    birds = INITIAL_BIRDS
    for week, quantity in deaths:
        if day >= week_start(week):
            birds -= quantity
    return birds


def main() -> None:
    """Ejecuta la generación de datos de demostración del lote."""
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        lot = db.query(BirdLot).filter(BirdLot.lot_code == LOT_CODE).first()
        if lot is None:
            raise SystemExit(f"No existe un lote con código '{LOT_CODE}'.")

        # --- Limpiar registros previos del lote y su auditoría ---
        db.query(EggProduction).filter(EggProduction.lot_id == lot.id).delete()
        db.query(FeedingRecord).filter(FeedingRecord.lot_id == lot.id).delete()
        db.query(Vaccination).filter(Vaccination.lot_id == lot.id).delete()
        db.query(Mortality).filter(Mortality.lot_id == lot.id).delete()
        db.query(Disease).filter(Disease.lot_id == lot.id).delete()
        for entity in [
            "BirdLot",
            "EggProduction",
            "FeedingRecord",
            "Vaccination",
            "Mortality",
            "Disease",
        ]:
            from app.models.audit_log import AuditLog

            db.query(AuditLog).filter(AuditLog.entity_type == entity).delete()

        # --- Actualizar el lote para el escenario simulado ---
        lot.entry_date = datetime.combine(ENTRY_DATE, time.min)
        lot.current_week = SEMANA_COMPRA + WEEKS_OF_HISTORY  # 51
        lot.current_quantity = CURRENT_BIRDS
        lot.observations = (
            "Lote simulado para demostración: creado el "
            f"{ENTRY_DATE.isoformat()} con {INITIAL_BIRDS} aves."
        )
        db.flush()

        trace = TraceabilityService(db)
        trace.log_event(
            "BirdLot",
            lot.id,
            "CREATE",
            1,
            changes={
                "lot_code": lot.lot_code,
                "breed": lot.breed,
                "initial_quantity": INITIAL_BIRDS,
                "entry_date": ENTRY_DATE.isoformat(),
            },
        )

        # --- Mortalidad: 3 aves en total (100 -> 97) ---
        deaths = [
            (18, 1),  # 1 ave en la semana 18
            (32, 1),  # 1 ave en la semana 32
            (45, 1),  # 1 ave en la semana 45
        ]
        mortality_data = [
            (18, "Selección por bajo peso", "Ave de menor peso del lote"),
            (32, "Afección respiratoria", "Tratamiento aplicado, sin éxito"),
            (45, "Síndrome de postura", "Baja productiva"),
        ]
        for week, cause, observations in mortality_data:
            record = Mortality(
                lot_id=lot.id,
                week=week,
                event_date=week_start(week),
                quantity=1,
                cause=cause,
                observations=observations,
            )
            db.add(record)
            db.flush()
            trace.log_event(
                "Mortality",
                record.id,
                "CREATE",
                1,
                changes={"week": week, "quantity": 1, "cause": cause},
            )

        # --- Vacunas (esquema típico de ponedoras) ---
        vaccine_data = [
            (16, "Newcastle (LaSota)", "2 ml por ave", "NC-2025-001"),
            (18, "Gumboro", "1 dosis por ave", "GB-2025-002"),
            (20, "Refuerzo Newcastle (LaSota)", "2 ml por ave", "NC-2025-011"),
            (24, "Viruela Aviar", "1 dosis por ave", "VA-2026-001"),
            (30, "Refuerzo Newcastle (LaSota)", "2 ml por ave", "NC-2026-002"),
            (40, "Refuerzo Newcastle (LaSota)", "2 ml por ave", "NC-2026-003"),
        ]
        for week, name, dosage, batch in vaccine_data:
            record = Vaccination(
                lot_id=lot.id,
                week=week,
                application_date=week_start(week),
                vaccine_name=name,
                dosage=dosage,
                batch_number=batch,
            )
            db.add(record)
            db.flush()
            trace.log_event(
                "Vaccination",
                record.id,
                "CREATE",
                1,
                changes={"week": week, "vaccine_name": name, "dosage": dosage},
            )

        # --- Alimentación diaria desde la entrada (1 registro/día) ---
        feed_per_bird_kg = 0.115
        feed_type = "Concentrado ponedora"
        feed_cost_per_kilo = 1850.0
        for day_offset in range((TODAY - ENTRY_DATE).days + 1):
            day = ENTRY_DATE + timedelta(days=day_offset)
            week = SEMANA_COMPRA + day_offset // 7
            birds = birds_on(day, deaths)
            kilos = round(birds * feed_per_bird_kg, 2)
            record = FeedingRecord(
                lot_id=lot.id,
                week=week,
                feed_date=day,
                feed_type=feed_type,
                kilos=kilos,
                cost_per_kilo=feed_cost_per_kilo,
                observations="Ración diaria",
            )
            db.add(record)
        db.flush()

        # --- Producción semanal: semanas 28 a 50 (una por semana) ---
        weekly_rates = [
            0.70, 0.75, 0.80, 0.84, 0.87, 0.89, 0.90, 0.91, 0.91, 0.91,
            0.90, 0.90, 0.89, 0.88, 0.87, 0.86, 0.85, 0.84, 0.83, 0.82,
            0.81, 0.80, 0.79,
        ]
        weekly_count = 0
        for week in range(SEMANA_POSTURA, SEMANA_POSTURA + len(weekly_rates)):
            rate = weekly_rates[week - SEMANA_POSTURA]
            egg_count = round(INITIAL_BIRDS * rate * 7)
            record = EggProduction(
                lot_id=lot.id,
                week=week,
                collection_date=week_start(week),
                collection_time=time(12, 0),
                egg_count=egg_count,
                avg_weight_grams=62.0,
                broken_eggs=2,
                observations=f"Registro semanal de la semana {week}",
            )
            db.add(record)
            db.flush()
            trace.log_event(
                "EggProduction",
                record.id,
                "CREATE",
                1,
                changes={
                    "week": week,
                    "collection_date": record.collection_date.isoformat(),
                    "egg_count": egg_count,
                },
            )
            weekly_count += 1

        # --- Producción diaria: últimos 7 días (para el gráfico) ---
        daily_count = 0
        for day_offset in range(6, -1, -1):
            day = TODAY - timedelta(days=day_offset)
            week = SEMANA_COMPRA + (day - ENTRY_DATE).days // 7
            birds = birds_on(day, deaths)
            egg_count = round(birds * 0.78)
            record = EggProduction(
                lot_id=lot.id,
                week=week,
                collection_date=day,
                collection_time=time(12, 0),
                egg_count=egg_count,
                avg_weight_grams=61.0,
                broken_eggs=1,
                observations="Recolección diaria",
            )
            db.add(record)
            db.flush()
            trace.log_event(
                "EggProduction",
                record.id,
                "CREATE",
                1,
                changes={
                    "week": week,
                    "collection_date": record.collection_date.isoformat(),
                    "egg_count": egg_count,
                },
            )
            daily_count += 1

        # --- Enfermedad (1 caso resuelto) ---
        disease = Disease(
            lot_id=lot.id,
            diagnosis_date=week_start(30),
            disease_name="Bronquitis leve",
            affected_quantity=2,
            symptoms="Tos leve y decaimiento",
            treatment="Antibiótico en el agua por 5 días",
            treatment_start_date=week_start(30),
            treatment_end_date=week_start(30) + timedelta(days=5),
            is_resolved=True,
        )
        db.add(disease)
        db.flush()
        trace.log_event(
            "Disease",
            disease.id,
            "CREATE",
            1,
            changes={"disease_name": disease.disease_name},
        )

        # --- Registro de trazabilidad final del lote ---
        trace.log_event(
            "BirdLot",
            lot.id,
            "UPDATE",
            1,
            changes={
                "current_week": lot.current_week,
                "current_quantity": lot.current_quantity,
            },
        )

        db.commit()

    print("Datos de demostración generados correctamente.")
    print(f"  Lote        : {LOT_CODE}")
    print(
        f"  Entrada     : {ENTRY_DATE.isoformat()} "
        f"({WEEKS_OF_HISTORY} semanas antes de {TODAY.isoformat()})"
    )
    print(f"  Semana      : {SEMANA_COMPRA + WEEKS_OF_HISTORY}")
    print(f"  Aves        : {INITIAL_BIRDS} iniciales -> {CURRENT_BIRDS} actuales")
    print(f"  Producción  : {weekly_count} registros semanales + {daily_count} diarios")
    print(f"  Vacunas     : {len(vaccine_data)}")
    print(f"  Mortalidad  : {len(mortality_data)} eventos (3 aves)")


if __name__ == "__main__":
    main()
