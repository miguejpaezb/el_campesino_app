# Módulo Trazabilidad (auditoría)

## Propósito

Exponer el historial de auditoría de cada entidad como una **cadena de hash
SHA-256 encadenado** (blockchain simulado) y permitir **verificar la
integridad** de dicha cadena. Cualquier alteración de un registro rompe la
cadena y es detectable.

## Concepto

Cada evento que modifica datos genera un `AuditLog` que incluye el hash del
registro anterior (`previous_hash`) y su propio hash (`current_hash`). Las
entidades auditadas son:

| Tipo | Entidad |
|---|---|
| `BirdLot` | Lote |
| `EggProduction` | Registro de producción |
| `FeedingRecord` | Registro de alimentación |
| `Vaccination` | Vacuna |
| `Mortality` | Mortalidad |
| `Disease` | Enfermedad |
| `FeedType` | Tipo de alimento (insumo) |

Acciones registradas: `CREATE`, `UPDATE` y `DELETE`.

## Frontend

`TraceabilityPage` (`/trazabilidad`) consume `traceabilityService.js`
(`GET /traceability/{entity_type}/{entity_id}` y
`POST /traceability/verify/{entity_type}/{entity_id}`) y reutiliza los
servicios de lotes, producción, alimentación, sanidad e insumos para poblar los
selectores de entidades:

- **Explorador por tipo de entidad** (píldoras): Lote, Producción,
  Alimentación, Vacuna, Mortalidad, Enfermedad e Insumo.
- **Selector contextual**: autocompletado de lote por coincidencia parcial del
  código con navegación por teclado (igual que en sanidad). Cuando el tipo de
  entidad pertenece a un lote se elige primero el lote y luego la instancia
  (registro de postura, suministro, vacuna, evento de mortalidad o enfermedad);
  en el caso de los insumos la lista sale del inventario. La primera entidad
  disponible se selecciona automáticamente.
- **Resumen de la cadena**: tipo e identificador de la entidad
  (`BirdLot #3`, `EggProduction #12`...), etiqueta descriptiva (fechas,
  cantidades) y conteo de bloques. El botón **"Verificar integridad"** llama al
  endpoint de verificación y muestra el resultado.
- **Banner de verificación**: verde con "Cadena íntegra · N registros" o rojo
  con "Alteración detectada en el bloque #N"; al detectarse una alteración se
  resalta el bloque señalado.
- **Cadena de bloques**: lista cronológica de los eventos de auditoría; cada
  bloque es expandible y muestra la acción (badge `CREATE`/`UPDATE`/`DELETE`),
  fecha y hora, autor (`Usuario #id` y su nombre si el rol es admin), los
  cambios registrados (tabla campo → valor desde el JSON) y los hashes
  anterior/actual con botón **copiar**. La coincidencia del encadenamiento se
  valida por bloque (el primero se identifica como "Bloque génesis").
- **Responsive**: en móvil los controles se apilan a lo ancho, las etiquetas
  largas se envuelven y los hashes se rompen en varias líneas.

## Endpoints que utiliza

Ver [Trazabilidad](../api.md#trazabilidad) en la referencia de la API.

## Reglas aplicables

La auditoría es inmutable: no hay edición ni borrado de eventos. Consultar
[Arquitectura](../arquitectura.md#auditoria-y-trazabilidad) y
[Reglas de negocio](../reglas-de-negocio.md).

---

← [Índice de módulos](./README.md) · ← [Índice general](../README.md)
