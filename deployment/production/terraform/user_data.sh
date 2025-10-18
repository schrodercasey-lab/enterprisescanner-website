#!/bin/bash
yum update -y
yum install -y docker git

# Start Docker
systemctl start docker
systemctl enable docker
usermod -a -G docker ec2-user

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Clone application
cd /opt
git clone https://github.com/enterprise-scanner/production-app.git
cd production-app

# Deploy application
/usr/local/bin/docker-compose up -d

# Configure nginx
amazon-linux-extras install nginx1
systemctl start nginx
systemctl enable nginx

# SSL configuration will be handled by ALB
echo "Enterprise Scanner production deployment complete" > /var/log/deployment.log
