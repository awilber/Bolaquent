#!/bin/bash

echo "🔧 DIRECT NGINX FIX: Simple proxy configuration for port 80"

ssh -i ~/.ssh/summerquest-key.pem ec2-user@54.161.222.239 << 'EOF'
set -e

echo "🔧 Configuring nginx to proxy port 80 → 5000"

# Remove conflicting configs
sudo rm -f /etc/nginx/sites-enabled/default
sudo rm -f /etc/nginx/conf.d/default.conf
sudo rm -f /etc/nginx/conf.d/*.conf

# Create simple proxy config
sudo tee /etc/nginx/conf.d/proxy.conf > /dev/null << 'CONFIG'
server {
    listen 80 default_server;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_buffering off;
        proxy_http_version 1.1;
    }
}
CONFIG

echo "🧪 Testing nginx configuration..."
sudo nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Configuration valid - restarting nginx..."
    sudo systemctl restart nginx
    sleep 3
    
    # Test the proxy
    if curl -f -s http://localhost/ > /dev/null; then
        echo "✅ SUCCESS: nginx proxy working"
        echo "🌐 http://54.161.222.239/ should now work!"
    else
        echo "❌ Proxy test failed"
        curl -I http://localhost/
    fi
else
    echo "❌ Nginx configuration invalid"
fi

echo "📊 Current status:"
echo "Flask on 5000: $(curl -s -o /dev/null -w '%{http_code}' http://localhost:5000/)"
echo "Nginx on 80: $(curl -s -o /dev/null -w '%{http_code}' http://localhost/)"

EOF

echo ""
echo "🎉 NGINX FIX COMPLETE!"
echo "🌐 Test: http://54.161.222.239/"