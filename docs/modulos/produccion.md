# Módulo Producción Diaria (huevos)

## Propósito

Registrar la recolección diaria de huevos por lote (cantidades aptas y no
aptas, con fecha y hora) y mostrar indicadores y gráficos de la producción.

## Frontend

`ProductionPage` (`/produccion`) consume los endpoints de producción a través
de `productionService.js`:

- **Selector de lote**: campo con autocompletado propio que filtra por
  coincidencia parcial del código (p. ej. escribir "1" lista los lotes cuyo
  código lo contenga), con navegación por teclado (flechas + Enter + Escape).
  Al elegir un lote se cargan sus datos e indicadores; si el texto no
  corresponde a ningún lote existente, los datos del módulo quedan en blanco.
- **Indicadores** (cards estilo dashboard): producción total del lote, promedio
  de postura semanal, porcentaje de postura del lote y producción actual del
  día. En móvil se muestran como carrusel horizontal. El promedio semanal y el
  porcentaje de postura se calculan sobre **días productivos** (fechas de
  recolección distintas), de modo que varios registros del mismo día no
  distorsionan los indicadores.
- **Gráfico por rango de fechas**: con filtro "Desde/Hasta" (por defecto hoy).
  Si el rango es de un solo día muestra una línea acumulada por hora de
  recolección con interpolación cúbica (`cubicInterpolationMode: 'monotone'`) y
  tooltip por proximidad (hora, huevos previos, recolectados, total acumulado,
  no aptos y comentario); con 2+ días muestra barras por día (tooltip con
  primer/último registro, huevos, no aptos, porcentaje de postura y promedio
  del día).
- **Registro de postura**: formulario con cantidad, no aptos/rotos, fecha y hora
  de recolección (por defecto actuales) y comentario. Valida que al menos una
  cantidad sea mayor a 0, fecha solo hoy/ayer y hora no futura. Si ya existe un
  registro con la misma fecha y hora, abre un modal que muestra el registro
  existente y ofrece **sumar las cantidades** (merge) previa confirmación.
- **Responsive**: en móvil el orden es título → selector → cards → formulario →
  gráfico.

## Endpoints que utiliza

Ver [Producción Diaria (huevos)](../api.md#produccion-diaria-huevos) en la
referencia de la API.

## Reglas aplicables

Etapa de postura (semana ≥ 28), límites de fecha/hora y días productivos.
Consultar [Reglas de negocio](../reglas-de-negocio.md).

---

← [Índice de módulos](./README.md) · ← [Índice general](../README.md)
