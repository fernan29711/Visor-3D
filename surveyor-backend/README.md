# Surveyor Backend - FastAPI

Backend profesional para plataforma SaaS de agrimensura.

## 📋 Requisitos

- Python 3.11+
- PostgreSQL 14+
- PostGIS 3.3+
- Redis 7+

## 🚀 Instalación

### 1. Crear entorno virtual

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

```bash
cp .env.example .env
```

Editar `.env` con tu configuración:
```
DATABASE_URL=postgresql://surveyor:surveyor123@localhost:5432/surveyor_db
SECRET_KEY=your-secret-key-change-in-production
DEBUG=True
```

### 4. Crear base de datos

```bash
# Crear BD si no existe
psql -U postgres -c "CREATE DATABASE surveyor_db;"
psql -U postgres -d surveyor_db -c "CREATE USER surveyor WITH PASSWORD 'surveyor123';"
psql -U postgres -d surveyor_db -c "ALTER ROLE surveyor SET client_encoding TO 'utf8';"
psql -U postgres -d surveyor_db -c "GRANT ALL PRIVILEGES ON DATABASE surveyor_db TO surveyor;"

# Habilitar PostGIS
psql -U surveyor -d surveyor_db -c "CREATE EXTENSION IF NOT EXISTS postgis;"
```

### 5. Ejecutar servidor

```bash
uvicorn app.main:app --reload
```

Acceder a: http://localhost:8000

## 📚 Documentación API

Una vez que el servidor esté corriendo:

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI JSON**: http://localhost:8000/api/openapi.json

## 🧪 Testing

### Ejecutar todos los tests

```bash
pytest
```

### Ejecutar tests específicos

```bash
pytest tests/test_auth.py -v
pytest tests/test_users.py -v
```

### Tests con coverage

```bash
pytest --cov=app tests/
```

## 📁 Estructura

```
app/
├── main.py              # FastAPI app
├── config.py            # Configuración
├── dependencies.py      # Inyección de dependencias
│
├── core/
│   ├── security.py      # JWT, hash, etc
│   ├── permissions.py   # RBAC
│   └── exceptions.py    # Custom exceptions
│
├── db/
│   ├── database.py      # Conexión BD
│   └── models.py        # Modelos SQLAlchemy
│
├── api/v1/
│   ├── router.py        # Router principal
│   ├── auth/            # Autenticación
│   ├── organizations/   # Organizaciones
│   ├── users/           # Usuarios
│   └── ...
│
├── services/            # Lógica de negocio
├── schemas/             # Validación (Pydantic)
└── utils/               # Utilidades

tests/
├── test_auth.py
├── test_users.py
└── ...
```

## 🔐 Autenticación

### Flujo de Login

```
1. POST /api/v1/auth/login
{
  "email": "user@example.com",
  "password": "password123"
}

2. Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "...",
  "token_type": "bearer",
  "expires_in": 1800
}

3. Usar token en headers:
Authorization: Bearer {access_token}
```

### Roles disponibles

- **superadmin**: Acceso total del sistema
- **admin**: Administrador de empresa
- **agrimensor**: Agrimensor profesional
- **technician**: Técnico de campo
- **client**: Cliente (acceso limitado)

## 📊 Modelos de BD

### Organizations (Empresas)
```
- id (UUID)
- name (string)
- rnc (string, opcional)
- subscription_plan (string)
- created_at, updated_at
```

### Users (Usuarios)
```
- id (UUID)
- organization_id (FK)
- email (string)
- password_hash (string)
- first_name, last_name (string)
- role (enum)
- is_active (boolean)
```

### Projects (Proyectos)
```
- id (UUID)
- organization_id (FK)
- client_id (FK)
- code, name (string)
- status (enum)
- location (Point, PostGIS)
- created_at, updated_at
```

### SurveyPoints (Puntos topográficos)
```
- id (UUID)
- project_id (FK)
- point_number (string)
- east, north (decimal)
- elevation (decimal, opcional)
- geometry (Point, PostGIS)
```

## 🛠️ Endpoints Disponibles

### Autenticación
- `POST /api/v1/auth/register` - Registrar usuario
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/refresh` - Refresh token
- `POST /api/v1/auth/logout` - Logout

### Usuarios
- `GET /api/v1/users` - Listar usuarios
- `POST /api/v1/users` - Crear usuario (admin)
- `GET /api/v1/users/me` - Usuario actual
- `GET /api/v1/users/{id}` - Detalle usuario
- `PATCH /api/v1/users/{id}` - Actualizar usuario
- `DELETE /api/v1/users/{id}` - Eliminar usuario (admin)

### Organizaciones
- `GET /api/v1/organizations/me` - Org actual
- `GET /api/v1/organizations/{id}` - Detalle org
- `PATCH /api/v1/organizations/{id}` - Actualizar org (admin)

## 🚢 Deployment

### Docker

```bash
# Build imagen
docker build -t surveyor-backend .

# Ejecutar
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://... \
  -e SECRET_KEY=... \
  surveyor-backend
```

### Docker Compose

```bash
cd ..
docker-compose up backend
```

## 🐛 Debugging

### Ver logs

```bash
# Con uvicorn
uvicorn app.main:app --reload --log-level debug
```

### Conectar a BD directamente

```bash
psql -U surveyor -d surveyor_db
```

### Ver tokens JWT

```python
from app.core.security import verify_token
payload = verify_token("your-token-here")
print(payload)
```

## ✅ Checklist de desarrollo

- [x] Autenticación JWT
- [x] RBAC
- [x] Modelos de BD
- [x] Servicios
- [x] Endpoints básicos
- [x] Tests
- [ ] Endpoints de Proyectos
- [ ] Endpoints de Puntos Topográficos
- [ ] Cálculos
- [ ] Importación/Exportación
- [ ] Mapa GIS

## 📞 Problemas comunes

### "Connection refused" en BD
```bash
# Verificar que PostgreSQL está corriendo
psql -U postgres -c "\l"
```

### "Module not found" en imports
```bash
# Asegurar estar en directorio correcto
cd surveyor-backend
python -m uvicorn app.main:app --reload
```

### CORS errors
Verificar configuración en `config.py`:
```python
CORS_ORIGINS = ["http://localhost:5173", ...]
```

## 📖 Recursos

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)
- [PostGIS Docs](https://postgis.net/documentation/)
