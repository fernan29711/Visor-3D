import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { HelmetProvider } from 'react-helmet-async'
import Layout from './components/common/Layout'
import ClientLayout from './components/client/ClientLayout'
import Dashboard from './pages/Dashboard'
import FinancialDashboard from './pages/FinancialDashboard'
import Projects from './pages/Projects'
import ProjectDetail from './pages/ProjectDetail'
import Quotes from './pages/Quotes'
import Invoices from './pages/Invoices'
import Reports from './pages/Reports'
import Drones from './pages/Drones'
import Notifications from './pages/Notifications'
import Webhooks from './pages/Webhooks'
import ClientDashboard from './pages/client/ClientDashboard'
import ClientQuotes from './pages/client/ClientQuotes'
import ClientInvoices from './pages/client/ClientInvoices'
import ClientProjects from './pages/client/ClientProjects'
import ProjectMap from './pages/ProjectMap'
import ClientProjectMap from './pages/client/ClientProjectMap'

const queryClient = new QueryClient()

function App() {
  return (
    <HelmetProvider>
      <QueryClientProvider client={queryClient}>
        <Router>
          <Routes>
            {/* Admin/Professional Portal */}
            <Route path="/" element={<Layout />}>
              <Route index element={<Dashboard />} />
              <Route path="dashboard" element={<Dashboard />} />
              <Route path="financial" element={<FinancialDashboard />} />
              <Route path="projects" element={<Projects />} />
              <Route path="projects/:projectId" element={<ProjectDetail />} />
              <Route path="projects/:projectId/map" element={<ProjectMap />} />
              <Route path="quotes" element={<Quotes />} />
              <Route path="invoices" element={<Invoices />} />
              <Route path="reports" element={<Reports />} />
              <Route path="drones" element={<Drones />} />
              <Route path="notifications" element={<Notifications />} />
              <Route path="webhooks" element={<Webhooks />} />
            </Route>

            {/* Client Portal */}
            <Route path="/client" element={<ClientLayout />}>
              <Route index element={<ClientDashboard />} />
              <Route path="dashboard" element={<ClientDashboard />} />
              <Route path="quotes" element={<ClientQuotes />} />
              <Route path="invoices" element={<ClientInvoices />} />
              <Route path="projects" element={<ClientProjects />} />
              <Route path="projects/:projectId/map" element={<ClientProjectMap />} />
            </Route>

            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Router>
      </QueryClientProvider>
    </HelmetProvider>
  )
}

export default App
