# Módulo Inventario de Aves (lotes)

## Propósito

Administrar los lotes de aves de la granja: crearlos, seguirlos semana a
semana, evaluar su rendimiento y descartarlos al final del ciclo.

## Frontend

`LotsPage` (`/lotes`) consume los endpoints de lotes a través de
`lotService.js`:

- **Listado**: tabla con selección múltiple, ID, `lot_code`, aves actuales,
  semana actual, mortalidad (%) y estado (badge "Activo"/"Descartado").
  Buscador en vivo por ID o `lot_code` y filtro por estado.
- **Crear lote**: modal con `lot_code`, raza, cantidad inicial, fecha de
  ingreso y observaciones (validación client-side).
- **Acciones por lote** (selector + botón "Aplicar"): editar (modal
  "Editando &lt;código&gt;" con raza y observaciones), avanzar semana (permite
  uno o varios lotes), evaluar (toast si aún no es la semana 90, modal con el
  resultado en caso contrario), resumen (modal con los indicadores productivos)
  y descartar (modal que pide la razón, cuenta regresiva de 5 s con barra
  decreciente y opción de cancelar).
- **Reglas de validación**: no se combinan acción + filtro a la vez; las
  acciones individuales exigen exactamente un lote; tras ejecutar una acción los
  selectores vuelven al valor predeterminado (sin alterar el resultado
  aplicado); el botón **"Limpiar filtros"** restablece buscador, selectores,
  filtro y selección sin recargar la página.
- **Responsive**: en móvil la tabla muestra solo las columnas esenciales
  (checkbox, ID, `lot_code`, estado), el buscador ocupa el ancho disponible y
  los botones de crear/limpiar son iconos (`add.svg`, `clean.svg`); los
  selectores y el botón Aplicar (icono `arrow.svg` rotado) se mantienen en una
  fila a su ancho natural.

## App móvil

`LotsScreen` (`movil/android/`, paquete `ui/screens/lots`) replica la página
web sobre los mismos endpoints:

- **Listado** con buscador (ID o `lot_code`), filtro por estado, selección
  múltiple y badge de estado; la tabla móvil muestra checkbox, ID, `lot_code` y
  estado.
- **Barra de acciones**: buscador, botones de crear (icono `add`) y limpiar
  (icono `clean`), selectores de **acción** y **filtro**, y botón **Aplicar**
  (icono `arrow`).
- **Modales** equivalentes: crear, editar, descartar (con cuenta regresiva de
  5 s), resultado de evaluación y resumen productivo.
- La lógica vive en `LotsViewModel`; el token JWT se adjunta de forma
  automática mediante un interceptor en `RetrofitClient`.

## Endpoints que utiliza

Ver [Inventario de Aves (lotes)](../api.md#inventario-de-aves-lotes) en la
referencia de la API.

## Reglas aplicables

Ciclo productivo, evaluación en semana 90 y descarte. Consultar
[Reglas de negocio](../reglas-de-negocio.md).

---

← [Índice de módulos](./README.md) · ← [Índice general](../README.md)
