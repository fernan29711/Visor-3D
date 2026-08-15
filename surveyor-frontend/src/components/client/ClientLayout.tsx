import { Outlet, useNavigate } from 'react-router-dom'
import { LogOut, User, Menu, X, Bell } from 'lucide-react'
import { useState } from 'react'

export default function ClientLayout() {
  const navigate = useNavigate()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const handleLogout = () => {
    localStorage.removeItem('token')
    navigate('/login')
  }

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <aside
        className={`${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        } md:translate-x-0 fixed md:relative z-30 w-64 h-full bg-white border-r border-gray-200 transition-transform duration-300`}
      >
        <div className="p-6">
          <h1 className="text-2xl font-bold text-blue-600">📐 Surveyor</h1>
          <p className="text-sm text-gray-600">Portal del Cliente</p>
        </div>

        <nav className="space-y-2 px-4">
          <button
            onClick={() => {
              navigate('/client/dashboard')
              setSidebarOpen(false)
            }}
            className="w-full text-left flex items-center gap-3 px-4 py-2 rounded-lg hover:bg-gray-100 text-gray-700"
          >
            <span>📊</span>
            Dashboard
          </button>
          <button
            onClick={() => {
              navigate('/client/quotes')
              setSidebarOpen(false)
            }}
            className="w-full text-left flex items-center gap-3 px-4 py-2 rounded-lg hover:bg-gray-100 text-gray-700"
          >
            <span>💰</span>
            Cotizaciones
          </button>
          <button
            onClick={() => {
              navigate('/client/invoices')
              setSidebarOpen(false)
            }}
            className="w-full text-left flex items-center gap-3 px-4 py-2 rounded-lg hover:bg-gray-100 text-gray-700"
          >
            <span>📄</span>
            Facturas
          </button>
          <button
            onClick={() => {
              navigate('/client/projects')
              setSidebarOpen(false)
            }}
            className="w-full text-left flex items-center gap-3 px-4 py-2 rounded-lg hover:bg-gray-100 text-gray-700"
          >
            <span>📍</span>
            Proyectos
          </button>
        </nav>
      </aside>

      {/* Close sidebar on mobile overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 md:hidden z-20"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="bg-white border-b border-gray-200 px-6 py-4 flex justify-between items-center">
          <div className="flex items-center gap-4">
            <button
              className="md:hidden p-2 hover:bg-gray-100 rounded-lg"
              onClick={() => setSidebarOpen(!sidebarOpen)}
            >
              {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
            </button>
            <h2 className="text-lg font-semibold text-gray-800">Portal del Cliente</h2>
          </div>

          <div className="flex items-center gap-4">
            <button className="relative p-2 text-gray-600 hover:bg-gray-100 rounded-lg">
              <Bell size={20} />
            </button>
            <div className="flex items-center gap-3 pl-4 border-l border-gray-200">
              <button className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg">
                <User size={20} />
              </button>
              <button
                onClick={handleLogout}
                className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg"
                title="Cerrar sesión"
              >
                <LogOut size={20} />
              </button>
            </div>
          </div>
        </header>

        {/* Main content area */}
        <main className="flex-1 overflow-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
