/**
 * Componente raíz de la aplicación.
 *
 * Define las rutas públicas y protegidas del sistema.
 *
 * @returns {JSX.Element} Router con las rutas de la aplicación.
 */
import { Route, Routes } from 'react-router-dom'
import Layout from './components/Layout.jsx'
import PageHeader from './components/PageHeader.jsx'
import ProtectedRoute from './components/ProtectedRoute.jsx'
import DashboardPage from './pages/DashboardPage.jsx'
import LoginPage from './pages/LoginPage.jsx'
import LotsPage from './pages/LotsPage.jsx'
import ProductionPage from './pages/ProductionPage.jsx'

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout>
              <DashboardPage />
            </Layout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/lotes"
        element={
          <ProtectedRoute>
            <Layout>
              <LotsPage />
            </Layout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/alimentacion"
        element={
          <ProtectedRoute>
            <Layout>
              <PageHeader eyebrow="Alimentación" title="En construcción" />
            </Layout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/sanidad"
        element={
          <ProtectedRoute>
            <Layout>
              <PageHeader eyebrow="Sanidad" title="En construcción" />
            </Layout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/produccion"
        element={
          <ProtectedRoute>
            <Layout>
              <ProductionPage />
            </Layout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/trazabilidad"
        element={
          <ProtectedRoute>
            <Layout>
              <PageHeader eyebrow="Trazabilidad" title="En construcción" />
            </Layout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/iot"
        element={
          <ProtectedRoute>
            <Layout>
              <PageHeader eyebrow="Monitoreo IoT" title="En construcción" />
            </Layout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/usuarios"
        element={
          <ProtectedRoute>
            <Layout>
              <PageHeader eyebrow="Usuarios" title="En construcción" />
            </Layout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/cuenta"
        element={
          <ProtectedRoute>
            <Layout>
              <PageHeader
                eyebrow="Administrar cuenta"
                title="En construcción"
              />
            </Layout>
          </ProtectedRoute>
        }
      />
    </Routes>
  )
}

export default App
