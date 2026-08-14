# Surveyor SaaS - Plataforma Profesional de Agrimensura

Plataforma SaaS completa para gestión integral de proyectos de agrimensura, topografía y mapeo geoespacial.

## 📋 Características principales

- ✅ Gestión multi-empresa (SaaS)
- ✅ RBAC (Control de acceso basado en roles)
- ✅ Gestión de clientes y proyectos
- ✅ Sistema de puntos topográficos
- ✅ Mapa GIS interactivo
- ✅ Cálculos topográficos (distancia, azimut, rumbo, área)
- ✅ Importación/Exportación (CSV, GeoJSON, DXF)
- ✅ Dashboard profesional

## 🚀 Quick Start

### Requisitos previos
- Docker & Docker Compose
- Git
- PostgreSQL 14+ (si ejecutas sin Docker)
- Python 3.11+ (si ejecutas sin Docker)
- Node.js 18+ (si ejecutas sin Docker)

### Opción 1: Docker Compose (Recomendado)

```bash
# Clonar repositorio
git clone <repo-url>
cd Visor-3D

# Crear archivo .env
cp surveyor-backend/.env.example surveyor-backend/.env

# Iniciar servicios
docker-compose up -d

# La aplicación estará disponible en:
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/api/docs
```

### Opción 2: Desarrollo Local

#### Backend

```bash
cd surveyor-backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Crear archivo .env
cp .env.example .env

# Ejecutar servidor
uvicorn app.main:app --reload
```

#### Frontend

```bash
cd surveyor-frontend

# Instalar dependencias
npm install

# Ejecutar servidor de desarrollo
npm run dev
```

## 📁 Estructura del Proyecto

```
Visor-3D/
├── surveyor-backend/          # Backend FastAPI
│   ├── app/
│   │   ├── api/v1/           # Endpoints de API
│   │   ├── db/               # Modelos y BD
│   │   ├── core/             # Seguridad y permisos
│   │   ├── services/         # Lógica de negocio
│   │   └── ...
│   ├── requirements.txt
│   ├── Dockerfile
│   └── README.md
│
├── surveyor-frontend/         # Frontend React + TypeScript
│   ├── src/
│   │   ├── components/       # Componentes React
│   │   ├── pages/           # Páginas
│   │   ├── services/        # Comunicación con API
│   │   ├── types/           # TypeScript types
│   │   └── ...
│   ├── package.json
│   ├── Dockerfile
│   └── README.md
│
├── docker-compose.yml        # Configuración de servicios
├── ARCHITECTURE.md           # Documentación de arquitectura
└── README.md                 # Este archivo
```

## 🗄️ Base de Datos

La aplicación utiliza **PostgreSQL 14+** con la extensión **PostGIS 3.3+**.

### Crear base de datos manualmente (sin Docker)

```bash
# Conectar a PostgreSQL
psql -U postgres

# Crear base de datos
CREATE DATABASE surveyor_db;
CREATE USER surveyor WITH PASSWORD 'surveyor123';
ALTER ROLE surveyor SET client_encoding TO 'utf8';
ALTER ROLE surveyor SET default_transaction_isolation TO 'read committed';
ALTER ROLE surveyor SET default_transaction_deferrable TO on;
ALTER ROLE surveyor SET default_time_zone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE surveyor_db TO surveyor;

# Activar PostGIS
\c surveyor_db
CREATE EXTENSION IF NOT EXISTS postgis;
```

## 🔐 Autenticación

El sistema usa **JWT (JSON Web Tokens)** para autenticación.

### Flujo de login
1. Usuario proporciona email y contraseña
2. Backend valida y genera JWT
3. Frontend almacena token
4. Requests incluyen: `Authorization: Bearer {token}`

### Roles disponibles
- **Superadmin**: Acceso total del sistema
- **Admin**: Administrador de empresa
- **Agrimensor**: Puede crear y gestionar proyectos
- **Technician**: Acceso limitado a campo
- **Client**: Acceso solo lectura

## 🗺️ API Endpoints

### Health Check
```bash
GET /
GET /health
GET /api/v1/status
```

### Autenticación
```bash
POST /api/v1/auth/login
POST /api/v1/auth/register
POST /api/v1/auth/refresh
POST /api/v1/auth/logout
```

### Clientes
```bash
GET    /api/v1/clients
POST   /api/v1/clients
GET    /api/v1/clients/{id}
PATCH  /api/v1/clients/{id}
DELETE /api/v1/clients/{id}
```

### Proyectos
```bash
GET    /api/v1/projects
POST   /api/v1/projects
GET    /api/v1/projects/{id}
PATCH  /api/v1/projects/{id}
DELETE /api/v1/projects/{id}
```

Ver documentación completa en `/api/docs` cuando ejecutes el backend.

## 📊 Cálculos Soportados

- Distancia entre puntos (horizontal e inclinada)
- Azimut y rumbo
- Área de polígonos
- Diferencia de elevación
- Coordenadas en diferentes sistemas (EPSG)

## 📤 Formatos de Importación/Exportación

### Importar
- CSV
- TXT
- Excel (XLSX)

### Exportar
- CSV
- GeoJSON
- DXF (AutoCAD)

## 🧪 Testing

```bash
# Backend
cd surveyor-backend
pytest tests/ -v

# Frontend
cd surveyor-frontend
npm run test
```

## 📝 Logs y Auditoría

Todos los cambios se registran en la tabla `audit_logs`:
- Usuario que realizó el cambio
- Acción ejecutada
- Tabla y registro afectado
- Cambios realizados
- Timestamp

## 🚢 Deployment

### Variables de Entorno Importantes
```
DATABASE_URL=postgresql://user:password@host:5432/db
SECRET_KEY=your-secret-key
DEBUG=False
ENVIRONMENT=production
CORS_ORIGINS=["https://app.example.com"]
```

### Docker Compose en Producción
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## 📚 Documentación

- [ARCHITECTURE.md](./ARCHITECTURE.md) - Arquitectura técnica
- [surveyor-backend/README.md](./surveyor-backend/README.md) - Backend
- [surveyor-frontend/README.md](./surveyor-frontend/README.md) - Frontend

## 🤝 Contribuir

1. Crear rama feature: `git checkout -b feature/AmazingFeature`
2. Commit cambios: `git commit -m 'Add AmazingFeature'`
3. Push a rama: `git push origin feature/AmazingFeature`
4. Abrir Pull Request

## 📄 Licencia

Este proyecto está bajo licencia privada.

## 👨‍💻 Autor

**Surveyor Team**

---

## 📞 Soporte

Para soporte técnico, contactar al equipo de desarrollo.

## 🗺️ Roadmap

- [ ] Fase 1: MVP Core (En progreso)
- [ ] Fase 2: Superficies y Topografía Avanzada
- [ ] Fase 3: Reportes y Documentación
- [ ] Fase 4: Aplicación Móvil
- [ ] Fase 5: Drones, 3D, IA

---

**Última actualización**: 2026-08-14
