/**
 * Servicio de autenticación.
 *
 * Encapsula las llamadas a los endpoints de auth del backend.
 */
import apiClient from './apiClient.js'

export const authService = {
  async login({ username, password }) {
    const { data } = await apiClient.post('/auth/login', { username, password })
    return data
  },

  async register(payload) {
    const { data } = await apiClient.post('/auth/register', payload)
    return data
  },

  async getMe() {
    const { data } = await apiClient.get('/auth/me')
    return data
  },
}
