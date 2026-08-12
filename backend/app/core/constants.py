"""Constantes de negocio del sistema avícola.

Migradas desde el ejercicio en clase (`docs/ejercicio_en_clase/domain/lote.py`)
para centralizar los valores que definen el ciclo productivo de un lote.

Attributes:
    CicloProductivo: Valores fijos del ciclo de vida productivo de las aves.
"""


class CicloProductivo:
    """Constantes del ciclo productivo de un lote de gallinas.

    Attributes:
        SEMANA_COMPRA: Semana de vida en la que se adquieren las aves.
        SEMANA_DE_POSTURA: Semana en la que el lote comienza a poner huevos.
        SEMANA_DE_EVALUACION: Semana en la que se evalúa el rendimiento del lote.
        EXTENSION_SEMANAS: Semanas adicionales si el lote aprueba la evaluación.
        PORCENTAJE_MINIMO_POSTURA: Porcentaje mínimo de postura para aprobar.
    """

    SEMANA_COMPRA = 16
    SEMANA_DE_POSTURA = 28
    SEMANA_DE_EVALUACION = 90
    EXTENSION_SEMANAS = 30
    PORCENTAJE_MINIMO_POSTURA = 80


class SensorThresholds:
    """Rangos seguros de las variables ambientales para las aves.

    Attributes:
        TEMPERATURE_MIN: Temperatura mínima segura en grados Celsius.
        TEMPERATURE_MAX: Temperatura máxima segura en grados Celsius.
        HUMIDITY_MIN: Humedad relativa mínima segura en porcentaje.
        HUMIDITY_MAX: Humedad relativa máxima segura en porcentaje.
        AMMONIA_MAX: Concentración máxima segura de amoníaco en ppm.
    """

    TEMPERATURE_MIN = 18.0
    TEMPERATURE_MAX = 30.0
    HUMIDITY_MIN = 40.0
    HUMIDITY_MAX = 70.0
    AMMONIA_MAX = 25.0


class SensorUnits:
    """Unidades de medida por tipo de sensor.

    Attributes:
        TEMPERATURE: Unidad de temperatura (°C).
        HUMIDITY: Unidad de humedad (%).
        AMMONIA: Unidad de amoníaco (ppm).
    """

    TEMPERATURE = "°C"
    HUMIDITY = "%"
    AMMONIA = "ppm"
