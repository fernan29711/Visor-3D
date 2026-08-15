import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Bell, X, AlertCircle, Info, CheckCircle } from 'lucide-react'
import { apiClient } from '../../services/api'

interface Notification {
  id: string
  notification_type: string
  title: string
  message: string
  priority: string
  is_read: boolean
  created_at: string
  action_url?: string
}

export default function NotificationCenter() {
  const [isOpen, setIsOpen] = useState(false)

  const { data: settings, refetch } = useQuery({
    queryKey: ['notification-settings'],
    queryFn: async () => {
      try {
        const response = await apiClient.client.get('/notifications/settings')
        return response.data
      } catch {
        return null
      }
    },
  })

  const handleMarkAsRead = async (notificationId: string) => {
    try {
      await apiClient.client.patch(`/notifications/${notificationId}/read`)
      refetch()
    } catch (error) {
      console.error('Error marking notification as read:', error)
    }
  }

  const handleDelete = async (notificationId: string) => {
    try {
      await apiClient.client.delete(`/notifications/${notificationId}`)
      refetch()
    } catch (error) {
      console.error('Error deleting notification:', error)
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical':
        return 'text-red-600 bg-red-50'
      case 'high':
        return 'text-orange-600 bg-orange-50'
      case 'medium':
        return 'text-yellow-600 bg-yellow-50'
      default:
        return 'text-blue-600 bg-blue-50'
    }
  }

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'critical':
      case 'high':
        return <AlertCircle size={16} />
      case 'medium':
        return <Info size={16} />
      default:
        return <CheckCircle size={16} />
    }
  }

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition"
      >
        <Bell size={20} />
        {settings?.unread_count > 0 && (
          <span className="absolute top-1 right-1 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
            {Math.min(settings.unread_count, 9)}
          </span>
        )}
        {settings?.has_critical && (
          <span className="absolute top-0 right-0 w-2 h-2 bg-red-600 rounded-full animate-pulse" />
        )}
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-96 bg-white rounded-lg shadow-lg z-50 max-h-96 overflow-y-auto">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b bg-gray-50 sticky top-0">
            <h3 className="font-bold text-gray-900">Notificaciones</h3>
            <div className="flex items-center gap-2">
              {settings?.unread_count > 0 && (
                <span className="text-xs bg-red-100 text-red-800 px-2 py-1 rounded">
                  {settings.unread_count} sin leer
                </span>
              )}
              <button
                onClick={() => setIsOpen(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                <X size={18} />
              </button>
            </div>
          </div>

          {/* Notifications List */}
          <div>
            {settings?.recent_notifications && settings.recent_notifications.length > 0 ? (
              settings.recent_notifications.map((notif: Notification) => (
                <div
                  key={notif.id}
                  className={`p-4 border-b hover:bg-gray-50 transition ${
                    !notif.is_read ? 'bg-blue-50' : ''
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <div className={`mt-1 ${getPriorityColor(notif.priority)}`}>
                      {getPriorityIcon(notif.priority)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-2">
                        <div>
                          <p className={`text-sm font-semibold truncate ${
                            !notif.is_read ? 'text-gray-900' : 'text-gray-700'
                          }`}>
                            {notif.title}
                          </p>
                          <p className="text-xs text-gray-600 mt-1 line-clamp-2">
                            {notif.message}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2 mt-2">
                        <p className="text-xs text-gray-500">
                          {new Date(notif.created_at).toLocaleDateString('es-ES', {
                            month: 'short',
                            day: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit',
                          })}
                        </p>
                        {!notif.is_read && (
                          <button
                            onClick={() => handleMarkAsRead(notif.id)}
                            className="text-xs text-blue-600 hover:text-blue-800"
                          >
                            Marcar como leído
                          </button>
                        )}
                        <button
                          onClick={() => handleDelete(notif.id)}
                          className="text-xs text-gray-500 hover:text-red-600"
                        >
                          Eliminar
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="p-8 text-center text-gray-500">
                <Bell size={32} className="mx-auto mb-2 text-gray-400" />
                <p>No hay notificaciones</p>
              </div>
            )}
          </div>

          {/* Footer */}
          {settings?.recent_notifications && settings.recent_notifications.length > 0 && (
            <div className="p-3 border-t bg-gray-50 text-center">
              <a
                href="/notifications"
                className="text-sm text-blue-600 hover:text-blue-800 font-medium"
              >
                Ver todas las notificaciones
              </a>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
