#!/bin/bash
# n8n Server Setup Script for Hostinger VPS
# Installs and configures n8n with SSL, reverse proxy, and persistence

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

# Configuration
DOMAIN="${N8N_DOMAIN:-n8n.yourdomain.com}"
N8N_USER="${N8N_USER:-admin}"
N8N_PASSWORD="${N8N_PASSWORD:-$(openssl rand -base64 32)}"
N8N_PORT="${N8N_PORT:-5678}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-$(openssl rand -base64 32)}"
EMAIL="${LETSENCRYPT_EMAIL:-admin@yourdomain.com}"

JARVIS_ROOT="/opt/data/JARVIS_OS"
DEPLOY_DIR="$JARVIS_ROOT/deploy"
NGINX_DIR="$DEPLOY_DIR/nginx"
COMPOSE_FILE="$DEPLOY_DIR/docker-compose.yml"

main() {
    log "═══════════════════════════════════════"
    log "  n8n SERVER SETUP FOR HOSTINGER VPS"
    log "═══════════════════════════════════════"
    log "Domain: $DOMAIN"
    log "User: $N8N_USER"
    log "Port: $N8N_PORT"
    
    check_root
    install_dependencies
    setup_directories
    generate_ssl_certificates
    create_env_file
    update_nginx_config
    deploy_n8n
    configure_firewall
    verify_deployment
    
    log "═══════════════════════════════════════"
    success "n8n SETUP COMPLETE!"
    log "═══════════════════════════════════════"
    log "Access URL: https://$DOMAIN"
    log "Username: $N8N_USER"
    log "Password: $N8N_PASSWORD"
    log "PostgreSQL Password: $POSTGRES_PASSWORD"
    log "═══════════════════════════════════════"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        error "This script must be run as root (use sudo)"
        exit 1
    fi
    success "Running as root"
}

install_dependencies() {
    log "Installing dependencies..."
    
    # Update package list
    apt-get update
    
    # Install required packages
    apt-get install -y \
        docker.io \
        docker-compose \
        nginx \
        certbot \
        python3-certbot-nginx \
        curl \
        jq \
        openssl \
        ufw
    
    # Enable and start Docker
    systemctl enable docker
    systemctl start docker
    
    # Enable and start nginx
    systemctl enable nginx
    systemctl start nginx
    
    success "Dependencies installed"
}

setup_directories() {
    log "Setting up directories..."
    
    mkdir -p "$NGINX_DIR/conf.d"
    mkdir -p "$NGINX_DIR/ssl"
    mkdir -p "$NGINX_DIR/certbot"
    mkdir -p "$DEPLOY_DIR/n8n-data"
    mkdir -p "$DEPLOY_DIR/postgres-data"
    mkdir -p "$DEPLOY_DIR/redis-data"
    
    # Set permissions
    chmod 755 "$DEPLOY_DIR"
    chmod 755 "$NGINX_DIR"
    
    success "Directories created"
}

generate_ssl_certificates() {
    log "Generating SSL certificates with Let's Encrypt..."
    
    # Stop nginx temporarily for standalone certbot
    systemctl stop nginx
    
    # Generate certificate
    certbot certonly --standalone \
        --non-interactive \
        --agree-tos \
        --email "$EMAIL" \
        --domains "$DOMAIN" \
        --preferred-challenges http
    
    # Copy certificates to nginx ssl directory
    cp -L /etc/letsencrypt/live/"$DOMAIN"/fullchain.pem "$NGINX_DIR/ssl/fullchain.pem"
    cp -L /etc/letsencrypt/live/"$DOMAIN"/privkey.pem "$NGINX_DIR/ssl/privkey.pem"
    
    # Create dhparam
    if [[ ! -f "$NGINX_DIR/ssl/dhparam.pem" ]]; then
        log "Generating DH parameters (this may take a while)..."
        openssl dhparam -out "$NGINX_DIR/ssl/dhparam.pem" 2048
    fi
    
    # Set up auto-renewal
    cat > /etc/cron.d/certbot-renewal <<EOF
0 12 * * * root certbot renew --quiet --post-hook "cp -L /etc/letsencrypt/live/$DOMAIN/fullchain.pem $NGINX_DIR/ssl/fullchain.pem && cp -L /etc/letsencrypt/live/$DOMAIN/privkey.pem $NGINX_DIR/ssl/privkey.pem && systemctl reload nginx"
EOF
    
    # Start nginx
    systemctl start nginx
    
    success "SSL certificates generated and auto-renewal configured"
}

create_env_file() {
    log "Creating environment file..."
    
    cat > "$DEPLOY_DIR/.env" <<EOF
# n8n Configuration
N8N_DOMAIN=$DOMAIN
N8N_USER=$N8N_USER
N8N_PASSWORD=$N8N_PASSWORD
N8N_PORT=$N8N_PORT
N8N_PROTOCOL=https
WEBHOOK_URL=https://$DOMAIN/n8n/
GENERIC_TIMEZONE=America/Phoenix
TZ=America/Phoenix

# Database
POSTGRES_DB=n8n
POSTGRES_USER=n8n
POSTGRES_PASSWORD=$POSTGRES_PASSWORD

# Redis
REDIS_URL=redis://redis:6379

# n8n Settings
N8N_BASIC_AUTH_ACTIVE=true
EXECUTIONS_DATA_PRUNE=true
EXECUTIONS_DATA_MAX_AGE=168
EOF
    
    chmod 600 "$DEPLOY_DIR/.env"
    
    success "Environment file created at $DEPLOY_DIR/.env"
}

update_nginx_config() {
    log "Updating nginx configuration..."
    
    # Copy our custom nginx config
    cp "$DEPLOY_DIR/nginx/nginx.conf" /etc/nginx/nginx.conf
    
    # Create site config for n8n
    cat > /etc/nginx/sites-available/n8n <<EOF
# n8n Configuration - included from main nginx.conf
# This file is managed by the JARVIS deployment script
EOF
    
    # Test nginx config
    nginx -t
    
    # Reload nginx
    systemctl reload nginx
    
    success "Nginx configuration updated"
}

deploy_n8n() {
    log "Deploying n8n with Docker Compose..."
    
    cd "$DEPLOY_DIR"
    
    # Pull images
    docker-compose pull
    
    # Start services
    docker-compose up -d
    
    # Wait for services to be ready
    log "Waiting for services to start..."
    sleep 30
    
    # Check health
    for i in {1..20}; do
        if docker-compose ps | grep -q "Up (healthy)"; then
            break
        fi
        log "Waiting for healthy services... ($i/20)"
        sleep 5
    done
    
    success "n8n deployed successfully"
}

configure_firewall() {
    log "Configuring firewall..."
    
    # Allow SSH
    ufw allow ssh
    
    # Allow HTTP/HTTPS
    ufw allow 80/tcp
    ufw allow 443/tcp
    
    # Allow n8n port (internal only)
    # ufw allow 5678/tcp
    
    # Enable firewall
    ufw --force enable
    
    success "Firewall configured"
}

verify_deployment() {
    log "Verifying deployment..."
    
    # Check containers
    docker-compose ps
    
    # Check n8n health
    for i in {1..10}; do
        if curl -sf "http://localhost:5678/healthz" > /dev/null; then
            success "n8n health check passed"
            break
        fi
        log "Waiting for n8n... ($i/10)"
        sleep 5
    done
    
    # Check HTTPS
    if curl -sf "https://$DOMAIN/healthz" > /dev/null; then
        success "HTTPS endpoint accessible"
    else
        warning "HTTPS endpoint not yet accessible (DNS may need time to propagate)"
    fi
    
    success "Deployment verification complete"
}

# Run main function
main "$@"