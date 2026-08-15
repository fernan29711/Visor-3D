import { useState } from 'react'
import { Helmet } from 'react-helmet-async'
import { apiClient } from '../services/api'
import { Download, FileText, Calendar } from 'lucide-react'

export default function Reports() {
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [downloading, setDownloading] = useState<string | null>(null)

  const handleDownloadReport = async (reportType: string) => {
    setDownloading(reportType)
    try {
      let url = `/reports/${reportType}/excel`
      if (reportType === 'invoices' && startDate && endDate) {
        url += `?start_date=${startDate}&end_date=${endDate}`
      }

      const response = await apiClient.client.get(url, {
        responseType: 'blob'
      })

      const blob = new Blob([response.data], {
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      })
      const urlBlob = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = urlBlob

      const filename = {
        financial: `reporte_financiero_${new Date().toISOString().split('T')[0]}.xlsx`,
        invoices: `reporte_facturas_${new Date().toISOString().split('T')[0]}.xlsx`,
        quotes: `reporte_cotizaciones_${new Date().toISOString().split('T')[0]}.xlsx`,
        clients: `reporte_clientes_${new Date().toISOString().split('T')[0]}.xlsx`,
      }

      link.setAttribute('download', filename[reportType as keyof typeof filename] || 'reporte.xlsx')
      document.body.appendChild(link)
      link.click()
      link.parentNode?.removeChild(link)
      window.URL.revokeObjectURL(urlBlob)
    } catch (error) {
      console.error('Error descargando reporte:', error)
      alert('Error al descargar el reporte')
    } finally {
      setDownloading(null)
    }
  }

  return (
    <>
      <Helmet>
        <title>Reportes - Visor 3D Surveyor</title>
      </Helmet>

      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Reportes</h1>
          <p className="text-gray-600 mt-2">Descarga reportes en formato Excel</p>
        </div>

        {/* Report Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Financial Report */}
          <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200 hover:shadow-lg transition">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h2 className="text-xl font-bold text-gray-900">Reporte Financiero</h2>
                <p className="text-gray-600 text-sm mt-1">Resumen completo de ingresos, cobranza y métricas</p>
              </div>
              <FileText className="text-blue-500" size={32} />
            </div>

            <div className="space-y-3">
              <p className="text-sm text-gray-600">Incluye:</p>
              <ul className="text-sm text-gray-700 space-y-1 list-disc list-inside">
                <li>Ingresos y cobranza</li>
                <li>Top clientes</li>
                <li>Conversión de cotizaciones</li>
              </ul>
              <button
                onClick={() => handleDownloadReport('financial')}
                disabled={downloading === 'financial'}
                className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 flex items-center justify-center gap-2 mt-4"
              >
                <Download size={18} />
                {downloading === 'financial' ? 'Descargando...' : 'Descargar'}
              </button>
            </div>
          </div>

          {/* Invoices Report */}
          <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200 hover:shadow-lg transition">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h2 className="text-xl font-bold text-gray-900">Reporte de Facturas</h2>
                <p className="text-gray-600 text-sm mt-1">Detalle de todas las facturas emitidas</p>
              </div>
              <FileText className="text-green-500" size={32} />
            </div>

            <div className="space-y-3">
              <p className="text-sm text-gray-600">Filtrar por fechas:</p>
              <div className="space-y-2">
                <input
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                  placeholder="Desde"
                />
                <input
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                  placeholder="Hasta"
                />
              </div>
              <button
                onClick={() => handleDownloadReport('invoices')}
                disabled={downloading === 'invoices'}
                className="w-full bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 disabled:bg-gray-400 flex items-center justify-center gap-2"
              >
                <Download size={18} />
                {downloading === 'invoices' ? 'Descargando...' : 'Descargar'}
              </button>
            </div>
          </div>

          {/* Quotes Report */}
          <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200 hover:shadow-lg transition">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h2 className="text-xl font-bold text-gray-900">Reporte de Cotizaciones</h2>
                <p className="text-gray-600 text-sm mt-1">Análisis de todas tus cotizaciones</p>
              </div>
              <FileText className="text-yellow-500" size={32} />
            </div>

            <div className="space-y-3">
              <p className="text-sm text-gray-600">Incluye:</p>
              <ul className="text-sm text-gray-700 space-y-1 list-disc list-inside">
                <li>Todas las cotizaciones</li>
                <li>Estados y montos</li>
                <li>Cálculos de impuestos</li>
              </ul>
              <button
                onClick={() => handleDownloadReport('quotes')}
                disabled={downloading === 'quotes'}
                className="w-full bg-yellow-600 text-white px-4 py-2 rounded-lg hover:bg-yellow-700 disabled:bg-gray-400 flex items-center justify-center gap-2 mt-4"
              >
                <Download size={18} />
                {downloading === 'quotes' ? 'Descargando...' : 'Descargar'}
              </button>
            </div>
          </div>

          {/* Clients Report */}
          <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200 hover:shadow-lg transition">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h2 className="text-xl font-bold text-gray-900">Reporte de Clientes</h2>
                <p className="text-gray-600 text-sm mt-1">Actividad y facturación por cliente</p>
              </div>
              <FileText className="text-purple-500" size={32} />
            </div>

            <div className="space-y-3">
              <p className="text-sm text-gray-600">Incluye:</p>
              <ul className="text-sm text-gray-700 space-y-1 list-disc list-inside">
                <li>Listado de clientes</li>
                <li>Cantidad de facturas</li>
                <li>Total facturado</li>
              </ul>
              <button
                onClick={() => handleDownloadReport('clients')}
                disabled={downloading === 'clients'}
                className="w-full bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 disabled:bg-gray-400 flex items-center justify-center gap-2 mt-4"
              >
                <Download size={18} />
                {downloading === 'clients' ? 'Descargando...' : 'Descargar'}
              </button>
            </div>
          </div>
        </div>

        {/* Info Section */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <div className="flex gap-4">
            <Calendar className="text-blue-600 flex-shrink-0" size={24} />
            <div>
              <h3 className="font-bold text-blue-900 mb-2">Formato Excel</h3>
              <p className="text-blue-800 text-sm">
                Los reportes se descargan en formato Excel (.xlsx) con estilos profesionales, tablas formateadas y cálculos automáticos. Puedes abrir los archivos en Excel, Google Sheets o cualquier aplicación compatible.
              </p>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}
