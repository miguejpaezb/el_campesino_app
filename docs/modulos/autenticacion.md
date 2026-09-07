# Módulo de Autenticación (usuarios + JWT)

## Propósito

Gestionar el acceso al sistema mediante credenciales. El backend emite tokens
JWT firmados y asigna **roles** (`admin`, `operario`, `veterinario`) que
controlan los permisos (el registro de usuarios y su listado son exclusivos de
`admin`).

## Backend

- Emisión y validación de JWT con python-jose.
- Contraseñas con hash bcrypt (passlib).
- El registro público fue eliminado: las cuentas solo las crea un usuario con
  rol `admin` (vía API o desde el frontend).

## Frontend

- `LoginPage` (`/login`) llama a `POST /api/v1/auth/login`, guarda el
  `access_token` en `localStorage` y obtiene el usuario con
  `GET /api/v1/auth/me`.
- `AuthContext` expone `user`, `loading`, `login` y `logout`; restaura la
  sesión al recargar la página validando el token con `/auth/me`. Si el token
  falta o es inválido, `ProtectedRoute` redirige a `/login`.
- `ProtectedRoute` envuelve las rutas protegidas y muestra un spinner mientras
  se valida el token.

## Endpoints que utiliza

Ver [Autenticación](../api.md#autenticacion) en la referencia de la API.

---

← [Índice de módulos](./README.md) · ← [Índice general](../README.md)
