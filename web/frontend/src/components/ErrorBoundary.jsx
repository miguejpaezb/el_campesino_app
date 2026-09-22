/**
 * Límite de errores global.
 *
 * Captura errores de renderizado para evitar que la aplicación
 * quede en pantalla en blanco y muestra un mensaje con opción de
 * recargar.
 *
 * @param {Object} props - Propiedades del componente.
 * @param {JSX.Element} props.children - Contenido protegido.
 * @returns {JSX.Element} Contenido o pantalla de error.
 */
import { Component } from 'react'
import { Button, Container } from 'react-bootstrap'
import PropTypes from 'prop-types'

class ErrorBoundary extends Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError() {
    return { hasError: true }
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error capturado por el ErrorBoundary:', error, errorInfo)
  }

  handleReload = () => {
    window.location.reload()
  }

  render() {
    if (this.state.hasError) {
      return (
        <Container className="d-flex flex-column align-items-center justify-content-center vh-100 text-center">
          <h1 className="mb-3">Algo salió mal</h1>
          <p className="text-muted mb-4">
            Ocurrió un error inesperado. Vuelve a cargar la página para
            continuar.
          </p>
          <Button variant="primary" onClick={this.handleReload}>
            Recargar página
          </Button>
        </Container>
      )
    }
    return this.props.children
  }
}

ErrorBoundary.propTypes = {
  children: PropTypes.node.isRequired,
}

export default ErrorBoundary
