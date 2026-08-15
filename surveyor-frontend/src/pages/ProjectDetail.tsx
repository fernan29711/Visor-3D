import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../services/api'
import { Helmet } from 'react-helmet-async'
import CSVImportExport from '../components/survey/CSVImportExport'
import { ArrowLeft, MapPin, Map } from 'lucide-react'

interface Project {
  id: string
  code: string
  name: string
  description: string
  status: string
  budget: number
  spent: number
  municipality: string
  province: string
  point_count: number
  latitude: number
  longitude: number
  created_at: string
}

export default function ProjectDetail() {
  const navigate = useNavigate()
  const { projectId } = useParams<{ projectId: string }>()
  const [activeTab, setActiveTab] = useState('overview')

  const { data: project, isLoading } = useQuery({
    queryKey: ['project', projectId],
    queryFn: async () => {
      const response = await apiClient.getProject(projectId!)
      return response.data as Project
    },
    enabled: !!projectId,
  })

  const { data: surveyPoints, isLoading: pointsLoading, refetch: refetchPoints } = useQuery({
    queryKey: ['survey-points', projectId],
    queryFn: async () => {
      const response = await apiClient.getSurveyPoints(projectId!, { limit: 50 })
      return response.data
    },
    enabled: !!projectId && activeTab === 'points',
  })

  if (isLoading) {
    return <div className="text-center py-8">Cargando proyecto...</div>
  }

  if (!project) {
    return <div className="text-center py-8 text-red-600">Proyecto no encontrado</div>
  }

  const spentPercentage = project.budget > 0 ? (project.spent / project.budget) * 100 : 0

  return (
    <>
      <Helmet>
        <title>{project.name} - Visor 3D Surveyor</title>
      </Helmet>

      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center gap-4">
          <button onClick={() => navigate('/projects')} className="p-2 hover:bg-gray-100 rounded-lg">
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{project.name}</h1>
            <p className="text-gray-600">Código: {project.code}</p>
          </div>
        </div>

        {/* Project Info Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-sm text-gray-600">Estado</p>
            <p className="text-xl font-semibold text-gray-900 mt-1">{project.status}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-sm text-gray-600">Puntos Topográficos</p>
            <p className="text-xl font-semibold text-gray-900 mt-1">{project.point_count}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-sm text-gray-600">Ubicación</p>
            <p className="text-sm text-gray-900 mt-1 flex items-center gap-1">
              <MapPin size={16} />
              {project.municipality}, {project.province}
            </p>
          </div>
        </div>

        {/* Budget Progress */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold text-gray-900 mb-4">Presupuesto</h3>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span className="text-gray-700">Gastado vs Presupuesto</span>
                <span className="font-medium">
                  RD$ {project.spent?.toLocaleString() || 0} / RD$ {project.budget?.toLocaleString() || 0}
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all ${
                    spentPercentage > 100 ? 'bg-red-500' : spentPercentage > 80 ? 'bg-yellow-500' : 'bg-green-500'
                  }`}
                  style={{ width: `${Math.min(spentPercentage, 100)}%` }}
                />
              </div>
              <p className="text-xs text-gray-600 mt-1">{spentPercentage.toFixed(1)}% utilizado</p>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200">
          <div className="flex gap-8">
            <button
              onClick={() => setActiveTab('overview')}
              className={`px-4 py-3 font-medium border-b-2 transition ${
                activeTab === 'overview'
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              General
            </button>
            <button
              onClick={() => setActiveTab('points')}
              className={`px-4 py-3 font-medium border-b-2 transition ${
                activeTab === 'points'
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              Puntos Topográficos
            </button>
            <button
              onClick={() => setActiveTab('import')}
              className={`px-4 py-3 font-medium border-b-2 transition ${
                activeTab === 'import'
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              Importar/Exportar
            </button>
            <button
              onClick={() => setActiveTab('map')}
              className={`px-4 py-3 font-medium border-b-2 transition flex items-center gap-2 ${
                activeTab === 'map'
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              <Map size={18} />
              Mapa
            </button>
          </div>
        </div>

        {/* Tab Content */}
        <div>
          {activeTab === 'overview' && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Descripción</h3>
              <p className="text-gray-700">{project.description || 'Sin descripción'}</p>
              <div className="mt-6 pt-6 border-t">
                <h4 className="font-semibold text-gray-900 mb-2">Información adicional</h4>
                <dl className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <dt className="text-gray-600">Municipio</dt>
                    <dd className="text-gray-900 font-medium">{project.municipality}</dd>
                  </div>
                  <div>
                    <dt className="text-gray-600">Provincia</dt>
                    <dd className="text-gray-900 font-medium">{project.province}</dd>
                  </div>
                  <div>
                    <dt className="text-gray-600">Ubicación</dt>
                    <dd className="text-gray-900 font-medium">
                      {project.latitude?.toFixed(4)}, {project.longitude?.toFixed(4)}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-gray-600">Creado</dt>
                    <dd className="text-gray-900 font-medium">
                      {new Date(project.created_at).toLocaleDateString('es-ES')}
                    </dd>
                  </div>
                </dl>
              </div>
            </div>
          )}

          {activeTab === 'points' && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Puntos Topográficos ({project.point_count})
              </h3>
              {pointsLoading ? (
                <p className="text-gray-600">Cargando puntos...</p>
              ) : surveyPoints && surveyPoints.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-2 text-left text-gray-900 font-medium">Punto</th>
                        <th className="px-4 py-2 text-left text-gray-900 font-medium">Este (E)</th>
                        <th className="px-4 py-2 text-left text-gray-900 font-medium">Norte (N)</th>
                        <th className="px-4 py-2 text-left text-gray-900 font-medium">Elevación (Z)</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y">
                      {surveyPoints.map((point: any) => (
                        <tr key={point.id} className="hover:bg-gray-50">
                          <td className="px-4 py-2">{point.point_number}</td>
                          <td className="px-4 py-2">{point.east.toFixed(3)}</td>
                          <td className="px-4 py-2">{point.north.toFixed(3)}</td>
                          <td className="px-4 py-2">{point.elevation.toFixed(2)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p className="text-gray-600">Sin puntos topográficos</p>
              )}
            </div>
          )}

          {activeTab === 'import' && (
            <div className="bg-white rounded-lg shadow p-6">
              <CSVImportExport
                projectId={projectId!}
                onImportSuccess={() => refetchPoints()}
              />
            </div>
          )}

          {activeTab === 'map' && (
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Visualización Geoespacial</h3>
                <button
                  onClick={() => navigate(`/projects/${projectId}/map`)}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-medium flex items-center gap-2"
                >
                  <Map size={18} />
                  Ver Mapa Completo
                </button>
              </div>
              <p className="text-gray-600">
                Haz clic en el botón de arriba para ver la visualización interactiva con puntos topográficos, cobertura de drones y parcelas.
              </p>
            </div>
          )}
        </div>
      </div>
    </>
  )
}
