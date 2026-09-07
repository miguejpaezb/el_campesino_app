# Guía de inicio

Contenido:

1. [Requisitos previos](#requisitos-previos)
2. [Puesta en marcha del backend](#puesta-en-marcha-del-backend)
3. [Pruebas y calidad del backend](#pruebas-y-calidad-del-backend)
4. [Puesta en marcha del frontend](#puesta-en-marcha-del-frontend)
5. [Crear el admin inicial](#crear-el-admin-inicial)
6. [Verificación de la conexión frontend ↔ backend](#verificacion-de-la-conexion-frontend--backend)
7. [Documentación personalizada del backend](#documentacion-personalizada-del-backend)

---

## Requisitos previos

- Python 3.11+ (probado con 3.14)
- Node.js 20+ y npm (probado con Node 24 / npm 11)
- [Postman](https://www.postman.com/) u otro cliente HTTP (opcional, para pruebas manuales)

## Puesta en marcha del backend

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

## Pruebas y calidad del backend

```powershell
.venv\Scripts\python.exe -m pytest
.venv\Scripts\python.exe -m ruff check app tests
.venv\Scripts\python.exe -m isort --check-only app tests
```

## Puesta en marcha del frontend

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

## Crear el admin inicial

El registro público de usuarios fue eliminado: las cuentas solo las crea un
usuario con rol `admin` (vía API o desde el frontend). Para el primer acceso se
crea el admin con el script CLI:

```powershell
.venv\Scripts\python.exe -m app.scripts.create_admin --username admin --email admin@example.com --password MiClave123
```

## Verificación de la conexión frontend ↔ backend

Con el backend y el frontend corriendo, la conexión entre ambos se valida con
el login, el dashboard y los módulos de lotes, producción, alimentación y
sanidad. Para un detalle del comportamiento de cada módulo consulta
[modulos](./modulos/README.md).

1. **Crear el admin inicial** (ver [arriba](#crear-el-admin-inicial)).
2. **Iniciar sesión** en <http://localhost:5173/login>: la `LoginPage` llama a
   `POST /api/v1/auth/login`, guarda el `access_token` en `localStorage` y
   obtiene el usuario con `GET /api/v1/auth/me`.
3. **Dashboard**: al autenticarse se redirige a `/`, donde `DashboardPage`
   muestra las tarjetas de producción (producción hoy, lotes activos, tasa de
   postura y mortalidad), el gráfico semanal de huevos con detalles por día y
   el resumen de la semana. El contador de **lotes activos** se obtiene con
   `GET /api/v1/lots/?active=true`.
4. **Módulo de lotes** (`/lotes`): `LotsPage` lista los lotes y permite
   buscarlos, filtrarlos y ejecutar acciones (crear, editar, avanzar semana,
   evaluar, resumen y descartar) contra la API real. Las llamadas de colección
   usan la barra final (`/lots/`) para evitar el redirect 307 de FastAPI, que
   hacía perder el header de autorización.
5. **Módulo de producción** (`/produccion`): `ProductionPage` busca el lote con
   autocompletado, muestra sus indicadores, visualiza la producción por rango de
   fechas y registra recolecciones. Si un registro coincide en fecha y hora con
   uno existente, la API responde `409` y el modal ofrece **sumar las
   cantidades** (`?merge=true`).
6. **Módulo de alimentación** (`/alimentacion`): `FeedingPage` muestra la tabla
   de lotes y el botón **"Gestión de alimento"** que abre el inventario
   (`/alimentacion/insumos`); desde el menú de un lote se registra alimentación
   (`POST /api/v1/lots/{id}/feeding`) o se navega al resumen
   (`/alimentacion/resumen/:lotId`).
7. **Módulo de sanidad** (`/sanidad`): `SanidadPage` permite elegir un lote y,
   con pestañas, consultar y registrar **vacunas**, **mortalidad** (descuenta
   aves y valida el máximo) y **enfermedades**. Se guardan contra
   `POST /api/v1/lots/{id}/vaccinations`, `POST /api/v1/lots/{id}/mortality` y
   `POST /api/v1/lots/{id}/diseases`.
8. **Sesión persistente**: el `AuthContext` restaura la sesión al recargar la
   página validando el token con `/auth/me`. Si el token falta o es inválido,
   `ProtectedRoute` redirige a `/login`.
9. **Verificación del proxy**: la petición sale por
   `http://localhost:5173/api/...` (Vite la reenvía a
   `http://localhost:8000/api/...`), lo que se confirma en las herramientas de
   desarrollador o ejecutando:

```powershell
curl.exe -X POST http://localhost:5173/api/v1/auth/login -H "Content-Type: application/json" -d '{"username":"juan","password":"MiClave123"}'
```

Una respuesta `200` con `access_token` confirma que frontend y backend están
conectados; un `401` indica credenciales incorrectas (la conexión sigue
funcionando).

## Documentación personalizada del backend

En `http://127.0.0.1:8000/docs` se sirve una **página de documentación propia**
(no Swagger UI), construida con HTML/CSS/JS vanilla. Lee la especificación
desde `/openapi.json` y se actualiza sola al agregar endpoints.

- **Estructura**: topbar con el nombre y la versión del proyecto, sidebar a la
  izquierda con el menú de secciones (agrupadas por tag de la API) y
  content-main a la derecha que carga la documentación de la sección
  seleccionada.
- **Scroll**: `body` con `overflow: hidden`; el sidebar y el content-main tienen
  `overflow-y: auto` (scroll independiente).
- **Responsive**: en pantallas menores a 768px el sidebar se oculta y se
  despliega con el botón de menú (hamburguesa).
- **Contenido por endpoint**: método HTTP con badge de color, ruta, summary,
  descripción, parámetros, request body (resolviendo `$ref`) y códigos de
  respuesta.
- **Archivos**: `backend/app/static/docs/` (`index.html`, `styles.css`,
  `app.js`) y la ruta `GET /docs` en `app/main.py`.
- Los estilos son **genéricos y básicos**; se ajustarán al estilo definitivo de
  la aplicación cuando se desarrolle el frontend.

---

¿Buscas los endpoints? → [Referencia de la API](./api.md)
¿Quieres entender el código? → [Arquitectura](./arquitectura.md)
← [Volver al índice](./README.md)
