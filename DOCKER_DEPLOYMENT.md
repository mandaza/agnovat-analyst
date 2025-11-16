# Docker Deployment Guide

**Deploy Agnovat Analyst to Docker** 🐳

---

## 🎯 Overview

This guide shows you how to deploy Agnovat Analyst using Docker containers. The deployment uses:

- **Docker container** for the FastAPI backend (port 8000)
- **MCP wrapper** on the host for Claude Desktop integration
- **docker-compose** for easy orchestration

### Architecture

```
┌─────────────────────┐
│  Claude Desktop     │  (Host)
└──────────┬──────────┘
           │ stdio
┌──────────▼──────────┐
│  mcp_server_docker  │  (Host - Python script)
└──────────┬──────────┘
           │ HTTP
┌──────────▼──────────┐
│  Docker Container   │
│  agnovat-analyst    │  Port 8000
│                     │
│  FastAPI Backend    │
│  23 Analysis Tools  │
└─────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Docker installed ([Get Docker](https://www.docker.com/get-started))
- docker-compose installed (included with Docker Desktop)
- Python 3.10+ on host (for MCP wrapper)

### One-Command Deployment

```bash
./docker-deploy.sh
```

That's it! The script will:
1. Build the Docker image
2. Start the container
3. Configure MCP for Claude Desktop
4. Provide next steps

---

## 📋 Manual Deployment

### Step 1: Build the Docker Image

```bash
# Build the image
docker-compose build

# Or build manually
docker build -t agnovat-analyst .
```

### Step 2: Start the Container

```bash
# Start with docker-compose
docker-compose up -d

# Or run manually
docker run -d \
  --name agnovat-analyst \
  -p 8000:8000 \
  -e DEBUG=False \
  -e LOG_LEVEL=INFO \
  agnovat-analyst
```

### Step 3: Verify It's Running

```bash
# Check container status
docker ps

# Test the server
curl http://localhost:8000/health

# View logs
docker logs agnovat-analyst
```

### Step 4: Configure Claude Desktop

```bash
# Copy the Docker MCP config
cp claude_desktop_config_docker.json ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Restart Claude Desktop
```

---

## 🛠️ Management Commands

Use the management script for easy control:

```bash
# Start containers
./docker-manage.sh start

# Stop containers
./docker-manage.sh stop

# Restart containers
./docker-manage.sh restart

# View logs
./docker-manage.sh logs

# Check status
./docker-manage.sh status

# Open shell in container
./docker-manage.sh shell

# Test the server
./docker-manage.sh test

# Rebuild from scratch
./docker-manage.sh rebuild

# Clean up everything
./docker-manage.sh clean
```

---

## 📁 Docker Files

### Dockerfile

Multi-stage build for optimized image:
- **Stage 1 (Builder):** Install dependencies, download spaCy model
- **Stage 2 (Runtime):** Minimal image with just what's needed
- **Non-root user:** Runs as `agnovat` user for security
- **Health check:** Automated health monitoring

### docker-compose.yml

Orchestrates the full stack:
- FastAPI backend on port 8000
- Volume mounts for documents and logs
- Health checks
- Auto-restart policy
- Optional Nginx proxy (commented out)

### .dockerignore

Excludes unnecessary files from the image:
- venv/, __pycache__/
- docs/, tests/
- .git/, .env

---

## 🔧 Configuration

### Environment Variables

Set in `docker-compose.yml`:

```yaml
environment:
  - HOST=0.0.0.0
  - PORT=8000
  - DEBUG=False
  - LOG_LEVEL=INFO
  - ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
  - BIAS_DETECTION_THRESHOLD=0.6
  - TEMPLATE_SIMILARITY_THRESHOLD=0.8
```

### Volume Mounts

Access files on the host:

```yaml
volumes:
  # Mount documents directory (read-only)
  - ./documents:/data:ro
  # Mount logs directory
  - ./logs:/app/logs
```

**Usage:**
```bash
# Create documents directory
mkdir -p documents

# Copy PDFs
cp /path/to/reports/*.pdf documents/

# Access in container as /data/*.pdf
```

---

## 🌐 Production Deployment

### With Nginx Reverse Proxy

1. **Uncomment Nginx in docker-compose.yml**

2. **Create nginx.conf:**

```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server agnovat-backend:8000;
    }

    server {
        listen 80;
        server_name your-domain.com;

        location / {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
    }

    # HTTPS configuration (requires SSL certificates)
    # server {
    #     listen 443 ssl;
    #     server_name your-domain.com;
    #     ssl_certificate /etc/nginx/ssl/cert.pem;
    #     ssl_certificate_key /etc/nginx/ssl/key.pem;
    #
    #     location / {
    #         proxy_pass http://backend;
    #     }
    # }
}
```

3. **Start with Nginx:**

```bash
docker-compose up -d
```

### Environment-Specific Configs

**Development:**
```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

**Production:**
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

## 🔍 Troubleshooting

### Container Won't Start

```bash
# Check logs
docker logs agnovat-analyst

# Check all logs
docker-compose logs

# Inspect container
docker inspect agnovat-analyst
```

**Common issues:**
- Port 8000 already in use: `lsof -i :8000`
- Permission errors: Check volume mount permissions
- Build errors: Try `docker-compose build --no-cache`

### Health Check Failing

```bash
# Manual health check
curl http://localhost:8000/health

# Check from inside container
docker exec agnovat-analyst curl http://localhost:8000/health

# View detailed health status
docker inspect --format='{{.State.Health.Status}}' agnovat-analyst
```

### MCP Connection Issues

```bash
# Verify backend is accessible from host
curl http://localhost:8000/health

# Check MCP wrapper can connect
python3 mcp_server_docker.py << 'EOF'
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}
EOF

# Test tools list
curl http://localhost:8000/openapi.json | grep -c "/api/"
```

### High Memory Usage

```bash
# Check resource usage
docker stats agnovat-analyst

# Limit resources in docker-compose.yml
services:
  agnovat-backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
```

---

## 📊 Monitoring

### View Logs

```bash
# Follow logs in real-time
docker logs -f agnovat-analyst

# Last 100 lines
docker logs --tail=100 agnovat-analyst

# Logs since 1 hour ago
docker logs --since=1h agnovat-analyst
```

### Resource Monitoring

```bash
# Real-time stats
docker stats

# Container details
docker inspect agnovat-analyst

# Disk usage
docker system df
```

### Health Monitoring

```bash
# Health status
docker inspect --format='{{json .State.Health}}' agnovat-analyst | python3 -m json.tool

# Continuous health monitoring
watch -n 5 'curl -s http://localhost:8000/health | python3 -m json.tool'
```

---

## 🔄 Updates & Maintenance

### Update the Application

```bash
# Pull latest code
git pull

# Rebuild and restart
./docker-manage.sh rebuild
```

### Update Dependencies

```bash
# Update requirements.txt
# Then rebuild
docker-compose build --no-cache
docker-compose up -d
```

### Backup Data

```bash
# Backup logs
tar -czf logs-backup-$(date +%Y%m%d).tar.gz logs/

# Backup documents
tar -czf documents-backup-$(date +%Y%m%d).tar.gz documents/
```

### Clean Up

```bash
# Remove stopped containers
docker container prune

# Remove unused images
docker image prune

# Remove unused volumes
docker volume prune

# Clean everything
docker system prune -a
```

---

## 🔐 Security Best Practices

### 1. Non-Root User

Container runs as `agnovat` user (UID 1000):
```dockerfile
USER agnovat
```

### 2. Read-Only Mounts

Mount documents as read-only:
```yaml
volumes:
  - ./documents:/data:ro
```

### 3. Network Isolation

Use bridge network:
```yaml
networks:
  - agnovat-network
```

### 4. Environment Variables

Never commit secrets:
```bash
# Use .env file (git-ignored)
echo "API_KEY=secret" > .env

# Reference in docker-compose.yml
env_file:
  - .env
```

### 5. HTTPS in Production

Always use HTTPS with Nginx:
```nginx
listen 443 ssl;
ssl_certificate /etc/nginx/ssl/cert.pem;
ssl_certificate_key /etc/nginx/ssl/key.pem;
```

---

## 📦 Docker Hub Deployment (Optional)

### Build and Push

```bash
# Tag image
docker tag agnovat-analyst yourusername/agnovat-analyst:latest

# Login to Docker Hub
docker login

# Push
docker push yourusername/agnovat-analyst:latest
```

### Pull and Run

```bash
# Others can now use
docker pull yourusername/agnovat-analyst:latest
docker run -d -p 8000:8000 yourusername/agnovat-analyst:latest
```

---

## 🎯 Best Practices

1. **Use docker-compose** for local development
2. **Use Kubernetes/Docker Swarm** for production at scale
3. **Monitor resource usage** regularly
4. **Keep images small** (multi-stage builds)
5. **Version your images** (use tags)
6. **Regular updates** for security patches
7. **Backup data** before updates
8. **Test in staging** before production

---

## 📞 Support

- **Docker Issues:** Check Docker logs first
- **MCP Issues:** Test backend HTTP endpoint
- **Container Issues:** Use `docker inspect`
- **General Help:** See main documentation in `docs/`

---

## ✅ Quick Reference

```bash
# Deploy everything
./docker-deploy.sh

# Management commands
./docker-manage.sh start|stop|restart|logs|status|shell|test|rebuild|clean

# Manual commands
docker-compose up -d               # Start
docker-compose stop                # Stop
docker-compose logs -f             # Logs
docker-compose ps                  # Status
docker-compose down                # Remove
docker-compose build --no-cache    # Rebuild

# Testing
curl http://localhost:8000/health
curl http://localhost:8000/docs
python3 test_mcp_connection.py
```

---

**Your Agnovat Analyst is now running in Docker!** 🐳🎉

All 23 tools are available via the containerized backend, accessible through Claude Desktop MCP integration.
