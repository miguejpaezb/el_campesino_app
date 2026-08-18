/**
 * Servicio de datos del inventario de insumos (alimentos).
 *
 * Encapsula las llamadas a los endpoints de inventario del backend:
 * listado, creación, actualización, ingreso de stock, suspensión y
 * eliminación de tipos de alimento.
 */
import apiClient from './apiClient.js'

export const feedStockService = {
  async getFeedStock(search) {
    const { data } = await apiClient.get('/feed-stock', {
      params: { search: search || undefined },
    })
    return data
  },

  async createFeedType(payload) {
    const { data } = await apiClient.post('/feed-stock', payload)
    return data
  },

  async updateFeedType(feedTypeId, payload) {
    const { data } = await apiClient.put(`/feed-stock/${feedTypeId}`, payload)
    return data
  },

  async addStock(feedTypeId, payload) {
    const { data } = await apiClient.post(
      `/feed-stock/${feedTypeId}/stock`,
      payload,
    )
    return data
  },

  async toggleSuspend(feedTypeId) {
    const { data } = await apiClient.post(`/feed-stock/${feedTypeId}/suspend`)
    return data
  },

  async deleteFeedType(feedTypeId) {
    await apiClient.delete(`/feed-stock/${feedTypeId}`)
  },
}

export default feedStockService
