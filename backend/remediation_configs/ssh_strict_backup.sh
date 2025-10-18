#!/bin/bash
# Backup script for ssh
# Generated: 2025-10-18T18:29:09.130573

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/root/config_backups"
CONFIG_FILE="/etc/ssh/sshd_config"

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
