#!/bin/bash
# SSL/TLS Setup with Let's Encrypt for Hostinger VPS
# Configures automatic SSL certificates for Mission Control + n8n

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
DOMAINS=("jarvis.yourdomain.com" "n8n.yourdomain.com")
EMAIL="${LETSENCRYPT_EMAIL:-admin@yourdomain.com}"
NGINX_SSL_DIR="/opt/data/JARVIS_OS/deploy/nginx/ssl"
CERTBOT_WEBROOT="/opt/data/JARVIS_OS/deploy/nginx/certbot"

main() {
    log "═══════════════════════════════════════"
    log "  SSL/TLS SETUP WITH LET'S ENCRYPT"
    log "═══════════════════════════════════════"
    log "Domains: ${DOMAINS[*]}"
    log "Email: $EMAIL"
    
    check_root
    install_certbot
    setup_directories
    obtain_certificates
    configure_nginx_ssl
    setup_auto_renewal
    verify_certificates
    
    log "═══════════════════════════════════════"
    success "SSL/TLS SETUP COMPLETE!"
    log "═══════════════════════════════════════"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        error "This script must be run as root (use sudo)"
        exit 1
    fi
}

install_certbot() {
    log "Installing Certbot..."
    apt-get update
    apt-get install -y certbot python3-certbot-nginx
    success "Certbot installed"
}

setup_directories() {
    log "Setting up directories..."
    mkdir -p "$NGINX_SSL_DIR"
    mkdir -p "$CERTBOT_WEBROOT"
    success "Directories created"
}

obtain_certificates() {
    log "Obtaining SSL certificates..."
    
    # Stop nginx if running
    systemctl stop nginx 2>/dev/null || true
    
    for domain in "${DOMAINS[@]}"; do
        log "Obtaining certificate for $domain..."
        certbot certonly --standalone \
            --non-interactive \
            --agree-tos \
            --email "$EMAIL" \
            --domains "$domain" \
            --preferred-challenges http
        
        if [[ $? -eq 0 ]]; then
            success "Certificate obtained for $domain"
        else
            error "Failed to obtain certificate for $domain"
            exit 1
        fi
    done
    
    # Copy certificates to nginx ssl directory
    for domain in "${DOMAINS[@]}"; do
        if [[ -d "/etc/letsencrypt/live/$domain" ]]; then
            cp -L "/etc/letsencrypt/live/$domain/fullchain.pem" "$NGINX_SSL_DIR/${domain}-fullchain.pem"
            cp -L "/etc/letsencrypt/live/$domain/privkey.pem" "$NGINX_SSL_DIR/${domain}-privkey.pem"
        fi
    done
    
    # Generate DH parameters
    if [[ ! -f "$NGINX_SSL_DIR/dhparam.pem" ]]; then
        log "Generating DH parameters (this may take a minute)..."
        openssl dhparam -out "$NGINX_SSL_DIR/dhparam.pem" 2048
    fi
    
    success "Certificates copied to nginx directory"
}

configure_nginx_ssl() {
    log "Configuring Nginx SSL..."
    
    # Create main SSL config snippet
    cat > "$NGINX_SSL_DIR/ssl-params.conf" <<EOF
# SSL Parameters for JARVIS
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;
ssl_prefer_server_ciphers off;
ssl_session_timeout 1d;
ssl_session_cache shared:SSL:50m;
ssl_session_tickets off;

# OCSP Stapling
ssl_stapling on;
ssl_stapling_verify on;
resolver 8.8.8.8 8.8.4.4 valid=300s;
resolver_timeout 5s;

# Security Headers
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
EOF
    
    success "SSL parameters configured"
}

setup_auto_renewal() {
    log "Setting up automatic certificate renewal..."
    
    # Create renewal script
    cat > /usr/local/bin/renew-jarvis-certs <<'RENEWAL_SCRIPT'
#!/bin/bash
# Renew JARVIS SSL certificates and reload nginx

DOMAINS=("jarvis.yourdomain.com" "n8n.yourdomain.com")
NGINX_SSL_DIR="/opt/data/JARVIS_OS/deploy/nginx/ssl"

log() { echo "[$(date)] $1"; }

log "Starting certificate renewal..."

# Renew certificates
certbot renew --quiet --post-hook "systemctl reload nginx"

# Copy renewed certificates
for domain in "${DOMAINS[@]}"; do
    if [[ -d "/etc/letsencrypt/live/$domain" ]]; then
        cp -L "/etc/letsencrypt/live/$domain/fullchain.pem" "$NGINX_SSL_DIR/${domain}-fullchain.pem"
        cp -L "/etc/letsencrypt/live/$domain/privkey.pem" "$NGINX_SSL_DIR/${domain}-privkey.pem"
        log "Copied renewed certificates for $domain"
    fi
done

# Reload nginx
systemctl reload nginx
log "Certificate renewal complete"
RENEWAL_SCRIPT

    chmod +x /usr/local/bin/renew-jarvis-certs
    
    # Add cron job for daily renewal check
    cat > /etc/cron.d/jarvis-certbot-renewal <<EOF
# Renew JARVIS SSL certificates daily at 2:30 AM
30 2 * * * root /usr/local/bin/renew-jarvis-certs >> /var/log/jarvis-certbot-renewal.log 2>&1
EOF
    
    success "Auto-renewal configured (daily at 2:30 AM)"
}

verify_certificates() {
    log "Verifying certificates..."
    
    for domain in "${DOMAINS[@]}"; do
        cert_file="$NGINX_SSL_DIR/${domain}-fullchain.pem"
        key_file="$NGINX_SSL_DIR/${domain}-privkey.pem"
        
        if [[ -f "$cert_file" && -f "$key_file" ]]; then
            # Check certificate validity
            expiry=$(openssl x509 -in "$cert_file" -noout -enddate | cut -d= -f2)
            log "$domain expires: $expiry"
            
            # Verify certificate and key match
            cert_mod=$(openssl x509 -noout -modulus -in "$cert_file" | openssl md5)
            key_mod=$(openssl rsa -noout -modulus -in "$key_file" | openssl md5)
            
            if [[ "$cert_mod" == "$key_mod" ]]; then
                success "$domain: Certificate and key match"
            else
                error "$domain: Certificate and key DO NOT MATCH"
                exit 1
            fi
        else
            error "$domain: Certificate files missing"
            exit 1
        fi
    done
    
    success "All certificates verified"
}

main "$@"