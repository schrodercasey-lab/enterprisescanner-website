#!/bin/bash
# Test script for nginx
# Generated: 2025-10-18T19:52:27.429774

echo "Testing configuration..."
nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Configuration is valid"
    exit 0
else
    echo "❌ Configuration has errors"
    exit 1
fi
