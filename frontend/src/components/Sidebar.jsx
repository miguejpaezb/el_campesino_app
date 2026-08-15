/**
 * Barra lateral de navegación.
 *
 * Replica el comportamiento del dashboard de referencia: menú con iconos,
 * colapso persistido en localStorage y drawer móvil.
 *
 * @param {Object} props - Propiedades del componente.
 * @param {boolean} props.collapsed - Si el sidebar está colapsado en escritorio.
 * @param {Function} props.onOpen - Expande/abre el sidebar.
 * @param {Function} props.onClose - Colapsa/cierra el sidebar.
 * @param {Function} props.onNavigate - Cierra el drawer móvil al navegar.
 * @returns {JSX.Element} Sidebar de navegación.
 */
import { useEffect, useRef, useState } from 'react'
import { createPortal } from 'react-dom'
import { NavLink } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth.js'

const USER_MENU_WIDTH = 375
const MOBILE_MENU_MARGIN = 15

const MENU_ITEMS = [
  { label: 'Dashboard', to: '/', icon: 'Dashboard.svg' },
  { label: 'Inventario Aves', to: '/lotes', icon: 'INVENTARIO_AVES.svg' },
  { label: 'Alimento', to: '/alimentacion', icon: 'ALIMENTO.svg' },
  { label: 'Sanidad', to: '/sanidad', icon: 'SANIDAD.svg' },
  {
    label: 'Producción Diaria',
    to: '/produccion',
    icon: 'PRODUCCION_DIARIA.svg',
  },
  { label: 'Trazabilidad', to: '/trazabilidad', icon: 'TRAZABILIDAD.svg' },
  { label: 'Monitoreo IoT', to: '/iot', icon: 'MONITOREO_IOT.svg' },
  { label: 'Usuarios', to: '/usuarios', icon: 'USUARIOS.svg' },
]

function Sidebar({ collapsed, onOpen, onClose, onNavigate }) {
  const { user, logout } = useAuth()
  const [menuOpen, setMenuOpen] = useState(false)
  const [menuPos, setMenuPos] = useState({ left: 0, bottom: 0 })
  const userMenuRef = useRef(null)
  const userBtnRef = useRef(null)
  const initial = user?.full_name?.charAt(0).toUpperCase() || 'A'
  const displayName = user?.full_name || user?.username || ''

  useEffect(() => {
    const handleClickOutside = (event) => {
      const isInsideMenu = userMenuRef.current?.contains(event.target)
      const isInsideButton = userBtnRef.current?.contains(event.target)
      if (!isInsideMenu && !isInsideButton) {
        setMenuOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const toggleMenu = () => {
    if (menuOpen) {
      setMenuOpen(false)
      return
    }
    const rect = userBtnRef.current?.getBoundingClientRect()
    if (window.innerWidth <= 768) {
      setMenuPos({
        left: MOBILE_MENU_MARGIN,
        bottom: rect ? window.innerHeight - rect.top + 12 : 0,
      })
    } else if (rect) {
      setMenuPos({
        left: Math.max(8, rect.right - USER_MENU_WIDTH),
        bottom: window.innerHeight - rect.top + 12,
      })
    }
    setMenuOpen(true)
  }

  return (
    <aside className={`sidebar ${collapsed ? 'collapsed' : ''}`}>
      <div className="header">
        <div className="logo">
          <img
            className="isotipo"
            src="/pluma.svg"
            alt="Logo El Campesino"
            onClick={onOpen}
          />
          <h2 className="app-name">El Campesino</h2>
        </div>
        <button onClick={onClose} aria-label="Cerrar menú">
          <img src="/icons/arrow.svg" alt="<" />
        </button>
      </div>

      <div className="menu">
        {MENU_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) => `btn ${isActive ? 'active' : ''}`}
            onClick={onNavigate}
          >
            <img src={`/icons/${item.icon}`} alt="" className="icon" />
            <span>{item.label}</span>
          </NavLink>
        ))}
      </div>

      <div className="user-settings">
        <div
          ref={userBtnRef}
          className={`btn user ${menuOpen ? 'active' : ''}`}
          onClick={toggleMenu}
          role="button"
          tabIndex={0}
        >
          <div className="avatar">{initial}</div>
          <span className="name-user">{user?.full_name}</span>
        </div>
      </div>

      {menuOpen &&
        createPortal(
          <div
            className="user-menu"
            style={{ left: menuPos.left, bottom: menuPos.bottom }}
            ref={userMenuRef}
          >
            <p className="user-menu-email">{user?.email}</p>
            <div className="user-menu-avatar">{initial}</div>
            <p className="user-menu-greeting">¡Hola, {displayName}!</p>
            <div className="user-menu-actions">
              <NavLink
                to="/cuenta"
                className="btn btn-outline"
                onClick={() => {
                  setMenuOpen(false)
                  onNavigate()
                }}
              >
                Administrar cuenta
              </NavLink>
              <button className="btn btn-danger" onClick={logout}>
                Cerrar sesión
              </button>
            </div>
            <div className="user-menu-footer">
              <a href="#">Políticas de privacidad</a>
              <span>-</span>
              <a href="#">Condiciones de Servicio</a>
            </div>
          </div>,
          document.body,
        )}
    </aside>
  )
}

export default Sidebar
