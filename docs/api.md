# API disponible (endpoints)

Contenido:

1. [Consideraciones generales](#consideraciones-generales)
2. [Autenticación](#autenticacion)
3. [Inventario de Aves (lotes)](#inventario-de-aves-lotes)
4. [Producción Diaria (huevos)](#produccion-diaria-huevos)
5. [Alimentación](#alimentacion)
6. [Inventario de Alimentos (insumos)](#inventario-de-alimentos-insumos)
7. [Sanidad](#sanidad)
8. [Trazabilidad](#trazabilidad)
9. [Monitoreo IoT](#monitoreo-iot)
10. [Ejemplo de uso rápido (Postman)](#ejemplo-de-uso-rapido-postman)

---

## Consideraciones generales

Todas las rutas usan el prefijo `/api/v1`. Todos los endpoints, excepto
`login`, requieren un token JWT (`Authorization: Bearer <token>`). `register`
y `users` requieren además el rol `admin`.

## Autenticación

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/api/v1/auth/register` | Crear un usuario (**solo admin**) |
| `GET` | `/api/v1/auth/users` | Listar usuarios (**solo admin**) |
| `POST` | `/api/v1/auth/login` | Iniciar sesión y obtener JWT |
| `GET` | `/api/v1/auth/me` | Datos del usuario autenticado |

## Inventario de Aves (lotes)

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/v1/lots/` | Listar lotes (`?active=true` para solo activos) |
| `POST` | `/api/v1/lots/` | Crear un lote |
| `GET` | `/api/v1/lots/{id}` | Obtener un lote |
| `PUT` | `/api/v1/lots/{id}` | Actualizar un lote |
| `DELETE` | `/api/v1/lots/{id}` | Descartar un lote (body: `{"reason": "..."}`) |
| `POST` | `/api/v1/lots/{id}/advance-week` | Avanzar una semana |
| `POST` | `/api/v1/lots/{id}/evaluate` | Evaluar el ciclo productivo |
| `GET` | `/api/v1/lots/{id}/summary` | Resumen productivo del lote |

## Producción Diaria (huevos)

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/v1/lots/{id}/production` | Registros de producción (`?from=&to=` por fecha) |
| `POST` | `/api/v1/lots/{id}/production` | Registrar producción diaria (fecha y hora de recolección). Si ya existe un registro con la misma fecha+hora devuelve `409` con el registro existente; usar `?merge=true` para sumar las cantidades |
| `GET` | `/api/v1/lots/{id}/production/total` | Total de huevos del lote |
| `GET` | `/api/v1/lots/{id}/production/average` | Promedio de postura por día productivo |
| `GET` | `/api/v1/lots/{id}/production/percentage` | Porcentaje de postura |

## Alimentación

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/v1/lots/{id}/feeding` | Registros de alimentación del lote |
| `POST` | `/api/v1/lots/{id}/feeding` | Registrar alimentación (`feed_type_id` opcional: toma el precio del inventario y descuenta stock) |
| `GET` | `/api/v1/lots/{id}/feeding/total` | Total de kilos consumidos |
| `GET` | `/api/v1/lots/{id}/feeding/cost` | Costo total de alimentación |

## Inventario de Alimentos (insumos)

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/v1/feed-stock` | Listar tipos de alimento (`?search=` por nombre) |
| `POST` | `/api/v1/feed-stock` | Crear un alimento (stock inicial y costo) |
| `PUT` | `/api/v1/feed-stock/{id}` | Editar nombre y stock mínimo |
| `POST` | `/api/v1/feed-stock/{id}/stock` | Añadir stock (`price_option: same` conserva el precio, `new` lo cambia) |
| `POST` | `/api/v1/feed-stock/{id}/suspend` | Suspender o reactivar un alimento |
| `DELETE` | `/api/v1/feed-stock/{id}` | Eliminar un alimento (el historial conserva el nombre) |
| `GET` | `/api/v1/feed-stock/{id}/movements` | Movimientos de ingreso de stock del alimento |

## Sanidad

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/v1/lots/{id}/vaccinations` | Vacunas del lote |
| `POST` | `/api/v1/lots/{id}/vaccinations` | Registrar vacuna |
| `GET` | `/api/v1/lots/{id}/mortality` | Registros de mortalidad |
| `POST` | `/api/v1/lots/{id}/mortality` | Registrar mortalidad (descuenta aves del lote) |
| `GET` | `/api/v1/lots/{id}/mortality/stats` | % mortalidad y % supervivencia |
| `GET` | `/api/v1/lots/{id}/diseases` | Enfermedades del lote |
| `POST` | `/api/v1/lots/{id}/diseases` | Registrar enfermedad |
| `PUT` | `/api/v1/lots/{id}/diseases/{disease_id}` | Actualizar tratamiento |
| `POST` | `/api/v1/lots/{id}/diseases/{disease_id}/resolve` | Marcar enfermedad como resuelta |

## Trazabilidad

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/v1/traceability/{entity_type}/{entity_id}` | Historial de auditoría de una entidad (ej: `BirdLot/1`) |
| `POST` | `/api/v1/traceability/verify/{entity_type}/{entity_id}` | Verificar integridad de la cadena de hash |

## Monitoreo IoT

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/v1/iot/readings` | Lecturas de sensores (`?lot_id=&sensor_type=`) |
| `POST` | `/api/v1/iot/readings` | Registrar lectura de sensor (calcula alerta automáticamente) |
| `GET` | `/api/v1/iot/alerts` | Lecturas con valores fuera del rango seguro |

## Ejemplo de uso rápido (Postman)

1. **Crear el admin inicial** (o pedirlo a un admin existente):

```powershell
.venv\Scripts\python.exe -m app.scripts.create_admin --username admin --email admin@example.com --password MiClave123
```

2. **Iniciar sesión** → `POST /api/v1/auth/login` (guarda el `access_token`):

```json
{
  "username": "juan",
  "password": "MiClave123"
}
```

3. **Crear lote** → `POST /api/v1/lots/` con `Authorization: Bearer <token>`:

```json
{
  "lot_code": "LOTE-001",
  "breed": "Ross 308",
  "initial_quantity": 1000
}
```

4. **Registrar alimentación** → `POST /api/v1/lots/1/feeding`:

```json
{
  "feed_type": "Concentrado",
  "kilos": 150,
  "cost_per_kilo": 2.5
}
```

5. **Ver resumen** → `GET /api/v1/lots/1/summary`

6. **Registrar una lectura de sensor** → `POST /api/v1/iot/readings`:

```json
{
  "sensor_id": "SENS-1",
  "sensor_type": "temperature",
  "value": 25.0
}
```

7. **Verificar la trazabilidad del lote** → `POST /api/v1/traceability/verify/BirdLot/1`

---

← [Volver al índice](./README.md)
