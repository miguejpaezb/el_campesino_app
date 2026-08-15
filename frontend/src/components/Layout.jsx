/**
 * Layout principal de las páginas autenticadas.
 *
 * Renderiza el botón de menú móvil, el sidebar y el contenido de la ruta
 * activa, gestionando el estado de colapso y el drawer en dispositivos
 * móviles.
 *
 * @param {Object} props - Propiedades del componente.
 * @param {JSX.Element} props.children - Contenido de la página actual.
 * @returns {JSX.Element} Layout con sidebar y contenedor principal.
 */
import { useCallback, useEffect, useState } from 'react'
import Sidebar from './Sidebar.jsx'
import './Layout.css'

const SIDEBAR_STATE_KEY = 'campesino-sidebar-collapsed'

const isMobileViewport = () => window.innerWidth <= 768

function Layout({ children }) {
  const [collapsed, setCollapsed] = useState(
    () => localStorage.getItem(SIDEBAR_STATE_KEY) === 'true',
  )
  const [mobileOpen, setMobileOpen] = useState(false)

  useEffect(() => {
    const handleResize = () => {
      if (isMobileViewport()) {
        setMobileOpen(false)
        setCollapsed(false)
      } else {
        setMobileOpen(false)
      }
    }
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  const openSidebar = useCallback(() => {
    if (isMobileViewport()) {
      setMobileOpen(true)
      return
    }
    setCollapsed(false)
    localStorage.setItem(SIDEBAR_STATE_KEY, String(false))
  }, [])

  const closeSidebar = useCallback(() => {
    if (isMobileViewport()) {
      setMobileOpen(false)
      return
    }
    setCollapsed(true)
    localStorage.setItem(SIDEBAR_STATE_KEY, String(true))
  }, [])

  return (
    <div
      className={`app-layout ${
        collapsed ? 'sidebar-collapsed' : ''
      } ${mobileOpen ? 'mobile-sidebar-open' : ''}`}
    >
      <button
        className="mobile-menu-toggle"
        onClick={() => setMobileOpen(true)}
        aria-label="Abrir menú"
      >
        <img src="/icons/menu-movil.svg" alt="Menú" />
      </button>
      <Sidebar
        collapsed={collapsed}
        onOpen={openSidebar}
        onClose={closeSidebar}
        onNavigate={() => setMobileOpen(false)}
      />
      <main className="main-container">{children}</main>
    </div>
  )
}

export default Layout
