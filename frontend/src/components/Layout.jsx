/**
 * Layout principal de las páginas autenticadas.
 *
 * Renderiza la barra de navegación y el contenido de la ruta activa.
 *
 * @param {Object} props - Propiedades del componente.
 * @param {JSX.Element} props.children - Contenido de la página actual.
 * @returns {JSX.Element} Layout con navbar y contenedor.
 */
import { Container } from 'react-bootstrap'
import AppNavbar from './Navbar.jsx'

function Layout({ children }) {
  return (
    <>
      <AppNavbar />
      <Container className="py-4">{children}</Container>
    </>
  )
}

export default Layout
