import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Helmet } from 'react-helmet-async'
import { MapPin, Eye, EyeOff } from 'lucide-react'
import { useState } from 'react'
import MapComponent from '../../components/map/MapComponent'
import { apiClient } from '../../services/api'

interface MapData {
  project_id: string
  project_name: string
  survey_points: any[]
  parcels: any[]
  drone_coverage: any[]
}

export default function ClientProjectMap() {
  const { projectId } = useParams()
  const [visibleLayers, setVisibleLayers] = useState({
    survey_points: true,
    parcels: true,
    drone_coverage: true,
  })

  const { data: mapData, isLoading, error } = useQuery({
    queryKey: ['client-project-map', projectId],
    queryFn: async () => {
      const response = await apiClient.client.get(`/geospatial/projects/${projectId}/map-features`)
      return response.data
    },
    enabled: !!projectId,
  })

  const toggleLayer = (layer: keyof typeof visibleLayers) => {
    setVisibleLayers((prev) => ({
      ...prev,
      [layer]: !prev[layer],
    }))
  }

  const filteredGeojsonData = mapData
    ? {
        survey_points: visibleLayers.survey_points ? mapData.survey_points : { type: 'FeatureCollection', features: [] },
        parcels: visibleLayers.parcels ? mapData.parcels : { type: 'FeatureCollection', features: [] },
        drone_coverage: visibleLayers.drone_coverage
          ? mapData.drone_coverage
          : { type: 'FeatureCollection', features: [] },
      }
    : null

  if (error) {
    return (
      <div className="h-screen flex items-center justify-center">
        <div className="text-center">
          <MapPin size={48} className="mx-auto mb-4 text-red-500" />
          <p className="text-red-600">Error al cargar los datos del mapa</p>
        </div>
      </div>
    )
  }

  return (
    <>
      <Helmet>
        <title>Mapa del Proyecto - Portal del Cliente</title>
      </Helmet>

      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Mapa del Proyecto</h1>
          {mapData && <p className="text-gray-600 mt-2">{mapData.project_name}</p>}
        </div>

        {/* Main Content */}
        <div className="flex gap-6">
          {/* Map */}
          <div className="flex-1 rounded-lg shadow-md overflow-hidden bg-white h-96">
            {isLoading ? (
              <div className="h-full flex items-center justify-center">
                <div className="text-center">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                  <p className="text-gray-600">Cargando mapa...</p>
                </div>
              </div>
            ) : (
              <MapComponent
                center={[19.0, -69.0]}
                zoom={12}
                geojsonData={filteredGeojsonData}
                className="h-full w-full"
              />
            )}
          </div>

          {/* Legend and Controls */}
          <div className="w-80">
            {/* Layer Toggle */}
            <div className="bg-white rounded-lg shadow-md p-4 mb-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Capas Visibles</h3>
              <div className="space-y-2">
                <button
                  onClick={() => toggleLayer('survey_points')}
                  className="w-full flex items-center gap-3 p-2 rounded-lg hover:bg-gray-50 transition"
                >
                  <div className={`w-4 h-4 rounded ${visibleLayers.survey_points ? 'bg-blue-500' : 'bg-gray-300'}`}></div>
                  <div className="flex-1 text-left">
                    <p className="font-medium text-gray-900">Puntos Topográficos</p>
                    <p className="text-xs text-gray-600">
                      {mapData?.survey_points.length || 0} puntos
                    </p>
                  </div>
                  {visibleLayers.survey_points ? (
                    <Eye size={16} className="text-gray-500" />
                  ) : (
                    <EyeOff size={16} className="text-gray-400" />
                  )}
                </button>

                <button
                  onClick={() => toggleLayer('drone_coverage')}
                  className="w-full flex items-center gap-3 p-2 rounded-lg hover:bg-gray-50 transition"
                >
                  <div className={`w-4 h-4 rounded ${visibleLayers.drone_coverage ? 'bg-pink-500' : 'bg-gray-300'}`}></div>
                  <div className="flex-1 text-left">
                    <p className="font-medium text-gray-900">Cobertura de Dron</p>
                    <p className="text-xs text-gray-600">
                      {mapData?.drone_coverage.length || 0} vuelos
                    </p>
                  </div>
                  {visibleLayers.drone_coverage ? (
                    <Eye size={16} className="text-gray-500" />
                  ) : (
                    <EyeOff size={16} className="text-gray-400" />
                  )}
                </button>

                <button
                  onClick={() => toggleLayer('parcels')}
                  className="w-full flex items-center gap-3 p-2 rounded-lg hover:bg-gray-50 transition"
                >
                  <div className={`w-4 h-4 rounded ${visibleLayers.parcels ? 'bg-green-500' : 'bg-gray-300'}`}></div>
                  <div className="flex-1 text-left">
                    <p className="font-medium text-gray-900">Parcelas</p>
                    <p className="text-xs text-gray-600">
                      {mapData?.parcels.length || 0} parcelas
                    </p>
                  </div>
                  {visibleLayers.parcels ? (
                    <Eye size={16} className="text-gray-500" />
                  ) : (
                    <EyeOff size={16} className="text-gray-400" />
                  )}
                </button>
              </div>
            </div>

            {/* Legend */}
            <div className="bg-white rounded-lg shadow-md p-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Leyenda</h3>
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <div className="w-6 h-6 bg-blue-500 rounded-full border-2 border-blue-700"></div>
                  <p className="text-sm text-gray-700">Puntos Topográficos</p>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-6 h-6 bg-pink-300 opacity-50 border-2 border-pink-600"></div>
                  <p className="text-sm text-gray-700">Área de Cobertura</p>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-6 h-6 bg-green-400"></div>
                  <p className="text-sm text-gray-700">Marcador de Parcela</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}
