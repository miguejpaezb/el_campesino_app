/**
 * Componente raíz de la aplicación.
 *
 * Define las rutas públicas y protegidas del sistema.
 *
 * @returns {JSX.Element} Router con las rutas de la aplicación.
 */
import { Route, Routes } from 'react-router-dom'
import Layout from './components/Layout.jsx'
import ProtectedRoute from './components/ProtectedRoute.jsx'
import DashboardPage from './pages/DashboardPage.jsx'
import LoginPage from './pages/LoginPage.jsx'

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
              <h1>Inventario de Aves</h1>
              <p>En construcción.</p>
            </Layout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/alimentacion"
        element={
          <ProtectedRoute>
            <Layout>
              <h1>Alimentación</h1>
              <p>En construcción.</p>
            </Layout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/sanidad"
        element={
          <ProtectedRoute>
            <Layout>
              <h1>Sanidad</h1>
              <p>En construcción.</p>
            </Layout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/produccion"
        element={
          <ProtectedRoute>
            <Layout>
              <h1>Producción Diaria</h1>
              <p>En construcción.</p>
            </Layout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/trazabilidad"
        element={
          <ProtectedRoute>
            <Layout>
              <h1>Trazabilidad</h1>
              <p>En construcción.</p>
            </Layout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/iot"
        element={
          <ProtectedRoute>
            <Layout>
              <h1>Monitoreo IoT</h1>
              <p>En construcción.</p>
            </Layout>
          </ProtectedRoute>
        }
      />
    </Routes>
  )
}

export default App
