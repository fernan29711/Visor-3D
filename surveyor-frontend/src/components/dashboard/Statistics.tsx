import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../../services/api'
import { TrendingUp, Users, Briefcase, MapPin } from 'lucide-react'

interface ProjectStats {
  total_projects: number
  pending: number
  in_field: number
  completed: number
  total_clients: number
  total_survey_points: number
  average_budget: number
}

export default function Statistics() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: async () => {
      const response = await apiClient.getProjectsSummary()
      return response.data as ProjectStats
    },
  })

  if (isLoading) {
    return <div className="text-center py-8">Cargando estadísticas...</div>
  }

  const cards = [
    {
      label: 'Proyectos Total',
      value: stats?.total_projects || 0,
      icon: Briefcase,
      color: 'bg-blue-500',
    },
    {
      label: 'En Campo',
      value: stats?.in_field || 0,
      icon: MapPin,
      color: 'bg-green-500',
    },
    {
      label: 'Pendientes',
      value: stats?.pending || 0,
      icon: TrendingUp,
      color: 'bg-yellow-500',
    },
    {
      label: 'Clientes',
      value: stats?.total_clients || 0,
      icon: Users,
      color: 'bg-purple-500',
    },
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {cards.map((card) => {
        const Icon = card.icon
        return (
          <div
            key={card.label}
            className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm font-medium">{card.label}</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">
                  {card.value}
                </p>
              </div>
              <div className={`${card.color} p-3 rounded-lg`}>
                <Icon className="w-6 h-6 text-white" />
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}
