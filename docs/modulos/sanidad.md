# Módulo Sanidad (vacunas, mortalidad, enfermedades)

## Propósito

Llevar el estado sanitario de cada lote: vacunación, mortalidad y
enfermedades, con indicadores de supervivencia.

## Frontend

`SanidadPage` (`/sanidad`) consume los endpoints de sanidad a través de
`sanidadService.js`:

- **Selector de lote**: autocompletado por coincidencia parcial del código con
  navegación por teclado (igual que en producción). Al elegir un lote se cargan
  sus indicadores y los tres historiales; el primer lote se selecciona
  automáticamente. Si el texto no corresponde a un lote existente, el panel
  queda en blanco.
- **Tarjetas indicadoras** (estilo dashboard): aves actuales, porcentaje de
  mortalidad, porcentaje de supervivencia y enfermedades activas. Los
  porcentajes provienen de `GET /lots/{id}/mortality/stats`; en móvil se
  muestran como carrusel horizontal.
- **Pestañas** Vacunas / Mortalidad / Enfermedades con contador: cada una lista
  los registros del lote en una tabla dentro de un panel (`.sanidad-table`).
- **Vacunas**: se registran con nombre, dosis, fecha de aplicación, semana
  (precargada con la semana actual del lote), lote del biológico y próxima
  aplicación opcional. Solo se permite en lotes activos.
- **Mortalidad**: el registro descuenta la cantidad de aves del lote y valida en
  el formulario que no exceda las aves actuales. Si el lote queda sin aves, el
  backend lo desactiva y la página lo refleja con un toast informativo y la
  actualización de las tarjetas (nuevo lote "Descartado").
- **Enfermedades**: registro con fecha de diagnóstico, aves afectadas, síntomas
  y tratamiento. El menú de cada fila permite **editar el tratamiento** (modal
  con síntomas, tratamiento y fechas) o **marcar como resuelta** (con
  confirmación). En lotes inactivos solo se permite consultar el historial y
  registrar enfermedades.
- **Responsive**: en móvil las tablas conservan solo las columnas esenciales,
  las tarjetas se muestran como carrusel y las pestañas se desplazan
  horizontalmente.

## Endpoints que utiliza

Ver [Sanidad](../api.md#sanidad) en la referencia de la API.

## Reglas aplicables

Vacunas solo en lotes activos y descuento de aves por mortalidad. Consultar
[Reglas de negocio](../reglas-de-negocio.md).

---

← [Índice de módulos](./README.md) · ← [Índice general](../README.md)
