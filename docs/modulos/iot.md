# Módulo Monitoreo IoT

## Propósito

Registrar lecturas de sensores ambientales del galpón (temperatura, humedad y
amoníaco) y alertar automáticamente cuando un valor queda fuera del rango
seguro.

> **Estado:** el backend está listo; el frontend de la ruta `/iot` está
> pendiente de implementar.

## Backend

- Registro de lecturas: al almacenar un valor, el backend calcula
  automáticamente si es una alerta (`is_alert`) según el rango seguro del tipo
  de sensor.
- Consulta de lecturas con filtros opcionales (`?lot_id=&sensor_type=`).
- Consulta de alertas: lecturas con valores fuera del rango seguro.

## Reglas de IoT (rangos seguros)

| Sensor | Unidad | Rango seguro |
|---|---|---|
| Temperatura | °C | 18 - 30 |
| Humedad | % | 40 - 70 |
| Amoníaco | ppm | < 25 |

Los valores fuera del rango se marcan automáticamente como alerta
(`is_alert: true`). Consultar
[Reglas de negocio](../reglas-de-negocio.md#reglas-de-iot-rangos-seguros-para-alertas).

## Endpoints que utiliza

Ver [Monitoreo IoT](../api.md#monitoreo-iot) en la referencia de la API.

---

← [Índice de módulos](./README.md) · ← [Índice general](../README.md)
