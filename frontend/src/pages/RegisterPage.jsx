/**
 * Página de registro de usuario.
 *
 * Valida en tiempo real la coincidencia de contraseñas y la longitud
 * mínima, crea la cuenta contra el backend y redirige al login.
 *
 * @returns {JSX.Element} Formulario de registro.
 */
import { useEffect, useRef, useState } from 'react'
import { Alert, Button, Form } from 'react-bootstrap'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { authService } from '../services/authService.js'
import { useAuth } from '../hooks/useAuth.js'
import { getErrorMessage } from '../utils/errors.js'
import './RegisterPage.css'

const MIN_PASSWORD_LENGTH = 8
const MIN_USERNAME_LENGTH = 3
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

function RegisterPage() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [fullName, setFullName] = useState('')
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [terms, setTerms] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)
  const [submitting, setSubmitting] = useState(false)
  const redirectTimeout = useRef(null)

  const fullNameValid = fullName.trim().length > 0
  const usernameValid =
    username.length >= MIN_USERNAME_LENGTH && username.length <= 50
  const emailValid = EMAIL_REGEX.test(email)
  const passwordTooShort =
    password.length > 0 && password.length < MIN_PASSWORD_LENGTH
  const confirmTouched = confirmPassword.length > 0
  const passwordsMatch = confirmTouched && password === confirmPassword
  const canSubmit =
    fullNameValid &&
    usernameValid &&
    emailValid &&
    !passwordTooShort &&
    passwordsMatch &&
    terms &&
    !submitting

  useEffect(() => {
    return () => {
      if (redirectTimeout.current) {
        clearTimeout(redirectTimeout.current)
      }
    }
  }, [])

  if (user) {
    return <Navigate to="/" replace />
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError(null)
    setSubmitting(true)
    try {
      await authService.register({
        username,
        email,
        password,
        full_name: fullName,
      })
      setSuccess(
        'Cuenta creada correctamente. Serás redirigido al inicio de sesión.',
      )
      redirectTimeout.current = setTimeout(() => {
        navigate('/login', { replace: true })
      }, 2500)
    } catch (err) {
      setError(getErrorMessage(err, 'No se pudo crear la cuenta'))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="register-page">
      <div className="column form">
        <div className="logo">
          <img src="/pluma.svg" alt="Logo El Campesino" />
          <h1>El Campesino</h1>
        </div>
        <div className="register-form">
          <h2>Crea tu cuenta</h2>
          {error && (
            <Alert variant="danger" className="mb-0">
              {error}
            </Alert>
          )}
          {success && (
            <Alert variant="success" className="mb-0">
              {success}{' '}
              <Link to="/login" className="alert-link">
                Ir a Iniciar Sesión
              </Link>
            </Alert>
          )}
          <Form onSubmit={handleSubmit} noValidate>
            <Form.Control
              type="text"
              className="register-control mb-2"
              placeholder="Nombre Completo"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              required
              isInvalid={fullName.length > 0 && !fullNameValid}
              isValid={fullName.length > 0 && fullNameValid}
            />
            <Form.Control.Feedback type="invalid" className="small">
              El nombre completo es obligatorio.
            </Form.Control.Feedback>
            <Form.Control
              type="text"
              className="register-control mb-2"
              placeholder="Nombre de Usuario"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              minLength={MIN_USERNAME_LENGTH}
              maxLength={50}
              isInvalid={username.length > 0 && !usernameValid}
              isValid={username.length > 0 && usernameValid}
            />
            <Form.Control.Feedback type="invalid" className="small">
              El nombre de usuario debe tener al menos {MIN_USERNAME_LENGTH}{' '}
              caracteres.
            </Form.Control.Feedback>
            <Form.Control
              type="email"
              className="register-control mb-2"
              placeholder="Correo Electrónico"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              isInvalid={email.length > 0 && !emailValid}
              isValid={email.length > 0 && emailValid}
            />
            <Form.Control.Feedback type="invalid" className="small">
              Ingresa un correo electrónico válido (ej: usuario@dominio.com).
            </Form.Control.Feedback>
            <div className="passwords">
              <div className="field">
                <Form.Control
                  type="password"
                  className="register-control"
                  placeholder="Contraseña"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  isInvalid={passwordTooShort}
                  isValid={!passwordTooShort && password.length > 0}
                />
                <Form.Control.Feedback type="invalid" className="small">
                  La contraseña debe tener al menos {MIN_PASSWORD_LENGTH}{' '}
                  caracteres.
                </Form.Control.Feedback>
              </div>
              <div className="field">
                <Form.Control
                  type="password"
                  className="register-control"
                  placeholder="Confirmar Contraseña"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                  isInvalid={confirmTouched && !passwordsMatch}
                  isValid={confirmTouched && passwordsMatch}
                />
                <Form.Control.Feedback type="invalid" className="small">
                  Las contraseñas no coinciden.
                </Form.Control.Feedback>
                <Form.Control.Feedback className="small">
                  Las contraseñas coinciden.
                </Form.Control.Feedback>
              </div>
            </div>
            <div className="terms-policy">
              <Form.Check
                type="checkbox"
                id="terms-policy"
                checked={terms}
                onChange={(e) => setTerms(e.target.checked)}
                required
              />
              <label htmlFor="terms-policy">
                Acepto los <a href="#">Términos de servicio</a> y la{' '}
                <a href="#">Política de privacidad</a>.
              </label>
            </div>
            <Button
              type="submit"
              className="register-button"
              disabled={!canSubmit}
            >
              {submitting ? 'Registrando...' : 'Registrarse'}
            </Button>
          </Form>
        </div>
        <p>
          ¿Ya tienes una cuenta? <Link to="/login">Iniciar Sesión</Link>
        </p>
      </div>

      <div className="column info">
        <div className="system-status">
          <div className="status"></div>
          <span>Estado del sistema: Óptimo</span>
        </div>
        <div className="info-system">
          <h2>
            Moldea el futuro de tu
            <br /> empresa avícola.
          </h2>
          <p>
            Únase a miles de productores modernos que optimizan la distribución
            de piensos, automatizan los umbrales climáticos y predicen con
            precisión la producción agrícola diaria.
          </p>
        </div>
      </div>
    </div>
  )
}

export default RegisterPage
