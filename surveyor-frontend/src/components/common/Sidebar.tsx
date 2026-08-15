import { Link } from 'react-router-dom'
import { Menu, Home, Map, FileText, Settings, DollarSign, Receipt, BarChart3 } from 'lucide-react'

export default function Sidebar() {
  return (
    <aside className="w-64 bg-white border-r border-gray-200 p-6">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-primary-600">📐 Surveyor</h1>
        <p className="text-sm text-gray-600">SaaS Professional</p>
      </div>

      <nav className="space-y-2">
        <Link to="/" className="flex items-center gap-3 px-4 py-2 rounded-lg hover:bg-gray-100 text-gray-700">
          <Home size={20} />
          Dashboard
        </Link>
        <Link to="/financial" className="flex items-center gap-3 px-4 py-2 rounded-lg hover:bg-gray-100 text-gray-700">
          <BarChart3 size={20} />
          Financiero
        </Link>
        <Link to="/projects" className="flex items-center gap-3 px-4 py-2 rounded-lg hover:bg-gray-100 text-gray-700">
          <Menu size={20} />
          Proyectos
        </Link>
        <Link to="/quotes" className="flex items-center gap-3 px-4 py-2 rounded-lg hover:bg-gray-100 text-gray-700">
          <DollarSign size={20} />
          Cotizaciones
        </Link>
        <Link to="/invoices" className="flex items-center gap-3 px-4 py-2 rounded-lg hover:bg-gray-100 text-gray-700">
          <Receipt size={20} />
          Facturas
        </Link>
        <Link to="/map" className="flex items-center gap-3 px-4 py-2 rounded-lg hover:bg-gray-100 text-gray-700">
          <Map size={20} />
          Mapa
        </Link>
        <Link to="/reports" className="flex items-center gap-3 px-4 py-2 rounded-lg hover:bg-gray-100 text-gray-700">
          <FileText size={20} />
          Reportes
        </Link>
        <Link to="/settings" className="flex items-center gap-3 px-4 py-2 rounded-lg hover:bg-gray-100 text-gray-700">
          <Settings size={20} />
          Configuración
        </Link>
      </nav>
    </aside>
  )
}
