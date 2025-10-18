#!/bin/bash
# Enterprise Scanner - Direct Production Server Deployment
# Run this script when you're already on the production server

set -e

echo "🚀 Enterprise Scanner - Production Server Deployment"
echo "===================================================="
echo ""
echo "Server: $(hostname)"
echo "User: $(whoami)"
echo ""

# Check if we're root
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  Not running as root. Some commands may require sudo."
fi

# Install Docker if not present
if ! command -v docker &> /dev/null; then
    echo "📦 Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    systemctl enable docker
    systemctl start docker
    echo "✅ Docker installed"
else
    echo "✅ Docker already installed"
fi

# Install Docker Compose if not present
if ! command -v docker-compose &> /dev/null; then
    echo "📦 Installing Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    echo "✅ Docker Compose installed"
else
    echo "✅ Docker Compose already installed"
fi

# Create application directory
APP_DIR="/opt/enterprisescanner"
echo ""
echo "📁 Creating application directory: $APP_DIR"
mkdir -p $APP_DIR
cd $APP_DIR

# Clone or pull repository
if [ -d ".git" ]; then
    echo "🔄 Updating existing repository..."
    git pull
else
    echo "📥 Cloning repository..."
    echo "Please enter your repository URL:"
    read REPO_URL
    git clone $REPO_URL .
fi

cd docker

# Configure environment
if [ ! -f ".env" ]; then
    echo ""
    echo "⚙️  Setting up environment configuration..."
    cp .env.example .env
    
    echo ""
    echo "🔐 Please configure the following in .env file:"
    echo "   - POSTGRES_PASSWORD"
    echo "   - REDIS_PASSWORD"
    echo "   - SECRET_KEY"
    echo "   - SSL_CERT_EMAIL"
    echo "   - DOMAIN_NAME"
    echo ""
    echo "Edit .env now? (y/n)"
    read EDIT_ENV
    
    if [ "$EDIT_ENV" = "y" ]; then
        nano .env
    fi
else
    echo "✅ Environment file already exists"
fi

# Setup SSL certificates
echo ""
echo "🔒 SSL Certificate Setup"
echo "1. Generate self-signed certificate (testing)"
echo "2. Setup Let's Encrypt (production)"
echo "3. Skip (already configured)"
echo ""
echo "Select option (1-3):"
read SSL_OPTION

case $SSL_OPTION in
    1)
        ./setup-ssl.sh
        ;;
    2)
        ./setup-ssl.sh production
        ;;
    3)
        echo "Skipping SSL setup"
        ;;
esac

# Configure firewall
echo ""
echo "🔥 Configuring firewall..."
if command -v ufw &> /dev/null; then
    ufw allow 22/tcp   # SSH
    ufw allow 80/tcp   # HTTP
    ufw allow 443/tcp  # HTTPS
    ufw --force enable
    echo "✅ Firewall configured"
else
    echo "⚠️  UFW not found. Please configure firewall manually:"
    echo "   - Allow port 22 (SSH)"
    echo "   - Allow port 80 (HTTP)"
    echo "   - Allow port 443 (HTTPS)"
fi

# Deploy
echo ""
echo "🚀 Ready to deploy!"
echo "Run deployment? (y/n)"
read DEPLOY

if [ "$DEPLOY" = "y" ]; then
    ./deploy-production.sh
else
    echo ""
    echo "✅ Setup complete! Run deployment manually with:"
    echo "   cd $APP_DIR/docker"
    echo "   ./deploy-production.sh"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Configure DNS to point to this server's IP"
echo "2. Ensure .env file has correct values"
echo "3. Run: ./deploy-production.sh"
