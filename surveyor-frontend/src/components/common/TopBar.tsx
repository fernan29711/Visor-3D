import { User, LogOut } from 'lucide-react'
import NotificationCenter from './NotificationCenter'

export default function TopBar() {
  return (
    <header className="bg-white border-b border-gray-200 px-8 py-4 flex justify-between items-center">
      <h2 className="text-lg font-semibold text-gray-800">Dashboard</h2>

      <div className="flex items-center gap-6">
        <NotificationCenter />

        <div className="flex items-center gap-3 pl-6 border-l border-gray-200">
          <div className="text-right">
            <p className="text-sm font-medium text-gray-800">Usuario</p>
            <p className="text-xs text-gray-600">Admin</p>
          </div>
          <button className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg">
            <User size={20} />
          </button>
          <button className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg">
            <LogOut size={20} />
          </button>
        </div>
      </div>
    </header>
  )
}
