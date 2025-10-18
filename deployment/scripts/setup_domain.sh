#!/bin/bash
set -e

echo "🌐 Setting up enterprisescanner.com domain"

# Get load balancer DNS from Terraform output
LB_DNS=$(cd deployment/production/terraform && terraform output -raw load_balancer_dns)

echo "📋 Load Balancer DNS: $LB_DNS"
echo ""
echo "🔧 Domain Configuration Instructions:"
echo "1. Log into your domain registrar (e.g., Namecheap, GoDaddy)"
echo "2. Create the following DNS records:"
echo ""
echo "   A Record:"
echo "   Name: @"
echo "   Value: [Load Balancer IP - get from AWS console]"
echo "   TTL: 300"
echo ""
echo "   CNAME Record:"
echo "   Name: www"
echo "   Value: enterprisescanner.com"
echo "   TTL: 300"
echo ""
echo "   MX Records (for email):"
echo "   Priority: 1, Value: aspmx.l.google.com"
echo "   Priority: 5, Value: alt1.aspmx.l.google.com"
echo "   Priority: 5, Value: alt2.aspmx.l.google.com"
echo "   Priority: 10, Value: alt3.aspmx.l.google.com"
echo "   Priority: 10, Value: alt4.aspmx.l.google.com"
echo ""
echo "3. Wait 5-30 minutes for DNS propagation"
echo "4. Test with: dig enterprisescanner.com"
echo ""
echo "✅ Domain setup instructions provided"
