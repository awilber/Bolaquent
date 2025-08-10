#!/bin/bash

# Fix AWS nginx configuration and ensure proper deployment
# This script will be executed via GitHub Actions deployment

echo "🔧 Fixing AWS nginx configuration and deployment..."

# Configure nginx to proxy to correct port
echo "📝 Updating nginx configuration..."
sudo tee /etc/nginx/sites-available/default > /dev/null << 'EOL'
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    
    server_name _;
    
    # Security headers
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
        proxy_request_buffering off;
        proxy_http_version 1.1;
        proxy_connect_timeout 5s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Static files served directly by nginx for performance
    location /static/ {
        alias /home/ec2-user/bolaquent-app/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOL

# Test nginx configuration
echo "🧪 Testing nginx configuration..."
sudo nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Nginx configuration is valid"
    
    # Reload nginx
    echo "🔄 Reloading nginx..."
    sudo systemctl reload nginx
    
    # Ensure nginx is running
    sudo systemctl enable nginx
    sudo systemctl start nginx
    
    echo "✅ Nginx has been updated and reloaded"
else
    echo "❌ Nginx configuration test failed"
    exit 1
fi

# Test the proxy configuration
echo "🔍 Testing proxy connection..."
sleep 2
curl -I http://localhost/ 2>&1 | head -5

if curl -f http://localhost/ > /dev/null 2>&1; then
    echo "✅ Nginx proxy is working correctly"
else
    echo "⚠️ Nginx proxy may need Flask app to be running"
fi

echo "🎉 AWS nginx configuration fix completed!"