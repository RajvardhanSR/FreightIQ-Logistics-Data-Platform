#!/usr/bin/env bash
# ==============================================================================
# FreightIQ Production Deployment Script
# Target: AWS Lightsail Ubuntu 22.04 LTS (IP: 35.154.89.200)
# ==============================================================================

set -euo pipefail

echo "=========================================================="
echo " FreightIQ Production Deployment Pipeline"
echo " Domain: https://rajvardhansinghrathore.in"
echo "=========================================================="

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST_DIR="${APP_DIR}/dist"
TARGET_WEB_ROOT="/var/www/freightiq"
BACKUP_DIR="/var/backups/wordpress_migration_$(date +%Y%m%d_%H%M%S)"

# Step 1: Ensure dist build exists and is up to date
echo "[1/6] Compiling latest production static build..."
python3 "${APP_DIR}/scripts/build.py"
python3 "${APP_DIR}/scripts/sitemap.py"
python3 "${APP_DIR}/scripts/validate_links.py"

# Step 2: Server-side execution check
if [ "$EUID" -ne 0 ] && [ ! -d "/var/www" ]; then
    echo "----------------------------------------------------------"
    echo "ℹ️  NOTE: Local compilation completed successfully!"
    echo "To deploy directly to the AWS Lightsail server, run:"
    echo "  rsync -avz --delete dist/ ubuntu@35.154.89.200:/tmp/freightiq_dist/"
    echo "  ssh ubuntu@35.154.89.200 'sudo bash -s' < scripts/deploy.sh"
    echo "----------------------------------------------------------"
    exit 0
fi

# Step 3: Safeguard & Backup Existing WordPress installation
echo "[2/6] Executing non-destructive backup of existing server state..."
mkdir -p "${BACKUP_DIR}"

if [ -d "/var/www/html" ]; then
    echo "  Backing up /var/www/html to ${BACKUP_DIR}..."
    cp -r /var/www/html "${BACKUP_DIR}/html_backup" || true
fi

if [ -d "/var/www/wordpress" ]; then
    echo "  Backing up /var/www/wordpress to ${BACKUP_DIR}..."
    cp -r /var/www/wordpress "${BACKUP_DIR}/wordpress_backup" || true
fi

# Step 4: Provision target directory and sync files
echo "[3/6] Deploying production build to ${TARGET_WEB_ROOT}..."
mkdir -p "${TARGET_WEB_ROOT}"

if [ -d "/tmp/freightiq_dist" ]; then
    cp -r /tmp/freightiq_dist/* "${TARGET_WEB_ROOT}/"
elif [ -d "${DIST_DIR}" ]; then
    cp -r "${DIST_DIR}"/* "${TARGET_WEB_ROOT}/"
fi

# Step 5: Secure permissions
echo "[4/6] Setting secure file permissions (www-data:www-data)..."
chown -R www-data:www-data "${TARGET_WEB_ROOT}"
chmod -R 755 "${TARGET_WEB_ROOT}"

# Step 6: Install and test Nginx Configuration
echo "[5/6] Updating Nginx configuration..."
cp "${APP_DIR}/nginx/freightiq.conf" /etc/nginx/sites-available/freightiq.conf
ln -sf /etc/nginx/sites-available/freightiq.conf /etc/nginx/sites-enabled/freightiq.conf

# Test Nginx syntax
nginx -t

echo "[6/6] Reloading Nginx service..."
systemctl reload nginx

echo "=========================================================="
echo "✅ FreightIQ successfully deployed to https://rajvardhansinghrathore.in"
echo "=========================================================="
