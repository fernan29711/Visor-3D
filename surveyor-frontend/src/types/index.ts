// User types
export interface User {
  id: string
  email: string
  first_name: string
  last_name: string
  role: UserRole
  is_active: boolean
}

export type UserRole = 'superadmin' | 'admin' | 'agrimensor' | 'technician' | 'client'

// Organization types
export interface Organization {
  id: string
  name: string
  rnc?: string
  logo_url?: string
  subscription_plan: string
}

// Project types
export interface Project {
  id: string
  code: string
  name: string
  client_id: string
  status: ProjectStatus
  municipality?: string
  province?: string
  budget?: number
  spent: number
  created_at: string
  updated_at: string
}

export type ProjectStatus =
  | 'pending'
  | 'planned'
  | 'in_field'
  | 'processing'
  | 'in_review'
  | 'completed'
  | 'delivered'
  | 'archived'

// Survey Point types
export interface SurveyPoint {
  id: string
  project_id: string
  point_number: string
  east: number
  north: number
  elevation?: number
  code?: string
  description?: string
  precision_horizontal?: number
  precision_vertical?: number
  gnss_status?: string
  created_at: string
}

// Geometry types
export interface Geometry {
  type: 'Point' | 'LineString' | 'Polygon'
  coordinates: number[] | number[][] | number[][][]
}

// API Response types
export interface ApiResponse<T> {
  data: T
  message?: string
  status: 'success' | 'error'
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}
