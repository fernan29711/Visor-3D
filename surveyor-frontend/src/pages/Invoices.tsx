import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../services/api'
import { Helmet } from 'react-helmet-async'
import { Plus, Search, Eye, Trash2, Download } from 'lucide-react'

interface Invoice {
  id: string
  ncf: string
  status: string
  total: number
  issue_date: string
  due_date: string
}

export default function Invoices() {
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('')

  const { data: invoices, isLoading } = useQuery({
    queryKey: ['invoices', searchTerm, statusFilter],
    queryFn: async () => {
      const response = await apiClient.getInvoices({
        status: statusFilter,
        limit: 100,
      })
      return response.data as Invoice[]
    },
  })

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      draft: 'bg-gray-100 text-gray-800',
      sent: 'bg-blue-100 text-blue-800',
      paid: 'bg-green-100 text-green-800',
      pending: 'bg-yellow-100 text-yellow-800',
      overdue: 'bg-red-100 text-red-800',
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }

  const handleDownloadPDF = async (invoiceId: string, ncf: string) => {
    try {
      const response = await apiClient.client.get(`/invoices/${invoiceId}/pdf`, {
        responseType: 'blob'
      })
      const url = window.URL.createObjectURL(response.data)
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `factura_${ncf || invoiceId}.pdf`)
      document.body.appendChild(link)
      link.click()
      link.parentNode?.removeChild(link)
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Error descargando PDF:', error)
    }
  }

  return (
    <>
      <Helmet>
        <title>Facturas - Visor 3D Surveyor</title>
      </Helmet>

      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Facturas</h1>
            <p className="text-gray-600 mt-2">Gestiona todas tus facturas de clientes</p>
          </div>
          <button className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 flex items-center gap-2">
            <Plus size={20} />
            Nueva Factura
          </button>
        </div>

        {/* Filters */}
        <div className="flex gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-3 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Buscar por NCF..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="">Todos los estados</option>
            <option value="draft">Borrador</option>
            <option value="sent">Enviada</option>
            <option value="paid">Pagada</option>
            <option value="pending">Pendiente</option>
            <option value="overdue">Vencida</option>
          </select>
        </div>

        {/* Invoices Table */}
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          {isLoading ? (
            <div className="p-8 text-center">Cargando facturas...</div>
          ) : invoices && invoices.length > 0 ? (
            <table className="w-full">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">NCF</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Estado</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Total</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Fecha Emisión</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Vencimiento</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Acciones</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {invoices.map((invoice) => (
                  <tr key={invoice.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 text-sm font-medium text-gray-900">{invoice.ncf || 'S/N'}</td>
                    <td className="px-6 py-4 text-sm">
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor(invoice.status)}`}>
                        {invoice.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-700">
                      RD$ {invoice.total?.toLocaleString() || '0'}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-700">
                      {new Date(invoice.issue_date).toLocaleDateString('es-ES')}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-700">
                      {new Date(invoice.due_date).toLocaleDateString('es-ES')}
                    </td>
                    <td className="px-6 py-4 text-sm flex gap-2">
                      <button className="text-blue-600 hover:text-blue-800">
                        <Eye size={16} />
                      </button>
                      <button
                        onClick={() => handleDownloadPDF(invoice.id, invoice.ncf)}
                        className="text-green-600 hover:text-green-800"
                        title="Descargar PDF"
                      >
                        <Download size={16} />
                      </button>
                      <button className="text-red-600 hover:text-red-800">
                        <Trash2 size={16} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="p-8 text-center text-gray-600">No hay facturas disponibles</div>
          )}
        </div>
      </div>
    </>
  )
}
