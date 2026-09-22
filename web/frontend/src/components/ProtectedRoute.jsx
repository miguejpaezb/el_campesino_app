/**
 * Guardia de rutas autenticadas.
 *
 * Redirige a /login si no hay usuario autenticado. Mientras se
 * valida el token, muestra un indicador de carga.
 *
 * @param {Object} props - Propiedades del componente.
 * @param {JSX.Element} props.children - Contenido protegido.
 * @returns {JSX.Element} Contenido o redirección.
 */
import { Navigate } from 'react-router-dom'
import { Spinner } from 'react-bootstrap'
import PropTypes from 'prop-types'
import { useAuth } from '../hooks/useAuth.js'

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div className="d-flex justify-content-center align-items-center vh-100">
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Cargando...</span>
        </Spinner>
      </div>
    )
  }

  if (!user) {
    return <Navigate to="/login" replace />
  }

  return children
}

ProtectedRoute.propTypes = {
  children: PropTypes.node.isRequired,
}

export default ProtectedRoute
