#!/bin/bash
set -e

echo "☸️  Deploying Enterprise Scanner to Kubernetes"

# Check kubectl
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl not found. Please install kubectl."
    exit 1
fi

# Check cluster connection
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Cannot connect to Kubernetes cluster."
    exit 1
fi

echo "✅ Kubernetes cluster connected"

# Deploy to Kubernetes
cd deployment/production/kubernetes

# Create namespace
echo "📁 Creating namespace..."
kubectl apply -f namespace.yaml

# Deploy application
echo "🚀 Deploying application..."
kubectl apply -f deployment.yaml

# Configure ingress
echo "🌐 Configuring ingress..."
kubectl apply -f ingress.yaml

# Wait for deployment
echo "⏳ Waiting for deployment to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/enterprise-scanner-app -n enterprise-scanner

# Get service status
echo "📊 Service status:"
kubectl get services -n enterprise-scanner
kubectl get ingress -n enterprise-scanner

echo "✅ Kubernetes deployment complete!"
