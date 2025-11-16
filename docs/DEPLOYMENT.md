# Agnovat Analyst - Deployment Guide

**Production deployment instructions for Agnovat Analyst MCP Server**

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development](#local-development)
3. [Production Deployment](#production-deployment)
4. [Docker Deployment](#docker-deployment)
5. [MCP Integration](#mcp-integration)
6. [Security Considerations](#security-considerations)
7. [Monitoring & Maintenance](#monitoring--maintenance)

---

## Prerequisites

### System Requirements

- **OS:** Linux, macOS, or Windows
- **Python:** 3.10 or higher
- **Memory:** 4GB RAM minimum, 8GB recommended
- **Storage:** 2GB for application + space for documents
- **Network:** Internet access for initial setup

### Software Dependencies

```bash
# Python packages (from requirements.txt)
fastapi>=0.104.0
fastapi-mcp>=0.1.0
uvicorn[standard]>=0.24.0
pydantic>=2.5.0
pydantic-settings>=2.1.0
loguru>=0.7.2
python-multipart>=0.0.6
PyPDF2>=3.0.0
pdfplumber>=0.10.3
spacy>=3.7.2
transformers>=4.35.0
python-dotenv>=1.0.0

# spaCy model
en_core_web_sm
```

---

## Local Development

### Setup

```bash
# 1. Clone repository
git clone <repository-url>
cd agnovat-docs

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# 4. Configure environment
cp .env.example .env
nano .env  # Edit as needed

# 5. Run development server
uvicorn app.main:app --reload
```

### Development Settings (.env)

```env
# Debug mode (enables /docs endpoint)
DEBUG=True

# Server configuration
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO

# CORS (allow all in development)
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:8000"]

# Analysis settings
BIAS_DETECTION_THRESHOLD=0.6
TEMPLATE_SIMILARITY_THRESHOLD=0.8
```

---

## Production Deployment

### Option 1: systemd Service (Linux)

#### 1. Create Service User

```bash
sudo useradd -r -s /bin/false agnovat
sudo mkdir -p /opt/agnovat-analyst
sudo chown agnovat:agnovat /opt/agnovat-analyst
```

#### 2. Install Application

```bash
# Copy files
sudo cp -r /path/to/agnovat-docs/* /opt/agnovat-analyst/
cd /opt/agnovat-analyst

# Install dependencies as agnovat user
sudo -u agnovat python3 -m venv venv
sudo -u agnovat venv/bin/pip install -r requirements.txt
sudo -u agnovat venv/bin/python -m spacy download en_core_web_sm
```

#### 3. Configure Environment

```bash
sudo nano /opt/agnovat-analyst/.env
```

Production .env:
```env
DEBUG=False
HOST=127.0.0.1
PORT=8000
LOG_LEVEL=WARNING
ALLOWED_ORIGINS=["https://yourdomain.com"]
```

#### 4. Create systemd Service

```bash
sudo nano /etc/systemd/system/agnovat-analyst.service
```

Service file:
```ini
[Unit]
Description=Agnovat Analyst MCP Server
After=network.target

[Service]
Type=simple
User=agnovat
Group=agnovat
WorkingDirectory=/opt/agnovat-analyst
Environment="PATH=/opt/agnovat-analyst/venv/bin"
ExecStart=/opt/agnovat-analyst/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 5. Start Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable agnovat-analyst
sudo systemctl start agnovat-analyst
sudo systemctl status agnovat-analyst
```

### Option 2: Nginx Reverse Proxy

#### Install Nginx

```bash
sudo apt install nginx  # Ubuntu/Debian
sudo yum install nginx  # CentOS/RHEL
```

#### Configure Nginx

```bash
sudo nano /etc/nginx/sites-available/agnovat-analyst
```

Nginx configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL certificates (use certbot)
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Proxy to FastAPI
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Increase upload size for PDFs
    client_max_body_size 50M;
}
```

Enable and start:
```bash
sudo ln -s /etc/nginx/sites-available/agnovat-analyst /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## Docker Deployment

### Dockerfile

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download en_core_web_sm

# Copy application
COPY app/ ./app/
COPY .env.example .env

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  agnovat-analyst:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data  # Mount for PDFs
      - ./logs:/app/logs  # Mount for logs
    environment:
      - DEBUG=False
      - HOST=0.0.0.0
      - PORT=8000
      - LOG_LEVEL=INFO
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Build and Run

```bash
# Build image
docker-compose build

# Start service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop service
docker-compose down
```

---

## MCP Integration

### Claude Desktop Integration

#### 1. Install Claude Desktop

Download from: https://claude.ai/download

#### 2. Configure MCP Server

Edit Claude Desktop config:
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

Add server configuration:
```json
{
  "mcpServers": {
    "agnovat-analyst": {
      "command": "uvicorn",
      "args": [
        "app.main:app",
        "--host",
        "localhost",
        "--port",
        "8000"
      ],
      "cwd": "/path/to/agnovat-docs",
      "env": {
        "PYTHONPATH": "/path/to/agnovat-docs"
      }
    }
  }
}
```

#### 3. Restart Claude Desktop

Claude will automatically connect to the MCP server on startup.

### MCP Tool Access

Once connected, Claude can use all 23 tools:

```
User: "Analyze this practitioner report for bias"
Claude: [Uses Tool 5: analyze_racism_bias]

User: "Generate a QCAT bundle for this case"
Claude: [Uses Tool 23: generate_qcat_bundle]
```

---

## Security Considerations

### Production Security Checklist

✅ **Application Security:**
- [ ] Set `DEBUG=False` in production
- [ ] Restrict CORS origins
- [ ] Use HTTPS only
- [ ] Implement rate limiting
- [ ] Sanitize file paths
- [ ] Validate all inputs

✅ **System Security:**
- [ ] Run as non-root user
- [ ] Restrict file permissions
- [ ] Enable firewall
- [ ] Keep dependencies updated
- [ ] Monitor logs for suspicious activity

✅ **Data Security:**
- [ ] Encrypt sensitive documents
- [ ] Implement access controls
- [ ] Regular backups
- [ ] Secure document storage
- [ ] Chain of custody tracking (SHA-256 hashes)

### Security Configuration

#### Rate Limiting (Optional)

Install slowapi:
```bash
pip install slowapi
```

Add to `app/main.py`:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/api/analysis/analyze-racism-bias")
@limiter.limit("10/minute")
async def analyze_bias(request: Request, ...):
    ...
```

#### File Path Validation

Already implemented in services - validates paths before processing.

---

## Monitoring & Maintenance

### Health Monitoring

```bash
# Check service status
systemctl status agnovat-analyst

# Check health endpoint
curl http://localhost:8000/health

# View logs
journalctl -u agnovat-analyst -f
```

### Log Management

Configure log rotation (`/etc/logrotate.d/agnovat-analyst`):
```
/var/log/agnovat-analyst/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 agnovat agnovat
    sharedscripts
    postrotate
        systemctl reload agnovat-analyst
    endscript
}
```

### Performance Monitoring

Monitor key metrics:
- **Response times:** Should be < 30s for most analyses
- **Memory usage:** Should stay under 2GB
- **CPU usage:** Spikes during analysis are normal
- **Disk usage:** Monitor document storage

### Updates

```bash
# Stop service
sudo systemctl stop agnovat-analyst

# Backup
sudo cp -r /opt/agnovat-analyst /opt/agnovat-analyst.backup

# Update code
cd /opt/agnovat-analyst
sudo -u agnovat git pull  # If using git

# Update dependencies
sudo -u agnovat venv/bin/pip install -r requirements.txt --upgrade

# Restart service
sudo systemctl start agnovat-analyst

# Verify
curl http://localhost:8000/health
```

### Backup Strategy

```bash
#!/bin/bash
# Daily backup script

BACKUP_DIR="/backups/agnovat-analyst"
DATE=$(date +%Y%m%d)

# Backup application
tar -czf "$BACKUP_DIR/app-$DATE.tar.gz" /opt/agnovat-analyst

# Backup documents (if stored locally)
tar -czf "$BACKUP_DIR/docs-$DATE.tar.gz" /path/to/documents

# Keep only last 30 days
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete
```

---

## Troubleshooting

### Service Won't Start

```bash
# Check logs
journalctl -u agnovat-analyst -n 50

# Check port availability
sudo lsof -i :8000

# Verify permissions
ls -la /opt/agnovat-analyst
```

### High Memory Usage

```bash
# Check memory
free -h

# Restart service
sudo systemctl restart agnovat-analyst

# Consider adding swap if needed
```

### Slow Response Times

- Check CPU/memory availability
- Reduce concurrent requests
- Consider horizontal scaling
- Optimize PDF processing

---

## Production Checklist

Before going live:

- [ ] All dependencies installed
- [ ] Environment variables configured
- [ ] DEBUG=False
- [ ] HTTPS enabled
- [ ] Firewall configured
- [ ] Backups configured
- [ ] Monitoring enabled
- [ ] Health checks passing
- [ ] Security review completed
- [ ] Documentation reviewed
- [ ] Test suite passing
- [ ] MCP integration tested

---

## Support

For deployment issues:
1. Check logs: `journalctl -u agnovat-analyst`
2. Verify configuration: Review .env file
3. Test endpoints: Use API documentation
4. Check GitHub issues
5. Contact support team

---

**Production deployment complete!** The Agnovat Analyst MCP Server is now ready for use. 🚀
