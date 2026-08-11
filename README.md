# Sistema de Gestión Avícola "El Campesino"

> **Proyecto académico** — Evidencia de aprendizaje para el Tecnólogo en **Análisis y Desarrollo de Software (ADSO)**, Ficha **3134556**.

Sistema de gestión modular para la granja avícola **"El Campesino"**. Administra lotes de aves, alimentación, sanidad, producción diaria de huevos, trazabilidad y monitoreo IoT.

---

## Estado del proyecto

| Módulo | Backend | Estado |
|---|---|---|
| **Autenticación (usuarios + JWT)** | `app/api/v1/auth.py` | Implementado |
| **Inventario de Aves (lotes)** | `app/api/v1/lots.py` | Implementado |
| **Producción Diaria (huevos)** | `app/api/v1/production.py` | Implementado |
| **Alimentación** | `app/api/v1/feeding.py` | Implementado |
| **Sanidad** (vacunas, enfermedades, mortalidad) | — | Pendiente |
| **Trazabilidad** (blockchain simulado) | — | Pendiente |
| **Monitoreo IoT** | — | Pendiente |
| **Pruebas + documentación** | — | Parcial |

---

## Tecnologías

| Capa | Tecnología |
|---|---|
| Backend | Python 3.11+ · FastAPI · SQLAlchemy 2.0 · Pydantic v2 |
| Autenticación | JWT (python-jose) + bcrypt (passlib) |
| Base de datos | SQLite (desarrollo) / PostgreSQL (producción) |
| Testing | Pytest + TestClient (httpx) |
| Calidad | Ruff (linter) + isort (orden de imports) |

---

## Requisitos previos

- Python 3.11+ (probado con 3.14)
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

- Documentación interactiva (Swagger): <http://127.0.0.1:8000/docs>
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

---

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
│   │       └── feeding.py        # Alimentación
│   ├── core/                     # Configuración, seguridad y constantes
│   │   ├── config.py             # Settings desde .env
│   │   ├── database.py           # Engine, sesión y Base de SQLAlchemy
│   │   ├── security.py           # JWT + bcrypt + dependencia de usuario
│   │   └── constants.py          # Constantes del ciclo productivo
│   ├── models/                   # Modelos ORM (SQLAlchemy 2.0)
│   │   ├── user.py
│   │   ├── bird_lot.py
│   │   ├── egg_production.py
│   │   └── feeding.py
│   ├── schemas/                  # Schemas Pydantic (DTOs)
│   ├── services/                 # Lógica de negocio
│   ├── repositories/             # Acceso a datos (CRUD)
│   └── main.py                   # Punto de entrada
├── tests/                        # Pruebas unitarias y de integración
├── requirements.txt
├── .env.example
└── pytest.ini
```

La lógica de dominio de lotes se adaptó del **ejercicio en clase**: las clases `LoteGallinas`, `RegistroPosturas`, `RegistroAlimentacion` y `LoteService` fueron migradas a modelos ORM y servicios de FastAPI.

---

## API disponible (endpoints)

Todas las rutas usan el prefijo `/api/v1`. Los endpoints de lotes, producción y alimentación requieren un token JWT (`Authorization: Bearer <token>`).

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

---

## Reglas de negocio implementadas (heredadas del ejercicio en clase)

- Un lote inicia en la **semana 16** (semana de compra) y arranca la postura en la **semana 28**.
- **Producción**: solo se registra si el lote está activo y en etapa de postura (semana ≥ 28).
- **Alimentación**: solo se registra si el lote está activo.
- **Evaluación** (semana 90): con porcentaje de postura < 80% el lote se descarta; con ≥ 80% se extienden 30 semanas.

---

*Última actualización: agosto 2026. El documento se actualiza conforme avanza el desarrollo.*
