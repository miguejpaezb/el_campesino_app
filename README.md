# Sistema de Gestión Avícola "El Campesino"

> **Proyecto académico** — Evidencia de aprendizaje para el Tecnólogo en **Análisis y Desarrollo de Software (ADSO)**, Ficha **3134556**.

![Python](https://img.shields.io/badge/-Python-3776AB?style=flat&logo=python&logoColor=white) ![FastAPI](https://img.shields.io/badge/-FastAPI-009688?style=flat&logo=fastapi&logoColor=white) ![React](https://img.shields.io/badge/-React-61DAFB?style=flat&logo=react&logoColor=black) ![SQLite](https://img.shields.io/badge/-SQLite-003B57?style=flat&logo=sqlite&logoColor=white) ![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-4169E1?style=flat&logo=postgresql&logoColor=white) ![JWT](https://img.shields.io/badge/-JWT-000000?style=flat&logo=jsonwebtokens&logoColor=white)

Sistema de gestión modular full-stack para la granja avícola **"El Campesino"**.
Administra lotes de aves, alimentación, sanidad, producción diaria de huevos,
trazabilidad (hash encadenado tipo blockchain) y monitoreo IoT en tiempo real.

**Highlights técnicos:**
- 🔐 Autenticación JWT con roles (admin/operario/veterinario)
- 🏗️ Arquitectura en capas (API → Servicios → Repositorios → ORM)
- 📊 Dashboards con gráficos interactivos y datos en tiempo real
- ⛓️ Trazabilidad con hash SHA-256 encadenado (auditoría inmutable)
- ✅ Testing con Pytest + linting (Ruff, ESLint)

---

## Documentación

La documentación completa vive en [`docs/`](./docs/README.md), dividida en
documentos cortos y navegables:

| Documento | Contenido |
|---|---|
| [Índice general](./docs/README.md) | Punto de entrada de la documentación |
| [Guía de inicio](./docs/guia-de-inicio.md) | Requisitos, instalación, puesta en marcha y verificación de la conexión |
| [Arquitectura](./docs/arquitectura.md) | Capas del backend, árbol de carpetas y patrones del frontend |
| [API disponible](./docs/api.md) | Todos los endpoints por módulo + ejemplo con Postman |
| [Reglas de negocio](./docs/reglas-de-negocio.md) | Reglas del dominio y rangos de sensores IoT |
| [Módulos](./docs/modulos/README.md) | Documentación funcional por módulo |

---

## Estado del proyecto

| Módulo | Backend | Frontend | Doc | Estado |
|---|---|---|---|---|
| **Autenticación** (usuarios + JWT) | `app/api/v1/auth.py` | `LoginPage` + `AuthContext` | [autenticacion.md](./docs/modulos/autenticacion.md) | Implementado (login funcional) |
| **Dashboard** | — | `DashboardPage` | [dashboard.md](./docs/modulos/dashboard.md) | Implementado |
| **Inventario de Aves** (lotes) | `app/api/v1/lots.py` | `LotsPage` (`/lotes`) | [lotes.md](./docs/modulos/lotes.md) | Implementado |
| **Producción Diaria** (huevos) | `app/api/v1/production.py` | `ProductionPage` (`/produccion`) | [produccion.md](./docs/modulos/produccion.md) | Implementado |
| **Alimentación** | `app/api/v1/feeding.py` + `feed_stock.py` | `FeedingPage` (`/alimentacion`), `FeedStockPage`, `FeedingSummaryPage` | [alimentacion.md](./docs/modulos/alimentacion.md) | Implementado |
| **Sanidad** (vacunas, mortalidad, enfermedades) | `app/api/v1/health.py` | `SanidadPage` (`/sanidad`) | [sanidad.md](./docs/modulos/sanidad.md) | Implementado |
| **Trazabilidad** (blockchain simulado) | `app/api/v1/traceability.py` | `TraceabilityPage` (`/trazabilidad`) | [trazabilidad.md](./docs/modulos/trazabilidad.md) | Implementado |
| **Monitoreo IoT** | `app/api/v1/iot.py` | Ruta `/iot` | [iot.md](./docs/modulos/iot.md) | Backend listo; frontend pendiente |
| **Frontend base** (layout, sidebar, dashboard) | — | `components/`, `pages/`, `contexts/`, `services/` | [arquitectura.md](./docs/arquitectura.md) | Implementado |
| **Pruebas + documentación** | — | — | [guia-de-inicio.md](./docs/guia-de-inicio.md) | Parcial |

---

## Tecnologías

| Capa | Tecnología |
|---|---|
| Backend | Python 3.11+ · FastAPI · SQLAlchemy 2.0 · Pydantic v2 |
| Frontend | React 19 · Vite · Bootstrap 5 (react-bootstrap) · React Router · Axios |
| Autenticación | JWT (python-jose) + bcrypt (passlib) |
| Base de datos | SQLite (desarrollo) / PostgreSQL (producción) |
| Testing | Pytest + TestClient (httpx) |
| Calidad | Ruff (linter) + isort (orden de imports) · ESLint + Prettier |

---

## Puesta en marcha rápida

Detalles y verificación de la conexión en la
[guía de inicio](./docs/guia-de-inicio.md).

**Backend** (desde `web/backend/`):

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
Copy-Item .env.example .env
.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

**Frontend** (desde `web/frontend/`):

```powershell
npm install
Copy-Item .env.example .env
npm run dev
```

Abrir <http://localhost:5173> (login en `/login`). El dev server de Vite
configura un **proxy** (`/api` → `http://localhost:8000`).

**Crear el primer admin:**

```powershell
.venv\Scripts\python.exe -m app.scripts.create_admin --username admin --email admin@example.com --password MiClave123
```

---

## Estructura del proyecto

```
EL_CAMPESINO/
├── web/            # Aplicación web
│   ├── backend/    # API FastAPI (app/ + tests/)
│   └── frontend/   # Aplicación React + Vite (src/)
├── movil/          # Aplicación móvil
│   └── android/    # App Android (Kotlin + Jetpack Compose)
└── docs/           # Documentación completa (índice, guías, API, módulos)
```

Detalle del árbol de carpetas y decisiones de arquitectura en
[arquitectura.md](./docs/arquitectura.md).

---

*Última actualización: septiembre 2026. La documentación se actualiza conforme avanza el desarrollo.*
