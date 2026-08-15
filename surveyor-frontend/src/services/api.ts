"""API Client configuration."""

import axios, { AxiosInstance } from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Add token to requests
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token')
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    // Handle token expiration
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true

          try {
            const refreshToken = localStorage.getItem('refresh_token')
            if (refreshToken) {
              const response = await this.client.post('/auth/refresh', {
                refresh_token: refreshToken,
              })

              const { access_token } = response.data
              localStorage.setItem('access_token', access_token)

              originalRequest.headers.Authorization = `Bearer ${access_token}`
              return this.client(originalRequest)
            }
          } catch (refreshError) {
            localStorage.removeItem('access_token')
            localStorage.removeItem('refresh_token')
            window.location.href = '/login'
          }
        }

        return Promise.reject(error)
      }
    )
  }

  // Auth endpoints
  register(data: any) {
    return this.client.post('/auth/register', data)
  }

  login(email: string, password: string) {
    return this.client.post('/auth/login', { email, password })
  }

  logout() {
    return this.client.post('/auth/logout')
  }

  // User endpoints
  getCurrentUser() {
    return this.client.get('/users/me')
  }

  // Project endpoints
  getProjects(params?: any) {
    return this.client.get('/projects', { params })
  }

  getProject(id: string) {
    return this.client.get(`/projects/${id}`)
  }

  createProject(data: any) {
    return this.client.post('/projects', data)
  }

  updateProject(id: string, data: any) {
    return this.client.patch(`/projects/${id}`, data)
  }

  deleteProject(id: string) {
    return this.client.delete(`/projects/${id}`)
  }

  getProjectsSummary() {
    return this.client.get('/projects/summary')
  }

  changeProjectStatus(id: string, status: string) {
    return this.client.post(`/projects/${id}/status/${status}`)
  }

  // Client endpoints
  getClients(params?: any) {
    return this.client.get('/clients', { params })
  }

  getClient(id: string) {
    return this.client.get(`/clients/${id}`)
  }

  createClient(data: any) {
    return this.client.post('/clients', data)
  }

  updateClient(id: string, data: any) {
    return this.client.patch(`/clients/${id}`, data)
  }

  deleteClient(id: string) {
    return this.client.delete(`/clients/${id}`)
  }

  // Survey points endpoints
  getSurveyPoints(projectId: string, params?: any) {
    return this.client.get(`/projects/${projectId}/survey-points`, { params })
  }

  getSurveyPointBounds(projectId: string) {
    return this.client.get(`/projects/${projectId}/survey-points/bounds`)
  }

  createSurveyPoint(projectId: string, data: any) {
    return this.client.post(`/projects/${projectId}/survey-points`, data)
  }

  updateSurveyPoint(projectId: string, pointId: string, data: any) {
    return this.client.patch(`/projects/${projectId}/survey-points/${pointId}`, data)
  }

  deleteSurveyPoint(projectId: string, pointId: string) {
    return this.client.delete(`/projects/${projectId}/survey-points/${pointId}`)
  }

  importSurveyPoints(projectId: string, data: any) {
    return this.client.post(`/projects/${projectId}/survey-points/bulk/import`, data)
  }

  uploadSurveyPointsCSV(projectId: string, file: File) {
    const formData = new FormData()
    formData.append('file', file)
    return this.client.post(
      `/projects/${projectId}/survey-points/csv/upload`,
      formData,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    )
  }

  exportSurveyPointsCSV(projectId: string) {
    return this.client.get(`/projects/${projectId}/survey-points/csv/export`, {
      responseType: 'blob',
    })
  }

  exportSurveyPointsGeoJSON(projectId: string) {
    return this.client.get(`/projects/${projectId}/survey-points/geojson/export`, {
      responseType: 'blob',
    })
  }

  // Calculations endpoints
  calculateDistance(data: any) {
    return this.client.post('/calculations/distance', data)
  }

  calculateAzimuth(data: any) {
    return this.client.post('/calculations/azimuth', data)
  }

  calculateArea(data: any) {
    return this.client.post('/calculations/area', data)
  }

  calculateSlope(data: any) {
    return this.client.post('/calculations/slope', data)
  }

  // Quote endpoints
  getQuotes(params?: any) {
    return this.client.get('/quotes', { params })
  }

  getQuote(id: string) {
    return this.client.get(`/quotes/${id}`)
  }

  createQuote(data: any) {
    return this.client.post('/quotes', data)
  }

  updateQuote(id: string, data: any) {
    return this.client.patch(`/quotes/${id}`, data)
  }

  deleteQuote(id: string) {
    return this.client.delete(`/quotes/${id}`)
  }

  changeQuoteStatus(id: string, status: string) {
    return this.client.post(`/quotes/${id}/status/${status}`)
  }

  getQuotesForClient(clientId: string) {
    return this.client.get(`/quotes/client/${clientId}`)
  }

  getQuotesSummary() {
    return this.client.get('/quotes/summary')
  }

  // Invoice endpoints
  getInvoices(params?: any) {
    return this.client.get('/invoices', { params })
  }

  getInvoice(id: string) {
    return this.client.get(`/invoices/${id}`)
  }

  createInvoice(data: any) {
    return this.client.post('/invoices', data)
  }

  updateInvoice(id: string, data: any) {
    return this.client.patch(`/invoices/${id}`, data)
  }

  deleteInvoice(id: string) {
    return this.client.delete(`/invoices/${id}`)
  }

  changeInvoiceStatus(id: string, status: string) {
    return this.client.post(`/invoices/${id}/status/${status}`)
  }

  getInvoicesForClient(clientId: string) {
    return this.client.get(`/invoices/client/${clientId}`)
  }

  getInvoicesForProject(projectId: string) {
    return this.client.get(`/invoices/project/${projectId}`)
  }

  getInvoicesSummary() {
    return this.client.get('/invoices/summary')
  }
}

export const apiClient = new ApiClient()
