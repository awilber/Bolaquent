#!/bin/bash

echo "🔧 Starting Flask on alternative port and updating nginx"

ssh -i bolaquent-key.pem -o StrictHostKeyChecking=no ec2-user@54.161.222.239 << 'ALTPORTEOF'
#!/bin/bash
set -e

cd /home/ec2-user/bolaquent-app

echo "🔍 Checking what's using port 5000..."
netstat -tlnp | grep :5000 || echo "No process found using netstat"
ps aux | grep -E "(python|Flask|app)" | grep -v grep || echo "No Python processes found"

echo "🚀 Starting Flask on port 5010 instead..."
source venv/bin/activate

# Set environment variables for alternative port
export FLASK_ENV=production
export PORT=5010
export FLASK_HOST=0.0.0.0

# Kill any existing processes first
pkill -f "python.*app.py" || true
sleep 3

# Start Flask on port 5010
nohup python app.py > app.log 2>&1 &
APP_PID=$!
echo $APP_PID > app.pid

echo "📝 Started Flask app with PID: $APP_PID on port 5010"

# Wait and verify
sleep 10

if ps -p $APP_PID > /dev/null; then
    echo "✅ Flask process $APP_PID is running"
    
    # Test the application on port 5010
    if curl -f http://localhost:5010/ > /dev/null 2>&1; then
        echo "✅ Flask responding on port 5010"
        
        # Test for embedded hero styles
        if curl -s http://localhost:5010/ | grep -q "hero-learning"; then
            echo "🎉 Embedded hero styles detected on port 5010!"
        else
            echo "⚠️ Hero styles not detected in response"
        fi
    else
        echo "❌ Flask not responding on port 5010"
        cat app.log
        exit 1
    fi
else
    echo "❌ Flask process died - checking logs:"
    cat app.log
    exit 1
fi

echo "🔧 Updating nginx to proxy to port 5010..."

# Update nginx configuration to point to 5010
sudo tee /etc/nginx/sites-available/default > /dev/null << 'NGINXUPDATE'
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:5010;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
        proxy_http_version 1.1;
        proxy_connect_timeout 10s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    location /static/ {
        alias /home/ec2-user/bolaquent-app/static/;
        expires 1h;
        add_header Cache-Control "public, immutable";
        try_files $uri $uri/ =404;
    }
}
NGINXUPDATE

echo "✅ Nginx configuration updated"

# Test and reload nginx
if sudo nginx -t; then
    echo "✅ Nginx config valid"
    sudo systemctl reload nginx
    echo "✅ Nginx reloaded"
else
    echo "❌ Nginx config failed"
    exit 1
fi

# Wait for nginx reload
sleep 5

echo "🌐 Testing external access..."
if curl -f http://localhost/ > /dev/null 2>&1; then
    echo "✅ Nginx proxy working"
    if curl -s http://localhost/ | grep -q "hero-learning"; then
        echo "🎉 SUCCESS: Embedded hero styles accessible via nginx!"
    else
        echo "⚠️ Hero styles not detected through nginx"
    fi
else
    echo "❌ Nginx proxy not working"
fi

echo "🌐 Application should now be accessible at http://54.161.222.239/"
echo "Flask running on internal port 5010, nginx proxying port 80 -> 5010"
ALTPORTEOF