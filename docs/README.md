# Documentación — Sistema de Gestión Avícola "El Campesino"

Bienvenido a la documentación del proyecto. Este índice organiza toda la
información en documentos cortos y navegables para que encuentres rápido lo
que busques.

> **Proyecto académico** — Evidencia de aprendizaje para el Tecnólogo en
> **Análisis y Desarrollo de Software (ADSO)**, Ficha **3134556**.

## Cómo navegar

- **¿Empiezas desde cero?** → [Guía de inicio](./guia-de-inicio.md)
- **¿Buscas un endpoint?** → [Referencia de la API](./api.md)
- **¿Quieres entender el código?** → [Arquitectura](./arquitectura.md)
- **¿Consultas una regla de negocio?** → [Reglas de negocio](./reglas-de-negocio.md)

## Guías

| Documento | Contenido |
|---|---|
| [Guía de inicio](./guia-de-inicio.md) | Requisitos, puesta en marcha (backend y frontend), creación del admin inicial, verificación de la conexión y calidad del código |

## Arquitectura

| Documento | Contenido |
|---|---|
| [Arquitectura](./arquitectura.md) | Arquitectura en capas del backend, árbol de carpetas (backend y frontend), decisiones técnicas y patrones del frontend |

## Referencia

| Documento | Contenido |
|---|---|
| [Reglas de negocio](./reglas-de-negocio.md) | Reglas heredadas del ejercicio en clase (ciclo productivo, producción, alimentación, sanidad) y rangos seguros de los sensores IoT |
| [API disponible](./api.md) | Referencia de todos los endpoints por módulo y ejemplo de uso rápido con Postman |

## Módulos

| Módulo | Ruta (frontend) | Documento |
|---|---|---|
| Autenticación (usuarios + JWT) | `/login` | [autenticacion.md](./modulos/autenticacion.md) |
| Dashboard | `/` | [dashboard.md](./modulos/dashboard.md) |
| Inventario de Aves (lotes) | `/lotes` | [lotes.md](./modulos/lotes.md) |
| Producción Diaria (huevos) | `/produccion` | [produccion.md](./modulos/produccion.md) |
| Alimentación (incl. insumos) | `/alimentacion` | [alimentacion.md](./modulos/alimentacion.md) |
| Sanidad | `/sanidad` | [sanidad.md](./modulos/sanidad.md) |
| Trazabilidad | `/trazabilidad` | [trazabilidad.md](./modulos/trazabilidad.md) |
| Monitoreo IoT | `/iot` | [iot.md](./modulos/iot.md) |

## Estado del proyecto

El resumen de lo implementado (backend/frontend) se mantiene en el
[README principal](../README.md).
