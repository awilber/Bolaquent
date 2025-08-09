#!/bin/bash
set -e

echo "🚨 EMERGENCY NGINX FIX - Make http://54.161.222.239/ work"

# Remove conflicting configs
sudo rm -f /etc/nginx/sites-enabled/* /etc/nginx/conf.d/*.conf

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
    
    location /static/ {
        alias /home/ec2-user/bolaquent-app/static/;
    }
}
CONFIG

# Test and restart nginx
sudo nginx -t && sudo systemctl restart nginx

# Test Flask is running
if ! pgrep -f "python.*app.py" > /dev/null; then
    cd /home/ec2-user/bolaquent-app
    source venv/bin/activate || true
    nohup ./venv/bin/python app.py > /tmp/flask.log 2>&1 &
    sleep 10
fi

# Test everything works
if curl -f http://localhost:5000/ && curl -f http://localhost/; then
    echo "✅ SUCCESS: http://54.161.222.239/ is now working!"
else
    echo "❌ Tests failed"
    exit 1
fi