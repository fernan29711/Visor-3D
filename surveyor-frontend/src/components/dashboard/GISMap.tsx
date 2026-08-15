import { useEffect, useRef } from 'react'
import { useQuery } from '@tanstack/react-query'
import maplibregl from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import { apiClient } from '../../services/api'

interface Project {
  id: string
  name: string
  latitude: number
  longitude: number
}

interface SurveyPoint {
  id: string
  point_number: string
  east: number
  north: number
}

export default function GISMap() {
  const mapContainer = useRef<HTMLDivElement>(null)
  const map = useRef<maplibregl.Map | null>(null)

  const { data: projects } = useQuery({
    queryKey: ['projects-map'],
    queryFn: async () => {
      const response = await apiClient.getProjects({ limit: 100 })
      return response.data as Project[]
    },
  })

  useEffect(() => {
    if (!mapContainer.current) return

    map.current = new maplibregl.Map({
      container: mapContainer.current,
      style: 'https://demotiles.maplibre.org/style.json',
      center: [-70.5, 19.0],
      zoom: 8,
    })

    if (!projects || projects.length === 0) return

    projects.forEach((project) => {
      if (project.latitude && project.longitude) {
        const marker = document.createElement('div')
        marker.className = 'w-8 h-8 bg-blue-500 rounded-full border-2 border-white shadow-lg cursor-pointer'

        new maplibregl.Marker({ element: marker })
          .setLngLat([project.longitude, project.latitude])
          .setPopup(
            new maplibregl.Popup({ offset: 25 }).setHTML(
              `<div class="p-2"><h3 class="font-bold">${project.name}</h3><p class="text-sm text-gray-600">${project.latitude.toFixed(4)}, ${project.longitude.toFixed(4)}</p></div>`
            )
          )
          .addTo(map.current!)
      }
    })
  }, [projects])

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      <div className="p-4 border-b">
        <h3 className="text-lg font-semibold text-gray-900">Ubicación de Proyectos</h3>
      </div>
      <div ref={mapContainer} className="w-full h-96" />
    </div>
  )
}
