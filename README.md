# Sistema de Gestión Avícola "El Campesino"

> **Proyecto académico** — Evidencia de aprendizaje para el Tecnólogo en **Análisis y Desarrollo de Software (ADSO)**, Ficha **3134556**.

Sistema de gestión modular para la granja avícola **"El Campesino"**. Administra lotes de aves, alimentación, sanidad, producción diaria de huevos, trazabilidad y monitoreo IoT.

---

## Estado del proyecto

| Módulo | Backend | Frontend | Estado |
|---|---|---|---|
| **Autenticación (usuarios + JWT)** | `app/api/v1/auth.py` | `LoginPage` + `AuthContext` | Implementado (login funcional) |
| **Inventario de Aves (lotes)** | `app/api/v1/lots.py` | `LotsPage` (ruta `/lotes`) | Implementado (listado, buscar, filtrar, crear, editar, avanzar semana, evaluar, resumen, descartar) |
| **Producción Diaria (huevos)** | `app/api/v1/production.py` | `ProductionPage` (ruta `/produccion`) | Implementado (autocompletado de lote, indicadores por día productivo, gráfico por rango, registro de postura con merge de coincidencias) |
| **Alimentación** | `app/api/v1/feeding.py` + `app/api/v1/feed_stock.py` | `FeedingPage` (`/alimentacion`), `FeedStockPage` (`/alimentacion/insumos`) y `FeedingSummaryPage` (`/alimentacion/resumen/:lotId`) | Implementado (inventario de alimentos con stock y precios, registro por lote con descuento de stock, resumen con gráfico por semanas e historial paginado) |
| **Sanidad** (vacunas, enfermedades, mortalidad) | `app/api/v1/health.py` | Ruta `/sanidad` | Backend listo; frontend pendiente |
| **Trazabilidad** (blockchain simulado) | `app/api/v1/traceability.py` | Ruta `/trazabilidad` | Backend listo; frontend pendiente |
| **Monitoreo IoT** | `app/api/v1/iot.py` | Ruta `/iot` | Backend listo; frontend pendiente |
| **Frontend base** (layout, sidebar, dashboard) | — | `components/`, `pages/`, `contexts/`, `services/` | Implementado (sidebar responsive, menú de usuario y dashboard con datos del backend y gráfico semanal con detalles por día) |
| **Pruebas + documentación** | — | — | Parcial |

---

## Tecnologías

| Capa | Tecnología |
|---|---|
| Backend | Python 3.11+ · FastAPI · SQLAlchemy 2.0 · Pydantic v2 |
| Frontend | React 19 · Vite · Bootstrap 5 (react-bootstrap) · React Router · Axios |
| Autenticación | JWT (python-jose) + bcrypt (passlib) |
| Base de datos | SQLite (desarrollo) / PostgreSQL (producción) |
| Testing | Pytest + TestClient (httpx) |
| Calidad | Ruff (linter) + isort (orden de imports) |
| Calidad frontend | ESLint + Prettier |

---

## Requisitos previos

- Python 3.11+ (probado con 3.14)
- Node.js 20+ y npm (probado con Node 24 / npm 11)
- [Postman](https://www.postman.com/) u otro cliente HTTP (opcional, para pruebas manuales)

---

## Puesta en marcha

### 1. Crear el entorno virtual e instalar dependencias

Desde la carpeta `backend`:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configurar variables de entorno

Copiar `.env.example` a `.env` y ajustar valores si es necesario:

```powershell
Copy-Item .env.example .env
```

### 3. Iniciar el servidor

```powershell
.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

- Documentación personalizada (página propia): <http://127.0.0.1:8000/docs>
- Documentación alternativa (ReDoc): <http://127.0.0.1:8000/redoc>
- Esquema OpenAPI: <http://127.0.0.1:8000/openapi.json>

### 4. Ejecutar los tests

```powershell
.venv\Scripts\python.exe -m pytest
```

### 5. Verificar calidad de código

```powershell
.venv\Scripts\python.exe -m ruff check app tests
.venv\Scripts\python.exe -m isort --check-only app tests
```

### 6. Iniciar el frontend (React + Bootstrap)

Desde la carpeta `frontend`:

```powershell
npm install
Copy-Item .env.example .env
npm run dev
```

- Abrir el navegador en <http://localhost:5173>.
- El dev server de Vite configura un **proxy** (`/api` → `http://localhost:8000`), de modo que el frontend usa rutas relativas y no sufre problemas de CORS.
- Verificar calidad de código del frontend:

```powershell
npm run lint
```

---

## Prueba de conexión frontend ↔ backend (login + dashboard + lotes + producción + alimentación)

Con el backend y el frontend corriendo, la conexión entre ambos se valida con el login, el dashboard, el módulo de lotes, el de producción y el de alimentación:

1. **Crear el usuario admin inicial** con el script CLI:

   ```powershell
   .venv\Scripts\python.exe -m app.scripts.create_admin --username admin --email admin@example.com --password MiClave123
   ```

   El registro público de usuarios fue eliminado: las cuentas solo las crea un
   usuario con rol `admin` (vía API o desde el frontend).

2. **Iniciar sesión** en <http://localhost:5173/login>: la `LoginPage` llama a `POST /api/v1/auth/login`, guarda el `access_token` en `localStorage` y obtiene el usuario con `GET /api/v1/auth/me`.

3. **Dashboard**: al autenticarse se redirige a `/`, donde `DashboardPage` muestra las tarjetas de producción (producción hoy, lotes activos, tasa de postura y mortalidad), el gráfico semanal de huevos con detalles por día (huevos, no aptos, postura, promedio y lotes con registro al pasar el cursor), el resumen de la semana y el historial de acciones. El contador de **lotes activos** se obtiene del backend con `GET /api/v1/lots/?active=true`.

4. **Módulo de lotes** (`/lotes`): `LotsPage` lista los lotes y permite buscarlos por ID o `lot_code`, filtrarlos por estado y ejecutar acciones (crear, editar, avanzar semana, evaluar, resumen y descartar) contra la API real. Nota: las llamadas de colección usan la barra final (`/lots/`) para evitar el redirect 307 de FastAPI, que hacía perder el header de autorización.

5. **Módulo de producción** (`/produccion`): `ProductionPage` permite buscar el lote con autocompletado por coincidencia parcial, muestra sus indicadores (total, promedio semanal, porcentaje de postura y producción del día), visualiza la producción por rango de fechas (línea acumulada por hora en un solo día, barras por día en rangos largos) y registra recolecciones con fecha y hora. Si un registro coincide en fecha y hora con uno existente, la API responde `409` y el modal ofrece **sumar las cantidades** (`?merge=true`).

6. **Módulo de alimentación** (`/alimentacion`): `FeedingPage` muestra la tabla de lotes y el botón **"Gestión de alimento"** que abre el inventario (`/alimentacion/insumos`). Allí se agregan alimentos (`POST /api/v1/feed-stock`) con stock, costo por kilo y stock mínimo; el menú de cada fila permite añadir stock, suspender o eliminar. De vuelta en `/alimentacion`, el menú de un lote → **Registrar alimentación** abre el modal con autocompletado de alimento (valida stock y muestra el valor del suministro) y guarda con `POST /api/v1/lots/{id}/feeding`. La opción **Ver resumen de alimentación** navega a `/alimentacion/resumen/:lotId`, con cards, gráfico por semanas, resumen del lapso e historial paginado.

7. **Sesión persistente**: el `AuthContext` restaura la sesión al recargar la página validando el token con `/auth/me`. Si el token falta o es inválido, `ProtectedRoute` redirige a `/login`.

8. **Verificación del proxy**: la petición sale por `http://localhost:5173/api/...` (Vite la reenvía a `http://localhost:8000/api/...`), lo que se puede confirmar con las herramientas de desarrollador del navegador (red) o ejecutando:

   ```powershell
   curl.exe -X POST http://localhost:5173/api/v1/auth/login -H "Content-Type: application/json" -d '{"username":"juan","password":"MiClave123"}'
   ```

   Una respuesta `200` con `access_token` confirma que frontend y backend están conectados; un `401` indica credenciales incorrectas (la conexión sigue funcionando).

---

## Documentación personalizada

En `http://127.0.0.1:8000/docs` se sirve una **página de documentación propia** (no Swagger UI), construida con HTML/CSS/JS vanilla. Lee la especificación desde `/openapi.json` y se actualiza sola al agregar endpoints.

- **Estructura**: topbar con el nombre y la versión del proyecto, sidebar a la izquierda con el menú de secciones (agrupadas por tag de la API) y content-main a la derecha que carga la documentación de la sección seleccionada.
- **Scroll**: `body` con `overflow: hidden`; el sidebar y el content-main tienen `overflow-y: auto` (scroll independiente).
- **Responsive**: en pantallas menores a 768px el sidebar se oculta y se despliega con el botón de menú (hamburguesa).
- **Contenido por endpoint**: método HTTP con badge de color, ruta, summary, descripción, parámetros, request body (resolviendo `$ref`) y códigos de respuesta.
- **Archivos**: `backend/app/static/docs/` (`index.html`, `styles.css`, `app.js`) y la ruta `GET /docs` en `app/main.py`.
- Los estilos son **genéricos y básicos**; se ajustarán al estilo definitivo de la aplicación cuando se desarrolle el frontend.

## Arquitectura

El backend sigue una **arquitectura en capas** (API → Servicios → Repositorios → Modelos ORM → Base de datos):

```
backend/
├── app/
│   ├── api/
│   │   ├── deps.py               # Dependencias compartidas (get_db, get_current_user)
│   │   └── v1/                   # Versionado de API (/api/v1)
│   │       ├── router.py         # Router principal que agrupa los endpoints
│   │       ├── auth.py           # Autenticación
│   │       ├── lots.py           # Inventario de aves
│   │       ├── production.py     # Producción diaria de huevos
│   │   ├── feeding.py        # Alimentación
│   │   ├── feed_stock.py     # Inventario de alimentos (insumos)
│   │   ├── health.py         # Sanidad (vacunas, mortalidad, enfermedades)
│   │       ├── traceability.py   # Trazabilidad (blockchain simulado)
│   │       └── iot.py            # Monitoreo IoT
│   ├── core/                     # Configuración, seguridad y constantes
│   │   ├── config.py             # Settings desde .env
│   │   ├── database.py           # Engine, sesión y Base de SQLAlchemy
│   │   ├── security.py           # JWT + bcrypt + dependencia de usuario
│   │   └── constants.py          # Ciclo productivo y umbrales de sensores
│   ├── models/                   # Modelos ORM (SQLAlchemy 2.0)
│   │   ├── user.py
│   │   ├── bird_lot.py
│   │   ├── egg_production.py
│   │   ├── feeding.py
│   │   ├── feed_stock.py         # Tipos de alimento + movimientos de stock
│   │   ├── vaccination.py
│   │   ├── mortality.py
│   │   ├── disease.py
│   │   ├── audit_log.py          # Trazabilidad (hash encadenado)
│   │   └── sensor_reading.py     # Lecturas IoT
│   ├── schemas/                  # Schemas Pydantic (DTOs)
│   ├── services/                 # Lógica de negocio
│   ├── repositories/             # Acceso a datos (CRUD)
│   ├── static/docs/              # Página de documentación personalizada
│   └── main.py                   # Punto de entrada
├── tests/                        # Pruebas unitarias y de integración
├── requirements.txt
├── .env.example
└── pytest.ini
```

La lógica de dominio de lotes se adaptó del **ejercicio en clase**: las clases `LoteGallinas`, `RegistroPosturas`, `RegistroAlimentacion`, `RegistroVacuna`, `RegistroMortalidad` y `LoteService` fueron migradas a modelos ORM y servicios de FastAPI. En el módulo de producción, `RegistroPosturas` quedó representado por `EggProduction`, que además de la fecha guarda la **hora de recolección** (`collection_time`).

Cada acción que modifica datos (crear/actualizar/descartar/avanzar/evaluar un lote, registrar producción, alimentación, vacunas, mortalidad o enfermedades) genera un **registro de auditoría** con un hash SHA-256 encadenado, simulando blockchain para garantizar la integridad del historial.

### Frontend (React + Vite + Bootstrap)

El frontend consume exclusivamente la API REST a través de Axios; nunca accede a la base de datos:

```
frontend/
├── public/                      # Archivos estáticos (favicon, iconos SVG)
├── src/
│   ├── components/              # Componentes reutilizables
│   │   ├── Layout.jsx/css       # Layout principal (sidebar + main-container)
│   │   ├── Sidebar.jsx          # Menú lateral (colapso persistido + drawer móvil)
│   │   ├── PageHeader.jsx       # Encabezado reutilizable (eyebrow + título)
│   │   ├── Modal.jsx            # Modal reutilizable (overlay, tecla Escape, footer)
│   │   ├── Toast.jsx            # Notificaciones toast (éxito/error/info)
│   │   ├── RowMenu.jsx/css      # Menú desplegable por fila (submenú)
│   │   ├── ProtectedRoute.jsx   # Guard de rutas autenticadas
│   │   └── ErrorBoundary.jsx
│   ├── pages/                   # Vistas completas
│   │   ├── LoginPage.jsx/css
│   │   ├── DashboardPage.jsx/css
│   │   ├── LotsPage.jsx/css     # Módulo Inventario de Aves (lotes)
│   │   ├── ProductionPage.jsx/css # Módulo Producción Diaria
│   │   ├── FeedingPage.jsx/css  # Módulo Alimentación (tabla de lotes)
│   │   ├── FeedStockPage.jsx/css # Inventario de alimentos (insumos)
│   │   └── FeedingSummaryPage.jsx/css # Resumen de alimentación por lote
│   ├── services/                # Clientes HTTP por módulo
│   │   ├── apiClient.js         # Axios con interceptor JWT (baseURL /api/v1)
│   │   ├── authService.js
│   │   ├── lotService.js        # CRUD + acciones de lotes
│   │   ├── productionService.js # Producción diaria (registro, merge, indicadores)
│   │   ├── feedingService.js    # Alimentación (registro, total kg, costo)
│   │   ├── feedStockService.js  # Inventario de alimentos (CRUD + stock)
│   │   └── dashboardService.js  # Agregación de datos del dashboard
│   ├── hooks/                   # Custom Hooks (useAuth)
│   ├── contexts/                # AuthContext (login/logout/sesión)
│   ├── utils/                   # Utilidades (getErrorMessage)
│   ├── App.jsx                  # Router con rutas públicas y protegidas
│   └── index.jsx                # Punto de entrada (BrowserRouter + AuthProvider + Bootstrap CSS)
├── vite.config.js               # Proxy de desarrollo /api → http://localhost:8000
├── .env.example                 # VITE_API_URL
└── package.json
```

- **Servicio HTTP**: `apiClient.js` define una instancia de Axios con `baseURL = VITE_API_URL` (`/api/v1`) y un interceptor que agrega `Authorization: Bearer <token>` a cada petición; en errores `401` limpia el token.
- **Autenticación**: `AuthContext` expone `user`, `loading`, `login` y `logout`; restaura la sesión validando el token con `GET /auth/me` al cargar la aplicación.
- **Rutas protegidas**: `ProtectedRoute` redirige a `/login` si no hay sesión y muestra un spinner mientras se valida el token.
- **Layout y sidebar**: `Layout` + `Sidebar` replican el diseño de referencia con colapso persistido en `localStorage` (escritorio) y drawer móvil; el menú de usuario (`avatar`) permite administrar la cuenta o cerrar sesión.
- **UI propia**: los componentes `Modal` y `Toast` usan clases propias con prefijo `app-` para no colisionar con las clases de Bootstrap (p. ej. `.toast`, `.modal-header`, `.btn-primary`), que ocultaban las notificaciones.
- **Rutas**: `/login` es pública; el resto (`/`, `/lotes`, `/alimentacion`, `/sanidad`, `/produccion`, `/trazabilidad`, `/iot`) están protegidas. Los módulos **`/lotes`**, **`/produccion`** y **`/alimentacion`** (incluye `/alimentacion/insumos` y `/alimentacion/resumen/:lotId`) están implementados; el resto de módulos son placeholders que se implementarán en fases siguientes.

### Producción Diaria (frontend)

`ProductionPage` (`/produccion`) consume los endpoints de producción a través de `productionService.js`:

- **Selector de lote**: campo con autocompletado propio que filtra por coincidencia parcial del código (p. ej. escribir "1" lista los lotes cuyo código lo contenga), con navegación por teclado (flechas + Enter + Escape). Al elegir un lote se cargan sus datos e indicadores; si el texto no corresponde a ningún lote existente, los datos del módulo quedan en blanco.
- **Indicadores** (cards estilo dashboard): producción total del lote, promedio de postura semanal, porcentaje de postura del lote y producción actual del día. En móvil se muestran como carrusel horizontal. El promedio semanal y el porcentaje de postura se calculan sobre **días productivos** (fechas de recolección distintas), de modo que varios registros del mismo día no distorsionan los indicadores.
- **Gráfico por rango de fechas**: con filtro "Desde/Hasta" (por defecto hoy). Si el rango es de un solo día muestra una línea acumulada por hora de recolección con interpolación cúbica (`cubicInterpolationMode: 'monotone'`) y tooltip por proximidad (hora, huevos previos, recolectados, total acumulado, no aptos y comentario); con 2+ días muestra barras por día (tooltip con primer/último registro, huevos, no aptos, porcentaje de postura y promedio del día).
- **Registro de postura**: formulario con cantidad, no aptos/rotos, fecha y hora de recolección (por defecto actuales) y comentario. Valida que al menos una cantidad sea mayor a 0, fecha solo hoy/ayer y hora no futura. Si ya existe un registro con la misma fecha y hora, abre un modal que muestra el registro existente y ofrece **sumar las cantidades** (merge) previa confirmación.
- **Responsive**: en móvil el orden es título → selector → cards → formulario → gráfico.

### Dashboard (frontend)

`DashboardPage` (`/`) agrega la información de los lotes activos a través de `dashboardService.js`:

- **Gráfico "Huevos por día"**: barras de los últimos 7 días con tooltip por día que muestra los huevos recolectados, no aptos, porcentaje de postura del día, promedio por lote y cantidad de lotes con registro ese día.

### Inventario de Aves (frontend)

`LotsPage` (`/lotes`) consume los endpoints de lotes a través de `lotService.js`:

- **Listado**: tabla con selección múltiple, ID, `lot_code`, aves actuales, semana actual, mortalidad (%) y estado (badge "Activo"/"Descartado"). Buscador en vivo por ID o `lot_code` y filtro por estado.
- **Crear lote**: modal con `lot_code`, raza, cantidad inicial, fecha de ingreso y observaciones (validación client-side).
- **Acciones por lote** (selector + botón "Aplicar"): editar (modal "Editando &lt;código&gt;" con raza y observaciones), avanzar semana (permite uno o varios lotes), evaluar (toast si aún no es la semana 90, modal con el resultado en caso contrario), resumen (modal con los indicadores productivos) y descartar (modal que pide la razón, cuenta regresiva de 5 s con barra decreciente y opción de cancelar).
- **Reglas de validación**: no se combinan acción + filtro a la vez; las acciones individuales exigen exactamente un lote; tras ejecutar una acción los selectores vuelven al valor predeterminado (sin alterar el resultado aplicado); el botón **"Limpiar filtros"** restablece buscador, selectores, filtro y selección sin recargar la página.
- **Responsive**: en móvil la tabla muestra solo las columnas esenciales (checkbox, ID, `lot_code`, estado), el buscador ocupa el ancho disponible y los botones de crear/limpiar son iconos (`add.svg`, `clean.svg`); los selectores y el botón Aplicar (icono `arrow.svg` rotado) se mantienen en una fila a su ancho natural.

### Alimentación (frontend)

El módulo se divide en tres pantallas: `FeedingPage` (`/alimentacion`), `FeedStockPage` (`/alimentacion/insumos`) y `FeedingSummaryPage` (`/alimentacion/resumen/:lotId`). Consumen `feedingService.js` y `feedStockService.js`:

- **Inventario de alimentos** (`FeedStockPage`): buscador por nombre, botón "Agregar alimento" y tabla con nombre, stock actual (con badge "Stock bajo" si `stock_kg ≤ min_stock_kg`), costo por kilo y fecha de la última actualización. Cada fila tiene un menú (`submenu.svg`) con: **Editar** (nombre y stock mínimo), **Añadir stock** (kilos y la opción "¿costó lo mismo que la última vez?" o "cambió el precio", con fecha del ingreso), **Suspender/Activar** y **Eliminar** (desvincula el historial conservando el nombre en los registros).
- **Registro por lote** (`FeedingPage`): buscador + tabla de lotes (ID, código/raza, aves, semana, estado). En la cabecera, el botón **"Gestión de alimento"** abre el inventario. Cada lote tiene un menú con **Registrar alimentación** (modal con autocompletado del alimento del inventario —solo activos— que muestra stock actual, costo por kilo y estado, más kilos, fecha, semana precargada y observaciones; el valor del suministro se calcula con el precio del inventario) y **Ver resumen de alimentación**.
- **Resumen por lote** (`FeedingSummaryPage`): cards de total consumido, costo total, registros y último suministro (carrusel en móvil); gráfico de barras "Kilos de alimento por día" con la ventana fija de los **últimos 7 días** y tooltip por día; panel de resumen del lapso (total, costo, registros, promedio por día y tipo más usado) y tabla del historial **paginada a 10 registros** por página (fecha, semana, tipo, kilos y costo total). El botón **Volver** usa el icono `arrow.svg` con fondo amarillo.
- **Responsive**: en móvil las tablas conservan solo las columnas esenciales (en `FeedingPage`: ID, lote y menú; en `FeedStockPage`: alimento, última actualización y menú, sin el badge de estado), las cards se muestran como carrusel y el orden de los paneles prioriza el resumen.

---

## API disponible (endpoints)

Todas las rutas usan el prefijo `/api/v1`. Todos los endpoints, excepto `login`, requieren un token JWT (`Authorization: Bearer <token>`). `register` y `users` requieren además el rol `admin`.

### Autenticación

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/api/v1/auth/register` | Crear un usuario (**solo admin**) |
| `GET` | `/api/v1/auth/users` | Listar usuarios (**solo admin**) |
| `POST` | `/api/v1/auth/login` | Iniciar sesión y obtener JWT |
| `GET` | `/api/v1/auth/me` | Datos del usuario autenticado |

### Inventario de Aves (lotes)

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

### Producción Diaria (huevos)

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/v1/lots/{id}/production` | Registros de producción (`?from=&to=` por fecha) |
| `POST` | `/api/v1/lots/{id}/production` | Registrar producción diaria (fecha y hora de recolección). Si ya existe un registro con la misma fecha+hora devuelve `409` con el registro existente; usar `?merge=true` para sumar las cantidades |
| `GET` | `/api/v1/lots/{id}/production/total` | Total de huevos del lote |
| `GET` | `/api/v1/lots/{id}/production/average` | Promedio de postura por día productivo |
| `GET` | `/api/v1/lots/{id}/production/percentage` | Porcentaje de postura |

### Alimentación

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/v1/lots/{id}/feeding` | Registros de alimentación del lote |
| `POST` | `/api/v1/lots/{id}/feeding` | Registrar alimentación (`feed_type_id` opcional: toma el precio del inventario y descuenta stock) |
| `GET` | `/api/v1/lots/{id}/feeding/total` | Total de kilos consumidos |
| `GET` | `/api/v1/lots/{id}/feeding/cost` | Costo total de alimentación |

### Inventario de Alimentos (insumos)

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/v1/feed-stock` | Listar tipos de alimento (`?search=` por nombre) |
| `POST` | `/api/v1/feed-stock` | Crear un alimento (stock inicial y costo) |
| `PUT` | `/api/v1/feed-stock/{id}` | Editar nombre y stock mínimo |
| `POST` | `/api/v1/feed-stock/{id}/stock` | Añadir stock (`price_option: same` conserva el precio, `new` lo cambia) |
| `POST` | `/api/v1/feed-stock/{id}/suspend` | Suspender o reactivar un alimento |
| `DELETE` | `/api/v1/feed-stock/{id}` | Eliminar un alimento (el historial conserva el nombre) |
| `GET` | `/api/v1/feed-stock/{id}/movements` | Movimientos de ingreso de stock del alimento |

### Sanidad

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

### Trazabilidad

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/v1/traceability/{entity_type}/{entity_id}` | Historial de auditoría de una entidad (ej: `BirdLot/1`) |
| `POST` | `/api/v1/traceability/verify/{entity_type}/{entity_id}` | Verificar integridad de la cadena de hash |

### Monitoreo IoT

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/v1/iot/readings` | Lecturas de sensores (`?lot_id=&sensor_type=`) |
| `POST` | `/api/v1/iot/readings` | Registrar lectura de sensor (calcula alerta automáticamente) |
| `GET` | `/api/v1/iot/alerts` | Lecturas con valores fuera del rango seguro |

---

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

## Reglas de negocio implementadas (heredadas del ejercicio en clase)

- Un lote inicia en la **semana 16** (semana de compra) y arranca la postura en la **semana 28**.
- **Producción**: solo se registra si el lote está activo y en etapa de postura (semana ≥ 28). Las cantidades (aptos y no aptos) deben ser ≥ 0 y al menos una mayor a 0; la fecha de recolección solo puede ser hoy o el día anterior, y la hora no puede ser futura. Varios registros del mismo día se permiten en horas distintas; si coinciden fecha y hora, las cantidades se suman al registro existente (merge). El promedio semanal y el porcentaje de postura se calculan agrupando por fecha de recolección distinta (**días productivos**), por lo que varios registros del mismo día cuentan como un solo día productivo y no distorsionan las métricas.
- **Alimentación**: solo se registra si el lote está activo. Si el registro usa `feed_type_id` (inventario), el alimento debe existir, estar activo (no suspendido) y tener **stock suficiente**; el stock se **descuenta** al registrar y el costo se toma del precio del inventario (el valor monetario del registro es `kilos × costo por kilo`). El tipo de alimento queda guardado como snapshot del nombre.
- **Inventario de alimentos**: cada tipo de alimento tiene un stock en kilos, un costo por kilo y un **stock mínimo** para notificar "Stock bajo" (`stock ≤ mínimo`). Al **añadir stock** se indica si el kilo costó lo mismo que la última vez o si cambió el precio. Un alimento **suspendido** no puede usarse para registrar alimentación. Al **eliminar** un alimento, los registros históricos conservan el nombre del producto (`feed_type_id` queda nulo) para mantener la trazabilidad del historial.
- **Vacunas**: solo se registran si el lote está activo.
- **Mortalidad**: resta aves al lote, no puede exceder las aves actuales, y si el lote queda sin aves se desactiva con razón "Muerte de todas las gallinas".
- **Evaluación** (semana 90): con porcentaje de postura < 80% el lote se descarta; con ≥ 80% se extienden 30 semanas.

> **Nota (base de datos existente):** al iniciar el backend en SQLite se aplican automáticamente migraciones ligeras (`_run_lightweight_migrations` en `app/main.py`) que agregan la columna `feeding_records.feed_type_id` a bases ya creadas y crean las tablas nuevas (`feed_types`, `feed_stock_movements`). Las columnas agregadas con anterioridad (p. ej. `egg_production.collection_time`) requieren `ALTER TABLE egg_production ADD COLUMN collection_time TIME;` la primera vez.

## Reglas de IoT (rangos seguros para alertas)

| Sensor | Unidad | Rango seguro |
|---|---|---|
| Temperatura | °C | 18 - 30 |
| Humedad | % | 40 - 70 |
| Amoníaco | ppm | < 25 |

Los valores fuera del rango se marcan automáticamente como alerta (`is_alert: true`).

---

*Última actualización: agosto 2026. El documento se actualiza conforme avanza el desarrollo.*