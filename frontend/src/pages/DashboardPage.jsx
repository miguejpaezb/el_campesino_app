/**
 * Página de inicio del panel administrativo.
 *
 * Muestra un resumen de los módulos del sistema con enlaces
 * para navegar a cada sección.
 *
 * @returns {JSX.Element} Dashboard con tarjetas de módulos.
 */
import { Card, Col, Row } from 'react-bootstrap'
import { useAuth } from '../hooks/useAuth.js'

const MODULES = [
  {
    title: 'Inventario de Aves',
    description: 'Registro y control de lotes, razas y cantidades de aves.',
    href: '/lotes',
  },
  {
    title: 'Alimentación',
    description: 'Tipos de alimento y registro de raciones por lote.',
    href: '/alimentacion',
  },
  {
    title: 'Sanidad',
    description: 'Vacunas, enfermedades, tratamientos y mortalidad.',
    href: '/sanidad',
  },
  {
    title: 'Producción Diaria',
    description: 'Huevos recolectados, peso promedio y muertes diarias.',
    href: '/produccion',
  },
  {
    title: 'Trazabilidad',
    description: 'Historial de auditoría con integridad tipo blockchain.',
    href: '/trazabilidad',
  },
  {
    title: 'Monitoreo IoT',
    description: 'Sensores de temperatura, humedad y amoníaco en tiempo real.',
    href: '/iot',
  },
]

function DashboardPage() {
  const { user } = useAuth()

  return (
    <>
      <h1 className="mb-4">Bienvenido, {user?.full_name}</h1>
      <Row xs={1} md={2} lg={3} className="g-4">
        {MODULES.map((mod) => (
          <Col key={mod.title}>
            <Card
              as="a"
              href={mod.href}
              className="text-decoration-none h-100"
              text="dark"
            >
              <Card.Body>
                <Card.Title>{mod.title}</Card.Title>
                <Card.Text>{mod.description}</Card.Text>
              </Card.Body>
            </Card>
          </Col>
        ))}
      </Row>
    </>
  )
}

export default DashboardPage
