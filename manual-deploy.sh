#!/bin/bash

echo "🔧 MANUAL DEPLOYMENT: Direct fix for http://54.161.222.239/"

# Create minimal deployment package
echo "📦 Creating minimal package..."
mkdir -p deploy-temp
cp app.py models.py config.py requirements-prod.txt deploy-temp/
cp -r templates static routes deploy-temp/

cd deploy-temp && zip -r ../minimal-deploy.zip . && cd .. && rm -rf deploy-temp

# Upload to S3
DEPLOY_FILE="minimal-$(date +%Y%m%d-%H%M%S).zip"
aws s3 cp minimal-deploy.zip "s3://bolaquent-deployments/$DEPLOY_FILE"

# Deploy to AWS
ssh ec2-user@54.161.222.239 << EOF
set -e

# Kill Flask processes
sudo pkill -f "python.*app.py" || true
sudo lsof -ti:5000 | xargs -r sudo kill -9 || true
sleep 3

# Setup deployment
cd /home/ec2-user
rm -rf bolaquent-minimal && mkdir bolaquent-minimal && cd bolaquent-minimal
aws s3 cp "s3://bolaquent-deployments/$DEPLOY_FILE" ./app.zip && unzip -q app.zip

# Setup Python
python3 -m venv venv && source venv/bin/activate && pip install -q -r requirements-prod.txt

# Configure nginx
sudo rm -f /etc/nginx/sites-enabled/default /etc/nginx/conf.d/*.conf
sudo tee /etc/nginx/conf.d/app.conf > /dev/null << 'CONFIG'
server {
    listen 80 default_server;
    server_name _;
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_buffering off;
        proxy_http_version 1.1;
    }
    location /static/ {
        alias /home/ec2-user/bolaquent-minimal/static/;
    }
}
CONFIG

# Restart nginx
sudo nginx -t && sudo systemctl restart nginx

# Start Flask
export PORT=5000 && nohup ./venv/bin/python app.py > flask.log 2>&1 &
echo \$! > flask.pid && sleep 15

# Test everything
if ps -p \$(cat flask.pid) > /dev/null && curl -f http://localhost:5000/ > /dev/null && curl -f http://localhost/ > /dev/null; then
    echo "✅ SUCCESS: http://54.161.222.239/ is now working!"
else
    echo "❌ FAILED - check logs"
    cat flask.log
fi
EOF

rm minimal-deploy.zip
echo "🎉 DEPLOYMENT COMPLETE! Test: http://54.161.222.239/"