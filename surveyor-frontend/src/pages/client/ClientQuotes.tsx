import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Helmet } from 'react-helmet-async'
import { Download, Eye } from 'lucide-react'
import { apiClient } from '../../services/api'

interface Quote {
  id: string
  quote_code: string
  project_name: string
  quote_date: string
  expiration_date?: string
  status: string
  total_amount: number
  discount_amount: number
  tax_amount: number
  subtotal_amount: number
}

export default function ClientQuotes() {
  const [selectedStatus, setSelectedStatus] = useState<string>('')

  const { data: quotes } = useQuery({
    queryKey: ['client-quotes', selectedStatus],
    queryFn: async () => {
      try {
        const url = selectedStatus
          ? `/client-portal/quotes?status=${selectedStatus}`
          : '/client-portal/quotes'
        const response = await apiClient.client.get(url)
        return response.data as Quote[]
      } catch {
        return []
      }
    },
  })

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'accepted':
        return 'bg-green-100 text-green-800'
      case 'rejected':
        return 'bg-red-100 text-red-800'
      case 'sent':
        return 'bg-blue-100 text-blue-800'
      case 'draft':
        return 'bg-gray-100 text-gray-800'
      case 'expired':
        return 'bg-yellow-100 text-yellow-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const handleDownloadPDF = (quoteId: string, quoteCode: string) => {
    apiClient.client.get(`/quotes/${quoteId}/pdf`, { responseType: 'blob' }).then((response) => {
      const blob = new Blob([response.data], { type: 'application/pdf' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `Cotizacion_${quoteCode}.pdf`
      a.click()
      window.URL.revokeObjectURL(url)
    })
  }

  return (
    <>
      <Helmet>
        <title>Cotizaciones - Portal del Cliente</title>
      </Helmet>

      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Mis Cotizaciones</h1>
          <p className="text-gray-600 mt-2">Visualiza y descarga todas tus cotizaciones</p>
        </div>

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
            {['draft', 'sent', 'accepted', 'rejected', 'expired'].map((status) => (
              <button
                key={status}
                onClick={() => setSelectedStatus(status)}
                className={`px-4 py-2 rounded-lg font-medium transition ${
                  selectedStatus === status
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {status.charAt(0).toUpperCase() + status.slice(1)}
              </button>
            ))}
          </div>
        </div>

        {/* Quotes Table */}
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          {quotes && quotes.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b">
                  <tr>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Código</th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Proyecto</th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Fecha</th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Vencimiento</th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Monto</th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Estado</th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Acciones</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {quotes.map((quote) => (
                    <tr key={quote.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 text-sm font-medium text-blue-600">
                        {quote.quote_code}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900">{quote.project_name}</td>
                      <td className="px-6 py-4 text-sm text-gray-600">
                        {new Date(quote.quote_date).toLocaleDateString('es-DO')}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600">
                        {quote.expiration_date
                          ? new Date(quote.expiration_date).toLocaleDateString('es-DO')
                          : '-'}
                      </td>
                      <td className="px-6 py-4 text-sm font-semibold text-gray-900">
                        RD${quote.total_amount.toLocaleString('es-DO', {
                          minimumFractionDigits: 2,
                        })}
                      </td>
                      <td className="px-6 py-4 text-sm">
                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(quote.status)}`}>
                          {quote.status === 'accepted'
                            ? 'Aceptada'
                            : quote.status === 'rejected'
                            ? 'Rechazada'
                            : quote.status === 'sent'
                            ? 'Enviada'
                            : quote.status === 'draft'
                            ? 'Borrador'
                            : 'Vencida'}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm">
                        <div className="flex gap-2">
                          <button
                            onClick={() => window.location.href = `/client/quotes/${quote.id}`}
                            className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition"
                            title="Ver detalles"
                          >
                            <Eye size={18} />
                          </button>
                          <button
                            onClick={() => handleDownloadPDF(quote.id, quote.quote_code)}
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
              <p>No hay cotizaciones</p>
            </div>
          )}
        </div>
      </div>
    </>
  )
}
