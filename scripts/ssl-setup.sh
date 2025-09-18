#!/bin/bash

# SSL/TLS Certificate Setup Script
# Supports Let's Encrypt with automatic renewal

set -e

# Configuration
DOMAIN=${1:-yourdomain.com}
EMAIL=${2:-admin@yourdomain.com}
SSL_DIR="/etc/ssl/certs"
NGINX_CONFIG_DIR="/etc/nginx/sites-enabled"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if certbot is installed
check_certbot() {
    if ! command -v certbot &> /dev/null; then
        print_status "Installing certbot..."
        apt-get update
        apt-get install -y certbot python3-certbot-nginx
        print_success "Certbot installed successfully"
    else
        print_success "Certbot is already installed"
    fi
}

# Function to validate domain
validate_domain() {
    print_status "Validating domain: $DOMAIN"
    
    if ! dig +short $DOMAIN | grep -E '^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$' > /dev/null; then
        print_error "Domain $DOMAIN does not resolve to an IP address"
        exit 1
    fi
    
    print_success "Domain $DOMAIN is valid"
}

# Function to create self-signed certificate for development
create_self_signed() {
    print_status "Creating self-signed certificate for development..."
    
    mkdir -p $SSL_DIR
    
    # Generate private key
    openssl genrsa -out $SSL_DIR/${DOMAIN}.key 2048
    
    # Generate certificate signing request
    openssl req -new -key $SSL_DIR/${DOMAIN}.key -out $SSL_DIR/${DOMAIN}.csr -subj "/CN=$DOMAIN"
    
    # Generate self-signed certificate
    openssl x509 -req -days 365 -in $SSL_DIR/${DOMAIN}.csr -signkey $SSL_DIR/${DOMAIN}.key -out $SSL_DIR/${DOMAIN}.crt
    
    # Clean up CSR
    rm $SSL_DIR/${DOMAIN}.csr
    
    print_success "Self-signed certificate created for $DOMAIN"
}

# Function to obtain Let's Encrypt certificate
obtain_letsencrypt() {
    print_status "Obtaining Let's Encrypt certificate for $DOMAIN..."
    
    # Stop nginx temporarily
    docker-compose stop nginx
    
    # Obtain certificate
    certbot certonly --standalone \
        --email $EMAIL \
        --agree-tos \
        --no-eff-email \
        --domains $DOMAIN,www.$DOMAIN
    
    if [ $? -eq 0 ]; then
        print_success "Let's Encrypt certificate obtained successfully"
        
        # Copy certificates to SSL directory
        mkdir -p $SSL_DIR
        cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem $SSL_DIR/${DOMAIN}.crt
        cp /etc/letsencrypt/live/$DOMAIN/privkey.pem $SSL_DIR/${DOMAIN}.key
        
        # Set proper permissions
        chmod 644 $SSL_DIR/${DOMAIN}.crt
        chmod 600 $SSL_DIR/${DOMAIN}.key
        
    else
        print_error "Failed to obtain Let's Encrypt certificate"
        exit 1
    fi
    
    # Restart nginx
    docker-compose start nginx
}

# Function to setup automatic renewal
setup_auto_renewal() {
    print_status "Setting up automatic certificate renewal..."
    
    # Create renewal script
    cat > /etc/cron.daily/certbot-renew << 'EOF'
#!/bin/bash
certbot renew --quiet --pre-hook "docker-compose stop nginx" --post-hook "docker-compose start nginx"
EOF
    
    chmod +x /etc/cron.daily/certbot-renew
    
    # Add to crontab as backup
    (crontab -l 2>/dev/null; echo "0 3 * * * /usr/bin/certbot renew --quiet --pre-hook 'docker-compose stop nginx' --post-hook 'docker-compose start nginx'") | crontab -
    
    print_success "Automatic renewal configured"
}

# Function to update nginx configuration
update_nginx_config() {
    print_status "Updating nginx configuration for SSL..."
    
    # Update production configuration
    sed -i "s/your-domain.com/$DOMAIN/g" nginx/sites-enabled/production.conf
    sed -i "s|/etc/ssl/certs/your-domain.crt|$SSL_DIR/${DOMAIN}.crt|g" nginx/sites-enabled/production.conf
    sed -i "s|/etc/ssl/private/your-domain.key|$SSL_DIR/${DOMAIN}.key|g" nginx/sites-enabled/production.conf
    
    print_success "Nginx configuration updated"
}

# Function to test SSL configuration
test_ssl_config() {
    print_status "Testing SSL configuration..."
    
    # Test nginx configuration
    docker-compose exec nginx nginx -t
    
    if [ $? -eq 0 ]; then
        print_success "Nginx configuration is valid"
        
        # Reload nginx
        docker-compose exec nginx nginx -s reload
        print_success "Nginx reloaded successfully"
    else
        print_error "Nginx configuration test failed"
        exit 1
    fi
    
    # Test SSL certificate
    sleep 5
    if openssl s_client -connect $DOMAIN:443 -servername $DOMAIN < /dev/null 2>/dev/null | openssl x509 -noout -text | grep -q "Subject:.*CN=$DOMAIN"; then
        print_success "SSL certificate is working correctly"
    else
        print_warning "SSL certificate test inconclusive"
    fi
}

# Function to show usage
show_usage() {
    echo "Usage: $0 <domain> <email> [options]"
    echo ""
    echo "Options:"
    echo "  --self-signed     Create self-signed certificate (for development)"
    echo "  --letsencrypt     Obtain Let's Encrypt certificate (for production)"
    echo "  --test           Test existing SSL configuration"
    echo ""
    echo "Examples:"
    echo "  $0 example.com admin@example.com --letsencrypt"
    echo "  $0 localhost admin@localhost --self-signed"
}

# Parse command line arguments
CERT_TYPE="letsencrypt"

for arg in "$@"; do
    case $arg in
        --self-signed)
            CERT_TYPE="self-signed"
            shift
            ;;
        --letsencrypt)
            CERT_TYPE="letsencrypt"
            shift
            ;;
        --test)
            CERT_TYPE="test"
            shift
            ;;
        --help|-h)
            show_usage
            exit 0
            ;;
    esac
done

# Validate input
if [ -z "$DOMAIN" ] || [ -z "$EMAIL" ]; then
    print_error "Domain and email are required"
    show_usage
    exit 1
fi

# Main execution
print_status "Starting SSL setup for domain: $DOMAIN"

case $CERT_TYPE in
    self-signed)
        create_self_signed
        ;;
    letsencrypt)
        check_certbot
        validate_domain
        obtain_letsencrypt
        setup_auto_renewal
        ;;
    test)
        test_ssl_config
        exit 0
        ;;
    *)
        print_error "Unknown certificate type: $CERT_TYPE"
        show_usage
        exit 1
        ;;
esac

update_nginx_config
test_ssl_config

print_success "SSL setup completed successfully for $DOMAIN"
print_status "Certificate location: $SSL_DIR/${DOMAIN}.crt"
print_status "Private key location: $SSL_DIR/${DOMAIN}.key"

if [ "$CERT_TYPE" = "letsencrypt" ]; then
    print_status "Certificate will auto-renew via cron job"
fi