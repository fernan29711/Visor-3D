import Statistics from '../components/dashboard/Statistics'
import ProjectStatusChart from '../components/dashboard/ProjectStatusChart'
import GISMap from '../components/dashboard/GISMap'
import { Helmet } from 'react-helmet-async'

export default function Dashboard() {
  return (
    <>
      <Helmet>
        <title>Dashboard - Visor 3D Surveyor</title>
      </Helmet>

      <div className="space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-2">
            Resumen de proyectos y estadísticas en tiempo real
          </p>
        </div>

        {/* Statistics Cards */}
        <Statistics />

        {/* Charts and Map Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <ProjectStatusChart />
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Actividad Reciente
            </h3>
            <div className="space-y-4">
              <div className="border-l-4 border-blue-500 pl-4 py-2">
                <p className="text-sm font-medium text-gray-900">
                  Proyecto creado
                </p>
                <p className="text-xs text-gray-500">Hace 2 horas</p>
              </div>
              <div className="border-l-4 border-green-500 pl-4 py-2">
                <p className="text-sm font-medium text-gray-900">
                  Puntos importados
                </p>
                <p className="text-xs text-gray-500">Hace 4 horas</p>
              </div>
              <div className="border-l-4 border-yellow-500 pl-4 py-2">
                <p className="text-sm font-medium text-gray-900">
                  Estado actualizado
                </p>
                <p className="text-xs text-gray-500">Hace 1 día</p>
              </div>
            </div>
          </div>
        </div>

        {/* GIS Map */}
        <GISMap />
      </div>
    </>
  )
}
