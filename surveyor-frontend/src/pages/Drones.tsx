import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Helmet } from 'react-helmet-async'
import { apiClient } from '../services/api'
import { Drone, Image, Calendar, MapPin, Eye, Trash2 } from 'lucide-react'

interface DronePhoto {
  id: string
  photo_name: string
  photo_url: string
  thumbnail_url?: string
  gps_latitude?: number
  gps_longitude?: number
  capture_time?: string
}

interface DroneFlight {
  id: string
  flight_name: string
  drone_model?: string
  flight_date: string
  status: string
  altitude_meters?: number
  area_coverage_hectares?: number
  total_photos: number
  processed_photos: number
  created_at: string
}

export default function Drones() {
  const [selectedFlight, setSelectedFlight] = useState<string | null>(null)
  const [selectedPhoto, setSelectedPhoto] = useState<DronePhoto | null>(null)

  const { data: flights } = useQuery({
    queryKey: ['drone-flights'],
    queryFn: async () => {
      try {
        const response = await apiClient.client.get('/drones/flights?limit=50')
        return response.data as DroneFlight[]
      } catch {
        return []
      }
    },
  })

  const { data: flightPhotos } = useQuery({
    queryKey: ['drone-photos', selectedFlight],
    queryFn: async () => {
      if (!selectedFlight) return []
      try {
        const response = await apiClient.client.get(`/drones/flights/${selectedFlight}/photos`)
        return response.data as DronePhoto[]
      } catch {
        return []
      }
    },
    enabled: !!selectedFlight,
  })

  const { data: summary } = useQuery({
    queryKey: ['drone-summary'],
    queryFn: async () => {
      try {
        const response = await apiClient.client.get('/drones/summary')
        return response.data
      } catch {
        return null
      }
    },
  })

  return (
    <>
      <Helmet>
        <title>Drones & 3D - Visor 3D Surveyor</title>
      </Helmet>

      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Drones & Modelos 3D</h1>
          <p className="text-gray-600 mt-2">Gestiona vuelos de drones y visualiza modelos 3D</p>
        </div>

        {/* Summary Cards */}
        {summary && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white p-4 rounded-lg shadow-md">
              <p className="text-gray-600 text-sm">Vuelos Completados</p>
              <p className="text-2xl font-bold text-gray-900">{summary.completed_flights || 0}</p>
            </div>
            <div className="bg-white p-4 rounded-lg shadow-md">
              <p className="text-gray-600 text-sm">Fotos Capturadas</p>
              <p className="text-2xl font-bold text-gray-900">{summary.total_photos_captured || 0}</p>
            </div>
            <div className="bg-white p-4 rounded-lg shadow-md">
              <p className="text-gray-600 text-sm">Área Cubierta (ha)</p>
              <p className="text-2xl font-bold text-gray-900">{summary.total_area_covered_hectares?.toFixed(2) || '0'}</p>
            </div>
            <div className="bg-white p-4 rounded-lg shadow-md">
              <p className="text-gray-600 text-sm">Modelos 3D</p>
              <p className="text-2xl font-bold text-gray-900">{summary.total_3d_models || 0}</p>
            </div>
          </div>
        )}

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Flights List */}
          <div className="lg:col-span-1 bg-white rounded-lg shadow-md overflow-hidden">
            <div className="bg-blue-50 border-b p-4">
              <h2 className="font-bold text-gray-900 flex items-center gap-2">
                <Drone size={20} />
                Vuelos de Drones
              </h2>
            </div>

            <div className="overflow-y-auto max-h-96">
              {flights && flights.length > 0 ? (
                <div className="divide-y">
                  {flights.map((flight) => (
                    <div
                      key={flight.id}
                      onClick={() => setSelectedFlight(flight.id)}
                      className={`p-4 cursor-pointer transition ${
                        selectedFlight === flight.id
                          ? 'bg-blue-100 border-l-4 border-blue-500'
                          : 'hover:bg-gray-50'
                      }`}
                    >
                      <p className="font-semibold text-gray-900 text-sm">{flight.flight_name}</p>
                      <div className="text-xs text-gray-600 mt-2 space-y-1">
                        <p className="flex items-center gap-1">
                          <Calendar size={14} />
                          {new Date(flight.flight_date).toLocaleDateString('es-ES')}
                        </p>
                        {flight.drone_model && (
                          <p className="flex items-center gap-1">
                            <Drone size={14} />
                            {flight.drone_model}
                          </p>
                        )}
                        <p className="flex items-center gap-1">
                          <Image size={14} />
                          {flight.total_photos} fotos
                        </p>
                        {flight.altitude_meters && (
                          <p className="flex items-center gap-1">
                            <MapPin size={14} />
                            {flight.altitude_meters}m altura
                          </p>
                        )}
                      </div>
                      <span className={`text-xs font-semibold mt-2 inline-block px-2 py-1 rounded ${
                        flight.status === 'completed'
                          ? 'bg-green-100 text-green-800'
                          : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {flight.status}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="p-8 text-center text-gray-600">
                  <Drone size={32} className="mx-auto mb-2 text-gray-400" />
                  <p>No hay vuelos de drones</p>
                </div>
              )}
            </div>
          </div>

          {/* Photos Gallery */}
          <div className="lg:col-span-2 bg-white rounded-lg shadow-md overflow-hidden">
            <div className="bg-blue-50 border-b p-4">
              <h2 className="font-bold text-gray-900 flex items-center gap-2">
                <Image size={20} />
                Galería de Fotos
              </h2>
            </div>

            {selectedFlight ? (
              <div className="p-6">
                {flightPhotos && flightPhotos.length > 0 ? (
                  <>
                    {/* Grid of Thumbnails */}
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
                      {flightPhotos.map((photo) => (
                        <div
                          key={photo.id}
                          onClick={() => setSelectedPhoto(photo)}
                          className={`relative cursor-pointer group overflow-hidden rounded-lg aspect-square bg-gray-100 ${
                            selectedPhoto?.id === photo.id ? 'ring-2 ring-blue-500' : ''
                          }`}
                        >
                          <img
                            src={photo.thumbnail_url || photo.photo_url}
                            alt={photo.photo_name}
                            className="w-full h-full object-cover group-hover:scale-110 transition"
                          />
                          <div className="absolute inset-0 bg-black opacity-0 group-hover:opacity-20 transition" />
                          <Eye size={20} className="absolute top-2 right-2 text-white opacity-0 group-hover:opacity-100 transition" />
                        </div>
                      ))}
                    </div>

                    {/* Selected Photo Viewer */}
                    {selectedPhoto && (
                      <div className="border-t pt-6">
                        <h3 className="font-bold text-gray-900 mb-4">{selectedPhoto.photo_name}</h3>
                        <div className="bg-gray-100 rounded-lg overflow-hidden mb-4 aspect-video">
                          <img
                            src={selectedPhoto.photo_url}
                            alt={selectedPhoto.photo_name}
                            className="w-full h-full object-contain"
                          />
                        </div>

                        {/* Photo Details */}
                        <div className="grid grid-cols-2 gap-4 text-sm">
                          {selectedPhoto.gps_latitude && (
                            <>
                              <div>
                                <p className="text-gray-600">Latitud</p>
                                <p className="font-semibold">{selectedPhoto.gps_latitude.toFixed(6)}</p>
                              </div>
                              <div>
                                <p className="text-gray-600">Longitud</p>
                                <p className="font-semibold">{selectedPhoto.gps_longitude?.toFixed(6)}</p>
                              </div>
                            </>
                          )}
                          {selectedPhoto.gps_altitude_meters && (
                            <div>
                              <p className="text-gray-600">Altitud</p>
                              <p className="font-semibold">{selectedPhoto.gps_altitude_meters}m</p>
                            </div>
                          )}
                          {selectedPhoto.capture_time && (
                            <div>
                              <p className="text-gray-600">Captura</p>
                              <p className="font-semibold">
                                {new Date(selectedPhoto.capture_time).toLocaleTimeString('es-ES')}
                              </p>
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </>
                ) : (
                  <div className="p-12 text-center text-gray-600">
                    <Image size={48} className="mx-auto mb-4 text-gray-400" />
                    <p>Este vuelo aún no tiene fotos</p>
                  </div>
                )}
              </div>
            ) : (
              <div className="p-12 text-center text-gray-600">
                <Image size={48} className="mx-auto mb-4 text-gray-400" />
                <p>Selecciona un vuelo para ver sus fotos</p>
              </div>
            )}
          </div>
        </div>

        {/* 3D Models Section */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Modelos 3D Disponibles</h2>
          {summary?.models_by_type && Object.keys(summary.models_by_type).length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {Object.entries(summary.models_by_type).map(([type, count]: [string, any]) => (
                <div key={type} className="bg-gradient-to-br from-blue-50 to-blue-100 p-4 rounded-lg">
                  <p className="text-sm text-gray-600 capitalize">{type.replace(/_/g, ' ')}</p>
                  <p className="text-3xl font-bold text-blue-600">{count}</p>
                  <p className="text-xs text-gray-500 mt-2">modelos disponibles</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-600">No hay modelos 3D generados aún</p>
          )}
        </div>
      </div>
    </>
  )
}
