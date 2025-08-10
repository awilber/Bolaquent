#!/bin/bash
set -e

echo "🚨 EMERGENCY AWS DEPLOYMENT - Fix nginx proxy to port 80"

# Create deployment package
zip -r emergency-deploy.zip . -x ".git/*" "__pycache__/*" "*.pyc" "venv/*" "emergency-deploy-bolaquent.sh"

# Upload to S3
DEPLOY_FILE="emergency-$(date +%Y%m%d-%H%M%S).zip"
aws s3 cp emergency-deploy.zip "s3://bolaquent-deployments/$DEPLOY_FILE"

# Create AWS deployment script
cat > /tmp/deploy.sh << 'EOF'
#!/bin/bash
set -e

# Kill all Flask processes
sudo pkill -f "python.*app.py" || true
sudo pkill -f "Flask" || true
sudo lsof -ti:5000 | xargs -r sudo kill -9 || true
sudo lsof -ti:80 | xargs -r sudo kill -9 || true
sleep 5

# Clean deployment area
cd /home/ec2-user
sudo rm -rf bolaquent-*
mkdir bolaquent-new
cd bolaquent-new

# Download and setup
aws s3 cp "s3://bolaquent-deployments/DEPLOY_FILE" ./app.zip
unzip -o app.zip
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-prod.txt

# Fix nginx - comprehensive approach
echo "Fixing nginx configuration..."

# Try sites-available first
if [ -d "/etc/nginx/sites-available" ]; then
    sudo tee /etc/nginx/sites-available/default > /dev/null << 'NGINX'
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
NGINX
    sudo ln -sf /etc/nginx/sites-available/default /etc/nginx/sites-enabled/default
else
    # Use conf.d approach
    sudo tee /etc/nginx/conf.d/app.conf > /dev/null << 'NGINX'
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
NGINX
    sudo rm -f /etc/nginx/conf.d/default.conf || true
fi

# Test and restart nginx
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx

# Start Flask
export PORT=5000
nohup ./venv/bin/python app.py > app.log 2>&1 &
echo $! > app.pid
sleep 10

# Verify everything works
curl -f http://localhost:5000/ && echo "✅ Flask OK"
curl -f http://localhost/ && echo "✅ Nginx OK" || echo "❌ Nginx failed"

echo "🎉 Deployment complete!"
EOF

# Deploy script with file substitution
sed "s/DEPLOY_FILE/$DEPLOY_FILE/g" /tmp/deploy.sh > /tmp/final-deploy.sh

# Execute on AWS
scp /tmp/final-deploy.sh ec2-user@54.161.222.239:~/deploy.sh
ssh ec2-user@54.161.222.239 'chmod +x deploy.sh && ./deploy.sh'

# Cleanup
rm emergency-deploy.zip /tmp/deploy.sh /tmp/final-deploy.sh

echo "🎉 COMPLETE! Test: http://54.161.222.239/"