/**
 * Servicio de datos del módulo de inventario de aves (lotes).
 *
 * Encapsula las llamadas a los endpoints de lotes del backend: listado,
 * creación, actualización, descarte, avance de semana, evaluación y
 * resumen productivo.
 */
import apiClient from './apiClient.js'

export const lotService = {
  async getLots() {
    const { data } = await apiClient.get('/lots/')
    return data
  },

  async getLot(lotId) {
    const { data } = await apiClient.get(`/lots/${lotId}`)
    return data
  },

  async createLot(payload) {
    const { data } = await apiClient.post('/lots/', payload)
    return data
  },

  async updateLot(lotId, payload) {
    const { data } = await apiClient.put(`/lots/${lotId}`, payload)
    return data
  },

  async discardLot(lotId, reason) {
    const { data } = await apiClient.delete(`/lots/${lotId}`, {
      data: { reason },
    })
    return data
  },

  async advanceWeek(lotId) {
    const { data } = await apiClient.post(`/lots/${lotId}/advance-week`)
    return data
  },

  async evaluateLot(lotId) {
    const { data } = await apiClient.post(`/lots/${lotId}/evaluate`)
    return data
  },

  async getSummary(lotId) {
    const { data } = await apiClient.get(`/lots/${lotId}/summary`)
    return data
  },
}

export default lotService
