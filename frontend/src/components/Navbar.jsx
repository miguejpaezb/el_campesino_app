/**
 * Barra de navegación superior con el nombre de la aplicación
 * y el menú de módulos.
 *
 * @param {Object} props - Propiedades del componente.
 * @param {string} props.brand - Nombre de la aplicación a mostrar.
 * @returns {JSX.Element} Navbar de Bootstrap.
 */
import { Navbar, Nav, Container, Button } from 'react-bootstrap'
import { NavLink } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth.js'

const MODULES = [
  { label: 'Inicio', to: '/' },
  { label: 'Lotes', to: '/lotes' },
  { label: 'Alimentación', to: '/alimentacion' },
  { label: 'Sanidad', to: '/sanidad' },
  { label: 'Producción', to: '/produccion' },
  { label: 'Trazabilidad', to: '/trazabilidad' },
  { label: 'Monitoreo IoT', to: '/iot' },
]

function AppNavbar({ brand = 'El Campesino' }) {
  const { user, logout } = useAuth()

  return (
    <Navbar bg="dark" variant="dark" expand="lg" sticky="top">
      <Container>
        <Navbar.Brand href="/">{brand}</Navbar.Brand>
        <Navbar.Toggle aria-controls="main-navbar" />
        <Navbar.Collapse id="main-navbar">
          <Nav className="me-auto">
            {MODULES.map((mod) => (
              <Nav.Link key={mod.to} as={NavLink} to={mod.to}>
                {mod.label}
              </Nav.Link>
            ))}
          </Nav>
          {user && (
            <div className="d-flex align-items-center gap-2">
              <span className="navbar-text text-light me-2">
                {user.full_name}
              </span>
              <Button variant="outline-light" size="sm" onClick={logout}>
                Salir
              </Button>
            </div>
          )}
        </Navbar.Collapse>
      </Container>
    </Navbar>
  )
}

export default AppNavbar
