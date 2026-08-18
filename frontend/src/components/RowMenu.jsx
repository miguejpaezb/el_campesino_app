/**
 * Menú desplegable por fila reutilizable.
 *
 * Muestra un botón con el icono de submenú que, al pulsarlo, abre un menú
 * posicionado cerca del botón con las acciones indicadas. Se cierra con un
 * clic fuera, al hacer scroll o al seleccionar una opción.
 *
 * @param {Object} props - Propiedades del componente.
 * @param {Array<{label: string, onClick: Function, danger?: boolean, disabled?: boolean}>} props.items - Opciones del menú.
 * @param {string} [props.label] - Etiqueta accesible del botón.
 * @returns {JSX.Element} Botón con menú desplegable.
 */
import { useEffect, useRef, useState } from 'react'
import { createPortal } from 'react-dom'
import './RowMenu.css'

function RowMenu({ items, label = 'Acciones' }) {
  const [open, setOpen] = useState(false)
  const [pos, setPos] = useState({ top: 0, right: 0 })
  const menuRef = useRef(null)
  const btnRef = useRef(null)

  useEffect(() => {
    const handleClickOutside = (event) => {
      const isInsideMenu = menuRef.current?.contains(event.target)
      const isInsideButton = btnRef.current?.contains(event.target)
      if (!isInsideMenu && !isInsideButton) {
        setOpen(false)
      }
    }
    const handleScroll = () => setOpen(false)
    document.addEventListener('mousedown', handleClickOutside)
    document.addEventListener('scroll', handleScroll, true)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
      document.removeEventListener('scroll', handleScroll, true)
    }
  }, [])

  const toggle = () => {
    if (open) {
      setOpen(false)
      return
    }
    const rect = btnRef.current?.getBoundingClientRect()
    if (!rect) return
    setPos({
      top: rect.bottom + 6,
      right: Math.max(8, window.innerWidth - rect.right),
    })
    setOpen(true)
  }

  const handleItem = (item) => {
    setOpen(false)
    item.onClick?.()
  }

  return (
    <>
      <button
        ref={btnRef}
        className="app-row-menu-btn"
        onClick={toggle}
        aria-label={label}
        aria-haspopup="menu"
        aria-expanded={open}
        type="button"
      >
        <img src="/icons/submenu.svg" alt="" />
      </button>
      {open &&
        createPortal(
          <div
            ref={menuRef}
            className="app-row-menu"
            style={{ top: pos.top, right: pos.right }}
            role="menu"
          >
            {items.map((item) => (
              <button
                key={item.label}
                type="button"
                role="menuitem"
                className={`app-row-menu-item ${
                  item.danger ? 'is-danger' : ''
                }`}
                onClick={() => handleItem(item)}
                disabled={item.disabled}
              >
                {item.label}
              </button>
            ))}
          </div>,
          document.body,
        )}
    </>
  )
}

export default RowMenu
