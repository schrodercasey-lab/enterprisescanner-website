# 🚀 Production Server Deployment - Direct Setup

## Your Current Situation

You're already logged into your production server:
```
root@enterprisescanner-prod-01:~#
```

**You don't need to SCP files!** You can deploy directly on the server.

## Option 1: Quick Manual Setup (Recommended)

### Step 1: Install Required Software

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Verify installations
docker --version
docker-compose --version
```

### Step 2: Transfer Files to Server

From your **local machine** (where you have the workspace):

```powershell
# Compress the docker directory
cd C:\Users\schro\OneDrive\Desktop\BugBountyScanner\workspace
tar -czf docker-deploy.tar.gz docker/

# Upload to server (replace with actual IP)
scp docker-deploy.tar.gz root@YOUR_SERVER_IP:/root/

# Or use SFTP, WinSCP, or your preferred method
```

### Step 3: Extract and Setup on Server

Back on your production server:

```bash
# Extract files
cd /root
tar -xzf docker-deploy.tar.gz

# Move to application directory
mkdir -p /opt/enterprisescanner
mv docker /opt/enterprisescanner/
cd /opt/enterprisescanner/docker

# Make scripts executable
chmod +x *.sh
```

### Step 4: Configure Environment

```bash
# Copy and edit environment file
cp .env.example .env
nano .env

# Update these critical values:
# - POSTGRES_PASSWORD=your_secure_password
# - REDIS_PASSWORD=your_secure_password
# - SECRET_KEY=random_64_character_string
# - SSL_CERT_EMAIL=your@email.com
# - DOMAIN_NAME=enterprisescanner.com
```

### Step 5: Setup SSL Certificates

```bash
# For production with Let's Encrypt:
./setup-ssl.sh production

# Or for testing with self-signed:
./setup-ssl.sh
```

### Step 6: Configure Firewall

```bash
# Install UFW if not present
apt-get update
apt-get install -y ufw

# Configure firewall
ufw allow 22/tcp   # SSH
ufw allow 80/tcp   # HTTP
ufw allow 443/tcp  # HTTPS
ufw enable
ufw status
```

### Step 7: Deploy!

```bash
# Run the deployment script
./deploy-production.sh

# This will:
# - Build all Docker images
# - Start all services
# - Run health checks
# - Show you the status
```

## Option 2: Automated Setup Script

If you have the files on the server already:

```bash
cd /opt/enterprisescanner/docker
./setup-production-server.sh
```

This will guide you through the entire setup process.

## Option 3: Use Git (If Repository is Online)

```bash
# Install Git
apt-get install -y git

# Clone your repository
cd /opt/enterprisescanner
git clone YOUR_REPO_URL .

# Follow steps 4-7 above
```

## Quick Transfer Methods

### Method 1: Using WinSCP (GUI - Easiest)
1. Download WinSCP
2. Connect to your server
3. Drag and drop the `docker` folder
4. Done!

### Method 2: Using PowerShell (from your Windows machine)

```powershell
# Create archive
cd C:\Users\schro\OneDrive\Desktop\BugBountyScanner\workspace
Compress-Archive -Path docker -DestinationPath docker.zip

# Upload (install OpenSSH first if needed)
scp docker.zip root@YOUR_SERVER_IP:/root/

# Then on server:
# unzip docker.zip
# cd docker
# chmod +x *.sh
```

### Method 3: Using Git

1. **On your local machine:**
   ```powershell
   cd C:\Users\schro\OneDrive\Desktop\BugBountyScanner\workspace
   git init
   git add docker/
   git commit -m "Production deployment files"
   git remote add origin YOUR_GITHUB_REPO
   git push -u origin main
   ```

2. **On your server:**
   ```bash
   cd /opt/enterprisescanner
   git clone YOUR_GITHUB_REPO .
   cd docker
   chmod +x *.sh
   ```

## Verification

After deployment, verify everything is running:

```bash
# Check running containers
docker ps

# Check health
curl http://localhost/health

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Check specific service
curl http://localhost:5001/health
```

## Troubleshooting

### Can't connect to Docker daemon
```bash
systemctl start docker
systemctl enable docker
```

### Permission denied on scripts
```bash
chmod +x *.sh
```

### Port already in use
```bash
# Check what's using port 80
netstat -tulpn | grep :80

# Stop conflicting service
systemctl stop apache2  # or nginx
```

### Firewall blocking connections
```bash
# Check firewall status
ufw status

# Allow required ports
ufw allow 80/tcp
ufw allow 443/tcp
```

## Next Steps After Deployment

1. **Configure DNS:**
   - Point your domain to your server IP
   - Add A record: enterprisescanner.com → YOUR_SERVER_IP
   - Add A record: www.enterprisescanner.com → YOUR_SERVER_IP

2. **Test SSL:**
   ```bash
   # Check certificate
   openssl s_client -connect enterprisescanner.com:443
   ```

3. **Monitor Services:**
   ```bash
   # Watch logs
   docker-compose -f docker-compose.prod.yml logs -f
   
   # Check resource usage
   docker stats
   ```

4. **Setup Backups:**
   ```bash
   # Add to crontab
   crontab -e
   
   # Add this line for daily 2 AM backups:
   0 2 * * * cd /opt/enterprisescanner/docker && docker-compose -f docker-compose.prod.yml exec -T postgres pg_dump -U admin enterprisescanner > /backups/db_$(date +\%Y\%m\%d).sql
   ```

## Quick Commands Reference

```bash
# Start services
docker-compose -f docker-compose.prod.yml up -d

# Stop services
docker-compose -f docker-compose.prod.yml down

# Restart service
docker-compose -f docker-compose.prod.yml restart nginx

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Check status
docker-compose -f docker-compose.prod.yml ps

# Update and redeploy
git pull
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

## 🎉 You're Ready!

Once you've transferred the files and run the deployment script, your Enterprise Scanner platform will be live on your production server!

**Access at:** https://enterprisescanner.com (after DNS is configured)
