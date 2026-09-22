# Módulos

Documentación funcional de cada módulo del sistema: propósito, comportamiento
del frontend, endpoints que utiliza y reglas de negocio aplicables.

> La app móvil (Android) reutiliza los mismos endpoints; por ahora solo
> implementa el módulo de **autenticación** (ver
> [autenticacion.md](./autenticacion.md#app-movil)).

| Módulo | Ruta (frontend) | Documento |
|---|---|---|
| Autenticación (usuarios + JWT) | `/login` | [autenticacion.md](./autenticacion.md) |
| Dashboard | `/` | [dashboard.md](./dashboard.md) |
| Inventario de Aves (lotes) | `/lotes` | [lotes.md](./lotes.md) |
| Producción Diaria (huevos) | `/produccion` | [produccion.md](./produccion.md) |
| Alimentación (incl. insumos y resumen) | `/alimentacion` | [alimentacion.md](./alimentacion.md) |
| Sanidad (vacunas, mortalidad, enfermedades) | `/sanidad` | [sanidad.md](./sanidad.md) |
| Trazabilidad (auditoría) | `/trazabilidad` | [trazabilidad.md](./trazabilidad.md) |
| Monitoreo IoT | `/iot` | [iot.md](./iot.md) |

---

← [Volver al índice de la documentación](../README.md)
