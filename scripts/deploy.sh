#!/bin/bash

# Surveyor SaaS Deployment Script
# Usage: ./scripts/deploy.sh [production|staging]

set -e

ENVIRONMENT="${1:-staging}"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🚀 Deploying Surveyor SaaS to $ENVIRONMENT environment..."

# Check if .env file exists
if [ ! -f "$PROJECT_ROOT/.env" ]; then
    echo "❌ .env file not found! Creating from .env.example..."
    cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/.env"
    echo "⚠️  Please update .env with your configuration and run again."
    exit 1
fi

# Load environment variables
export $(cat "$PROJECT_ROOT/.env" | grep -v '^#' | xargs)

# Build Docker images
echo "📦 Building Docker images..."
if [ "$ENVIRONMENT" = "production" ]; then
    docker-compose -f "$PROJECT_ROOT/docker-compose.prod.yml" build
else
    docker-compose -f "$PROJECT_ROOT/docker-compose.yml" build
fi

# Stop existing containers
echo "🛑 Stopping existing containers..."
if [ "$ENVIRONMENT" = "production" ]; then
    docker-compose -f "$PROJECT_ROOT/docker-compose.prod.yml" down
else
    docker-compose -f "$PROJECT_ROOT/docker-compose.yml" down
fi

# Start services
echo "🚀 Starting services..."
if [ "$ENVIRONMENT" = "production" ]; then
    docker-compose -f "$PROJECT_ROOT/docker-compose.prod.yml" up -d
else
    docker-compose -f "$PROJECT_ROOT/docker-compose.yml" up -d
fi

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Run database migrations
echo "🗄️  Running database migrations..."
if [ "$ENVIRONMENT" = "production" ]; then
    docker-compose -f "$PROJECT_ROOT/docker-compose.prod.yml" exec -T backend python -m alembic upgrade head
else
    docker-compose -f "$PROJECT_ROOT/docker-compose.yml" exec backend python -m alembic upgrade head
fi

# Verify deployment
echo "✅ Verifying deployment..."
if curl -f http://localhost:8000/api/v1/status > /dev/null 2>&1; then
    echo "✅ Backend is running!"
else
    echo "❌ Backend health check failed!"
    exit 1
fi

if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is running!"
else
    echo "❌ Frontend health check failed!"
    exit 1
fi

echo ""
echo "🎉 Deployment completed successfully!"
echo ""
echo "📍 Service URLs:"
echo "   Frontend:   http://localhost:3000"
echo "   Backend:    http://localhost:8000"
echo "   API Docs:   http://localhost:8000/docs"
echo "   Nginx:      http://localhost"
echo ""
echo "💾 Database:"
echo "   Host: localhost"
echo "   Port: 5432"
echo "   User: $POSTGRES_USER"
echo ""
echo "📝 View logs:"
echo "   docker-compose logs -f"
echo ""
