import { useQuery } from '@tanstack/react-query'
import { Helmet } from 'react-helmet-async'
import { apiClient } from '../services/api'
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts'
import { TrendingUp, DollarSign, FileText, AlertCircle } from 'lucide-react'

export default function FinancialDashboard() {
  const { data: summary } = useQuery({
    queryKey: ['financial-summary'],
    queryFn: async () => {
      const response = await apiClient.client.get('/financial/summary')
      return response.data
    },
  })

  const { data: revenueByMonth } = useQuery({
    queryKey: ['revenue-by-month'],
    queryFn: async () => {
      const response = await apiClient.client.get('/financial/revenue-by-month?months=12')
      return response.data?.reverse() || []
    },
  })

  const { data: paymentDistribution } = useQuery({
    queryKey: ['payment-status-distribution'],
    queryFn: async () => {
      const response = await apiClient.client.get('/financial/payment-status-distribution')
      return response.data
    },
  })

  const { data: topClients } = useQuery({
    queryKey: ['top-clients'],
    queryFn: async () => {
      const response = await apiClient.client.get('/financial/top-clients?limit=5')
      return response.data || []
    },
  })

  const { data: quoteConversion } = useQuery({
    queryKey: ['quote-conversion'],
    queryFn: async () => {
      const response = await apiClient.client.get('/financial/quote-conversion')
      return response.data
    },
  })

  const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']

  const pieData = paymentDistribution?.distribution ? [
    { name: 'Pagada', value: paymentDistribution.distribution.paid, fill: '#10b981' },
    { name: 'Pendiente', value: paymentDistribution.distribution.pending, fill: '#f59e0b' },
    { name: 'Vencida', value: paymentDistribution.distribution.overdue, fill: '#ef4444' },
    { name: 'Enviada', value: paymentDistribution.distribution.sent, fill: '#3b82f6' },
    { name: 'Borrador', value: paymentDistribution.distribution.draft, fill: '#9ca3af' },
  ].filter(item => item.value > 0) : []

  return (
    <>
      <Helmet>
        <title>Dashboard Financiero - Visor 3D Surveyor</title>
      </Helmet>

      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard Financiero</h1>
          <p className="text-gray-600 mt-2">Análisis de ingresos, cobranza y rentabilidad</p>
        </div>

        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-blue-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Ingresos Totales</p>
                <p className="text-2xl font-bold text-gray-900">
                  RD$ {summary?.total_issued?.toLocaleString() || '0'}
                </p>
              </div>
              <DollarSign className="text-blue-500" size={40} />
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-green-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Cobrado</p>
                <p className="text-2xl font-bold text-gray-900">
                  RD$ {summary?.total_paid?.toLocaleString() || '0'}
                </p>
              </div>
              <TrendingUp className="text-green-500" size={40} />
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-yellow-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Pendiente</p>
                <p className="text-2xl font-bold text-gray-900">
                  RD$ {summary?.total_pending?.toLocaleString() || '0'}
                </p>
              </div>
              <FileText className="text-yellow-500" size={40} />
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-red-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Vencida</p>
                <p className="text-2xl font-bold text-gray-900">
                  RD$ {summary?.total_overdue?.toLocaleString() || '0'}
                </p>
              </div>
              <AlertCircle className="text-red-500" size={40} />
            </div>
          </div>
        </div>

        {/* Collection Rate */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Tasa de Cobranza</h2>
          <div className="flex items-center gap-4">
            <div className="flex-1">
              <div className="text-4xl font-bold text-blue-600">{summary?.collection_rate || 0}%</div>
              <p className="text-gray-600 mt-2">
                {summary?.total_paid?.toLocaleString() || '0'} de {summary?.total_issued?.toLocaleString() || '0'} cobrado
              </p>
            </div>
            <div className="w-24 h-24 bg-blue-50 rounded-full flex items-center justify-center">
              <span className="text-3xl font-bold text-blue-600">{summary?.collection_rate || 0}%</span>
            </div>
          </div>
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Revenue by Month */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Ingresos por Mes</h2>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={revenueByMonth}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip formatter={(value) => `RD$ ${value.toLocaleString()}`} />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="revenue"
                  stroke="#3b82f6"
                  name="Ingresos"
                  strokeWidth={2}
                  dot={{ fill: '#3b82f6', r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Payment Status Distribution */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Distribución de Estados</h2>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value }) => `${name} (${value})`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => `${value}`} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Top Clients */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Clientes Top por Ingresos</h2>
          <div className="overflow-x-auto">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={topClients}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="client_name" />
                <YAxis />
                <Tooltip formatter={(value) => `RD$ ${value.toLocaleString()}`} />
                <Legend />
                <Bar dataKey="total_revenue" fill="#10b981" name="Ingresos" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Quote Conversion & Profitability */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Quote Conversion */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Conversión de Cotizaciones</h2>
            <div className="space-y-4">
              <div className="flex justify-between">
                <span className="text-gray-600">Cotizaciones Enviadas:</span>
                <span className="font-bold">{quoteConversion?.sent_quotes || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Cotizaciones Aceptadas:</span>
                <span className="font-bold text-green-600">{quoteConversion?.accepted_quotes || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Tasa de Conversión:</span>
                <span className="font-bold text-blue-600">{quoteConversion?.conversion_rate || 0}%</span>
              </div>
              <div className="pt-4 border-t">
                <div className="flex justify-between">
                  <span className="text-gray-600">Total de Cotizaciones:</span>
                  <span className="font-bold">{quoteConversion?.total_quotes || 0}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Summary Stats */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Resumen de Facturación</h2>
            <div className="space-y-4">
              <div className="flex justify-between">
                <span className="text-gray-600">Promedio por Factura:</span>
                <span className="font-bold">RD$ {summary?.average_invoice_value?.toLocaleString() || '0'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Total de Facturas:</span>
                <span className="font-bold">{summary?.total_invoices || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Facturación Promedio/Mes:</span>
                <span className="font-bold text-blue-600">
                  RD$ {summary?.total_issued && summary.total_invoices ?
                    (summary.total_issued / 12).toLocaleString() : '0'}
                </span>
              </div>
              <div className="pt-4 border-t">
                <div className="flex justify-between">
                  <span className="text-gray-600">Proyección Anual:</span>
                  <span className="font-bold text-green-600">
                    RD$ {summary?.total_issued?.toLocaleString() || '0'}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}
