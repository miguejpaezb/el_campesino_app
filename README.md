# Sistema de Gestión Avícola "El Campesino"

> **Proyecto académico** — Evidencia de aprendizaje para el Tecnólogo en **Análisis y Desarrollo de Software (ADSO)**, Ficha **3134556**.

Sistema de gestión modular para la granja avícola **"El Campesino"**. Administra lotes de aves, alimentación, sanidad, producción diaria de huevos, trazabilidad y monitoreo IoT.

---

## Estado del proyecto

| Módulo | Backend | Frontend | Estado |
|---|---|---|---|
| **Autenticación (usuarios + JWT)** | `app/api/v1/auth.py` | `LoginPage` + `AuthContext` | Implementado (login funcional) |
| **Inventario de Aves (lotes)** | `app/api/v1/lots.py` | Ruta `/lotes` | Backend listo; frontend pendiente |
| **Producción Diaria (huevos)** | `app/api/v1/production.py` | Ruta `/produccion` | Backend listo; frontend pendiente |
| **Alimentación** | `app/api/v1/feeding.py` | Ruta `/alimentacion` | Backend listo; frontend pendiente |
| **Sanidad** (vacunas, enfermedades, mortalidad) | `app/api/v1/health.py` | Ruta `/sanidad` | Backend listo; frontend pendiente |
| **Trazabilidad** (blockchain simulado) | `app/api/v1/traceability.py` | Ruta `/trazabilidad` | Backend listo; frontend pendiente |
| **Monitoreo IoT** | `app/api/v1/iot.py` | Ruta `/iot` | Backend listo; frontend pendiente |
| **Frontend base** (layout, routing, dashboard) | — | `components/`, `pages/`, `contexts/` | Iniciado (login + dashboard lite) |
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

## Prueba de conexión frontend ↔ backend (login + dashboard lite)

Con el backend y el frontend corriendo, la conexión entre ambos se valida con una versión lite de login y dashboard:

1. **Registrar un usuario** (una sola vez) vía la API:
   `POST http://localhost:5173/api/v1/auth/register` (pasa por el proxy hacia el backend).

   ```json
   {
     "username": "juan",
     "email": "juan@example.com",
     "password": "MiClave123",
     "full_name": "Juan Perez"
   }
   ```

2. **Iniciar sesión** en <http://localhost:5173/login>: la `LoginPage` llama a `POST /api/v1/auth/login`, guarda el `access_token` en `localStorage` y obtiene el usuario con `GET /api/v1/auth/me`.

3. **Dashboard**: al autenticarse se redirige a `/`, donde `DashboardPage` muestra las tarjetas de los 6 módulos del sistema y el nombre del usuario.

4. **Sesión persistente**: el `AuthContext` restaura la sesión al recargar la página validando el token con `/auth/me`. Si el token falta o es inválido, `ProtectedRoute` redirige a `/login`.

5. **Verificación del proxy**: la petición sale por `http://localhost:5173/api/...` (Vite la reenvía a `http://localhost:8000/api/...`), lo que se puede confirmar con las herramientas de desarrollador del navegador (red) o ejecutando:

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
│   │       ├── feeding.py        # Alimentación
│   │       ├── health.py         # Sanidad (vacunas, mortalidad, enfermedades)
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

La lógica de dominio de lotes se adaptó del **ejercicio en clase**: las clases `LoteGallinas`, `RegistroPosturas`, `RegistroAlimentacion`, `RegistroVacuna`, `RegistroMortalidad` y `LoteService` fueron migradas a modelos ORM y servicios de FastAPI.

Cada acción que modifica datos (crear/actualizar/descartar/avanzar/evaluar un lote, registrar producción, alimentación, vacunas, mortalidad o enfermedades) genera un **registro de auditoría** con un hash SHA-256 encadenado, simulando blockchain para garantizar la integridad del historial.

### Frontend (React + Vite + Bootstrap)

El frontend consume exclusivamente la API REST a través de Axios; nunca accede a la base de datos:

```
frontend/
├── public/                      # Archivos estáticos (favicon)
├── src/
│   ├── components/              # Componentes reutilizables (Navbar, Layout, ProtectedRoute)
│   ├── pages/                   # Vistas completas (LoginPage, DashboardPage, módulos)
│   ├── services/                # Clientes HTTP (apiClient con interceptor JWT, authService)
│   ├── hooks/                   # Custom Hooks (useAuth)
│   ├── contexts/                # Contextos de React (AuthContext: login/logout/sesión)
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
- **Rutas**: `/login` es pública; el resto (`/`, `/lotes`, `/alimentacion`, `/sanidad`, `/produccion`, `/trazabilidad`, `/iot`) están protegidas. Las de módulos son placeholders que se implementarán en la fase siguiente.

---

## API disponible (endpoints)

Todas las rutas usan el prefijo `/api/v1`. Todos los endpoints, excepto `register` y `login`, requieren un token JWT (`Authorization: Bearer <token>`).

### Autenticación

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/api/v1/auth/register` | Crear un usuario |
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
| `POST` | `/api/v1/lots/{id}/production` | Registrar producción diaria |
| `GET` | `/api/v1/lots/{id}/production/total` | Total de huevos del lote |
| `GET` | `/api/v1/lots/{id}/production/average` | Promedio semanal de postura |
| `GET` | `/api/v1/lots/{id}/production/percentage` | Porcentaje de postura |

### Alimentación

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/v1/lots/{id}/feeding` | Registros de alimentación del lote |
| `POST` | `/api/v1/lots/{id}/feeding` | Registrar alimentación |
| `GET` | `/api/v1/lots/{id}/feeding/total` | Total de kilos consumidos |
| `GET` | `/api/v1/lots/{id}/feeding/cost` | Costo total de alimentación |

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

1. **Registrar usuario** → `POST /api/v1/auth/register`:

```json
{
  "username": "juan",
  "email": "juan@example.com",
  "password": "MiClave123",
  "full_name": "Juan Perez"
}
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
- **Producción**: solo se registra si el lote está activo y en etapa de postura (semana ≥ 28).
- **Alimentación**: solo se registra si el lote está activo.
- **Vacunas**: solo se registran si el lote está activo.
- **Mortalidad**: resta aves al lote, no puede exceder las aves actuales, y si el lote queda sin aves se desactiva con razón "Muerte de todas las gallinas".
- **Evaluación** (semana 90): con porcentaje de postura < 80% el lote se descarta; con ≥ 80% se extienden 30 semanas.

## Reglas de IoT (rangos seguros para alertas)

| Sensor | Unidad | Rango seguro |
|---|---|---|
| Temperatura | °C | 18 - 30 |
| Humedad | % | 40 - 70 |
| Amoníaco | ppm | < 25 |

Los valores fuera del rango se marcan automáticamente como alerta (`is_alert: true`).

---

*Última actualización: agosto 2026. El documento se actualiza conforme avanza el desarrollo.*