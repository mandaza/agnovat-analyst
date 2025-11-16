#!/bin/bash

# Agnovat Analyst - Remote Server Deployment Script
# Automated deployment to cloud servers (AWS, DigitalOcean, GCP, etc.)

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "========================================="
echo "Agnovat Analyst - Remote Deployment"
echo "========================================="
echo ""

# Parse command line arguments
DOMAIN=""
EMAIL=""
SERVER_IP=""
SSH_USER="root"

while [[ $# -gt 0 ]]; do
    case $1 in
        --domain)
            DOMAIN="$2"
            shift 2
            ;;
        --email)
            EMAIL="$2"
            shift 2
            ;;
        --server)
            SERVER_IP="$2"
            shift 2
            ;;
        --user)
            SSH_USER="$2"
            shift 2
            ;;
        --help)
            echo "Usage: ./deploy-remote.sh --domain your-domain.com --email your@email.com --server SERVER_IP [--user SSH_USER]"
            echo ""
            echo "Required:"
            echo "  --domain    Your domain name (e.g., example.com)"
            echo "  --email     Your email for SSL certificate"
            echo "  --server    Server IP address"
            echo ""
            echo "Optional:"
            echo "  --user      SSH user (default: root)"
            echo ""
            echo "Example:"
            echo "  ./deploy-remote.sh --domain api.example.com --email admin@example.com --server 123.45.67.89"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Validate required arguments
if [ -z "$DOMAIN" ] || [ -z "$EMAIL" ] || [ -z "$SERVER_IP" ]; then
    echo -e "${RED}Error: Missing required arguments${NC}"
    echo ""
    echo "Usage: ./deploy-remote.sh --domain your-domain.com --email your@email.com --server SERVER_IP"
    echo "Use --help for more information"
    exit 1
fi

echo -e "${BLUE}Configuration:${NC}"
echo "  Domain: $DOMAIN"
echo "  Email: $EMAIL"
echo "  Server: $SERVER_IP"
echo "  SSH User: $SSH_USER"
echo ""

# Test SSH connection
echo -e "${BLUE}🔌 Step 1: Testing SSH connection...${NC}"
if ! ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "echo 'SSH connection successful'" > /dev/null 2>&1; then
    echo -e "${RED}❌ Cannot connect to server via SSH${NC}"
    echo "Please ensure:"
    echo "  1. Server IP is correct: $SERVER_IP"
    echo "  2. SSH key is set up for user: $SSH_USER"
    echo "  3. Server firewall allows SSH (port 22)"
    exit 1
fi
echo -e "${GREEN}✅ SSH connection successful${NC}"

# Install Docker and dependencies
echo ""
echo -e "${BLUE}🐳 Step 2: Installing Docker and dependencies...${NC}"
ssh $SSH_USER@$SERVER_IP << 'REMOTE_SETUP'
set -e

# Update system
echo "Updating system packages..."
apt update && apt upgrade -y

# Install essential tools
echo "Installing essential tools..."
apt install -y curl git ufw fail2ban nginx certbot python3-certbot-nginx

# Install Docker
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
else
    echo "Docker already installed"
fi

# Install docker-compose
if ! command -v docker-compose &> /dev/null; then
    echo "Installing docker-compose..."
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
else
    echo "docker-compose already installed"
fi

# Configure firewall
echo "Configuring firewall..."
ufw --force enable
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp

echo "Server setup complete!"
REMOTE_SETUP

echo -e "${GREEN}✅ Server dependencies installed${NC}"

# Deploy application
echo ""
echo -e "${BLUE}📦 Step 3: Deploying application...${NC}"

# Create deployment directory
ssh $SSH_USER@$SERVER_IP "mkdir -p ~/agnovat-analyst"

# Copy project files to server
echo "Copying project files..."
rsync -avz --exclude='.git' --exclude='venv' --exclude='__pycache__' --exclude='logs' --exclude='*.log' \
    ./ $SSH_USER@$SERVER_IP:~/agnovat-analyst/

# Create production environment file
echo "Creating production environment..."
ssh $SSH_USER@$SERVER_IP "cat > ~/agnovat-analyst/.env.production << 'ENV_EOF'
HOST=0.0.0.0
PORT=8000
DEBUG=False
LOG_LEVEL=INFO
ALLOWED_ORIGINS=https://$DOMAIN
BIAS_DETECTION_THRESHOLD=0.6
TEMPLATE_SIMILARITY_THRESHOLD=0.8
ENV_EOF"

# Build and start Docker containers
echo "Building Docker image..."
ssh $SSH_USER@$SERVER_IP << 'DOCKER_DEPLOY'
cd ~/agnovat-analyst
docker-compose -f docker-compose.yml -f docker-compose.production.yml build
docker-compose -f docker-compose.yml -f docker-compose.production.yml up -d
DOCKER_DEPLOY

echo -e "${GREEN}✅ Application deployed${NC}"

# Configure Nginx
echo ""
echo -e "${BLUE}🌐 Step 4: Configuring Nginx...${NC}"

# Create Nginx configuration
ssh $SSH_USER@$SERVER_IP bash -c "cat > /etc/nginx/sites-available/agnovat << 'NGINX_EOF'
# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name $DOMAIN;

    # Allow Let's Encrypt verification
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }

    # Redirect everything else to HTTPS
    location / {
        return 301 https://\$server_name\$request_uri;
    }
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name $DOMAIN;

    # SSL Configuration (will be added by certbot)
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security headers
    add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;
    add_header X-Frame-Options \"SAMEORIGIN\" always;
    add_header X-Content-Type-Options \"nosniff\" always;
    add_header X-XSS-Protection \"1; mode=block\" always;

    # Rate limiting
    limit_req_zone \$binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req zone=api_limit burst=20 nodelay;

    # Proxy to Docker container
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;

        # Timeouts for long-running requests
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }

    # Health check endpoint (no rate limiting)
    location /health {
        proxy_pass http://localhost:8000/health;
        access_log off;
        limit_req off;
    }

    # API docs (optional)
    location /docs {
        proxy_pass http://localhost:8000/docs;
    }
}
NGINX_EOF"

# Enable Nginx site
ssh $SSH_USER@$SERVER_IP << 'NGINX_ENABLE'
ln -sf /etc/nginx/sites-available/agnovat /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx
NGINX_ENABLE

echo -e "${GREEN}✅ Nginx configured${NC}"

# Set up SSL certificate
echo ""
echo -e "${BLUE}🔐 Step 5: Setting up SSL certificate...${NC}"

# Wait for DNS to propagate
echo "Checking DNS propagation for $DOMAIN..."
RETRIES=0
MAX_RETRIES=12
while [ $RETRIES -lt $MAX_RETRIES ]; do
    if nslookup $DOMAIN | grep -q "$SERVER_IP"; then
        echo -e "${GREEN}✅ DNS is configured correctly${NC}"
        break
    fi
    RETRIES=$((RETRIES + 1))
    if [ $RETRIES -lt $MAX_RETRIES ]; then
        echo "DNS not yet propagated. Waiting 10 seconds... (Attempt $RETRIES/$MAX_RETRIES)"
        sleep 10
    fi
done

if [ $RETRIES -eq $MAX_RETRIES ]; then
    echo -e "${YELLOW}⚠️  Warning: DNS propagation check timed out${NC}"
    echo "Please ensure your domain's A record points to: $SERVER_IP"
    echo "You can set up SSL manually later with:"
    echo "  ssh $SSH_USER@$SERVER_IP"
    echo "  sudo certbot --nginx -d $DOMAIN --email $EMAIL"
else
    # Obtain SSL certificate
    echo "Obtaining SSL certificate from Let's Encrypt..."
    ssh $SSH_USER@$SERVER_IP "certbot --nginx -d $DOMAIN --email $EMAIL --agree-tos --non-interactive --redirect"
    echo -e "${GREEN}✅ SSL certificate installed${NC}"
fi

# Verify deployment
echo ""
echo -e "${BLUE}🧪 Step 6: Verifying deployment...${NC}"

# Check if Docker container is running
if ssh $SSH_USER@$SERVER_IP "docker ps | grep -q agnovat-analyst"; then
    echo -e "${GREEN}✅ Docker container is running${NC}"
else
    echo -e "${RED}❌ Docker container is not running${NC}"
    exit 1
fi

# Check if Nginx is running
if ssh $SSH_USER@$SERVER_IP "systemctl is-active --quiet nginx"; then
    echo -e "${GREEN}✅ Nginx is running${NC}"
else
    echo -e "${RED}❌ Nginx is not running${NC}"
    exit 1
fi

# Test health endpoint
echo "Testing health endpoint..."
sleep 3
if curl -sf https://$DOMAIN/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Server is responding via HTTPS${NC}"
else
    echo -e "${YELLOW}⚠️  HTTPS health check failed (SSL may still be setting up)${NC}"
    echo "Trying HTTP..."
    if ssh $SSH_USER@$SERVER_IP "curl -sf http://localhost:8000/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Server is responding locally${NC}"
    else
        echo -e "${RED}❌ Server health check failed${NC}"
        exit 1
    fi
fi

# Create local MCP wrapper for remote connection
echo ""
echo -e "${BLUE}🔌 Step 7: Creating local MCP configuration...${NC}"

cat > mcp_server_remote.py << 'MCP_REMOTE_EOF'
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
BACKEND_URL = "https://$DOMAIN"

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
MCP_REMOTE_EOF

# Replace domain placeholder
sed -i.bak "s|\$DOMAIN|$DOMAIN|g" mcp_server_remote.py
rm -f mcp_server_remote.py.bak
chmod +x mcp_server_remote.py

# Create Claude Desktop config for remote
cat > claude_desktop_config_remote.json << CONFIG_EOF
{
  "mcpServers": {
    "agnovat-analyst": {
      "command": "$(which python3)",
      "args": [
        "$(pwd)/mcp_server_remote.py"
      ],
      "cwd": "$(pwd)",
      "env": {
        "PYTHONPATH": "$(pwd)"
      }
    }
  }
}
CONFIG_EOF

echo -e "${GREEN}✅ MCP configuration created${NC}"

echo ""
echo "========================================="
echo -e "${GREEN}✅ Remote Deployment Complete!${NC}"
echo "========================================="
echo ""
echo "Your Agnovat Analyst is now running at:"
echo "  🌐 https://$DOMAIN"
echo ""
echo "Next steps:"
echo ""
echo "1. Configure Claude Desktop MCP:"
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "   cp claude_desktop_config_remote.json ~/Library/Application\\ Support/Claude/claude_desktop_config.json"
else
    echo "   cp claude_desktop_config_remote.json ~/.config/Claude/claude_desktop_config.json"
fi
echo ""
echo "2. Restart Claude Desktop (Cmd+Q or Ctrl+Q, then reopen)"
echo ""
echo "3. Test in Claude:"
echo '   "List all available Agnovat tools"'
echo ""
echo "Server management (via SSH):"
echo "  ssh $SSH_USER@$SERVER_IP"
echo "  cd ~/agnovat-analyst"
echo "  docker-compose logs -f              # View logs"
echo "  docker-compose ps                   # Check status"
echo "  docker-compose restart              # Restart"
echo ""
echo "Health check:"
echo "  curl https://$DOMAIN/health"
echo ""
echo "API documentation:"
echo "  https://$DOMAIN/docs"
echo ""
echo -e "${GREEN}🎉 Deployment successful!${NC}"
