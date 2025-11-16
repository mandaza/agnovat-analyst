#!/bin/bash

# Agnovat Analyst - Security Hardening Script
# Run this on your remote server to apply security best practices

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "========================================="
echo "Agnovat Analyst - Security Hardening"
echo "========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Error: This script must be run as root${NC}"
    echo "Please run: sudo $0"
    exit 1
fi

# 1. Configure UFW Firewall
echo -e "${BLUE}🔥 Step 1: Configuring firewall (UFW)...${NC}"

# Install UFW if not present
if ! command -v ufw &> /dev/null; then
    apt-get update
    apt-get install -y ufw
fi

# Reset UFW to default
ufw --force reset

# Default policies
ufw default deny incoming
ufw default allow outgoing

# Allow SSH (prevent lockout)
ufw allow OpenSSH
ufw allow 22/tcp

# Allow HTTP and HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Enable UFW
ufw --force enable

echo -e "${GREEN}✅ Firewall configured${NC}"

# 2. Install and configure Fail2Ban
echo ""
echo -e "${BLUE}🛡️  Step 2: Installing Fail2Ban...${NC}"

if ! command -v fail2ban-client &> /dev/null; then
    apt-get install -y fail2ban
fi

# Create local jail configuration
cat > /etc/fail2ban/jail.local << 'F2B_EOF'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5
destemail = root@localhost
sendername = Fail2Ban

[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log
maxretry = 3
bantime = 86400

[nginx-http-auth]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 3

[nginx-limit-req]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 10
F2B_EOF

# Restart Fail2Ban
systemctl restart fail2ban
systemctl enable fail2ban

echo -e "${GREEN}✅ Fail2Ban installed and configured${NC}"

# 3. Configure SSH hardening
echo ""
echo -e "${BLUE}🔑 Step 3: Hardening SSH...${NC}"

# Backup original SSH config
cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup

# Apply SSH hardening
cat > /etc/ssh/sshd_config.d/hardening.conf << 'SSH_EOF'
# Disable root login (use sudo instead)
PermitRootLogin no

# Disable password authentication (use SSH keys)
PasswordAuthentication no
ChallengeResponseAuthentication no

# Disable empty passwords
PermitEmptyPasswords no

# Use SSH protocol 2 only
Protocol 2

# Disable X11 forwarding
X11Forwarding no

# Limit authentication attempts
MaxAuthTries 3

# Set login grace time
LoginGraceTime 60

# Allow only specific users (uncomment and customize)
# AllowUsers your-username

# Use strong ciphers
Ciphers chacha20-poly1305@openssh.com,aes256-gcm@openssh.com,aes128-gcm@openssh.com,aes256-ctr,aes192-ctr,aes128-ctr
MACs hmac-sha2-512-etm@openssh.com,hmac-sha2-256-etm@openssh.com,hmac-sha2-512,hmac-sha2-256
KexAlgorithms curve25519-sha256,curve25519-sha256@libssh.org,diffie-hellman-group-exchange-sha256
SSH_EOF

# Test SSH configuration
if sshd -t; then
    echo -e "${GREEN}✅ SSH configuration is valid${NC}"
    echo -e "${YELLOW}⚠️  SSH will be reloaded after completion${NC}"
else
    echo -e "${RED}❌ SSH configuration is invalid, reverting...${NC}"
    rm /etc/ssh/sshd_config.d/hardening.conf
    exit 1
fi

# 4. Set up automatic security updates
echo ""
echo -e "${BLUE}🔄 Step 4: Configuring automatic security updates...${NC}"

apt-get install -y unattended-upgrades apt-listchanges

# Configure unattended upgrades
cat > /etc/apt/apt.conf.d/50unattended-upgrades << 'UU_EOF'
Unattended-Upgrade::Allowed-Origins {
    "${distro_id}:${distro_codename}-security";
};

Unattended-Upgrade::AutoFixInterruptedDpkg "true";
Unattended-Upgrade::MinimalSteps "true";
Unattended-Upgrade::InstallOnShutdown "false";
Unattended-Upgrade::Remove-Unused-Kernel-Packages "true";
Unattended-Upgrade::Remove-Unused-Dependencies "true";
Unattended-Upgrade::Automatic-Reboot "false";
UU_EOF

# Enable automatic updates
cat > /etc/apt/apt.conf.d/20auto-upgrades << 'AU_EOF'
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Download-Upgradeable-Packages "1";
APT::Periodic::AutocleanInterval "7";
APT::Periodic::Unattended-Upgrade "1";
AU_EOF

echo -e "${GREEN}✅ Automatic security updates enabled${NC}"

# 5. Secure shared memory
echo ""
echo -e "${BLUE}🔒 Step 5: Securing shared memory...${NC}"

if ! grep -q "tmpfs /run/shm" /etc/fstab; then
    echo "tmpfs /run/shm tmpfs defaults,noexec,nosuid 0 0" >> /etc/fstab
    echo -e "${GREEN}✅ Shared memory secured (will apply after reboot)${NC}"
else
    echo -e "${GREEN}✅ Shared memory already secured${NC}"
fi

# 6. Configure system limits
echo ""
echo -e "${BLUE}⚙️  Step 6: Configuring system limits...${NC}"

cat > /etc/security/limits.d/99-agnovat.conf << 'LIMITS_EOF'
# Maximum number of open files
* soft nofile 65536
* hard nofile 65536

# Maximum number of processes
* soft nproc 32768
* hard nproc 32768
LIMITS_EOF

echo -e "${GREEN}✅ System limits configured${NC}"

# 7. Set up log rotation
echo ""
echo -e "${BLUE}📝 Step 7: Configuring log rotation...${NC}"

cat > /etc/logrotate.d/agnovat << 'LOGROTATE_EOF'
/var/log/nginx/agnovat-*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data adm
    sharedscripts
    postrotate
        [ -f /var/run/nginx.pid ] && kill -USR1 `cat /var/run/nginx.pid`
    endscript
}

/home/*/agnovat-analyst/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 0644 root root
}
LOGROTATE_EOF

echo -e "${GREEN}✅ Log rotation configured${NC}"

# 8. Create security monitoring script
echo ""
echo -e "${BLUE}👁️  Step 8: Creating security monitoring script...${NC}"

cat > /usr/local/bin/agnovat-security-check.sh << 'MONITOR_EOF'
#!/bin/bash

echo "=== Agnovat Security Check ==="
echo "Date: $(date)"
echo ""

echo "1. Failed SSH login attempts (last 24h):"
grep "Failed password" /var/log/auth.log | grep "$(date +%b\ %d)" | wc -l

echo ""
echo "2. Fail2Ban banned IPs:"
fail2ban-client status sshd | grep "Banned IP"

echo ""
echo "3. Disk usage:"
df -h | grep -E '^/dev/'

echo ""
echo "4. Docker container status:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "5. Recent system errors:"
journalctl -p err -n 10 --no-pager

echo ""
echo "6. Nginx status:"
systemctl status nginx --no-pager | head -5

echo ""
echo "7. SSL certificate expiry:"
if [ -d "/etc/letsencrypt/live" ]; then
    for cert in /etc/letsencrypt/live/*/cert.pem; do
        domain=$(basename $(dirname $cert))
        expiry=$(openssl x509 -enddate -noout -in "$cert" | cut -d= -f2)
        echo "  $domain: $expiry"
    done
else
    echo "  No SSL certificates found"
fi

echo ""
echo "=== End Security Check ==="
MONITOR_EOF

chmod +x /usr/local/bin/agnovat-security-check.sh

echo -e "${GREEN}✅ Security monitoring script created${NC}"
echo "   Run with: /usr/local/bin/agnovat-security-check.sh"

# 9. Create backup script
echo ""
echo -e "${BLUE}💾 Step 9: Creating backup script...${NC}"

cat > /usr/local/bin/agnovat-backup.sh << 'BACKUP_EOF'
#!/bin/bash

BACKUP_DIR="/backups/agnovat"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=7

mkdir -p $BACKUP_DIR

echo "Starting backup at $(date)"

# Backup Docker volumes
docker run --rm \
  -v agnovat_data:/data \
  -v $BACKUP_DIR:/backup \
  ubuntu tar czf /backup/data-$DATE.tar.gz /data 2>/dev/null

# Backup application configs
if [ -d "$HOME/agnovat-analyst" ]; then
    tar czf $BACKUP_DIR/config-$DATE.tar.gz \
        $HOME/agnovat-analyst/.env.production \
        /etc/nginx/sites-available/agnovat 2>/dev/null
fi

# Cleanup old backups
find $BACKUP_DIR -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup completed at $(date)"
echo "Backup location: $BACKUP_DIR"
ls -lh $BACKUP_DIR/*$DATE*
BACKUP_EOF

chmod +x /usr/local/bin/agnovat-backup.sh

echo -e "${GREEN}✅ Backup script created${NC}"
echo "   Run with: /usr/local/bin/agnovat-backup.sh"

# 10. Set up cron jobs
echo ""
echo -e "${BLUE}⏰ Step 10: Setting up cron jobs...${NC}"

# Create crontab entries
(crontab -l 2>/dev/null; echo "# Agnovat Analyst - Security monitoring (daily at 2 AM)") | crontab -
(crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/agnovat-security-check.sh >> /var/log/agnovat-security-check.log 2>&1") | crontab -
(crontab -l 2>/dev/null; echo "# Agnovat Analyst - Backups (daily at 3 AM)") | crontab -
(crontab -l 2>/dev/null; echo "0 3 * * * /usr/local/bin/agnovat-backup.sh >> /var/log/agnovat-backup.log 2>&1") | crontab -
(crontab -l 2>/dev/null; echo "# Agnovat Analyst - SSL certificate renewal check (weekly)") | crontab -
(crontab -l 2>/dev/null; echo "0 4 * * 0 certbot renew --quiet --post-hook 'systemctl reload nginx'") | crontab -

echo -e "${GREEN}✅ Cron jobs configured${NC}"

# 11. Kernel security parameters
echo ""
echo -e "${BLUE}🔧 Step 11: Setting kernel security parameters...${NC}"

cat > /etc/sysctl.d/99-agnovat-security.conf << 'SYSCTL_EOF'
# IP Spoofing protection
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.default.rp_filter = 1

# Ignore ICMP redirects
net.ipv4.conf.all.accept_redirects = 0
net.ipv6.conf.all.accept_redirects = 0

# Ignore send redirects
net.ipv4.conf.all.send_redirects = 0

# Disable source packet routing
net.ipv4.conf.all.accept_source_route = 0
net.ipv6.conf.all.accept_source_route = 0

# Log Martians
net.ipv4.conf.all.log_martians = 1

# Ignore ICMP ping requests
net.ipv4.icmp_echo_ignore_all = 0

# Ignore Broadcast Request
net.ipv4.icmp_echo_ignore_broadcasts = 1

# SYN flood protection
net.ipv4.tcp_syncookies = 1
net.ipv4.tcp_max_syn_backlog = 2048
net.ipv4.tcp_synack_retries = 2
net.ipv4.tcp_syn_retries = 5

# Increase local port range
net.ipv4.ip_local_port_range = 1024 65535

# TCP keepalive
net.ipv4.tcp_keepalive_time = 600
net.ipv4.tcp_keepalive_probes = 5
net.ipv4.tcp_keepalive_intvl = 15
SYSCTL_EOF

# Apply sysctl settings
sysctl -p /etc/sysctl.d/99-agnovat-security.conf > /dev/null

echo -e "${GREEN}✅ Kernel security parameters applied${NC}"

# Summary
echo ""
echo "========================================="
echo -e "${GREEN}✅ Security Hardening Complete!${NC}"
echo "========================================="
echo ""
echo "Applied security measures:"
echo "  ✅ UFW firewall configured (ports 22, 80, 443)"
echo "  ✅ Fail2Ban installed and active"
echo "  ✅ SSH hardened (key-based auth, no root login)"
echo "  ✅ Automatic security updates enabled"
echo "  ✅ Shared memory secured"
echo "  ✅ System limits configured"
echo "  ✅ Log rotation configured"
echo "  ✅ Security monitoring script created"
echo "  ✅ Backup script created"
echo "  ✅ Cron jobs scheduled"
echo "  ✅ Kernel security parameters optimized"
echo ""
echo "Scheduled tasks:"
echo "  - Daily security check at 2:00 AM"
echo "  - Daily backup at 3:00 AM"
echo "  - Weekly SSL renewal check on Sundays at 4:00 AM"
echo ""
echo "Manual commands:"
echo "  Security check: /usr/local/bin/agnovat-security-check.sh"
echo "  Backup:         /usr/local/bin/agnovat-backup.sh"
echo "  View logs:      journalctl -f"
echo "  UFW status:     ufw status verbose"
echo "  Fail2Ban:       fail2ban-client status"
echo ""
echo -e "${YELLOW}⚠️  Important: SSH will be reloaded now${NC}"
echo "If you're using password auth, make sure you have SSH key access set up first!"
echo ""
read -p "Reload SSH service now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    systemctl reload sshd
    echo -e "${GREEN}✅ SSH service reloaded${NC}"
else
    echo -e "${YELLOW}⚠️  Remember to reload SSH manually: sudo systemctl reload sshd${NC}"
fi

echo ""
echo "🎉 Server is now hardened and secure!"
