/**
 * Hook de acceso al contexto de autenticación.
 *
 * @returns {Object} Estado y acciones del contexto de autenticación.
 */
import { useContext } from 'react'
import { AuthContext } from '../contexts/AuthContext.js'

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth debe usarse dentro de un AuthProvider')
  }
  return context
}
