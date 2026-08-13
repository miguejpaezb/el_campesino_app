/**
 * Proveedor del contexto de autenticación.
 *
 * Expone el estado del usuario, el token y las acciones de login/logout
 * a toda la aplicación.
 */
import { useCallback, useEffect, useMemo, useState } from 'react'
import PropTypes from 'prop-types'
import { authService } from '../services/authService.js'
import { AuthContext } from './AuthContext.js'

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(() =>
    Boolean(localStorage.getItem('token')),
  )

  const login = useCallback(async (credentials) => {
    const { access_token: token } = await authService.login(credentials)
    localStorage.setItem('token', token)
    const me = await authService.getMe()
    setUser(me)
    return me
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem('token')
    setUser(null)
  }, [])

  useEffect(() => {
    if (!localStorage.getItem('token')) {
      return
    }
    let mounted = true
    authService
      .getMe()
      .then((me) => {
        if (mounted) setUser(me)
      })
      .catch(() => {
        if (mounted) localStorage.removeItem('token')
      })
      .finally(() => {
        if (mounted) setLoading(false)
      })
    return () => {
      mounted = false
    }
  }, [])

  const value = useMemo(
    () => ({ user, loading, login, logout }),
    [user, loading, login, logout],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

AuthProvider.propTypes = {
  children: PropTypes.node.isRequired,
}

export default AuthProvider
