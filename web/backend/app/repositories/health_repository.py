"""Repositorio de acceso a datos para el módulo de sanidad.

Encapsula las consultas a las tablas `vaccinations`, `mortality` y
`diseases` mediante SQLAlchemy, abstrayendo a la capa de servicios de los
detalles de persistencia.
"""

from sqlalchemy.orm import Session

from app.models.disease import Disease
from app.models.mortality import Mortality
from app.models.vaccination import Vaccination


class HealthRepository:
    """Acceso a datos de las entidades de sanidad."""

    def __init__(self, db: Session):
        self.db = db

    # ============================ Vacunas ============================

    def get_vaccinations(self, lot_id: int) -> list[Vaccination]:
        """Lista las vacunas aplicadas a un lote.

        Args:
            lot_id: Identificador del lote.

        Returns:
            Lista con las vacunas encontradas.
        """
        return (
            self.db.query(Vaccination)
            .filter(Vaccination.lot_id == lot_id)
            .all()
        )

    def create_vaccination(self, record: Vaccination) -> Vaccination:
        """Persiste una nueva vacuna.

        Args:
            record: Instancia de `Vaccination` a crear.

        Returns:
            La vacuna recién creada.
        """
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    # ============================ Mortalidad ============================

    def get_mortalities(self, lot_id: int) -> list[Mortality]:
        """Lista los registros de mortalidad de un lote.

        Args:
            lot_id: Identificador del lote.

        Returns:
            Lista con los registros encontrados.
        """
        return (
            self.db.query(Mortality).filter(Mortality.lot_id == lot_id).all()
        )

    def create_mortality(self, record: Mortality) -> Mortality:
        """Persiste un nuevo registro de mortalidad.

        Args:
            record: Instancia de `Mortality` a crear.

        Returns:
            El registro recién creado.
        """
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    # ============================ Enfermedades ============================

    def get_diseases(self, lot_id: int) -> list[Disease]:
        """Lista las enfermedades de un lote.

        Args:
            lot_id: Identificador del lote.

        Returns:
            Lista con las enfermedades encontradas.
        """
        return self.db.query(Disease).filter(Disease.lot_id == lot_id).all()

    def get_disease(self, disease_id: int) -> Disease | None:
        """Busca una enfermedad por su identificador.

        Args:
            disease_id: Identificador de la enfermedad.

        Returns:
            La enfermedad encontrada o None si no existe.
        """
        return self.db.get(Disease, disease_id)

    def create_disease(self, record: Disease) -> Disease:
        """Persiste una nueva enfermedad.

        Args:
            record: Instancia de `Disease` a crear.

        Returns:
            La enfermedad recién creada.
        """
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def update_disease(self, record: Disease) -> Disease:
        """Persiste los cambios de una enfermedad existente.

        Args:
            record: Instancia de `Disease` con los cambios aplicados.

        Returns:
            La enfermedad actualizada.
        """
        self.db.commit()
        self.db.refresh(record)
        return record
