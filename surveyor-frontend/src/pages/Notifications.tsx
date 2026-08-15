import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { Helmet } from 'react-helmet-async'
import { Bell, Settings, AlertCircle, Info, CheckCircle, Trash2, Check } from 'lucide-react'
import { apiClient } from '../services/api'

interface Notification {
  id: string
  notification_type: string
  title: string
  message: string
  priority: string
  is_read: boolean
  created_at: string
  related_entity_type?: string
  related_entity_id?: string
  action_url?: string
}

interface NotificationPreferences {
  id: string
  quote_notifications: boolean
  invoice_notifications: boolean
  project_notifications: boolean
  flight_notifications: boolean
  system_notifications: boolean
  email_enabled: boolean
  sms_enabled: boolean
  push_enabled: boolean
  quiet_hours_enabled: boolean
  quiet_hours_start?: string
  quiet_hours_end?: string
  email_digest: boolean
  email_frequency: string
  critical_alerts_always_on: boolean
}

export default function Notifications() {
  const [activeTab, setActiveTab] = useState<'notifications' | 'preferences'>('notifications')
  const [selectedNotifications, setSelectedNotifications] = useState<Set<string>>(new Set())
  const [preferences, setPreferences] = useState<NotificationPreferences | null>(null)

  const { data: notifications, refetch: refetchNotifications } = useQuery({
    queryKey: ['notifications'],
    queryFn: async () => {
      try {
        const response = await apiClient.client.get('/notifications?limit=100')
        return response.data as Notification[]
      } catch {
        return []
      }
    },
  })

  const { data: preferencesData } = useQuery({
    queryKey: ['notification-preferences'],
    queryFn: async () => {
      try {
        const response = await apiClient.client.get('/notifications/preferences/me')
        setPreferences(response.data)
        return response.data
      } catch {
        return null
      }
    },
  })

  const markAsReadMutation = useMutation({
    mutationFn: async (notificationId: string) => {
      await apiClient.client.patch(`/notifications/${notificationId}/read`)
    },
    onSuccess: () => {
      refetchNotifications()
    },
  })

  const deleteNotificationMutation = useMutation({
    mutationFn: async (notificationId: string) => {
      await apiClient.client.delete(`/notifications/${notificationId}`)
    },
    onSuccess: () => {
      refetchNotifications()
    },
  })

  const updatePreferencesMutation = useMutation({
    mutationFn: async (data: Partial<NotificationPreferences>) => {
      const response = await apiClient.client.put('/notifications/preferences/me', data)
      return response.data
    },
    onSuccess: (data) => {
      setPreferences(data)
    },
  })

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical':
        return 'bg-red-100 text-red-800'
      case 'high':
        return 'bg-orange-100 text-orange-800'
      case 'medium':
        return 'bg-yellow-100 text-yellow-800'
      default:
        return 'bg-blue-100 text-blue-800'
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

  const handleToggleNotification = (notificationId: string) => {
    const newSelected = new Set(selectedNotifications)
    if (newSelected.has(notificationId)) {
      newSelected.delete(notificationId)
    } else {
      newSelected.add(notificationId)
    }
    setSelectedNotifications(newSelected)
  }

  const handleMarkSelectedAsRead = () => {
    selectedNotifications.forEach(id => {
      markAsReadMutation.mutate(id)
    })
    setSelectedNotifications(new Set())
  }

  const handleDeleteSelected = () => {
    selectedNotifications.forEach(id => {
      deleteNotificationMutation.mutate(id)
    })
    setSelectedNotifications(new Set())
  }

  const handlePreferenceChange = (field: keyof NotificationPreferences, value: boolean | string) => {
    const updated = { ...preferences, [field]: value }
    setPreferences(updated as NotificationPreferences)
    updatePreferencesMutation.mutate({ [field]: value })
  }

  return (
    <>
      <Helmet>
        <title>Notificaciones - Visor 3D Surveyor</title>
      </Helmet>

      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Notificaciones</h1>
          <p className="text-gray-600 mt-2">Gestiona tus alertas y preferencias de notificaciones</p>
        </div>

        {/* Tabs */}
        <div className="flex gap-4 border-b">
          <button
            onClick={() => setActiveTab('notifications')}
            className={`px-4 py-2 font-medium border-b-2 transition ${
              activeTab === 'notifications'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            <div className="flex items-center gap-2">
              <Bell size={20} />
              Notificaciones
            </div>
          </button>
          <button
            onClick={() => setActiveTab('preferences')}
            className={`px-4 py-2 font-medium border-b-2 transition ${
              activeTab === 'preferences'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            <div className="flex items-center gap-2">
              <Settings size={20} />
              Preferencias
            </div>
          </button>
        </div>

        {/* Notifications Tab */}
        {activeTab === 'notifications' && (
          <div className="space-y-4">
            {selectedNotifications.size > 0 && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex items-center justify-between">
                <p className="text-sm text-blue-900">
                  {selectedNotifications.size} notificación(es) seleccionada(s)
                </p>
                <div className="flex gap-2">
                  <button
                    onClick={handleMarkSelectedAsRead}
                    className="flex items-center gap-2 px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
                  >
                    <Check size={16} />
                    Marcar como leído
                  </button>
                  <button
                    onClick={handleDeleteSelected}
                    className="flex items-center gap-2 px-3 py-1 text-sm bg-red-600 text-white rounded hover:bg-red-700"
                  >
                    <Trash2 size={16} />
                    Eliminar
                  </button>
                </div>
              </div>
            )}

            {notifications && notifications.length > 0 ? (
              <div className="space-y-3">
                {notifications.map((notif) => (
                  <div
                    key={notif.id}
                    className={`bg-white p-4 rounded-lg shadow-sm hover:shadow-md transition border-l-4 ${
                      notif.priority === 'critical'
                        ? 'border-red-500'
                        : notif.priority === 'high'
                        ? 'border-orange-500'
                        : notif.priority === 'medium'
                        ? 'border-yellow-500'
                        : 'border-blue-500'
                    } ${!notif.is_read ? 'bg-blue-50' : ''}`}
                  >
                    <div className="flex items-start gap-3">
                      <input
                        type="checkbox"
                        checked={selectedNotifications.has(notif.id)}
                        onChange={() => handleToggleNotification(notif.id)}
                        className="mt-1 w-4 h-4 text-blue-600 rounded"
                      />
                      <div className={`mt-1 ${getPriorityColor(notif.priority)} p-2 rounded`}>
                        {getPriorityIcon(notif.priority)}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-start justify-between">
                          <div>
                            <p className={`font-semibold ${!notif.is_read ? 'text-gray-900' : 'text-gray-700'}`}>
                              {notif.title}
                            </p>
                            <p className="text-sm text-gray-600 mt-1">{notif.message}</p>
                          </div>
                          <span className={`text-xs px-2 py-1 rounded font-medium ${getPriorityColor(notif.priority)}`}>
                            {notif.priority}
                          </span>
                        </div>
                        <div className="flex items-center gap-4 mt-3">
                          <p className="text-xs text-gray-500">
                            {new Date(notif.created_at).toLocaleDateString('es-ES', {
                              year: 'numeric',
                              month: 'long',
                              day: 'numeric',
                              hour: '2-digit',
                              minute: '2-digit',
                            })}
                          </p>
                          {!notif.is_read && (
                            <button
                              onClick={() => markAsReadMutation.mutate(notif.id)}
                              className="text-xs text-blue-600 hover:text-blue-800 font-medium"
                            >
                              Marcar como leído
                            </button>
                          )}
                          <button
                            onClick={() => deleteNotificationMutation.mutate(notif.id)}
                            className="text-xs text-red-600 hover:text-red-800 font-medium"
                          >
                            Eliminar
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="bg-white p-12 rounded-lg text-center">
                <Bell size={48} className="mx-auto mb-4 text-gray-300" />
                <p className="text-gray-600">No hay notificaciones</p>
              </div>
            )}
          </div>
        )}

        {/* Preferences Tab */}
        {activeTab === 'preferences' && preferences && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Notification Types */}
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h2 className="text-lg font-bold text-gray-900 mb-4">Tipos de Notificaciones</h2>
              <div className="space-y-4">
                {[
                  { key: 'quote_notifications', label: 'Cotizaciones' },
                  { key: 'invoice_notifications', label: 'Facturas' },
                  { key: 'project_notifications', label: 'Proyectos' },
                  { key: 'flight_notifications', label: 'Vuelos de Drones' },
                  { key: 'system_notifications', label: 'Alertas del Sistema' },
                ].map(({ key, label }) => (
                  <label key={key} className="flex items-center gap-3">
                    <input
                      type="checkbox"
                      checked={preferences[key as keyof NotificationPreferences] as boolean}
                      onChange={(e) => handlePreferenceChange(key as keyof NotificationPreferences, e.target.checked)}
                      className="w-4 h-4 text-blue-600 rounded"
                    />
                    <span className="text-gray-700">{label}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Channels */}
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h2 className="text-lg font-bold text-gray-900 mb-4">Canales de Entrega</h2>
              <div className="space-y-4">
                {[
                  { key: 'email_enabled', label: 'Email', soon: false },
                  { key: 'sms_enabled', label: 'SMS', soon: true },
                  { key: 'push_enabled', label: 'Notificaciones Push', soon: true },
                ].map(({ key, label, soon }) => (
                  <label key={key} className="flex items-center gap-3 opacity-75">
                    <input
                      type="checkbox"
                      checked={preferences[key as keyof NotificationPreferences] as boolean}
                      onChange={(e) => handlePreferenceChange(key as keyof NotificationPreferences, e.target.checked)}
                      disabled={soon}
                      className="w-4 h-4 text-blue-600 rounded disabled:opacity-50"
                    />
                    <span className="text-gray-700">
                      {label}
                      {soon && <span className="text-xs text-gray-500 ml-2">(próximamente)</span>}
                    </span>
                  </label>
                ))}
              </div>
            </div>

            {/* Email Settings */}
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h2 className="text-lg font-bold text-gray-900 mb-4">Configuración de Email</h2>
              <div className="space-y-4">
                <label className="flex items-center gap-3">
                  <input
                    type="checkbox"
                    checked={preferences.email_digest}
                    onChange={(e) => handlePreferenceChange('email_digest', e.target.checked)}
                    className="w-4 h-4 text-blue-600 rounded"
                  />
                  <span className="text-gray-700">Resumen diario por email</span>
                </label>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Frecuencia de envío
                  </label>
                  <select
                    value={preferences.email_frequency}
                    onChange={(e) => handlePreferenceChange('email_frequency', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                  >
                    <option value="realtime">Tiempo Real</option>
                    <option value="daily">Diario</option>
                    <option value="weekly">Semanal</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Quiet Hours */}
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h2 className="text-lg font-bold text-gray-900 mb-4">Horas Silenciosas</h2>
              <div className="space-y-4">
                <label className="flex items-center gap-3">
                  <input
                    type="checkbox"
                    checked={preferences.quiet_hours_enabled}
                    onChange={(e) => handlePreferenceChange('quiet_hours_enabled', e.target.checked)}
                    className="w-4 h-4 text-blue-600 rounded"
                  />
                  <span className="text-gray-700">Habilitar horas silenciosas</span>
                </label>
                {preferences.quiet_hours_enabled && (
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Inicio
                      </label>
                      <input
                        type="time"
                        value={preferences.quiet_hours_start || '22:00'}
                        onChange={(e) => handlePreferenceChange('quiet_hours_start', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Fin
                      </label>
                      <input
                        type="time"
                        value={preferences.quiet_hours_end || '08:00'}
                        onChange={(e) => handlePreferenceChange('quiet_hours_end', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                      />
                    </div>
                  </div>
                )}
                <label className="flex items-center gap-3 border-t pt-4">
                  <input
                    type="checkbox"
                    checked={preferences.critical_alerts_always_on}
                    onChange={(e) => handlePreferenceChange('critical_alerts_always_on', e.target.checked)}
                    className="w-4 h-4 text-blue-600 rounded"
                  />
                  <span className="text-gray-700">Las alertas críticas siempre se entregan</span>
                </label>
              </div>
            </div>
          </div>
        )}
      </div>
    </>
  )
}
