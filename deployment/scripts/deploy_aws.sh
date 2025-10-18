#!/bin/bash
set -e

echo "Starting Enterprise Scanner AWS Deployment"

# Check prerequisites
if ! command -v terraform &> /dev/null; then
    echo "❌ Terraform not found. Please install Terraform."
    exit 1
fi

if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Please install AWS CLI."
    exit 1
fi

# Verify AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials not configured. Please run 'aws configure'."
    exit 1
fi

echo "✅ Prerequisites verified"

# Navigate to Terraform directory
cd deployment/production/terraform

# Initialize Terraform
echo "🔧 Initializing Terraform..."
terraform init

# Plan deployment
echo "📋 Planning deployment..."
terraform plan -out=production.tfplan

# Apply deployment
echo "🚀 Deploying infrastructure..."
terraform apply production.tfplan

# Get outputs
echo "📊 Deployment outputs:"
terraform output

echo "✅ AWS infrastructure deployment complete!"
echo "🌐 Next: Configure domain DNS to point to the load balancer"
