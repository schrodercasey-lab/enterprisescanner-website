#!/bin/bash
set -e

echo "📊 Setting up production monitoring"

# Install monitoring tools
echo "🔧 Installing monitoring components..."

# Prometheus
kubectl create namespace monitoring || true
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install prometheus prometheus-community/kube-prometheus-stack --namespace monitoring

# Grafana dashboard
echo "📈 Setting up Grafana dashboards..."
echo "Default admin password for Grafana:"
kubectl get secret --namespace monitoring prometheus-grafana -o jsonpath="{.data.admin-password}" | base64 --decode

# DataDog (optional - requires API key)
if [ ! -z "$DATADOG_API_KEY" ]; then
    echo "🐕 Setting up DataDog monitoring..."
    helm repo add datadog https://helm.datadoghq.com
    helm install datadog-agent datadog/datadog \
        --set datadog.apiKey=$DATADOG_API_KEY \
        --set datadog.site="datadoghq.com"
fi

echo "✅ Monitoring setup complete!"
echo "🌐 Access Grafana at: kubectl port-forward svc/prometheus-grafana 3000:80 -n monitoring"
