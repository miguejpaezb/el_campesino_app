# Módulo Alimentación (incl. insumos y resumen)

## Propósito

Registrar el alimento suministrado a cada lote, administrar el inventario de
insumos (tipos de alimento con stock y precios) y consultar el resumen de
consumo y costos por lote.

## Frontend

El módulo se divide en tres pantallas: `FeedingPage` (`/alimentacion`),
`FeedStockPage` (`/alimentacion/insumos`) y `FeedingSummaryPage`
(`/alimentacion/resumen/:lotId`). Consumen `feedingService.js` y
`feedStockService.js`:

- **Inventario de alimentos** (`FeedStockPage`): buscador por nombre, botón
  "Agregar alimento" y tabla con nombre, stock actual (con badge "Stock bajo"
  si `stock_kg ≤ min_stock_kg`), costo por kilo y fecha de la última
  actualización. Cada fila tiene un menú (`submenu.svg`) con: **Editar** (nombre
  y stock mínimo), **Añadir stock** (kilos y la opción "¿costó lo mismo que la
  última vez?" o "cambió el precio", con fecha del ingreso),
  **Suspender/Activar** y **Eliminar** (desvincula el historial conservando el
  nombre en los registros).
- **Registro por lote** (`FeedingPage`): buscador + tabla de lotes (ID,
  código/raza, aves, semana, estado). En la cabecera, el botón **"Gestión de
  alimento"** abre el inventario. Cada lote tiene un menú con **Registrar
  alimentación** (modal con autocompletado del alimento del inventario —solo
  activos— que muestra stock actual, costo por kilo y estado, más kilos, fecha,
  semana precargada y observaciones; el valor del suministro se calcula con el
  precio del inventario) y **Ver resumen de alimentación**.
- **Resumen por lote** (`FeedingSummaryPage`): cards de total consumido, costo
  total, registros y último suministro (carrusel en móvil); gráfico de barras
  "Kilos de alimento por día" con la ventana fija de los **últimos 7 días** y
  tooltip por día; panel de resumen del lapso (total, costo, registros, promedio
  por día y tipo más usado) y tabla del historial **paginada a 10 registros** por
  página (fecha, semana, tipo, kilos y costo total). El botón **Volver** usa el
  icono `arrow.svg` con fondo amarillo.
- **Responsive**: en móvil las tablas conservan solo las columnas esenciales (en
  `FeedingPage`: ID, lote y menú; en `FeedStockPage`: alimento, última
  actualización y menú, sin el badge de estado), las cards se muestran como
  carrusel y el orden de los paneles prioriza el resumen.

## Endpoints que utiliza

Ver [Alimentación](../api.md#alimentacion) e
[Inventario de Alimentos (insumos)](../api.md#inventario-de-alimentos-insumos)
en la referencia de la API.

## Reglas aplicables

Descuento de stock, snapshot del nombre, stock mínimo y suspensión de insumos.
Consultar [Reglas de negocio](../reglas-de-negocio.md).

---

← [Índice de módulos](./README.md) · ← [Índice general](../README.md)
