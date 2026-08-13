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
import { Alert, Button, Card, Container, Form } from 'react-bootstrap'
import { Navigate, useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth.js'
import { getErrorMessage } from '../utils/errors.js'

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
    <Container className="d-flex justify-content-center align-items-center vh-100">
      <Card style={{ width: '100%', maxWidth: 400 }}>
        <Card.Body>
          <Card.Title className="text-center mb-3">
            El Campesino - Iniciar sesión
          </Card.Title>
          {error && <Alert variant="danger">{error}</Alert>}
          <Form onSubmit={handleSubmit}>
            <Form.Group className="mb-3" controlId="login-username">
              <Form.Label>Usuario</Form.Label>
              <Form.Control
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                autoFocus
              />
            </Form.Group>
            <Form.Group className="mb-3" controlId="login-password">
              <Form.Label>Contraseña</Form.Label>
              <Form.Control
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </Form.Group>
            <Button
              type="submit"
              variant="primary"
              className="w-100"
              disabled={submitting}
            >
              {submitting ? 'Ingresando...' : 'Ingresar'}
            </Button>
          </Form>
        </Card.Body>
      </Card>
    </Container>
  )
}

export default LoginPage
