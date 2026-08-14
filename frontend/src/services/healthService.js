/**
 * Servicio de salud del sistema.
 *
 * Permite verificar si el backend está operativo consultando
 * el endpoint público de salud.
 */
import apiClient from './apiClient.js'

export const healthService = {
  async check() {
    const { data } = await apiClient.get('/health')
    return data
  },
}

export default healthService
