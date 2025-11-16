# Remote Server Deployment Guide

**Deploy Agnovat Analyst to Your Online Server** 🌐

---

## 🎯 Overview

This guide covers deploying Agnovat Analyst to a remote server (VPS, cloud instance, dedicated server) with Docker.

### Supported Platforms

- ✅ **AWS EC2** (Amazon Web Services)
- ✅ **DigitalOcean Droplets**
- ✅ **Google Cloud Compute Engine**
- ✅ **Azure Virtual Machines**
- ✅ **Linode**
- ✅ **Any VPS with Docker support**

### What You'll Get

```
┌──────────────────┐
│ Claude Desktop   │ (Your computer)
└────────┬─────────┘
         │ HTTPS
┌────────▼─────────┐
│ Your Server      │
│ your-domain.com  │
│                  │
│ ┌──────────────┐ │
│ │   Nginx      │ │ Port 443 (HTTPS)
│ │ (SSL/Proxy)  │ │
│ └──────┬───────┘ │
│        │         │
│ ┌──────▼───────┐ │
│ │   Docker     │ │
│ │  agnovat     │ │ Port 8000
│ │  container   │ │
│ └──────────────┘ │
└──────────────────┘
```

---

## 🚀 Quick Start (3 Commands)

If you already have a server with Docker:

```bash
# 1. Clone on server
ssh user@your-server.com
git clone https://github.com/yourusername/agnovat-analyst.git
cd agnovat-analyst

# 2. Deploy
./deploy-remote.sh

# 3. Access
# Open https://your-server.com in browser
```

---

## 📋 Prerequisites

### On Your Server

- ✅ Linux server (Ubuntu 20.04+ recommended)
- ✅ Root or sudo access
- ✅ Public IP address or domain name
- ✅ Ports 80 and 443 open
- ✅ At least 2GB RAM, 20GB disk

### On Your Computer

- ✅ SSH access to server
- ✅ Git installed
- ✅ Claude Desktop installed

---

## 🏗️ Server Setup

### Step 1: Choose Your Server

#### Option A: DigitalOcean (Recommended for beginners)

1. Create account at https://www.digitalocean.com
2. Create new Droplet:
   - **Image:** Ubuntu 22.04 LTS
   - **Plan:** Basic ($12/month - 2GB RAM)
   - **Datacenter:** Choose closest to you
   - **Authentication:** SSH key (recommended)
3. Note your server IP

#### Option B: AWS EC2

1. Launch EC2 instance:
   - **AMI:** Ubuntu Server 22.04 LTS
   - **Instance Type:** t3.small (2GB RAM)
   - **Security Group:** Allow ports 22, 80, 443
2. Download `.pem` key file
3. Note your public IP

#### Option C: Google Cloud

1. Create Compute Engine instance:
   - **Machine type:** e2-small
   - **Boot disk:** Ubuntu 22.04 LTS
   - **Firewall:** Allow HTTP and HTTPS traffic
2. Note external IP

### Step 2: Initial Server Configuration

```bash
# SSH into your server
ssh root@YOUR_SERVER_IP

# Update system
apt update && apt upgrade -y

# Install essential tools
apt install -y curl git ufw fail2ban

# Configure firewall
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable

# Create non-root user (recommended)
adduser agnovat
usermod -aG sudo agnovat
su - agnovat
```

### Step 3: Install Docker

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER

# Install docker-compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version

# Log out and back in for group changes
exit
ssh agnovat@YOUR_SERVER_IP
```

### Step 4: Set Up Domain (Optional but Recommended)

1. **Buy a domain** (e.g., namecheap.com, godaddy.com)
2. **Add DNS A record:**
   - Type: A
   - Host: @
   - Value: YOUR_SERVER_IP
   - TTL: 3600

Wait 5-60 minutes for DNS to propagate.

---

## 🚢 Deployment Methods

### Method 1: Automated Deployment (Easiest)

I'll create a script for you:

```bash
# On your server
git clone https://github.com/yourusername/agnovat-analyst.git
cd agnovat-analyst

# Run deployment script
./deploy-remote.sh --domain your-domain.com --email your@email.com
```

### Method 2: Manual Deployment

```bash
# On your server
cd agnovat-analyst

# Create production environment file
cat > .env.production << 'EOF'
HOST=0.0.0.0
PORT=8000
DEBUG=False
LOG_LEVEL=INFO
ALLOWED_ORIGINS=https://your-domain.com
EOF

# Deploy with production config
docker-compose -f docker-compose.yml -f docker-compose.production.yml up -d

# Set up Nginx with SSL
sudo apt install -y nginx certbot python3-certbot-nginx

# Configure Nginx (see below)
sudo nano /etc/nginx/sites-available/agnovat

# Enable site
sudo ln -s /etc/nginx/sites-available/agnovat /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com
```

---

## 🔐 Security Configuration

### SSL/HTTPS Setup

#### Option 1: Let's Encrypt (Free, Automated)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate (interactive)
sudo certbot --nginx -d your-domain.com

# Auto-renewal (already set up by certbot)
sudo certbot renew --dry-run
```

#### Option 2: Custom SSL Certificate

```bash
# Place your certificates
sudo mkdir -p /etc/nginx/ssl
sudo cp your-cert.pem /etc/nginx/ssl/cert.pem
sudo cp your-key.pem /etc/nginx/ssl/key.pem
sudo chmod 600 /etc/nginx/ssl/*.pem
```

### Nginx Configuration

Create `/etc/nginx/sites-available/agnovat`:

```nginx
# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req zone=api_limit burst=20 nodelay;

    # Proxy to Docker container
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts for long-running requests
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }

    # Health check endpoint (no rate limiting)
    location /health {
        proxy_pass http://localhost:8000/health;
        access_log off;
    }

    # API docs (optional - disable in production)
    location /docs {
        # Uncomment to protect with password
        # auth_basic "Restricted";
        # auth_basic_user_file /etc/nginx/.htpasswd;
        proxy_pass http://localhost:8000/docs;
    }
}
```

Enable and test:

```bash
sudo ln -s /etc/nginx/sites-available/agnovat /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Firewall Configuration

```bash
# Configure UFW
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
sudo ufw status
```

### API Authentication (Optional but Recommended)

Create API key authentication:

```bash
# Generate API key
API_KEY=$(openssl rand -hex 32)
echo "API_KEY=$API_KEY" >> .env.production

# Add to Nginx
sudo htpasswd -c /etc/nginx/.htpasswd admin
```

---

## 🔌 Connect Claude Desktop to Remote Server

### Update MCP Configuration

Create `mcp_server_remote.py` on your local machine:

```python
#!/usr/bin/env python3
"""
MCP Server for Claude Desktop - Remote Server Version
Connects to Agnovat backend running on remote server
"""

import sys
import json
import asyncio
from typing import Any, Dict
import httpx
from loguru import logger

# Configure logger
logger.remove()
logger.add(sys.stderr, level="INFO")

# Remote server URL
BACKEND_URL = "https://your-domain.com"  # Change this!

# Import MCP server class
import os
sys.path.insert(0, os.path.dirname(__file__))
from mcp_server import MCPStdioServer

class MCPRemoteServer(MCPStdioServer):
    def __init__(self):
        super().__init__(base_url=BACKEND_URL)

async def main():
    logger.info(f"Starting MCP server (Remote: {BACKEND_URL})")
    server = MCPRemoteServer()
    await server.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)
```

### Claude Desktop Configuration

Update `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "agnovat-analyst": {
      "command": "/path/to/venv/bin/python",
      "args": [
        "/path/to/agnovat-analyst/mcp_server_remote.py"
      ],
      "cwd": "/path/to/agnovat-analyst",
      "env": {
        "PYTHONPATH": "/path/to/agnovat-analyst"
      }
    }
  }
}
```

---

## 📊 Monitoring & Maintenance

### View Logs

```bash
# Docker logs
docker logs -f agnovat-analyst

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# System logs
sudo journalctl -u docker -f
```

### Health Monitoring

```bash
# Check service health
curl https://your-domain.com/health

# Check Docker status
docker ps
docker stats agnovat-analyst

# Check Nginx status
sudo systemctl status nginx
```

### Automated Monitoring

Install monitoring:

```bash
# Install Netdata (real-time monitoring)
bash <(curl -Ss https://my-netdata.io/kickstart.sh)

# Access at http://YOUR_SERVER_IP:19999
```

### Backup

```bash
# Create backup script
cat > ~/backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=/backups/agnovat-$DATE

mkdir -p $BACKUP_DIR

# Backup Docker volumes
docker run --rm \
  -v agnovat_data:/data \
  -v $BACKUP_DIR:/backup \
  ubuntu tar czf /backup/data.tar.gz /data

# Backup configs
cp -r ~/agnovat-analyst/.env.production $BACKUP_DIR/
cp /etc/nginx/sites-available/agnovat $BACKUP_DIR/

echo "Backup completed: $BACKUP_DIR"
EOF

chmod +x ~/backup.sh

# Run backup
~/backup.sh

# Schedule daily backups
crontab -e
# Add: 0 2 * * * /home/agnovat/backup.sh
```

---

## 🔄 Updates & Maintenance

### Update Application

```bash
# On server
cd ~/agnovat-analyst

# Pull latest code
git pull

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Verify
curl https://your-domain.com/health
```

### Zero-Downtime Updates

```bash
# Build new image
docker-compose build

# Start new container
docker-compose up -d --no-deps --build agnovat-backend

# Old container auto-removed
```

---

## 🚨 Troubleshooting

### Server Not Accessible

```bash
# Check if Docker is running
docker ps

# Check if ports are open
sudo netstat -tlnp | grep -E ':(80|443|8000)'

# Check firewall
sudo ufw status

# Check Nginx
sudo nginx -t
sudo systemctl status nginx

# Check DNS
nslookup your-domain.com
```

### SSL Certificate Issues

```bash
# Renew certificate
sudo certbot renew --force-renewal

# Check certificate
sudo certbot certificates

# Test SSL
curl -vI https://your-domain.com
```

### High Memory Usage

```bash
# Check Docker stats
docker stats

# Restart container
docker-compose restart

# Limit resources
# Add to docker-compose.yml:
deploy:
  resources:
    limits:
      cpus: '1'
      memory: 1G
```

---

## 💰 Cost Estimates

### Monthly Costs

| Provider | Plan | Specs | Cost |
|----------|------|-------|------|
| DigitalOcean | Basic | 2GB RAM, 1 CPU | $12/mo |
| AWS EC2 | t3.small | 2GB RAM, 2 CPU | ~$15/mo |
| Linode | Nanode | 1GB RAM, 1 CPU | $5/mo |
| Google Cloud | e2-small | 2GB RAM, 2 CPU | ~$14/mo |

**Domain:** ~$10-15/year
**SSL Certificate:** Free (Let's Encrypt)

**Total: ~$12-20/month**

---

## ✅ Post-Deployment Checklist

- [ ] Server accessible via SSH
- [ ] Docker and docker-compose installed
- [ ] Application running (`docker ps`)
- [ ] Health endpoint accessible (`curl http://localhost:8000/health`)
- [ ] Nginx configured and running
- [ ] SSL certificate installed
- [ ] HTTPS working (`https://your-domain.com`)
- [ ] Firewall configured
- [ ] DNS pointing to server
- [ ] Claude Desktop MCP configured
- [ ] Backups scheduled
- [ ] Monitoring set up

---

## 📞 Support

**Server Issues:**
- Check logs: `docker logs agnovat-analyst`
- Check Nginx: `sudo nginx -t`
- Check firewall: `sudo ufw status`

**Connection Issues:**
- Test health: `curl https://your-domain.com/health`
- Check DNS: `nslookup your-domain.com`
- Check SSL: `curl -vI https://your-domain.com`

---

**Your Agnovat Analyst is now running on your server!** 🌐🎉

Access it from anywhere via `https://your-domain.com` and use with Claude Desktop through MCP!
