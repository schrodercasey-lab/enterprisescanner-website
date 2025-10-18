#!/bin/bash
# Test script for nginx
# Generated: 2025-10-18T18:29:09.137528

echo "Testing configuration..."
nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Configuration is valid"
    exit 0
else
    echo "❌ Configuration has errors"
    exit 1
fi
