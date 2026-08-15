# Surveyor SaaS - Arquitectura Técnica

## 1. Visión General

Plataforma profesional SaaS multi-tenant para agrimensura, topografía y gestión de proyectos geoespaciales, diseñada para proporcionar un flujo completo desde la cotización hasta la entrega de entregables.

## 2. Stack Tecnológico

### Frontend
- **React 18** + TypeScript
- **Vite** para build
- **TailwindCSS** para estilos
- **React Router** para navegación
- **React Query** para manejo de estado async
- **MapLibre GL JS** para visualización GIS
- **Turf.js** para cálculos geoespaciales
- **Recharts** para gráficos

### Backend
- **Python 3.11**
- **FastAPI** framework
- **SQLAlchemy** ORM
- **PostgreSQL 14+** + PostGIS 3.3+
- **Redis** para cache y sesiones
- **Celery** para procesamiento asincrónico
- **GeoPandas**, **Shapely**, **PyProj** para operaciones GIS
- **GDAL/OGR** para importación/exportación de formatos

### Infrastructure
- **Docker** + **Docker Compose** para containerización
- **PostgreSQL** con extensión PostGIS
- **Redis** para cache distribuido
- **S3-compatible** storage para archivos

## 3. Arquitectura de Capas

```
┌─────────────────────────────────────┐
│     Frontend (React + TypeScript)   │
│  Responsive: Web, Tablet, Mobile    │
└────────────┬────────────────────────┘
             │ HTTP/WebSocket
┌────────────┴────────────────────────┐
│    API Gateway + Authentication     │
│  JWT/OAuth, Rate Limiting, Cors     │
└────────────┬────────────────────────┘
             │
┌────────────┴────────────────────────┐
│    Backend Services (FastAPI)       │
│  - Auth & Authorization (RBAC)      │
│  - Tenant Management                │
│  - Project Management               │
│  - Survey & Topography              │
│  - GIS Operations                   │
│  - File Management                  │
│  - Reporting & Export               │
└────────────┬────────────────────────┘
             │
┌────────────┴────────────────────────┐
│    Data Layer                       │
│  - PostgreSQL + PostGIS             │
│  - Redis (Cache/Sessions)           │
│  - Elasticsearch (Audit logs)       │
└────────────┬────────────────────────┘
             │
┌────────────┴────────────────────────┐
│    Processing & Storage             │
│  - S3-compatible Storage            │
│  - GDAL/GeoPandas                   │
│  - Celery (Async Tasks)             │
└─────────────────────────────────────┘
```

## 4. Estructura del Backend

```
surveyor-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration
│   │
│   ├── core/
│   │   ├── security.py         # JWT, OAuth, Bcrypt
│   │   ├── permissions.py      # RBAC
│   │   └── exceptions.py       # Custom exceptions
│   │
│   ├── db/
│   │   ├── database.py         # DB connection
│   │   ├── session.py          # Session management
│   │   └── models.py           # SQLAlchemy models
│   │
│   ├── api/v1/
│   │   ├── router.py           # Main API router
│   │   ├── auth/               # Authentication endpoints
│   │   ├── organizations/      # Organization CRUD
│   │   ├── users/              # User management
│   │   ├── clients/            # Client CRM
│   │   ├── projects/           # Project management
│   │   ├── survey_points/      # Topographic points
│   │   ├── geometries/         # Geometric operations
│   │   ├── calculations/       # Math calculations
│   │   ├── exports/            # Export operations
│   │   ├── imports/            # Import operations
│   │   └── ...
│   │
│   ├── services/               # Business logic
│   │   ├── auth_service.py
│   │   ├── project_service.py
│   │   ├── survey_service.py
│   │   ├── gis_service.py
│   │   ├── calculation_service.py
│   │   ├── export_service.py
│   │   └── ...
│   │
│   ├── schemas/                # Pydantic validation
│   │   ├── auth.py
│   │   ├── projects.py
│   │   ├── survey.py
│   │   └── ...
│   │
│   ├── tasks/                  # Celery async tasks
│   │   ├── imports.py
│   │   ├── exports.py
│   │   ├── processing.py
│   │   └── ...
│   │
│   └── utils/
│       ├── gis_utils.py        # GIS helpers
│       ├── calculations.py     # Math functions
│       ├── validators.py       # Validation logic
│       └── coordinates.py      # Coordinate transformations
│
├── migrations/                 # Alembic DB migrations
├── tests/                      # Test suite
├── requirements.txt
├── .env.example
├── Dockerfile
└── README.md
```

## 5. Estructura del Frontend

```
surveyor-frontend/
├── src/
│   ├── index.tsx
│   ├── App.tsx
│   │
│   ├── components/
│   │   ├── auth/              # Login, Register
│   │   ├── dashboard/         # Dashboard widgets
│   │   ├── projects/          # Project components
│   │   ├── map/               # GIS map components
│   │   ├── survey/            # Survey point components
│   │   └── common/            # Shared components
│   │
│   ├── pages/
│   │   ├── DashboardPage.tsx
│   │   ├── ProjectsPage.tsx
│   │   ├── MapPage.tsx
│   │   └── ...
│   │
│   ├── services/
│   │   ├── api.ts             # Axios config
│   │   ├── auth.service.ts
│   │   ├── projects.service.ts
│   │   ├── gis.service.ts
│   │   └── ...
│   │
│   ├── hooks/
│   │   ├── useAuth.ts
│   │   ├── useProject.ts
│   │   ├── useMap.ts
│   │   └── ...
│   │
│   ├── utils/
│   │   ├── calculations.ts
│   │   ├── formatters.ts
│   │   ├── validators.ts
│   │   └── coordinates.ts
│   │
│   ├── types/
│   │   ├── index.ts
│   │   ├── api.ts
│   │   └── models.ts
│   │
│   ├── styles/
│   │   ├── globals.css
│   │   └── theme.ts
│   │
│   └── assets/
│       ├── icons/
│       └── images/
│
├── public/
├── index.html
├── vite.config.ts
├── tailwind.config.js
├── tsconfig.json
└── package.json
```

## 6. Modelos de Base de Datos

### Entidades Principales

**organizations**
- Empresa/Organización (multi-tenant)
- Aislamiento de datos por organización

**users**
- Usuarios del sistema
- Roles: superadmin, admin, agrimensor, technician, client

**clients**
- Clientes/Proyectos
- CRM integrado

**projects**
- Proyectos de agrimensura
- Estados: pending, planned, in_field, processing, in_review, completed, delivered, archived

**survey_points**
- Puntos topográficos
- Coordenadas (Este, Norte, Elevación)
- Metadatos GNSS

**geometries**
- Entidades geométricas (puntos, líneas, polígonos)
- PostGIS geometry type

**surfaces**
- Superficies topográficas (TIN, MDT, MDS)

**parcels**
- Parcelas de terreno
- Geometría Polygon

**equipment**
- Inventario de equipos
- Tipos: GNSS, Estación Total, Nivel, Drones, Cámaras

**quotes**
- Cotizaciones a clientes

**invoices**
- Facturas y pagos

**documents**
- Archivos del proyecto

**audit_logs**
- Registro de auditoría de cambios

## 7. Flujo de Autenticación

```
1. Usuario inicia sesión
   ↓
2. Backend valida credenciales
   ↓
3. Backend genera JWT con claims
   (sub, exp, org_id, role, permissions)
   ↓
4. Frontend almacena token en localStorage
   ↓
5. Requests incluyen: Authorization: Bearer {token}
   ↓
6. Backend valida token en cada request
   ↓
7. Token expire → Refresh token
```

## 8. Flujo de Autorización (RBAC)

```
Usuario → Rol → Permisos → Recursos

Roles predefinidos:
- Superadmin: Acceso total
- Admin: Acceso a empresa
- Agrimensor: Acceso a proyectos asignados
- Technician: Acceso limitado a campo
- Client: Acceso solo lectura a proyectos
```

## 9. Flujo de Multi-Tenancy

```
request.headers["Authorization"] → JWT
↓
extract org_id from JWT claims
↓
prefix_queries_with: WHERE organization_id = {org_id}
↓
Datos aislados por organización
↓
Row-level security en PostgreSQL
```

## 10. API Endpoints (Fase 1)

### Authentication
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/register` - Registro
- `POST /api/v1/auth/refresh` - Refresh token
- `POST /api/v1/auth/logout` - Logout

### Organizations
- `GET /api/v1/organizations` - Listar
- `POST /api/v1/organizations` - Crear
- `GET /api/v1/organizations/{id}` - Detalle
- `PATCH /api/v1/organizations/{id}` - Actualizar

### Clients
- `GET /api/v1/clients` - Listar
- `POST /api/v1/clients` - Crear
- `GET /api/v1/clients/{id}` - Detalle
- `PATCH /api/v1/clients/{id}` - Actualizar
- `DELETE /api/v1/clients/{id}` - Eliminar

### Projects
- `GET /api/v1/projects` - Listar con filtros
- `POST /api/v1/projects` - Crear
- `GET /api/v1/projects/{id}` - Detalle
- `PATCH /api/v1/projects/{id}` - Actualizar
- `DELETE /api/v1/projects/{id}` - Eliminar

### Survey Points
- `GET /api/v1/projects/{id}/survey-points` - Listar
- `POST /api/v1/projects/{id}/survey-points` - Crear
- `PATCH /api/v1/survey-points/{id}` - Actualizar
- `DELETE /api/v1/survey-points/{id}` - Eliminar
- `POST /api/v1/projects/{id}/survey-points/import` - Importar CSV

### Calculations
- `POST /api/v1/calculations/distance` - Distancia
- `POST /api/v1/calculations/azimuth` - Azimut
- `POST /api/v1/calculations/bearing` - Rumbo
- `POST /api/v1/calculations/area` - Área de polígono

### Exports
- `POST /api/v1/projects/{id}/export/csv` - Export CSV
- `POST /api/v1/projects/{id}/export/geojson` - Export GeoJSON
- `POST /api/v1/projects/{id}/export/dxf` - Export DXF

## 11. Decisiones Arquitectónicas

1. **PostgreSQL + PostGIS** sobre MongoDB
   - GIS es relacional por naturaleza
   - PostGIS es estándar de facto
   - Mejor performance con geometrías

2. **FastAPI** sobre Django
   - Más rápido (async nativo)
   - Type hints incorporados
   - Mejor para microservicios

3. **MapLibre GL JS** sobre Leaflet
   - WebGL para mejor performance
   - Mejor soporte 3D futuro
   - Open source

4. **Celery para async** sobre APScheduler
   - Distribuida y escalable
   - Mejor para tasks largas
   - Integración con Redis

## 12. Seguridad

- **Autenticación**: JWT con HS256
- **Autorización**: RBAC + Row-level security
- **Validación**: Pydantic en backend, Zod en frontend
- **Encriptación**: Bcrypt para contraseñas, HTTPS en prod
- **CORS**: Configurado por entorno
- **Rate limiting**: A implementar en API Gateway
- **Auditoría**: Logs de todas las operaciones
- **Validación de archivos**: Tipo, tamaño, virus scan

## 13. Performance

- **Indexing**: Índices espaciales en PostGIS
- **Caching**: Redis para sesiones y resultados
- **Paginación**: Por defecto 20 items
- **Lazy loading**: En mapas y tablas
- **Compression**: GZip en API responses
- **CDN**: Para assets en producción

## 14. Testing

- **Unit tests**: Lógica de negocio
- **Integration tests**: API endpoints
- **E2E tests**: Flujos críticos
- **Coverage target**: 80%+
- **Test data**: Fixtures con datos reales

## 15. Deployment

- **Dev**: Docker Compose local
- **Staging**: Kubernetes cluster
- **Prod**: Managed services (RDS, ElastiCache, ECS)
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus + Grafana
- **Logs**: ELK Stack

## 16. Roadmap

- **Fase 1** (4 sem): MVP core
- **Fase 2** (3 sem): Superficies y topografía avanzada
- **Fase 3** (2 sem): Reportes y documentación
- **Fase 4** (3 sem): Aplicación móvil
- **Fase 5** (4 sem): Features avanzadas y IA
