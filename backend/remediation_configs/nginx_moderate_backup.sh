#!/bin/bash
# Backup script for nginx
# Generated: 2025-10-18T18:29:09.137528

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/root/config_backups"
CONFIG_FILE="/etc/nginx/nginx.conf"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup configuration
if [ -f "$CONFIG_FILE" ]; then
    cp "$CONFIG_FILE" "$BACKUP_DIR/$(basename $CONFIG_FILE).$TIMESTAMP.backup"
    echo "✅ Backup created: $BACKUP_DIR/$(basename $CONFIG_FILE).$TIMESTAMP.backup"
else
    echo "❌ Config file not found: $CONFIG_FILE"
    exit 1
fi
