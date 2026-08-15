# Deployment Guide - Surveyor SaaS Platform

Guía completa para desplegar la aplicación en Railway.app

## Prerrequisitos

1. Cuenta en [Railway.app](https://railway.app)
2. GitHub conectado a Railway
3. [Railway CLI](https://docs.railway.app/cli/installation) instalado (opcional)

## Opción 1: Despliegue automático con Railway Dashboard (Recomendado)

### Paso 1: Conectar repositorio

1. Ve a [railway.app](https://railway.app)
2. Inicia sesión con GitHub
3. Haz clic en "New Project"
4. Selecciona "Deploy from GitHub repo"
5. Busca y selecciona `fernan29711/Visor-3D`
6. Selecciona rama `claude/surveyor-saas-platform-85enbr`

### Paso 2: Configurar variables de entorno

En el panel de Railway, añade estas variables:

**Backend:**
```
DATABASE_URL=postgresql://...  # Railway proporciona esto automáticamente
SECRET_KEY=<genera-una-clave-segura>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
CORS_ORIGINS=["https://tu-dominio-frontend.railway.app"]
ENVIRONMENT=production
DEBUG=False
```

**Frontend:**
```
VITE_API_URL=https://tu-dominio-backend.railway.app/api/v1
```

### Paso 3: Crear servicios

Railway detectará automáticamente:
- **PostgreSQL** - Base de datos
- **Backend** - Dockerfile.backend (Puerto 8000)
- **Frontend** - Dockerfile.frontend (Puerto 3000)

### Paso 4: Customizar dominios

1. Cada servicio obtendrá un dominio `.railway.app` automático
2. Opcionalmente, conecta tus propios dominios

## Opción 2: Despliegue manual con Railway CLI

```bash
# 1. Instalar Railway CLI
npm install -g @railway/cli

# 2. Autenticarse
railway login

# 3. Crear nuevo proyecto
railway init

# 4. Configurar variables de entorno
railway variables:set DATABASE_URL=postgresql://...
railway variables:set SECRET_KEY=<clave-segura>
# ... más variables

# 5. Desplegar
railway up
```

## Despliegue con Docker Compose (Local primero)

```bash
# Build de imágenes
docker-compose build

# Iniciar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f

# Ejecutar migraciones
docker-compose exec backend python -m alembic upgrade head
```

## Variables de entorno críticas para producción

```bash
# SEGURIDAD
SECRET_KEY=$(openssl rand -hex 32)

# DATABASE - Railway proporciona automáticamente
DATABASE_URL=postgresql://user:pass@host:port/dbname

# CORS - Actualiza con tu dominio
CORS_ORIGINS=["https://mi-app.railway.app"]

# JWT
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ALGORITHM=HS256

# API Frontend
VITE_API_URL=https://api.mi-app.railway.app/api/v1

# Logging
LOG_LEVEL=INFO
ENVIRONMENT=production
DEBUG=False
```

## Verificar despliegue

1. **Backend**: Visita `https://tu-backend.railway.app/docs` 
   - Deberías ver OpenAPI/Swagger docs
   - Endpoint de health check: `GET /api/v1/status`

2. **Frontend**: Visita `https://tu-frontend.railway.app`
   - Login con credenciales de prueba
   - Prueba cada módulo

3. **Base de datos**: Verifica conectividad
   ```bash
   railway database connect postgres
   ```

## Solución de problemas

### Backend no inicia
```bash
# Ver logs en Railway dashboard o:
railway logs backend

# Verificar migraciones
railway exec backend python -m alembic current
```

### Frontend no carga datos
1. Verifica CORS en backend
2. Comprueba `VITE_API_URL` en frontend
3. Revisa console del navegador (F12)

### Problemas con PostGIS
Railway PostgreSQL incluye PostGIS. Si hay error:
```bash
# Conectar y activar extensión
railway database connect postgres
CREATE EXTENSION IF NOT EXISTS postgis;
```

## Scaling y optimización

Para producción:
- Aumenta replicas del backend en Railway
- Configura caching con Redis
- Usa CDN para assets estáticos
- Configura backups automáticos de BD

## Monitoreo

Railway proporciona:
- Métricas de CPU/memoria
- Logs en tiempo real
- Alertas de uptime
- Estadísticas de deployment

## Rollback

Si algo falla:
1. Railway guarda automaticamente todos los deployments
2. Haz clic en "Redeploy" en el dashboard
3. Selecciona un deployment anterior

## Próximos pasos

- [ ] Configura dominio personalizado
- [ ] Configura email (SMTP)
- [ ] Configura almacenamiento S3 (opcional)
- [ ] Configura backups diarios
- [ ] Configura monitoreo y alertas
- [ ] Configura CI/CD con tests automáticos

## Recursos

- [Documentación Railway](https://docs.railway.app)
- [Dockerfile best practices](https://docs.docker.com/develop/dev-best-practices/dockerfile_best-practices/)
- [FastAPI deployment](https://fastapi.tiangolo.com/deployment/)
- [PostGIS en Railway](https://railway.app/docs/databases/postgresql)

---

**¿Necesitas ayuda?** Contacta con el equipo de Railway en discord.gg/railway
