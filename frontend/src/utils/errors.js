/**
 * Utilidades para procesar errores de la aplicación.
 */

/**
 * Extrae un mensaje legible desde un error de Axios.
 *
 * Maneja tanto los errores con `detail` como string (errores HTTP
 * comunes) como los errores de validación 422 de FastAPI, donde
 * `detail` es un arreglo de objetos con un `msg` por campo.
 *
 * @param {Error} error - Error capturado por Axios.
 * @param {string} fallback - Mensaje por defecto si no hay detalle.
 * @returns {string} Mensaje de error legible.
 */
export function getErrorMessage(
  error,
  fallback = 'Ocurrió un error inesperado',
) {
  const detail = error?.response?.data?.detail
  if (typeof detail === 'string') {
    return detail
  }
  if (Array.isArray(detail)) {
    const messages = detail
      .map((item) => item?.msg)
      .filter((msg) => typeof msg === 'string' && msg.length > 0)
    if (messages.length > 0) {
      return messages.join('. ')
    }
  }
  return fallback
}
