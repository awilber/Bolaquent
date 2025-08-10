#!/bin/bash

# Targeted fix for nginx static file serving issue
# This script fixes only the static file permissions and nginx configuration

echo "🔧 Fixing nginx static file serving..."

# Fix static file permissions
sudo chmod -R 755 /home/ec2-user/bolaquent-app/static/
sudo chown -R nginx:nginx /home/ec2-user/bolaquent-app/static/ || sudo chown -R www-data:www-data /home/ec2-user/bolaquent-app/static/

# Create minimal nginx config fix
sudo tee /etc/nginx/conf.d/static-fix.conf > /dev/null << 'STATICFIX'
server {
    listen 80;
    server_name _;

    # Main proxy
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
        proxy_http_version 1.1;
    }
    
    # Static files fix
    location /static/ {
        alias /home/ec2-user/bolaquent-app/static/;
        expires 1h;
        add_header Cache-Control "public";
        try_files $uri $uri/ =404;
    }
}
STATICFIX

# Remove conflicting configs
sudo rm -f /etc/nginx/conf.d/bolaquent-final.conf 2>/dev/null || true
sudo rm -f /etc/nginx/sites-enabled/default 2>/dev/null || true
sudo rm -f /etc/nginx/sites-available/default 2>/dev/null || true

# Test and reload nginx
if sudo nginx -t; then
    echo "✅ Nginx config valid"
    sudo systemctl reload nginx
    echo "✅ Nginx reloaded"
else
    echo "❌ Nginx config failed"
    exit 1
fi

# Test static file access
sleep 2
if curl -f http://localhost/static/css/themes.css > /dev/null 2>&1; then
    echo "✅ Static files accessible"
else
    echo "⚠️ Static files still not accessible"
fi