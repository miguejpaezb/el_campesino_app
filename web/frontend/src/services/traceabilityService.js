/**
 * Servicio de datos del módulo de trazabilidad (auditoría).
 *
 * Encapsula las llamadas a los endpoints de trazabilidad del backend: el
 * historial (cadena de hash) de una entidad y la verificación de integridad
 * de su cadena.
 */
import apiClient from './apiClient.js'

export const traceabilityService = {
  async getHistory(entityType, entityId) {
    const { data } = await apiClient.get(
      `/traceability/${entityType}/${entityId}`,
    )
    return data
  },

  async verify(entityType, entityId) {
    const { data } = await apiClient.post(
      `/traceability/verify/${entityType}/${entityId}`,
    )
    return data
  },
}

export default traceabilityService
