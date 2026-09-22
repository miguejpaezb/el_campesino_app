/**
 * Modal reutilizable de la aplicación.
 *
 * Renderiza un overlay, el encabezado con título y subtítulo opcional, el
 * cuerpo y el pie con las acciones. Cierra con el botón X, la tecla Escape
 * o un clic en el fondo según `onClose`.
 *
 * @param {Object} props - Propiedades del componente.
 * @param {boolean} props.open - Si el modal está visible.
 * @param {string} props.title - Título del encabezado.
 * @param {string} [props.subtitle] - Subtítulo opcional del encabezado.
 * @param {Function} props.onClose - Callback para cerrar el modal.
 * @param {JSX.Element} [props.footer] - Contenido del pie del modal.
 * @param {JSX.Element} props.children - Contenido del cuerpo.
 * @param {string} [props.size] - Clase opcional para el ancho del modal.
 * @returns {JSX.Element} Modal o null si está cerrado.
 */
import { useEffect } from 'react'
import { createPortal } from 'react-dom'

function Modal({ open, title, subtitle, onClose, footer, children, size }) {
  useEffect(() => {
    if (!open) return undefined
    const handleKey = (event) => {
      if (event.key === 'Escape') onClose()
    }
    document.addEventListener('keydown', handleKey)
    return () => document.removeEventListener('keydown', handleKey)
  }, [open, onClose])

  if (!open) return null

  return createPortal(
    <div
      className="app-modal-overlay"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) onClose()
      }}
    >
      <div
        className={`app-modal-shell ${size ? `app-modal-${size}` : ''}`}
        role="dialog"
        aria-modal="true"
      >
        <div className="app-modal-header">
          <div>
            <h3>{title}</h3>
            {subtitle && <p>{subtitle}</p>}
          </div>
          <button
            className="app-modal-close"
            onClick={onClose}
            aria-label="Cerrar"
          >
            <img src="/icons/close.svg" alt="×" />
          </button>
        </div>
        <div className="app-modal-body">{children}</div>
        {footer && <div className="app-modal-footer">{footer}</div>}
      </div>
    </div>,
    document.body,
  )
}

export default Modal
