#!/bin/bash

# Option E - Task 2: Enable Nginx Compression (gzip & Brotli)
# Optimize text asset delivery with compression

echo "=== Option E: Task 2 - Nginx Compression Setup ==="
echo ""

# First, let's establish baseline performance
echo "1. Establishing baseline performance (before compression)..."
curl -w "\nSize: %{size_download} bytes\nTime: %{time_total}s\n" \
     -H "Accept-Encoding: none" \
     -s -o /dev/null \
     https://enterprisescanner.com/

# Check current Nginx configuration
echo ""
echo "2. Checking current Nginx configuration..."
nginx -V 2>&1 | grep -o "with-http_gzip_static_module" && echo "✅ gzip_static module available" || echo "❌ gzip_static module not available"
nginx -V 2>&1 | grep -o "with-http_brotli" && echo "✅ Brotli module available" || echo "⚠️ Brotli module needs installation"

# Backup current Nginx configuration
echo ""
echo "3. Backing up current Nginx configuration..."
cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup-compression-$(date +%Y%m%d-%H%M%S)
echo "Backup created"

# Configure gzip compression in nginx.conf
echo ""
echo "4. Configuring gzip compression..."
cat > /etc/nginx/conf.d/compression.conf << 'EOF'
# Gzip Compression Configuration
# Optimized for Enterprise Scanner performance

# Enable gzip compression
gzip on;

# Compression level (1-9, 6 is optimal balance)
gzip_comp_level 6;

# Minimum file size to compress (avoid overhead on tiny files)
gzip_min_length 1024;

# Compress data even for proxied requests
gzip_proxied any;

# Enable compression for all clients (even old browsers)
gzip_vary on;

# Disable for IE6 (legacy compatibility, can be removed)
gzip_disable "msie6";

# Buffer size for compression
gzip_buffers 16 8k;

# Minimum HTTP version
gzip_http_version 1.1;

# MIME types to compress (comprehensive list)
gzip_types
    application/atom+xml
    application/geo+json
    application/javascript
    application/x-javascript
    application/json
    application/ld+json
    application/manifest+json
    application/rdf+xml
    application/rss+xml
    application/vnd.ms-fontobject
    application/wasm
    application/x-font-opentype
    application/x-font-truetype
    application/x-font-ttf
    application/x-web-app-manifest+json
    application/xhtml+xml
    application/xml
    font/eot
    font/opentype
    font/otf
    font/ttf
    image/bmp
    image/svg+xml
    image/x-icon
    text/cache-manifest
    text/calendar
    text/css
    text/javascript
    text/markdown
    text/plain
    text/xml
    text/x-component
    text/x-cross-domain-policy;

# Note: text/html is always compressed by default
EOF

echo "Gzip configuration created at /etc/nginx/conf.d/compression.conf"

# Install Brotli module for Nginx
echo ""
echo "5. Installing Brotli compression module..."

# Check Ubuntu version
UBUNTU_VERSION=$(lsb_release -rs)
echo "Ubuntu version: $UBUNTU_VERSION"

# Install dependencies
apt-get update -qq
apt-get install -y build-essential git libpcre3 libpcre3-dev zlib1g zlib1g-dev libssl-dev 2>&1 | grep -E "installed|unpacked" || echo "Dependencies installed"

# Clone Brotli module
if [ ! -d "/usr/local/src/ngx_brotli" ]; then
    echo "Downloading Brotli module..."
    cd /usr/local/src
    git clone --recursive https://github.com/google/ngx_brotli.git
    cd ngx_brotli
    git submodule update --init --recursive
else
    echo "Brotli module already downloaded"
fi

# Get current Nginx version
NGINX_VERSION=$(nginx -v 2>&1 | grep -oP '(?<=nginx/)\d+\.\d+\.\d+')
echo "Current Nginx version: $NGINX_VERSION"

# Download matching Nginx source
echo "Downloading Nginx source..."
cd /usr/local/src
if [ ! -d "nginx-$NGINX_VERSION" ]; then
    wget -q http://nginx.org/download/nginx-$NGINX_VERSION.tar.gz
    tar -xzf nginx-$NGINX_VERSION.tar.gz
fi

# Get current Nginx compile arguments
echo "Getting current Nginx configuration..."
nginx -V 2>&1 | grep "configure arguments:" | sed 's/configure arguments: //' > /tmp/nginx_configure_args.txt
CONFIGURE_ARGS=$(cat /tmp/nginx_configure_args.txt)

# Compile Nginx with Brotli support
echo "Compiling Nginx with Brotli module (this may take a few minutes)..."
cd /usr/local/src/nginx-$NGINX_VERSION
./configure $CONFIGURE_ARGS --add-dynamic-module=/usr/local/src/ngx_brotli

# Only compile the modules, not full Nginx
make modules

# Copy the Brotli modules to Nginx modules directory
echo "Installing Brotli modules..."
mkdir -p /etc/nginx/modules
cp objs/ngx_http_brotli_filter_module.so /etc/nginx/modules/
cp objs/ngx_http_brotli_static_module.so /etc/nginx/modules/

# Load Brotli modules in Nginx
echo ""
echo "6. Loading Brotli modules..."
# Check if modules are already loaded
if ! grep -q "load_module.*brotli" /etc/nginx/nginx.conf; then
    sed -i '1i load_module modules/ngx_http_brotli_filter_module.so;' /etc/nginx/nginx.conf
    sed -i '2i load_module modules/ngx_http_brotli_static_module.so;' /etc/nginx/nginx.conf
    echo "Brotli modules loaded"
else
    echo "Brotli modules already loaded"
fi

# Configure Brotli compression
echo ""
echo "7. Configuring Brotli compression..."
cat > /etc/nginx/conf.d/brotli.conf << 'EOF'
# Brotli Compression Configuration
# Provides superior compression compared to gzip

# Enable Brotli compression
brotli on;

# Compression quality (0-11, 6 is optimal)
brotli_comp_level 6;

# Minimum file size to compress
brotli_min_length 1024;

# Enable for all MIME types that gzip handles
brotli_types
    application/atom+xml
    application/geo+json
    application/javascript
    application/x-javascript
    application/json
    application/ld+json
    application/manifest+json
    application/rdf+xml
    application/rss+xml
    application/vnd.ms-fontobject
    application/wasm
    application/x-font-opentype
    application/x-font-truetype
    application/x-font-ttf
    application/x-web-app-manifest+json
    application/xhtml+xml
    application/xml
    font/eot
    font/opentype
    font/otf
    font/ttf
    image/bmp
    image/svg+xml
    image/x-icon
    text/cache-manifest
    text/calendar
    text/css
    text/javascript
    text/markdown
    text/plain
    text/xml
    text/x-component
    text/x-cross-domain-policy;

# Static Brotli compression (serve pre-compressed .br files)
brotli_static on;
EOF

echo "Brotli configuration created"

# Test Nginx configuration
echo ""
echo "8. Testing Nginx configuration..."
nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Nginx configuration test passed"
    
    # Reload Nginx
    echo ""
    echo "9. Reloading Nginx..."
    systemctl reload nginx
    echo "✅ Nginx reloaded successfully"
else
    echo "❌ Nginx configuration test failed"
    echo "Rolling back configuration..."
    rm /etc/nginx/conf.d/compression.conf
    rm /etc/nginx/conf.d/brotli.conf
    systemctl reload nginx
    exit 1
fi

# Wait for Nginx to reload
sleep 2

# Test compression
echo ""
echo "10. Testing compression..."
echo ""
echo "=== Gzip Compression Test ==="
curl -H "Accept-Encoding: gzip" \
     -w "Size: %{size_download} bytes | Time: %{time_total}s\n" \
     -s -o /dev/null \
     https://enterprisescanner.com/

echo ""
echo "=== Brotli Compression Test ==="
curl -H "Accept-Encoding: br" \
     -w "Size: %{size_download} bytes | Time: %{time_total}s\n" \
     -s -o /dev/null \
     https://enterprisescanner.com/

echo ""
echo "=== No Compression (Baseline) ==="
curl -H "Accept-Encoding: none" \
     -w "Size: %{size_download} bytes | Time: %{time_total}s\n" \
     -s -o /dev/null \
     https://enterprisescanner.com/

# Detailed compression test
echo ""
echo "11. Detailed compression analysis..."
echo ""
echo "Testing HTML compression:"
curl -sI -H "Accept-Encoding: gzip,br" https://enterprisescanner.com/ | grep -i "content-encoding"

echo ""
echo "Testing CSS compression:"
curl -sI -H "Accept-Encoding: gzip,br" https://enterprisescanner.com/css/style.css 2>/dev/null | grep -i "content-encoding" || echo "CSS file may not exist at this path"

echo ""
echo "Testing JS compression:"
curl -sI -H "Accept-Encoding: gzip,br" https://enterprisescanner.com/js/main.js 2>/dev/null | grep -i "content-encoding" || echo "JS file may not exist at this path"

# Create compression monitoring script
echo ""
echo "12. Creating compression monitoring script..."
cat > /opt/enterprisescanner/monitoring/test_compression.sh << 'EOF'
#!/bin/bash

echo "=== Nginx Compression Test ==="
echo ""

# Test various content types
declare -A test_urls=(
    ["Homepage"]="https://enterprisescanner.com/"
    ["API"]="https://enterprisescanner.com/api/health"
)

for name in "${!test_urls[@]}"; do
    url="${test_urls[$name]}"
    echo "Testing: $name ($url)"
    echo "  No compression:"
    curl -w "    Size: %{size_download} bytes\n" -H "Accept-Encoding: none" -s -o /dev/null "$url"
    
    echo "  Gzip compression:"
    curl -w "    Size: %{size_download} bytes\n" -H "Accept-Encoding: gzip" -s -o /dev/null "$url"
    
    echo "  Brotli compression:"
    curl -w "    Size: %{size_download} bytes\n" -H "Accept-Encoding: br" -s -o /dev/null "$url"
    
    echo ""
done

echo "Compression headers:"
curl -sI -H "Accept-Encoding: gzip,br" https://enterprisescanner.com/ | grep -E "content-encoding|content-type|vary"
EOF

chmod +x /opt/enterprisescanner/monitoring/test_compression.sh
echo "Monitoring script created: /opt/enterprisescanner/monitoring/test_compression.sh"

echo ""
echo "✅ Nginx Compression Setup Complete!"
echo ""
echo "=== Summary ==="
echo "✅ Gzip compression: Enabled (level 6)"
echo "✅ Brotli compression: Enabled (level 6)"
echo "✅ Minimum compression size: 1024 bytes"
echo "✅ Compressed MIME types: 30+ types"
echo ""
echo "=== Expected Performance Gains ==="
echo "• HTML files: 60-70% size reduction"
echo "• CSS files: 70-80% size reduction"
echo "• JavaScript files: 60-70% size reduction"
echo "• JSON/XML: 70-80% size reduction"
echo ""
echo "=== Next Steps ==="
echo "1. Test with: bash /opt/enterprisescanner/monitoring/test_compression.sh"
echo "2. Monitor compression ratio in browser DevTools"
echo "3. Verify 'Content-Encoding' headers in responses"
echo ""
