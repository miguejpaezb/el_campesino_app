/**
 * Página de inicio de sesión.
 *
 * Valida credenciales contra el backend y redirige al dashboard
 * una vez autenticado.
 *
 * @param {Object} props - Propiedades del componente.
 * @param {Function} [props.onLoginSuccess] - Callback tras iniciar sesión.
 * @returns {JSX.Element} Formulario de login.
 */
import { useState } from 'react'
import { Alert, Button, Form } from 'react-bootstrap'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth.js'
import { getErrorMessage } from '../utils/errors.js'
import './LoginPage.css'

function LoginPage({ onLoginSuccess }) {
  const { user, login } = useAuth()
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)
  const [submitting, setSubmitting] = useState(false)

  if (user) {
    return <Navigate to="/" replace />
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError(null)
    setSubmitting(true)
    try {
      await login({ username, password })
      if (onLoginSuccess) onLoginSuccess()
      navigate('/', { replace: true })
    } catch (err) {
      setError(getErrorMessage(err, 'No se pudo iniciar sesión'))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="login-page">
      <div className="column form">
        <div className="logo">
          <img src="/pluma.svg" alt="Logo El Campesino" />
          <h1>El Campesino</h1>
        </div>
        <div className="login-form">
          <h2>Iniciar Sesión</h2>
          {error && (
            <Alert variant="danger" className="mb-0">
              {error}
            </Alert>
          )}
          <Form onSubmit={handleSubmit}>
            <Form.Control
              type="text"
              className="login-control mb-2"
              placeholder="Nombre de Usuario"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              autoFocus
            />
            <Form.Control
              type="password"
              className="login-control mb-2"
              placeholder="Contraseña"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            <Button
              type="submit"
              className="login-button"
              disabled={submitting}
            >
              {submitting ? 'Ingresando...' : 'Ingresar'}
            </Button>
          </Form>
          <a href="#" className="forgot-link">
            Olvidé mi contraseña
          </a>
        </div>
        <p>
          ¿No tiene una cuenta? <Link to="/register">Crear cuenta</Link>
        </p>
      </div>

      <div className="column info">
        <div className="system-status">
          <div className="status"></div>
          <span>Estado del sistema: Óptimo</span>
        </div>
        <div className="info-system">
          <h2>Una avicultura más inteligente comienza aquí.</h2>
          <p>
            Supervise el bienestar de sus aves, automatice el control climático
            y realice un seguimiento de la producción de huevos con un panel de
            control de alta precisión diseñado para productores con visión de
            futuro.
          </p>
        </div>
      </div>
    </div>
  )
}

export default LoginPage
