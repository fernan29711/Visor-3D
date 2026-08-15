# ⚡ Deploy en Railway en 5 Minutos

## Opción A: Despliegue AUTOMÁTICO (Recomendado)

### Paso 1: Crear cuenta en Railway
1. Ve a https://railway.app
2. Haz clic en "Start a new project"
3. Selecciona "Deploy with GitHub"
4. Autoriza Railway con GitHub

### Paso 2: Conectar repositorio
1. En Railway, selecciona "GitHub Repo"
2. Busca y selecciona: `fernan29711/Visor-3D`
3. Selecciona rama: `claude/surveyor-saas-platform-85enbr`
4. Haz clic en "Deploy"

### Paso 3: Configurar variables de entorno
Railway creará automáticamente el servicio PostgreSQL. Ahora configura:

1. **En el panel de Railway**, ve a la pestaña "Variables"
2. Haz clic en "+ Add Variable" y agrega:

```
SECRET_KEY=8daf1cebcd762147a5c243d32858a392c2615781184b45b7cc0228544858d627
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO
```

3. El `DATABASE_URL` se configurará automáticamente por Railway

### Paso 4: Déjalo deploying
- Railway construirá automáticamente los Dockerfiles
- Verás el progreso en tiempo real
- Cuando esté listo, obtendrás URLs como:
  - Backend: `https://visor-3d-backend-prod.railway.app`
  - Frontend: `https://visor-3d-frontend-prod.railway.app`

### Paso 5: Actualizar CORS en el backend
1. En el backend, ve a "Variables"
2. Actualiza CORS_ORIGINS:
```
CORS_ORIGINS=["https://visor-3d-frontend-prod.railway.app"]
```

3. El backend se redesplegará automáticamente

### ✅ ¡Listo!
Tu app estará en línea en: `https://visor-3d-frontend-prod.railway.app`

---

## Opción B: Despliegue Local (Con Docker)

Si tienes Docker en tu máquina:

```bash
# 1. Clonar el repositorio
git clone https://github.com/fernan29711/Visor-3D.git
cd Visor-3D

# 2. Copiar .env
cp .env.example .env

# 3. Editar .env (ajusta DATABASE_URL si es necesario)
# En Mac/Linux:
nano .env

# 4. Ejecutar deployment
./scripts/deploy.sh

# 5. Esperar 2-3 minutos a que se inicie
# Luego acceder en http://localhost:3000
```

---

## Opción C: Despliegue en VPS (DigitalOcean, Linode, etc.)

Si tienes un VPS con Linux:

```bash
# 1. SSH en tu servidor
ssh root@tu-servidor-ip

# 2. Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 3. Clonar repo
git clone https://github.com/fernan29711/Visor-3D.git
cd Visor-3D

# 4. Ejecutar deployment
sudo ./scripts/deploy.sh production

# 5. Configurar dominio (A record)
# Apunta tu dominio a la IP del servidor
```

---

## 🔐 Credenciales de Prueba

Para acceder a la app por primera vez:

**Para crear un usuario admin en la BD:**

```sql
-- Conectar a PostgreSQL en Railway o tu máquina local
-- Luego ejecutar migraciones con:
python -m alembic upgrade head

-- Luego crear usuario via API (endpoint /api/v1/auth/signup)
```

### URLs importantes

| Componente | URL |
|-----------|-----|
| Frontend | https://visor-3d-frontend-prod.railway.app |
| Backend | https://visor-3d-backend-prod.railway.app |
| API Docs | https://visor-3d-backend-prod.railway.app/docs |
| Database | Manejado por Railway automáticamente |

---

## 🆘 Troubleshooting

### Backend no inicia
1. Ve a "Logs" en Railway
2. Busca errores de `alembic` (migraciones)
3. Intenta "Redeploy" en Railway

### Frontend no conecta al backend
1. Verifica CORS_ORIGINS en backend
2. Verifica VITE_API_URL en frontend
3. Abre DevTools (F12) y revisa Network tab

### Base de datos no conecta
1. Railway PostgreSQL se crea automáticamente
2. Si hay error, intenta "Reset Database" en Railway

---

## 📝 Pasos siguientes

Después de desplegar:

- [ ] Crear usuario admin (POST /api/v1/auth/signup)
- [ ] Configurar dominio personalizado
- [ ] Configurar email SMTP (opcional)
- [ ] Configurar backups automáticos (Railway lo hace)
- [ ] Monitorear logs y métricas (Railway dashboard)

---

**¿Necesitas ayuda?** 
- Railway Docs: https://docs.railway.app
- GitHub Issues: https://github.com/fernan29711/Visor-3D/issues
