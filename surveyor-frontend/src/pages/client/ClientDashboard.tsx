import { useQuery } from '@tanstack/react-query'
import { Helmet } from 'react-helmet-async'
import { TrendingUp, FileText, DollarSign, CheckCircle, AlertCircle } from 'lucide-react'
import { apiClient } from '../../services/api'

interface DashboardStats {
  total_quotes: number
  pending_quotes: number
  accepted_quotes: number
  total_invoices: number
  paid_invoices: number
  pending_invoices: number
  overdue_invoices: number
  total_amount_invoiced: number
  total_amount_paid: number
  total_amount_pending: number
  active_projects: number
}

export default function ClientDashboard() {
  const { data: stats } = useQuery({
    queryKey: ['client-dashboard-stats'],
    queryFn: async () => {
      try {
        const response = await apiClient.client.get('/client-portal/dashboard/stats')
        return response.data as DashboardStats
      } catch {
        return null
      }
    },
  })

  return (
    <>
      <Helmet>
        <title>Dashboard - Portal del Cliente Surveyor</title>
      </Helmet>

      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Bienvenido al Portal</h1>
          <p className="text-gray-600 mt-2">Visualiza el estado de tus cotizaciones, facturas y proyectos</p>
        </div>

        {/* Stats Grid */}
        {stats && (
          <>
            {/* Top Row - Financial Summary */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-blue-500">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-600 text-sm">Total Facturado</p>
                    <p className="text-3xl font-bold text-gray-900 mt-2">
                      RD${stats.total_amount_invoiced.toLocaleString('es-DO', {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2,
                      })}
                    </p>
                  </div>
                  <DollarSign size={40} className="text-blue-500 opacity-20" />
                </div>
              </div>

              <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-green-500">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-600 text-sm">Pagado</p>
                    <p className="text-3xl font-bold text-green-600 mt-2">
                      RD${stats.total_amount_paid.toLocaleString('es-DO', {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2,
                      })}
                    </p>
                  </div>
                  <CheckCircle size={40} className="text-green-500 opacity-20" />
                </div>
              </div>

              <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-orange-500">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-600 text-sm">Pendiente</p>
                    <p className="text-3xl font-bold text-orange-600 mt-2">
                      RD${stats.total_amount_pending.toLocaleString('es-DO', {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2,
                      })}
                    </p>
                  </div>
                  <AlertCircle size={40} className="text-orange-500 opacity-20" />
                </div>
              </div>
            </div>

            {/* Second Row - Document Counts */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-white p-6 rounded-lg shadow-md">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-600 text-sm">Cotizaciones</p>
                    <p className="text-2xl font-bold text-gray-900 mt-2">{stats.total_quotes}</p>
                    <div className="text-xs text-blue-600 mt-2">
                      {stats.pending_quotes} pendientes
                    </div>
                  </div>
                  <span className="text-3xl">💰</span>
                </div>
              </div>

              <div className="bg-white p-6 rounded-lg shadow-md">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-600 text-sm">Facturas</p>
                    <p className="text-2xl font-bold text-gray-900 mt-2">{stats.total_invoices}</p>
                    <div className="text-xs text-green-600 mt-2">
                      {stats.paid_invoices} pagadas
                    </div>
                  </div>
                  <span className="text-3xl">📄</span>
                </div>
              </div>

              <div className="bg-white p-6 rounded-lg shadow-md">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-600 text-sm">Proyectos Activos</p>
                    <p className="text-2xl font-bold text-gray-900 mt-2">{stats.active_projects}</p>
                    <div className="text-xs text-blue-600 mt-2">En proceso</div>
                  </div>
                  <span className="text-3xl">📍</span>
                </div>
              </div>

              <div className="bg-white p-6 rounded-lg shadow-md">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-600 text-sm">Vencidas</p>
                    <p className={`text-2xl font-bold mt-2 ${
                      stats.overdue_invoices > 0 ? 'text-red-600' : 'text-gray-900'
                    }`}>
                      {stats.overdue_invoices}
                    </p>
                    <div className="text-xs text-red-600 mt-2">Requieren pago</div>
                  </div>
                  <span className="text-3xl">⚠️</span>
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="bg-gradient-to-r from-blue-50 to-blue-100 p-6 rounded-lg border border-blue-200">
              <h2 className="font-bold text-gray-900 mb-4">Acciones Rápidas</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <a
                  href="/client/quotes"
                  className="flex items-center gap-3 p-4 bg-white rounded-lg hover:shadow-md transition text-blue-600 font-medium"
                >
                  <FileText size={24} />
                  Ver Cotizaciones
                </a>
                <a
                  href="/client/invoices"
                  className="flex items-center gap-3 p-4 bg-white rounded-lg hover:shadow-md transition text-blue-600 font-medium"
                >
                  <FileText size={24} />
                  Ver Facturas
                </a>
                <a
                  href="/client/projects"
                  className="flex items-center gap-3 p-4 bg-white rounded-lg hover:shadow-md transition text-blue-600 font-medium"
                >
                  <TrendingUp size={24} />
                  Ver Proyectos
                </a>
              </div>
            </div>

            {/* Info Box */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
              <h3 className="font-bold text-gray-900 mb-2">💡 Información</h3>
              <p className="text-sm text-gray-700">
                Este es tu portal privado para acceder a cotizaciones, facturas y proyectos.
                Puedes descargar documentos en PDF y ver el estado de tus pagos en tiempo real.
              </p>
            </div>
          </>
        )}
      </div>
    </>
  )
}
