# Arquitectura

Contenido:

1. [Backend (Python + FastAPI)](#backend-python--fastapi)
2. [Auditoría y trazabilidad](#auditoria-y-trazabilidad)
3. [Frontend (React + Vite + Bootstrap)](#frontend-react--vite--bootstrap)
4. [Patrones y decisiones del frontend](#patrones-y-decisiones-del-frontend)
5. [App móvil (Android)](#app-movil-android)

---

## Backend (Python + FastAPI)

El backend sigue una **arquitectura en capas**
(API → Servicios → Repositorios → Modelos ORM → Base de datos):

```
web/backend/
├── app/
│   ├── api/
│   │   ├── deps.py               # Dependencias compartidas (get_db, get_current_user)
│   │   └── v1/                   # Versionado de API (/api/v1)
│   │       ├── router.py         # Router principal que agrupa los endpoints
│   │       ├── auth.py           # Autenticación
│   │       ├── lots.py           # Inventario de aves
│   │       ├── production.py     # Producción diaria de huevos
│   │       ├── feeding.py        # Alimentación
│   │       ├── feed_stock.py     # Inventario de alimentos (insumos)
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

### Nota de origen

La lógica de dominio de lotes se adaptó del **ejercicio en clase**: las clases
`LoteGallinas`, `RegistroPosturas`, `RegistroAlimentacion`, `RegistroVacuna`,
`RegistroMortalidad` y `LoteService` fueron migradas a modelos ORM y servicios
de FastAPI. En el módulo de producción, `RegistroPosturas` quedó representado
por `EggProduction`, que además de la fecha guarda la **hora de recolección**
(`collection_time`).

## Auditoría y trazabilidad

Cada acción que modifica datos (crear/actualizar/descartar/avanzar/evaluar un
lote, registrar producción, alimentación, vacunas, mortalidad o enfermedades)
genera un **registro de auditoría** con un hash SHA-256 encadenado, simulando
blockchain para garantizar la integridad del historial.

Detalle en [módulo de trazabilidad](./modulos/trazabilidad.md).

## Frontend (React + Vite + Bootstrap)

El frontend consume exclusivamente la API REST a través de Axios; nunca accede
a la base de datos:

```
web/frontend/
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
│   ├── pages/                   # Vistas completas (una por módulo)
│   ├── services/                # Clientes HTTP por módulo
│   │   ├── apiClient.js         # Axios con interceptor JWT (baseURL /api/v1)
│   │   └── *Service.js          # Un servicio por módulo (auth, lot, production, ...)
│   ├── hooks/                   # Custom Hooks (useAuth)
│   ├── contexts/                # AuthContext (login/logout/sesión)
│   ├── utils/                   # Utilidades (getErrorMessage)
│   ├── App.jsx                  # Router con rutas públicas y protegidas
│   └── index.jsx                # Punto de entrada (BrowserRouter + AuthProvider + Bootstrap CSS)
├── vite.config.js               # Proxy de desarrollo /api → http://localhost:8000
├── .env.example                 # VITE_API_URL
└── package.json
```

Las páginas del frontend (`pages/`) se corresponden con los módulos que se
documentan en [modulos](./modulos/README.md).

## Patrones y decisiones del frontend

- **Servicio HTTP**: `apiClient.js` define una instancia de Axios con
  `baseURL = VITE_API_URL` (`/api/v1`) y un interceptor que agrega
  `Authorization: Bearer <token>` a cada petición; en errores `401` limpia el
  token.
- **Autenticación**: `AuthContext` expone `user`, `loading`, `login` y
  `logout`; restaura la sesión validando el token con `GET /auth/me` al cargar
  la aplicación.
- **Rutas protegidas**: `ProtectedRoute` redirige a `/login` si no hay sesión y
  muestra un spinner mientras se valida el token.
- **Layout y sidebar**: `Layout` + `Sidebar` replican el diseño de referencia
  con colapso persistido en `localStorage` (escritorio) y drawer móvil; el menú
  de usuario (`avatar`) permite administrar la cuenta o cerrar sesión.
- **UI propia**: los componentes `Modal` y `Toast` usan clases propias con
  prefijo `app-` para no colisionar con las clases de Bootstrap (p. ej.
  `.toast`, `.modal-header`, `.btn-primary`), que ocultaban las notificaciones.
- **Rutas**: `/login` es pública; el resto (`/`, `/lotes`, `/alimentacion`,
  `/sanidad`, `/produccion`, `/trazabilidad`, `/iot`) están protegidas.

## App móvil (Android)

Aplicación Android nativa (Kotlin + Jetpack Compose) que consume la misma API
REST que el frontend web:

```
movil/android/
├── app/
│   └── src/main/
│       ├── java/com/miguelpaezdev/elcampesino/
│       │   ├── MainActivity.kt        # Punto de entrada (Compose)
│       │   ├── data/                  # ApiService, RetrofitClient, DTOs y session/
│       │   └── ui/                    # navigation/, components/, screens/ y theme/
│       └── AndroidManifest.xml
├── gradle/                            # Wrapper de Gradle
├── build.gradle.kts
└── settings.gradle.kts
```

- **Red**: `RetrofitClient` configura Retrofit + OkHttp (con logging en DEBUG)
  y expone `ApiService`, que por ahora cubre `POST auth/login` y `GET auth/me`.
- **Base URL**: apunta al backend desplegado (`https://elcampesino.gvs.lat/api/v1/`).
- **Autenticación**: el token JWT se envía con el header
  `Authorization: Bearer <token>`.
- **Sesión persistente**: el `access_token` (y el usuario) se guardan con
  **DataStore Preferences** (`data/session/SessionManager.kt`). Al abrir la app,
  `MainActivity` lee el token y lo revalida con `GET /auth/me`: si es válido,
  restaura la sesión sin volver a pedir credenciales; si es rechazado, limpia el
  almacenamiento y muestra el login. La sesión solo se cierra con el botón
  **Cerrar sesión**.
- **Expiración del token**: el backend emite JWT con **90 días** de validez
  (`JWT_EXPIRATION_MINUTES=129600`), de modo que la sesión se mantiene aunque el
  usuario cierre o actualice la app.
- **Navegación**: `AppShell` monta un `ModalNavigationDrawer` (menú lateral) con
  un botón flotante superior izquierdo y un `NavHost` (navigation-compose) con
  transiciones `slide + fade`. Las pantallas se definen en `ui/navigation/`
  (`Destinations`, `AppNavHost`, `AppShell`) y por ahora solo muestran el
  encabezado (`PageHeader`: eyebrow + título) de cada sección.
- **Menú de usuario**: la tarjeta flotante (`UserMenu`) muestra el email, el
  avatar con la inicial, el saludo, los botones **Administrar cuenta** y
  **Cerrar sesión**, y los enlaces de políticas/condiciones.

---

← [Volver al índice](./README.md)
