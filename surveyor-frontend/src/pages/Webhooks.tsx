import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Helmet } from 'react-helmet-async'
import { Plus, Trash2, Edit2, Eye, Check, X, Send, AlertCircle } from 'lucide-react'
import { apiClient } from '../services/api'

interface Webhook {
  id: string
  name: string
  url: string
  events: string[]
  is_active: boolean
  status: string
  retry_count: number
  retry_delay_seconds: number
  created_at: string
  last_triggered_at?: string
}

interface Delivery {
  id: string
  event_type: string
  status: string
  response_status?: number
  error_message?: string
  created_at: string
}

export default function Webhooks() {
  const queryClient = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [selectedWebhook, setSelectedWebhook] = useState<Webhook | null>(null)
  const [showDeliveries, setShowDeliveries] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    url: '',
    events: [] as string[],
    is_active: true,
    retry_count: 3,
    retry_delay_seconds: 300,
  })

  const { data: webhooks = [], isLoading } = useQuery({
    queryKey: ['webhooks'],
    queryFn: async () => {
      const response = await apiClient.get('/webhooks')
      return response.data
    },
  })

  const { data: events = [] } = useQuery({
    queryKey: ['webhook-events'],
    queryFn: async () => {
      const response = await apiClient.get('/webhooks/events')
      return response.data
    },
  })

  const { data: deliveries = { total: 0, items: [] } } = useQuery({
    queryKey: ['webhook-deliveries', selectedWebhook?.id],
    queryFn: async () => {
      if (!selectedWebhook) return { total: 0, items: [] }
      const response = await apiClient.get(`/webhooks/${selectedWebhook.id}/deliveries`)
      return response.data
    },
    enabled: !!selectedWebhook,
  })

  const createMutation = useMutation({
    mutationFn: (data: any) => apiClient.post('/webhooks', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['webhooks'] })
      setShowForm(false)
      resetForm()
    },
  })

  const updateMutation = useMutation({
    mutationFn: (data: any) => apiClient.patch(`/webhooks/${editingId}`, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['webhooks'] })
      setEditingId(null)
      resetForm()
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => apiClient.delete(`/webhooks/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['webhooks'] })
    },
  })

  const testMutation = useMutation({
    mutationFn: (id: string) => apiClient.post(`/webhooks/${id}/test`, {}),
  })

  const resetForm = () => {
    setFormData({
      name: '',
      url: '',
      events: [],
      is_active: true,
      retry_count: 3,
      retry_delay_seconds: 300,
    })
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (editingId) {
      await updateMutation.mutateAsync(formData)
    } else {
      await createMutation.mutateAsync(formData)
    }
  }

  const handleEdit = (webhook: Webhook) => {
    setEditingId(webhook.id)
    setFormData({
      name: webhook.name,
      url: webhook.url,
      events: webhook.events,
      is_active: webhook.is_active,
      retry_count: webhook.retry_count,
      retry_delay_seconds: webhook.retry_delay_seconds,
    })
    setShowForm(true)
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800'
      case 'inactive':
        return 'bg-gray-100 text-gray-800'
      case 'failed':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getDeliveryStatusColor = (status: string) => {
    switch (status) {
      case 'delivered':
        return 'bg-green-100 text-green-800'
      case 'pending':
        return 'bg-yellow-100 text-yellow-800'
      case 'failed':
        return 'bg-red-100 text-red-800'
      case 'retrying':
        return 'bg-orange-100 text-orange-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <>
      <Helmet>
        <title>Webhooks - Visor 3D Surveyor</title>
      </Helmet>

      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Webhooks</h1>
            <p className="text-gray-600 mt-2">Manage webhook integrations for your organization</p>
          </div>
          <button
            onClick={() => {
              setEditingId(null)
              resetForm()
              setShowForm(true)
            }}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-medium"
          >
            <Plus size={18} />
            New Webhook
          </button>
        </div>

        {/* Form */}
        {showForm && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              {editingId ? 'Edit Webhook' : 'Create Webhook'}
            </h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">URL</label>
                <input
                  type="url"
                  value={formData.url}
                  onChange={(e) => setFormData({ ...formData, url: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Events</label>
                <div className="grid grid-cols-2 gap-2 max-h-48 overflow-y-auto border border-gray-300 rounded-lg p-3">
                  {events.map((event: any) => (
                    <label key={event.value} className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={formData.events.includes(event.value)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setFormData({
                              ...formData,
                              events: [...formData.events, event.value],
                            })
                          } else {
                            setFormData({
                              ...formData,
                              events: formData.events.filter((ev) => ev !== event.value),
                            })
                          }
                        }}
                        className="w-4 h-4 rounded"
                      />
                      <span className="text-sm text-gray-700">{event.label}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Retry Count</label>
                  <input
                    type="number"
                    min="0"
                    max="10"
                    value={formData.retry_count}
                    onChange={(e) => setFormData({ ...formData, retry_count: parseInt(e.target.value) })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Retry Delay (seconds)</label>
                  <input
                    type="number"
                    min="60"
                    max="3600"
                    step="60"
                    value={formData.retry_delay_seconds}
                    onChange={(e) => setFormData({ ...formData, retry_delay_seconds: parseInt(e.target.value) })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={formData.is_active}
                    onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                    className="w-4 h-4 rounded"
                  />
                  <span className="text-sm font-medium text-gray-700">Active</span>
                </label>
              </div>

              <div className="flex gap-2 pt-4">
                <button
                  type="submit"
                  disabled={createMutation.isPending || updateMutation.isPending}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-medium disabled:opacity-50"
                >
                  {editingId ? 'Update' : 'Create'} Webhook
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowForm(false)
                    setEditingId(null)
                    resetForm()
                  }}
                  className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition font-medium"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Webhooks List */}
        {isLoading ? (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          </div>
        ) : webhooks.length > 0 ? (
          <div className="space-y-3">
            {webhooks.map((webhook: Webhook) => (
              <div key={webhook.id} className="bg-white rounded-lg shadow-md p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900">{webhook.name}</h3>
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(webhook.status)}`}>
                        {webhook.status}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">{webhook.url}</p>
                    <div className="flex items-center gap-4 text-sm text-gray-600">
                      <span>{webhook.events.length} event(s)</span>
                      <span>Retry: {webhook.retry_count} × {webhook.retry_delay_seconds}s</span>
                      {webhook.last_triggered_at && (
                        <span>Last triggered: {new Date(webhook.last_triggered_at).toLocaleString()}</span>
                      )}
                    </div>
                  </div>

                  <div className="flex gap-2">
                    <button
                      onClick={() => setSelectedWebhook(webhook) || setShowDeliveries(true)}
                      title="View deliveries"
                      className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition"
                    >
                      <Eye size={18} />
                    </button>
                    <button
                      onClick={() => testMutation.mutate(webhook.id)}
                      title="Test webhook"
                      className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition"
                    >
                      <Send size={18} />
                    </button>
                    <button
                      onClick={() => handleEdit(webhook)}
                      title="Edit webhook"
                      className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition"
                    >
                      <Edit2 size={18} />
                    </button>
                    <button
                      onClick={() => {
                        if (confirm('Delete this webhook?')) {
                          deleteMutation.mutate(webhook.id)
                        }
                      }}
                      title="Delete webhook"
                      className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition"
                    >
                      <Trash2 size={18} />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow-md p-12 text-center">
            <AlertCircle size={48} className="mx-auto mb-4 text-gray-300" />
            <p className="text-gray-600">No webhooks configured yet</p>
          </div>
        )}

        {/* Deliveries Modal */}
        {showDeliveries && selectedWebhook && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg shadow-lg max-w-4xl w-full max-h-96 overflow-hidden flex flex-col">
              <div className="flex items-center justify-between p-6 border-b">
                <h2 className="text-xl font-semibold text-gray-900">
                  Delivery Logs - {selectedWebhook.name}
                </h2>
                <button
                  onClick={() => {
                    setShowDeliveries(false)
                    setSelectedWebhook(null)
                  }}
                  className="p-1 hover:bg-gray-100 rounded"
                >
                  <X size={20} />
                </button>
              </div>

              <div className="flex-1 overflow-y-auto">
                {deliveries.items.length > 0 ? (
                  <table className="w-full text-sm">
                    <thead className="bg-gray-50 sticky top-0">
                      <tr>
                        <th className="px-4 py-2 text-left text-gray-900 font-medium">Event</th>
                        <th className="px-4 py-2 text-left text-gray-900 font-medium">Status</th>
                        <th className="px-4 py-2 text-left text-gray-900 font-medium">Response</th>
                        <th className="px-4 py-2 text-left text-gray-900 font-medium">Timestamp</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y">
                      {deliveries.items.map((delivery: Delivery) => (
                        <tr key={delivery.id} className="hover:bg-gray-50">
                          <td className="px-4 py-2 text-gray-700">{delivery.event_type}</td>
                          <td className="px-4 py-2">
                            <span className={`px-2 py-1 rounded text-xs font-medium ${getDeliveryStatusColor(delivery.status)}`}>
                              {delivery.status}
                            </span>
                          </td>
                          <td className="px-4 py-2 text-gray-600">
                            {delivery.response_status || delivery.error_message || '-'}
                          </td>
                          <td className="px-4 py-2 text-gray-600 text-xs">
                            {new Date(delivery.created_at).toLocaleString()}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                ) : (
                  <div className="p-8 text-center text-gray-600">
                    No deliveries yet
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </>
  )
}
