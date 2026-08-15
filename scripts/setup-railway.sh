#!/bin/bash

# Setup script for Railway.app deployment
# This script generates all necessary secrets and configuration

set -e

echo "🚀 Surveyor SaaS - Railway Setup Helper"
echo "========================================"
echo ""

# Generate secrets
echo "🔐 Generating secrets..."
SECRET_KEY=$(openssl rand -hex 32)
RANDOM_PWD=$(openssl rand -base64 12)

# Create .env for reference
cat > .env.railway << EOF
# Generated on $(date)
# Copy these values to Railway dashboard

# Backend Configuration
SECRET_KEY=$SECRET_KEY
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database (Railway creates this automatically)
# DATABASE_URL will be set by Railway automatically
# Don't edit these - Railway handles them

# CORS Settings (update with your frontend URL)
CORS_ORIGINS=["https://YOUR_FRONTEND_URL.railway.app"]

# Frontend
VITE_API_URL=https://YOUR_BACKEND_URL.railway.app/api/v1

# Environment
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO
EOF

echo "✅ Configuration created in .env.railway"
echo ""

# Display setup instructions
cat << EOF
📋 RAILWAY SETUP INSTRUCTIONS
=============================

1️⃣  Go to https://railway.app and create a free account

2️⃣  Click "New Project" → "Deploy from GitHub repo"
   - Select: fernan29711/Visor-3D
   - Branch: claude/surveyor-saas-platform-85enbr

3️⃣  Railway will auto-detect and create:
   ✓ PostgreSQL database (with PostGIS)
   ✓ Backend service (from Dockerfile.backend)
   ✓ Frontend service (from Dockerfile.frontend)

4️⃣  In Railway dashboard, add these Environment Variables:

   SECRET_KEY=$SECRET_KEY
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   REFRESH_TOKEN_EXPIRE_DAYS=7
   ENVIRONMENT=production
   DEBUG=False
   LOG_LEVEL=INFO

5️⃣  Wait for deployment to complete (~3-5 minutes)

6️⃣  Once deployed, Railway will show you:
   - Backend URL: https://your-backend.railway.app
   - Frontend URL: https://your-frontend.railway.app

7️⃣  Update CORS in backend:
   CORS_ORIGINS=["https://your-frontend.railway.app"]

8️⃣  Create admin user (after deployment):

   Backend has admin created via /api/v1/auth/signup endpoint
   Or contact support for setup assistance

✨ Your app will be live and accessible from anywhere!

═══════════════════════════════════════════════════════════

🎯 Quick Links After Deployment:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📱 Frontend:      https://your-frontend.railway.app
🔧 API Docs:      https://your-backend.railway.app/docs
📊 API Status:    https://your-backend.railway.app/api/v1/status
🗄️  Database:      PostgreSQL + PostGIS (managed by Railway)

═══════════════════════════════════════════════════════════

💡 TIPS:
  • Railway gives you $5/month free credit
  • PostgreSQL + PostGIS is included
  • SSL/HTTPS is automatic
  • Domains are auto-generated (.railway.app)
  • You can add your own domain later
  • Backups are automatic

❓ Need help? Check DEPLOYMENT.md for detailed instructions

EOF

echo ""
echo "📁 Configuration saved to: .env.railway"
echo ""
echo "🎉 Ready to deploy on Railway!"
