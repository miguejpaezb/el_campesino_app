# Módulo Dashboard

## Propósito

Mostrar en la ruta `/` un resumen del estado actual de la granja con datos
reales del backend y gráficos interactivos.

## Frontend

`DashboardPage` (`/`) agrega la información de los lotes activos a través de
`dashboardService.js`:

- **Gráfico "Huevos por día"**: barras de los últimos 7 días con tooltip por día
  que muestra los huevos recolectados, no aptos, porcentaje de postura del día,
  promedio por lote y cantidad de lotes con registro ese día.
- **Tarjetas de producción**: producción hoy, lotes activos, tasa de postura y
  mortalidad. El contador de **lotes activos** se obtiene con
  `GET /api/v1/lots/?active=true`.

## Reglas aplicables

Consultar [Reglas de negocio](../reglas-de-negocio.md).

---

← [Índice de módulos](./README.md) · ← [Índice general](../README.md)
