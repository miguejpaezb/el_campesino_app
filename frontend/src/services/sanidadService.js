/**
 * Servicio de datos del módulo de sanidad.
 *
 * Encapsula las llamadas a los endpoints de sanidad del backend por lote:
 * vacunas, mortalidad (con sus porcentajes) y enfermedades (registro,
 * actualización de tratamiento y resolución).
 */
import apiClient from './apiClient.js'

export const sanidadService = {
  // ============================ Vacunas ============================

  async listVaccinations(lotId) {
    const { data } = await apiClient.get(`/lots/${lotId}/vaccinations`)
    return data
  },

  async registerVaccination(lotId, payload) {
    const { data } = await apiClient.post(
      `/lots/${lotId}/vaccinations`,
      payload,
    )
    return data
  },

  // ============================ Mortalidad ============================

  async listMortality(lotId) {
    const { data } = await apiClient.get(`/lots/${lotId}/mortality`)
    return data
  },

  async registerMortality(lotId, payload) {
    const { data } = await apiClient.post(`/lots/${lotId}/mortality`, payload)
    return data
  },

  async mortalityStats(lotId) {
    const { data } = await apiClient.get(`/lots/${lotId}/mortality/stats`)
    return data
  },

  // ============================ Enfermedades ============================

  async listDiseases(lotId) {
    const { data } = await apiClient.get(`/lots/${lotId}/diseases`)
    return data
  },

  async registerDisease(lotId, payload) {
    const { data } = await apiClient.post(`/lots/${lotId}/diseases`, payload)
    return data
  },

  async updateDisease(lotId, diseaseId, payload) {
    const { data } = await apiClient.put(
      `/lots/${lotId}/diseases/${diseaseId}`,
      payload,
    )
    return data
  },

  async resolveDisease(lotId, diseaseId) {
    const { data } = await apiClient.post(
      `/lots/${lotId}/diseases/${diseaseId}/resolve`,
    )
    return data
  },
}

export default sanidadService
