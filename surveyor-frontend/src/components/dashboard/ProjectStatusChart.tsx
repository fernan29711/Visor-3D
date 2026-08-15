import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../../services/api'
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts'

interface ProjectStats {
  pending: number
  in_field: number
  completed: number
  on_hold: number
  cancelled: number
}

const COLORS = ['#fbbf24', '#10b981', '#3b82f6', '#f59e0b', '#ef4444']

export default function ProjectStatusChart() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['project-status-stats'],
    queryFn: async () => {
      const response = await apiClient.getProjectsSummary()
      return response.data as ProjectStats
    },
  })

  if (isLoading) {
    return <div className="text-center py-8">Cargando gráfico...</div>
  }

  const data = [
    { name: 'Pendientes', value: stats?.pending || 0 },
    { name: 'En Campo', value: stats?.in_field || 0 },
    { name: 'Completados', value: stats?.completed || 0 },
    { name: 'En Pausa', value: stats?.on_hold || 0 },
    { name: 'Cancelados', value: stats?.cancelled || 0 },
  ].filter((item) => item.value > 0)

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-6">
        Proyectos por Estado
      </h3>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, value }) => `${name}: ${value}`}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  )
}
