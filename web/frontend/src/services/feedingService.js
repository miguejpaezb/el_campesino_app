/**
 * Servicio de datos del módulo de alimentación.
 *
 * Encapsula las llamadas a los endpoints de alimentación del backend:
 * listado de registros por lote, registro de un suministro, total de kilos
 * consumidos y costo total.
 */
import apiClient from './apiClient.js'

export const feedingService = {
  async getFeeding(lotId) {
    const { data } = await apiClient.get(`/lots/${lotId}/feeding`)
    return data
  },

  async registerFeeding(lotId, payload) {
    const { data } = await apiClient.post(`/lots/${lotId}/feeding`, payload)
    return data
  },

  async getTotalKg(lotId) {
    const { data } = await apiClient.get(`/lots/${lotId}/feeding/total`)
    return data.total_feed_kg
  },

  async getTotalCost(lotId) {
    const { data } = await apiClient.get(`/lots/${lotId}/feeding/cost`)
    return data.total_feed_cost
  },
}

export default feedingService
