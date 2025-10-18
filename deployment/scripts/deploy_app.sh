#!/bin/bash
set -e

echo "📦 Deploying Enterprise Scanner Application"

# Build Docker image
echo "🔨 Building production Docker image..."
docker build -f deployment/production/docker/Dockerfile -t enterprise-scanner:production .

# Tag for registry (update with your registry)
# docker tag enterprise-scanner:production your-registry/enterprise-scanner:production

# Push to registry (uncomment when ready)
# docker push your-registry/enterprise-scanner:production

# Deploy with Docker Compose (for single server)
echo "🚀 Deploying with Docker Compose..."
cd deployment/production/docker
docker-compose -f docker-compose.production.yml up -d

# Health check
echo "🏥 Performing health check..."
sleep 30

if curl -f http://localhost:5000/api/health > /dev/null 2>&1; then
    echo "✅ Application deployment successful!"
    echo "🌐 Application running at: http://localhost:5000"
else
    echo "❌ Health check failed"
    echo "📋 Container logs:"
    docker-compose -f docker-compose.production.yml logs app
    exit 1
fi

echo "✅ Enterprise Scanner deployed successfully!"
