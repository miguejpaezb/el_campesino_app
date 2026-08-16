/**
 * Servicio de datos del módulo de producción diaria.
 *
 * Encapsula las llamadas a los endpoints de producción del backend: listado
 * por fechas, registro (creación o merge), total de huevos, promedio semanal
 * de postura y porcentaje de postura.
 */
import apiClient from './apiClient.js'

export const productionService = {
  async getProduction(lotId, from, to) {
    const { data } = await apiClient.get(`/lots/${lotId}/production`, {
      params: { from, to },
    })
    return data
  },

  async registerProduction(lotId, payload) {
    const { data } = await apiClient.post(`/lots/${lotId}/production`, payload)
    return data
  },

  async mergeProduction(lotId, payload) {
    const { data } = await apiClient.post(
      `/lots/${lotId}/production`,
      payload,
      {
        params: { merge: true },
      },
    )
    return data
  },

  async getTotal(lotId) {
    const { data } = await apiClient.get(`/lots/${lotId}/production/total`)
    return data.total_eggs
  },

  async getAverage(lotId) {
    const { data } = await apiClient.get(`/lots/${lotId}/production/average`)
    return data.average_weekly_production
  },

  async getPercentage(lotId) {
    const { data } = await apiClient.get(`/lots/${lotId}/production/percentage`)
    return data.laying_percentage
  },
}

export default productionService
