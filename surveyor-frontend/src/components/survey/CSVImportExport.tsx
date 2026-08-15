import { useState, useRef } from 'react'
import { useMutation } from '@tanstack/react-query'
import { apiClient } from '../../services/api'
import { Upload, Download, AlertCircle } from 'lucide-react'

interface CSVImportExportProps {
  projectId: string
  onImportSuccess?: () => void
}

export default function CSVImportExport({ projectId, onImportSuccess }: CSVImportExportProps) {
  const [dragActive, setDragActive] = useState(false)
  const [importError, setImportError] = useState<string | null>(null)
  const [importSuccess, setImportSuccess] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const importMutation = useMutation({
    mutationFn: async (file: File) => {
      const response = await apiClient.uploadSurveyPointsCSV(projectId, file)
      return response.data
    },
    onSuccess: (data) => {
      setImportSuccess(true)
      setImportError(null)
      if (onImportSuccess) onImportSuccess()
      setTimeout(() => setImportSuccess(false), 3000)
    },
    onError: (error: any) => {
      setImportError(error.response?.data?.detail || 'Error importing CSV')
      setImportSuccess(false)
    },
  })

  const exportMutation = useMutation({
    mutationFn: async () => {
      const response = await apiClient.exportSurveyPointsCSV(projectId)
      return { data: response.data, format: 'csv' }
    },
    onSuccess: (result) => {
      const url = window.URL.createObjectURL(new Blob([result.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `survey_points_${projectId}.${result.format}`)
      document.body.appendChild(link)
      link.click()
      link.parentNode?.removeChild(link)
      window.URL.revokeObjectURL(url)
    },
    onError: (error: any) => {
      setImportError(error.response?.data?.detail || 'Error exporting')
    },
  })

  const exportGeoJSONMutation = useMutation({
    mutationFn: async () => {
      const response = await apiClient.exportSurveyPointsGeoJSON(projectId)
      return { data: response.data, format: 'geojson' }
    },
    onSuccess: (result) => {
      const url = window.URL.createObjectURL(new Blob([result.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `survey_points_${projectId}.${result.format}`)
      document.body.appendChild(link)
      link.click()
      link.parentNode?.removeChild(link)
      window.URL.revokeObjectURL(url)
    },
    onError: (error: any) => {
      setImportError(error.response?.data?.detail || 'Error exporting')
    },
  })

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0]
      if (file.type === 'text/csv' || file.name.endsWith('.csv')) {
        importMutation.mutate(file)
      } else {
        setImportError('Por favor, selecciona un archivo CSV')
      }
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      importMutation.mutate(e.target.files[0])
    }
  }

  return (
    <div className="space-y-4">
      {/* Alerts */}
      {importError && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex gap-3">
          <AlertCircle className="text-red-600 flex-shrink-0" size={20} />
          <div>
            <p className="text-sm font-medium text-red-900">Error en la importación</p>
            <p className="text-sm text-red-700 mt-1">{importError}</p>
          </div>
        </div>
      )}

      {importSuccess && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <p className="text-sm font-medium text-green-900">✅ Puntos importados exitosamente</p>
        </div>
      )}

      {/* Import Section */}
      <div>
        <label className="block text-sm font-medium text-gray-900 mb-2">
          Importar Puntos desde CSV
        </label>
        <div
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition ${
            dragActive
              ? 'border-primary-500 bg-primary-50'
              : 'border-gray-300 hover:border-gray-400'
          }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".csv"
            onChange={handleFileSelect}
            className="hidden"
          />

          <Upload className="mx-auto mb-3 text-gray-400" size={32} />
          <p className="text-sm text-gray-700 font-medium">
            Arrastra tu archivo CSV aquí o{' '}
            <button
              onClick={() => fileInputRef.current?.click()}
              className="text-primary-600 hover:text-primary-700 font-semibold"
            >
              selecciona
            </button>
          </p>
          <p className="text-xs text-gray-500 mt-1">
            Soporta columnas: point_number, east, north, elevation (opcional: pdop, hdop, vdop, satellite_count)
          </p>

          {importMutation.isPending && (
            <p className="text-sm text-primary-600 mt-3">Importando...</p>
          )}
        </div>
      </div>

      {/* Export Section */}
      <div>
        <label className="block text-sm font-medium text-gray-900 mb-3">
          Exportar Puntos
        </label>
        <div className="space-y-2">
          <button
            onClick={() => exportMutation.mutate()}
            disabled={exportMutation.isPending}
            className="w-full bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 disabled:opacity-50 flex items-center justify-center gap-2"
          >
            <Download size={20} />
            {exportMutation.isPending ? 'Exportando...' : 'Descargar CSV'}
          </button>
          <button
            onClick={() => exportGeoJSONMutation.mutate()}
            disabled={exportGeoJSONMutation.isPending}
            className="w-full bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50 flex items-center justify-center gap-2"
          >
            <Download size={20} />
            {exportGeoJSONMutation.isPending ? 'Exportando...' : 'Descargar GeoJSON'}
          </button>
        </div>
      </div>
    </div>
  )
}
