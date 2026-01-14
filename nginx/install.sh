#!/bin/bash

# TaskMind Nginx Setup Script for GCP VM
# Run this script on your GCP VM to configure Nginx with SSL
# Usage: sudo ./install.sh taskmind.cloud.hnagnurtme.id.vn your-email@example.com

set -e

echo "=== TaskMind Nginx Setup with SSL ==="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (sudo)"
    exit 1
fi

# Variables
DOMAIN=${1:-"taskmind.cloud.hnagnurtme.id.vn"}
EMAIL=${2:-"admin@hnagnurtme.id.vn"}
NGINX_CONF_DIR="/etc/nginx"
SITES_AVAILABLE="$NGINX_CONF_DIR/sites-available"
SITES_ENABLED="$NGINX_CONF_DIR/sites-enabled"
SNIPPETS_DIR="$NGINX_CONF_DIR/snippets"
CERTBOT_DIR="/var/www/certbot"
CONF_FILE="taskmind.conf"
SITE_NAME="taskmind"

echo "Domain: $DOMAIN"
echo "Email: $EMAIL"

# Install nginx if not installed
if ! command -v nginx &> /dev/null; then
    echo "Installing Nginx..."
    apt update
    apt install -y nginx
fi

# Install Certbot
if ! command -v certbot &> /dev/null; then
    echo "Installing Certbot..."
    apt install -y certbot python3-certbot-nginx
fi

# Create directories
echo "Creating directories..."
mkdir -p "$SNIPPETS_DIR"
mkdir -p "$CERTBOT_DIR"

# Copy configuration files
echo "Copying configuration files..."
if [ -f "ssl-params.conf" ]; then
    cp ssl-params.conf "$SNIPPETS_DIR/ssl-params.conf"
else
    echo "Warning: ssl-params.conf not found, skipping..."
fi

if [ -f "$CONF_FILE" ]; then
    cp "$CONF_FILE" "$SITES_AVAILABLE/$SITE_NAME"
else
    echo "Error: $CONF_FILE not found!"
    exit 1
fi

# Enable site
echo "Enabling site..."
ln -sf "$SITES_AVAILABLE/$SITE_NAME" "$SITES_ENABLED/$SITE_NAME"

# Remove default site
rm -f "$SITES_ENABLED/default"

# Test configuration
echo "Testing Nginx configuration..."
nginx -t

# Reload nginx
echo "Reloading Nginx..."
systemctl reload nginx
systemctl enable nginx

# Check if SSL certificate already exists
if [ -d "/etc/letsencrypt/live/$DOMAIN" ]; then
    echo "SSL certificate already exists for $DOMAIN"
else
    # Obtain SSL certificate
    echo "Obtaining SSL certificate from Let's Encrypt..."
    certbot certonly --webroot \
        -w "$CERTBOT_DIR" \
        -d "$DOMAIN" \
        --email "$EMAIL" \
        --agree-tos \
        --no-eff-email \
        --non-interactive \
        --quiet || {
            echo "Failed to obtain SSL certificate"
            echo "Make sure:"
            echo "  1. DNS is properly configured for $DOMAIN"
            echo "  2. Port 80 is accessible from the internet"
            echo "  3. No firewall blocking HTTP traffic"
            exit 1
        }
    
    echo "SSL certificate obtained successfully!"
    
    # Reload nginx to apply SSL
    nginx -t && systemctl reload nginx
fi

# Setup auto-renewal
echo "Setting up SSL auto-renewal..."
systemctl enable certbot.timer
systemctl start certbot.timer

echo ""
echo "=== Setup Complete ==="
echo ""
echo "✓ Nginx installed and configured"
echo "✓ SSL certificate obtained for $DOMAIN"
echo "✓ Auto-renewal enabled"
echo ""
echo "URLs:"
echo "  - API: https://$DOMAIN"
echo "  - Health: https://$DOMAIN/api/v1/health"
echo "  - Docs: https://$DOMAIN/docs"
echo ""
echo "Next steps:"
echo "1. Start Docker containers: docker-compose -f docker-compose.prod.yml up -d"
echo "2. Check status: systemctl status nginx"
echo "3. View logs: journalctl -u nginx -f"
echo ""
