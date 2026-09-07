# Reglas de negocio

Contenido:

1. [Reglas heredadas del ejercicio en clase](#reglas-heredadas-del-ejercicio-en-clase)
2. [Reglas de IoT (rangos seguros para alertas)](#reglas-de-iot-rangos-seguros-para-alertas)
3. [Nota sobre bases de datos existentes](#nota-sobre-bases-de-datos-existentes)

---

## Reglas heredadas del ejercicio en clase

- Un lote inicia en la **semana 16** (semana de compra) y arranca la postura en
  la **semana 28**.
- **Producción**: solo se registra si el lote está activo y en etapa de postura
  (semana ≥ 28). Las cantidades (aptos y no aptos) deben ser ≥ 0 y al menos una
  mayor a 0; la fecha de recolección solo puede ser hoy o el día anterior, y la
  hora no puede ser futura. Varios registros del mismo día se permiten en horas
  distintas; si coinciden fecha y hora, las cantidades se suman al registro
  existente (merge). El promedio semanal y el porcentaje de postura se calculan
  agrupando por fecha de recolección distinta (**días productivos**), por lo
  que varios registros del mismo día cuentan como un solo día productivo y no
  distorsionan las métricas.
- **Alimentación**: solo se registra si el lote está activo. Si el registro usa
  `feed_type_id` (inventario), el alimento debe existir, estar activo (no
  suspendido) y tener **stock suficiente**; el stock se **descuenta** al
  registrar y el costo se toma del precio del inventario (el valor monetario
  del registro es `kilos × costo por kilo`). El tipo de alimento queda guardado
  como snapshot del nombre.
- **Inventario de alimentos**: cada tipo de alimento tiene un stock en kilos,
  un costo por kilo y un **stock mínimo** para notificar "Stock bajo"
  (`stock ≤ mínimo`). Al **añadir stock** se indica si el kilo costó lo mismo
  que la última vez o si cambió el precio. Un alimento **suspendido** no puede
  usarse para registrar alimentación. Al **eliminar** un alimento, los registros
  históricos conservan el nombre del producto (`feed_type_id` queda nulo) para
  mantener la trazabilidad del historial.
- **Vacunas**: solo se registran si el lote está activo.
- **Mortalidad**: resta aves al lote, no puede exceder las aves actuales, y si
  el lote queda sin aves se desactiva con razón "Muerte de todas las gallinas".
- **Evaluación** (semana 90): con porcentaje de postura < 80% el lote se
  descarta; con ≥ 80% se extienden 30 semanas.

## Reglas de IoT (rangos seguros para alertas)

| Sensor | Unidad | Rango seguro |
|---|---|---|
| Temperatura | °C | 18 - 30 |
| Humedad | % | 40 - 70 |
| Amoníaco | ppm | < 25 |

Los valores fuera del rango se marcan automáticamente como alerta
(`is_alert: true`).

## Nota sobre bases de datos existentes

Al iniciar el backend en SQLite se aplican automáticamente migraciones ligeras
(`_run_lightweight_migrations` en `app/main.py`) que agregan la columna
`feeding_records.feed_type_id` a bases ya creadas y crean las tablas nuevas
(`feed_types`, `feed_stock_movements`). Las columnas agregadas con anterioridad
(p. ej. `egg_production.collection_time`) requieren
`ALTER TABLE egg_production ADD COLUMN collection_time TIME;` la primera vez.

---

← [Volver al índice](./README.md)
