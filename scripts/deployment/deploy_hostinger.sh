#!/bin/bash
# JARVIS OS - Hostinger VPS Complete Setup Script
# Deploys Mission Control + n8n + All Services to Hostinger VPS

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"; }
success() { echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] ✓${NC} $1"; }
warning() { echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] ⚠${NC} $1"; }
error() { echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ✗${NC} $1"; }

# Load environment variables
ENV_FILE="/opt/jarvis/deploy/.env"
if [[ -f "$ENV_FILE" ]]; then
    set -a
    source "$ENV_FILE"
    set +a
fi

# Configuration
DOMAIN="${JARVIS_DOMAIN:-jarvis.yourdomain.com}"
N8N_DOMAIN="${N8N_DOMAIN:-n8n.yourdomain.com}"
GITHUB_REPO="${GITHUB_REPO:-yourusername/JARVIS_OS}"
JARVIS_ROOT="/opt/data/JARVIS_OS"
DEPLOY_DIR="$JARVIS_ROOT/deploy"

main() {
    log "═══════════════════════════════════════════"
    log "  JARVIS OS - HOSTINGER VPS DEPLOYMENT"
    log "═══════════════════════════════════════════"
    log "Domain: $DOMAIN"
    log "n8n Domain: $N8N_DOMAIN"
    log "GitHub Repo: $GITHUB_REPO"
    
    check_root
    install_dependencies
    setup_ssh_keys
    clone_repository
    setup_environment
    generate_ssl_certificates
    deploy_services
    configure_firewall
    setup_cron_jobs
    verify_deployment
    
    log "═══════════════════════════════════════════"
    success "DEPLOYMENT COMPLETE!"
    log "═══════════════════════════════════════════"
    log "Mission Control: https://$DOMAIN"
    log "n8n Editor: https://$N8N_DOMAIN"
    log "Username: ${N8N_BASIC_AUTH_USER:-admin}"
    log "Password: ${N8N_BASIC_AUTH_PASSWORD:-<generated>}"
    log "═══════════════════════════════════════════"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        error "Must run as root. Use: sudo $0"
        exit 1
    fi
    success "Running as root"
}

install_dependencies() {
    log "Installing system dependencies..."
    
    apt-get update
    apt-get install -y \
        docker.io \
        docker-compose \
        nginx \
        certbot \
        python3-certbot-nginx \
        curl \
        jq \
        openssl \
        ufw \
        git \
        htop \
        net-tools \
        rsync
    
    # Enable services
    systemctl enable docker nginx
    systemctl start docker nginx
    
    # Install Docker Compose v2 if not present
    if ! docker compose version &>/dev/null; then
        log "Installing Docker Compose v2..."
        curl -SL https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-linux-x86_64 \
            -o /usr/local/bin/docker-compose
        chmod +x /usr/local/bin/docker-compose
    fi
    
    success "Dependencies installed"
}

setup_ssh_keys() {
    log "Setting up SSH keys for GitHub..."
    
    mkdir -p /root/.ssh
    chmod 700 /root/.ssh
    
    if [[ ! -f /root/.ssh/id_ed25519 ]]; then
        ssh-keygen -t ed25519 -C "jarvis@hostinger" -f /root/.ssh/id_ed25519 -N ""
        success "Generated new SSH key"
    else
        log "SSH key already exists"
    fi
    
    log "Add this public key to GitHub (Settings > SSH Keys):"
    cat /root/.ssh/id_ed25519.pub
    
    # Test GitHub connection
    ssh-keyscan github.com >> /root/.ssh/known_hosts 2>/dev/null
    chmod 644 /root/.ssh/known_hosts
}

clone_repository() {
    log "Cloning JARVIS OS repository..."
    
    if [[ -d "$JARVIS_ROOT" ]]; then
        log "Repository exists, pulling latest..."
        cd "$JARVIS_ROOT"
        git pull origin main
    else
        git clone "git@github.com:$GITHUB_REPO.git" "$JARVIS_ROOT"
        cd "$JARVIS_ROOT"
    fi
    
    success "Repository ready at $JARVIS_ROOT"
}

setup_environment() {
    log "Setting up environment configuration..."
    
    cd "$DEPLOY_DIR"
    
    if [[ ! -f ".env" ]]; then
        cat > .env <<EOF
# JARVIS OS Environment Configuration
# Generated on $(date)

# Domain Configuration
JARVIS_DOMAIN=$DOMAIN
N8N_DOMAIN=$N8N_DOMAIN

# n8n Configuration
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=$(openssl rand -base64 32)
N8N_API_KEY=$(openssl rand -base64 48)

# Database
POSTGRES_DB=n8n
POSTGRES_USER=n8n
POSTGRES_PASSWORD=$(openssl rand -base64 32)

# Redis
REDIS_PASSWORD=$(openssl rand -base64 32)

# GitHub
GITHUB_PAT=${GITHUB_PAT:-}
GITHUB_USERNAME=${GITHUB_USERNAME:-}
GITHUB_WEBHOOK_SECRET=$(openssl rand -base64 32)

# Hostinger
HOSTINGER_HOST=$(hostname -I | awk '{print $1}')
HOSTINGER_USER=root
HOSTINGER_PORT=65002

# Let's Encrypt
LETSENCRYPT_EMAIL=admin@$DOMAIN

# Timezone
TZ=America/Phoenix
GENERIC_TIMEZONE=America/Phoenix
EOF
        success "Created .env file"
    else
        log "Environment file already exists"
    fi
    
    # Secure the env file
    chmod 600 .env
}

generate_ssl_certificates() {
    log "Generating SSL certificates with Let's Encrypt..."
    
    # Stop nginx for standalone certbot
    systemctl stop nginx
    
    # Generate certificates for both domains
    for domain in "$DOMAIN" "$N8N_DOMAIN"; do
        certbot certonly --standalone \
            --non-interactive \
            --agree-tos \
            --email "${LETSENCRYPT_EMAIL:-admin@$domain}" \
            --domains "$domain" \
            --preferred-challenges http
    done
    
    # Copy certificates to nginx ssl directory
    mkdir -p "$DEPLOY_DIR/nginx/ssl"
    cp -L "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" "$DEPLOY_DIR/nginx/ssl/fullchain.pem"
    cp -L "/etc/letsencrypt/live/$DOMAIN/privkey.pem" "$DEPLOY_DIR/nginx/ssl/privkey.pem"
    
    # Create dhparam
    if [[ ! -f "$DEPLOY_DIR/nginx/ssl/dhparam.pem" ]]; then
        log "Generating DH parameters..."
        openssl dhparam -out "$DEPLOY_DIR/nginx/ssl/dhparam.pem" 2048
    fi
    
    # Setup auto-renewal
    cat > /etc/cron.d/certbot-renewal <<EOF
0 12 * * * root certbot renew --quiet --post-hook "
    cp -L /etc/letsencrypt/live/$DOMAIN/fullchain.pem $DEPLOY_DIR/nginx/ssl/fullchain.pem
    cp -L /etc/letsencrypt/live/$DOMAIN/privkey.pem $DEPLOY_DIR/nginx/ssl/privkey.pem
    systemctl reload nginx
"
EOF
    
    systemctl start nginx
    success "SSL certificates generated"
}

deploy_services() {
    log "Deploying services with Docker Compose..."
    
    cd "$DEPLOY_DIR"
    
    # Build and start services
    docker compose build --no-cache
    docker compose up -d --remove-orphans
    
    # Wait for services
    log "Waiting for services to start..."
    sleep 30
    
    # Check health
    local max_attempts=20
    local attempt=0
    
    while [[ $attempt -lt $max_attempts ]]; do
        if docker compose ps | grep -q "healthy"; then
            break
        fi
        attempt=$((attempt + 1))
        log "Waiting for healthy services... ($attempt/$max_attempts)"
        sleep 10
    done
    
    docker compose ps
    success "Services deployed"
}

configure_firewall() {
    log "Configuring UFW firewall..."
    
    ufw --force enable
    ufw default deny incoming
    ufw default allow outgoing
    ufw allow 22/tcp      # SSH
    ufw allow 80/tcp      # HTTP
    ufw allow 443/tcp     # HTTPS
    ufw allow 65002/tcp   # Hostinger SSH
    
    # Allow Docker internal network
    ufw allow from 172.17.0.0/16
    ufw allow from 172.18.0.0/16
    ufw allow from 172.19.0.0/16
    ufw allow from 172.20.0.0/16
    
    success "Firewall configured"
}

setup_cron_jobs() {
    log "Setting up system cron jobs..."
    
    cat > /etc/cron.d/jarvis-os <<EOF
# JARVIS OS Scheduled Jobs

# Daily backup at 3 AM
0 3 * * * root cd $DEPLOY_DIR && docker compose exec -T backup_service python -m services.backup_service.backup_scheduler --full >> /var/log/jarvis-backup.log 2>&1

# Daily health check at 6 AM
0 6 * * * root cd $DEPLOY_DIR && docker compose exec -T mission_control curl -sf http://localhost:8080/health >> /var/log/jarvis-health.log 2>&1

# Weekly cleanup on Sunday at 2 AM
0 2 * * 0 root docker system prune -f >> /var/log/jarvis-cleanup.log 2>&1

# Log rotation daily
0 4 * * * root /usr/sbin/logrotate /etc/logrotate.d/jarvis-os

# Certificate renewal check (handled by certbot cron)
EOF
    
    # Logrotate config
    cat > /etc/logrotate.d/jarvis-os <<EOF
/var/log/jarvis-*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 root root
}
EOF
    
    success "Cron jobs configured"
}

verify_deployment() {
    log "Verifying deployment..."
    
    local checks_passed=0
    local checks_total=4
    
    # Check Mission Control
    if curl -sf "https://$DOMAIN/health" > /dev/null; then
        success "Mission Control: HEALTHY"
        checks_passed=$((checks_passed + 1))
    else
        warning "Mission Control: NOT RESPONDING"
    fi
    
    # Check n8n
    if curl -sf "https://$N8N_DOMAIN/healthz" > /dev/null; then
        success "n8n: HEALTHY"
        checks_passed=$((checks_passed + 1))
    else
        warning "n8n: NOT RESPONDING"
    fi
    
    # Check Docker services
    if docker compose -f "$DEPLOY_DIR/docker-compose.yml" ps | grep -q "Up"; then
        success "Docker Services: RUNNING"
        checks_passed=$((checks_passed + 1))
    else
        warning "Docker Services: SOME DOWN"
    fi
    
    # Check SSL
    if openssl s_client -connect "$DOMAIN:443" -servername "$DOMAIN" </dev/null 2>/dev/null | openssl x509 -noout -checkend 86400 > /dev/null; then
        success "SSL Certificate: VALID"
        checks_passed=$((checks_passed + 1))
    else
        warning "SSL Certificate: EXPIRING SOON OR INVALID"
    fi
    
    log "Health Checks: $checks_passed/$checks_total passed"
    
    if [[ $checks_passed -eq $checks_total ]]; then
        success "ALL CHECKS PASSED - SYSTEM OPERATIONAL"
        return 0
    else
        warning "Some checks failed - review logs"
        return 1
    fi
}

# Handle script arguments
case "${1:-deploy}" in
    deploy)
        main
        ;;
    stop)
        log "Stopping all services..."
        cd "$DEPLOY_DIR" && docker compose down
        success "Services stopped"
        ;;
    restart)
        $0 stop
        sleep 5
        $0 deploy
        ;;
    status)
        cd "$DEPLOY_DIR" && docker compose ps
        ;;
    logs)
        cd "$DEPLOY_DIR" && docker compose logs -f --tail=100
        ;;
    update)
        log "Updating repository and redeploying..."
        cd "$JARVIS_ROOT" && git pull origin main
        $0 deploy
        ;;
    backup)
        log "Running manual backup..."
        cd "$DEPLOY_DIR" && docker compose exec -T backup_service python -m services.backup_service.backup_scheduler --full
        ;;
    *)
        echo "Usage: $0 {deploy|stop|restart|status|logs|update|backup}"
        exit 1
        ;;
esac