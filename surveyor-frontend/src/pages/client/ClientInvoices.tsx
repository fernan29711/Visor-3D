import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Helmet } from 'react-helmet-async'
import { Download, Eye, AlertCircle } from 'lucide-react'
import { apiClient } from '../../services/api'

interface Invoice {
  id: string
  ncf: string
  project_name: string
  issue_date: string
  due_date: string
  status: string
  subtotal_amount: number
  tax_amount: number
  total_amount: number
  amount_paid: number
  days_overdue: number
}

export default function ClientInvoices() {
  const [selectedStatus, setSelectedStatus] = useState<string>('')

  const { data: invoices } = useQuery({
    queryKey: ['client-invoices', selectedStatus],
    queryFn: async () => {
      try {
        const url = selectedStatus
          ? `/client-portal/invoices?status=${selectedStatus}`
          : '/client-portal/invoices'
        const response = await apiClient.client.get(url)
        return response.data as Invoice[]
      } catch {
        return []
      }
    },
  })

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'paid':
        return 'bg-green-100 text-green-800'
      case 'pending':
        return 'bg-blue-100 text-blue-800'
      case 'overdue':
        return 'bg-red-100 text-red-800'
      case 'sent':
        return 'bg-yellow-100 text-yellow-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getTotalOutstanding = () => {
    return invoices?.reduce((sum, inv) => sum + (inv.total_amount - inv.amount_paid), 0) || 0
  }

  const handleDownloadPDF = (invoiceId: string, ncf: string) => {
    apiClient.client.get(`/invoices/${invoiceId}/pdf`, { responseType: 'blob' }).then((response) => {
      const blob = new Blob([response.data], { type: 'application/pdf' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `Factura_${ncf}.pdf`
      a.click()
      window.URL.revokeObjectURL(url)
    })
  }

  return (
    <>
      <Helmet>
        <title>Facturas - Portal del Cliente</title>
      </Helmet>

      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Mis Facturas</h1>
          <p className="text-gray-600 mt-2">Visualiza y descarga todas tus facturas</p>
        </div>

        {/* Summary Cards */}
        {invoices && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white p-4 rounded-lg shadow-md border-l-4 border-green-500">
              <p className="text-gray-600 text-sm">Total Pagado</p>
              <p className="text-2xl font-bold text-green-600 mt-2">
                RD${invoices
                  .reduce((sum, inv) => sum + inv.amount_paid, 0)
                  .toLocaleString('es-DO', { minimumFractionDigits: 2 })}
              </p>
            </div>
            <div className="bg-white p-4 rounded-lg shadow-md border-l-4 border-orange-500">
              <p className="text-gray-600 text-sm">Pendiente de Pago</p>
              <p className="text-2xl font-bold text-orange-600 mt-2">
                RD${getTotalOutstanding().toLocaleString('es-DO', {
                  minimumFractionDigits: 2,
                })}
              </p>
            </div>
            <div className="bg-white p-4 rounded-lg shadow-md border-l-4 border-red-500">
              <p className="text-gray-600 text-sm">Vencidas</p>
              <p className="text-2xl font-bold text-red-600 mt-2">
                {invoices.filter((i) => i.status === 'overdue').length}
              </p>
            </div>
          </div>
        )}

        {/* Filters */}
        <div className="bg-white p-4 rounded-lg shadow-md">
          <label className="block text-sm font-medium text-gray-700 mb-2">Filtrar por estado</label>
          <div className="flex gap-2 flex-wrap">
            <button
              onClick={() => setSelectedStatus('')}
              className={`px-4 py-2 rounded-lg font-medium transition ${
                selectedStatus === ''
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Todas
            </button>
            {['sent', 'pending', 'paid', 'overdue'].map((status) => (
              <button
                key={status}
                onClick={() => setSelectedStatus(status)}
                className={`px-4 py-2 rounded-lg font-medium transition ${
                  selectedStatus === status
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {status === 'sent'
                  ? 'Enviadas'
                  : status === 'pending'
                  ? 'Pendientes'
                  : status === 'paid'
                  ? 'Pagadas'
                  : 'Vencidas'}
              </button>
            ))}
          </div>
        </div>

        {/* Invoices Table */}
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          {invoices && invoices.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b">
                  <tr>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">NCF</th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Proyecto</th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Fecha Emisión</th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Vencimiento</th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Monto</th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Pagado</th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Estado</th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Acciones</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {invoices.map((invoice) => (
                    <tr key={invoice.id} className={`hover:bg-gray-50 ${
                      invoice.status === 'overdue' ? 'bg-red-50' : ''
                    }`}>
                      <td className="px-6 py-4 text-sm font-medium text-blue-600">
                        {invoice.ncf}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900">{invoice.project_name}</td>
                      <td className="px-6 py-4 text-sm text-gray-600">
                        {new Date(invoice.issue_date).toLocaleDateString('es-DO')}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600">
                        {new Date(invoice.due_date).toLocaleDateString('es-DO')}
                      </td>
                      <td className="px-6 py-4 text-sm font-semibold text-gray-900">
                        RD${invoice.total_amount.toLocaleString('es-DO', {
                          minimumFractionDigits: 2,
                        })}
                      </td>
                      <td className="px-6 py-4 text-sm">
                        <div className="flex items-center gap-2">
                          <span className="font-medium">
                            RD${invoice.amount_paid.toLocaleString('es-DO', {
                              minimumFractionDigits: 2,
                            })}
                          </span>
                          {invoice.total_amount - invoice.amount_paid > 0 && (
                            <span className="text-xs text-orange-600">
                              RD${(invoice.total_amount - invoice.amount_paid).toLocaleString('es-DO', {
                                minimumFractionDigits: 2,
                              })} pendiente
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-sm">
                        <div className="flex items-center gap-2">
                          {invoice.status === 'overdue' && (
                            <AlertCircle size={16} className="text-red-600" />
                          )}
                          <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(invoice.status)}`}>
                            {invoice.status === 'paid'
                              ? 'Pagada'
                              : invoice.status === 'pending'
                              ? 'Pendiente'
                              : invoice.status === 'overdue'
                              ? 'Vencida'
                              : 'Enviada'}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-sm">
                        <div className="flex gap-2">
                          <button
                            onClick={() => window.location.href = `/client/invoices/${invoice.id}`}
                            className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition"
                            title="Ver detalles"
                          >
                            <Eye size={18} />
                          </button>
                          <button
                            onClick={() => handleDownloadPDF(invoice.id, invoice.ncf)}
                            className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition"
                            title="Descargar PDF"
                          >
                            <Download size={18} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="p-8 text-center text-gray-600">
              <p>No hay facturas</p>
            </div>
          )}
        </div>
      </div>
    </>
  )
}
