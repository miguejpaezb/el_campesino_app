/**
 * Extrae un mensaje legible desde un error de Axios.
 *
 * @param {Error} error - Error capturado por Axios.
 * @param {string} fallback - Mensaje por defecto si no hay detalle.
 * @returns {string} Mensaje de error legible.
 */
export function getErrorMessage(
  error,
  fallback = 'Ocurrió un error inesperado',
) {
  return error?.response?.data?.detail || fallback
}
