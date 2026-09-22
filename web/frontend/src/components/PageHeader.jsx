/**
 * Encabezado de página reutilizable.
 *
 * Renderiza la etiqueta superior (eyebrow) en mayúsculas de color marrón
 * y el título principal, replicando el estilo del dashboard.
 *
 * @param {Object} props - Propiedades del componente.
 * @param {string} props.eyebrow - Etiqueta superior de la página.
 * @param {string} props.title - Título principal de la página.
 * @returns {JSX.Element} Encabezado de la página.
 */
function PageHeader({ eyebrow, title }) {
  return (
    <header className="dashboard-header">
      <div>
        <p className="eyebrow">{eyebrow}</p>
        <h1>{title}</h1>
      </div>
    </header>
  )
}

export default PageHeader
