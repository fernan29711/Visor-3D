import { useEffect, useRef } from 'react'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import 'leaflet-draw/dist/leaflet.draw.css'

interface MapComponentProps {
  center?: [number, number]
  zoom?: number
  geojsonData?: any
  onMapReady?: (map: L.Map) => void
  className?: string
}

export default function MapComponent({
  center = [19.0, -69.0],
  zoom = 12,
  geojsonData,
  onMapReady,
  className = 'w-full h-full',
}: MapComponentProps) {
  const mapRef = useRef<L.Map | null>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const layersRef = useRef<{ [key: string]: L.LayerGroup }>({})

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return

    mapRef.current = L.map(containerRef.current).setView(center, zoom)

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors',
      maxZoom: 19,
    }).addTo(mapRef.current)

    layersRef.current.survey_points = L.layerGroup().addTo(mapRef.current)
    layersRef.current.parcels = L.layerGroup().addTo(mapRef.current)
    layersRef.current.drone_coverage = L.layerGroup().addTo(mapRef.current)

    if (onMapReady) {
      onMapReady(mapRef.current)
    }

    return () => {
      if (mapRef.current) {
        mapRef.current.remove()
        mapRef.current = null
      }
    }
  }, [center, zoom, onMapReady])

  useEffect(() => {
    if (!mapRef.current || !geojsonData) return

    if (geojsonData.survey_points?.features) {
      const layer = layersRef.current.survey_points
      layer.clearLayers()

      geojsonData.survey_points.features.forEach((feature: any) => {
        if (feature.geometry?.type === 'Point') {
          const [lon, lat] = feature.geometry.coordinates
          L.circleMarker([lat, lon], {
            radius: 6,
            fillColor: '#3b82f6',
            color: '#1e40af',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.8,
          })
            .bindPopup(
              `<strong>${feature.properties.point_number}</strong><br/>
              Elevation: ${feature.properties.elevation}m<br/>
              Code: ${feature.properties.code || 'N/A'}`
            )
            .addTo(layer)
        }
      })
    }

    if (geojsonData.drone_coverage?.features) {
      const layer = layersRef.current.drone_coverage
      layer.clearLayers()

      geojsonData.drone_coverage.features.forEach((feature: any) => {
        if (feature.geometry?.type === 'Polygon') {
          L.polygon(
            feature.geometry.coordinates[0].map((coord: [number, number]) => [coord[1], coord[0]]),
            {
              color: '#ec4899',
              weight: 2,
              opacity: 0.5,
              fillColor: '#ec4899',
              fillOpacity: 0.1,
            }
          )
            .bindPopup(
              `<strong>${feature.properties.flight_name}</strong><br/>
              Date: ${new Date(feature.properties.flight_date).toLocaleDateString()}<br/>
              Coverage: ${feature.properties.area_coverage_hectares}ha<br/>
              Photos: ${feature.properties.photo_count}`
            )
            .addTo(layer)
        }
      })
    }

    if (geojsonData.parcels?.features) {
      const layer = layersRef.current.parcels
      layer.clearLayers()

      geojsonData.parcels.features.forEach((feature: any) => {
        L.marker([feature.properties.lat || 0, feature.properties.lon || 0], {
          icon: L.icon({
            iconUrl: 'https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/images/marker-icon.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41],
          }),
        })
          .bindPopup(
            `<strong>${feature.properties.parcel_number}</strong><br/>
            Owner: ${feature.properties.owner_name || 'N/A'}<br/>
            Area: ${feature.properties.area}m²`
          )
          .addTo(layer)
      })
    }
  }, [geojsonData])

  return (
    <div
      ref={containerRef}
      className={className}
      style={{
        backgroundColor: '#f3f4f6',
        zIndex: 0,
      }}
    />
  )
}
