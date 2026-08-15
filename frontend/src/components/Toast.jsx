/**
 * Contenedor de notificaciones tipo toast.
 *
 * Muestra apiladas las notificaciones con su tipo (éxito, error o
 * informativo) y un botón para cerrarlas manualmente.
 *
 * @param {Object} props - Propiedades del componente.
 * @param {Array} props.toasts - Lista de toasts: `{ id, type, message }`.
 * @param {Function} props.onDismiss - Callback para eliminar un toast por id.
 * @returns {JSX.Element} Contenedor de toasts.
 */
function Toast({ toasts, onDismiss }) {
  return (
    <div className="toast-container" aria-live="polite">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={`toast toast-${toast.type}`}
          role="status"
        >
          <span className="toast-dot" aria-hidden="true"></span>
          <p>{toast.message}</p>
          <button
            className="toast-close"
            onClick={() => onDismiss(toast.id)}
            aria-label="Cerrar notificación"
          >
            ×
          </button>
        </div>
      ))}
    </div>
  )
}

export default Toast
