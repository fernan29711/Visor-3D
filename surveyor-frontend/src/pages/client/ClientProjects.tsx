import { useQuery } from '@tanstack/react-query'
import { Helmet } from 'react-helmet-async'
import { MapPin, Calendar, TrendingUp } from 'lucide-react'
import { apiClient } from '../../services/api'

interface Project {
  id: string
  project_name: string
  location: string
  status: string
  start_date: string
  estimated_end_date?: string
  total_budget: number
  total_spent: number
  progress_percentage: number
  description?: string
}

export default function ClientProjects() {
  const { data: projects } = useQuery({
    queryKey: ['client-projects'],
    queryFn: async () => {
      try {
        const response = await apiClient.client.get('/client-portal/projects')
        return response.data as Project[]
      } catch {
        return []
      }
    },
  })

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800'
      case 'in_progress':
        return 'bg-blue-100 text-blue-800'
      case 'paused':
        return 'bg-yellow-100 text-yellow-800'
      case 'cancelled':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <>
      <Helmet>
        <title>Proyectos - Portal del Cliente</title>
      </Helmet>

      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Mis Proyectos</h1>
          <p className="text-gray-600 mt-2">Visualiza el estado y detalles de tus proyectos</p>
        </div>

        {/* Projects Grid */}
        {projects && projects.length > 0 ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {projects.map((project) => (
              <div
                key={project.id}
                className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition cursor-pointer"
                onClick={() => (window.location.href = `/client/projects/${project.id}`)}
              >
                {/* Header */}
                <div className="bg-gradient-to-r from-blue-500 to-blue-600 p-6 text-white">
                  <h3 className="text-xl font-bold">{project.project_name}</h3>
                  <div className="flex items-center gap-2 mt-2 text-blue-100">
                    <MapPin size={16} />
                    <span>{project.location}</span>
                  </div>
                </div>

                {/* Content */}
                <div className="p-6 space-y-4">
                  {/* Status */}
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600 text-sm">Estado</span>
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(project.status)}`}>
                      {project.status === 'completed'
                        ? 'Completado'
                        : project.status === 'in_progress'
                        ? 'En Progreso'
                        : project.status === 'paused'
                        ? 'Pausado'
                        : 'Cancelado'}
                    </span>
                  </div>

                  {/* Dates */}
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-gray-600 text-sm">Inicio</p>
                      <p className="font-semibold text-gray-900">
                        {new Date(project.start_date).toLocaleDateString('es-DO')}
                      </p>
                    </div>
                    {project.estimated_end_date && (
                      <div>
                        <p className="text-gray-600 text-sm">Fin Estimado</p>
                        <p className="font-semibold text-gray-900">
                          {new Date(project.estimated_end_date).toLocaleDateString('es-DO')}
                        </p>
                      </div>
                    )}
                  </div>

                  {/* Budget Info */}
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <p className="text-gray-600 text-sm">Presupuesto</p>
                      <p className="font-semibold text-gray-900">
                        RD${project.total_spent.toLocaleString('es-DO', { minimumFractionDigits: 2 })} /
                        RD${project.total_budget.toLocaleString('es-DO', { minimumFractionDigits: 2 })}
                      </p>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full transition ${
                          project.progress_percentage > 100
                            ? 'bg-red-500'
                            : project.progress_percentage > 80
                            ? 'bg-yellow-500'
                            : 'bg-green-500'
                        }`}
                        style={{ width: `${Math.min(project.progress_percentage, 100)}%` }}
                      />
                    </div>
                    <p className="text-sm text-gray-600 mt-1">
                      {project.progress_percentage}% utilizado
                    </p>
                  </div>

                  {/* Description */}
                  {project.description && (
                    <div className="border-t pt-4">
                      <p className="text-gray-600 text-sm">{project.description}</p>
                    </div>
                  )}

                  {/* Footer */}
                  <div className="border-t pt-4 flex gap-2">
                    <button className="flex-1 flex items-center justify-center gap-2 py-2 px-4 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition font-medium text-sm">
                      <TrendingUp size={16} />
                      Ver Detalles
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow-md p-12 text-center">
            <MapPin size={48} className="mx-auto mb-4 text-gray-300" />
            <p className="text-gray-600">No hay proyectos asignados</p>
          </div>
        )}
      </div>
    </>
  )
}
