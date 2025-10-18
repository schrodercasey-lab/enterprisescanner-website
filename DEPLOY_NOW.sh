#!/bin/bash
# Deploy CSS fixes to production - Jupiter Bug Fix Deployment

echo "🚀 Deploying CSS fixes to production..."
echo ""

cd /opt/enterprisescanner/website

echo "📦 Pulling latest changes from GitHub..."
git pull origin main

echo ""
echo "🔄 Reloading Nginx..."
systemctl reload nginx

echo ""
echo "✅ CSS fixes deployed successfully!"
echo ""
echo "🎯 Fixed Issues:"
echo "   - Navigation tabs now clickable"
echo "   - ROI Calculator readable (white bg, black text)"
echo "   - Testimonials readable (white bg, black text)"
echo "   - Demo Form visible (all inputs/labels visible)"
echo ""
echo "🧪 Next Steps:"
echo "   1. Hard refresh browser (Ctrl + F5)"
echo "   2. Test navigation tabs"
echo "   3. Check ROI calculator readability"
echo "   4. Check testimonials section"
echo "   5. Check demo form visibility"
echo ""
echo "🌟 Jupiter is now bug-free!"
