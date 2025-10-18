#!/bin/bash
# Test script for ssh
# Generated: 2025-10-18T18:29:09.130573

echo "Testing configuration..."
sshd -t

if [ $? -eq 0 ]; then
    echo "✅ Configuration is valid"
    exit 0
else
    echo "❌ Configuration has errors"
    exit 1
fi
