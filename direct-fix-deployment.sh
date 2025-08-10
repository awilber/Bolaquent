#!/bin/bash

echo "🚀 Direct AWS Fix Deployment - Force Update Flask and Nginx"

# Upload current version to S3
echo "📦 Preparing deployment package..."
zip -r direct-deploy.zip . -x ".git/*" "__pycache__/*" "*.pyc" ".DS_Store" "venv/*" "node_modules/*"

echo "☁️ Uploading to S3..."
aws configure set aws_access_key_id $AWS_ACCESS_KEY_ID
aws configure set aws_secret_access_key $AWS_SECRET_ACCESS_KEY
aws configure set default.region us-east-1

DEPLOY_FILE="bolaquent-direct-$(date +%Y%m%d-%H%M%S).zip"
aws s3 cp direct-deploy.zip s3://bolaquent-deployments/$DEPLOY_FILE

echo "🔄 Connecting to AWS and deploying..."

# Create deployment script that will run on AWS
cat > deploy-script.sh << 'EOF'
#!/bin/bash
set -e

echo "🛑 Stopping ALL Flask processes..."
sudo pkill -f "python.*app.py" || true
sudo pkill -f "Flask" || true
lsof -ti:5000 | xargs -r sudo kill -9 || true
lsof -ti:5001 | xargs -r sudo kill -9 || true
sleep 5

echo "🗂️ Cleaning up old deployments..."
cd ~
sudo rm -rf bolaquent-app* bolaquent-*.zip
mkdir -p bolaquent-app
cd bolaquent-app

echo "📥 Downloading latest deployment..."
aws s3 cp s3://bolaquent-deployments/DEPLOY_FILE_PLACEHOLDER ./deploy.zip
unzip -o deploy.zip

echo "🐍 Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-prod.txt

echo "🔧 Fixing nginx configuration..."
# Find correct nginx config location
if [ -f /etc/nginx/sites-available/default ]; then
    NGINX_CONFIG="/etc/nginx/sites-available/default"
elif [ -f /etc/nginx/conf.d/default.conf ]; then
    NGINX_CONFIG="/etc/nginx/conf.d/default.conf"  
else
    NGINX_CONFIG="/etc/nginx/nginx.conf"
    echo "⚠️ Using main nginx.conf - may need manual adjustment"
fi

echo "📝 Writing nginx configuration to: $NGINX_CONFIG"
if [[ "$NGINX_CONFIG" == *"nginx.conf" ]]; then
    # For main nginx.conf, we need to add server block inside http block
    sudo cp $NGINX_CONFIG ${NGINX_CONFIG}.backup
    sudo sed -i '/http {/a\
    server {\
        listen 80 default_server;\
        server_name _;\
        location / {\
            proxy_pass http://127.0.0.1:5000;\
            proxy_set_header Host $host;\
            proxy_set_header X-Real-IP $remote_addr;\
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\
        }\
    }' $NGINX_CONFIG
else
    # For sites-available or conf.d, replace entire file
    sudo tee $NGINX_CONFIG > /dev/null << 'NGINXEOF'
server {
    listen 80 default_server;
    listen [::]:80 default_server;
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
        expires 1y;
    }
}
NGINXEOF
fi

echo "🧪 Testing nginx configuration..."
sudo nginx -t

echo "🔄 Restarting nginx..."
sudo systemctl restart nginx
sudo systemctl enable nginx

echo "🚀 Starting new Flask application..."
export FLASK_ENV=production
export PORT=5000
nohup ./venv/bin/python app.py > app.log 2>&1 &
APP_PID=$!
echo $APP_PID > app.pid
echo "📝 Flask started with PID: $APP_PID"

echo "⏳ Waiting for Flask to start..."
sleep 10

echo "🧪 Testing deployment..."
if ps -p $APP_PID > /dev/null; then
    echo "✅ Flask process is running"
    echo "🔍 Testing endpoints..."
    curl -I http://localhost:5000/ && echo "✅ Flask app responds"
    curl -I http://localhost/ && echo "✅ Nginx proxy works" || echo "⚠️ Nginx needs troubleshooting"
    
    echo "🌙 Checking dark mode deployment..."
    curl -s http://localhost:5000/ | grep -E "(dark-mode|data-theme)" && echo "✅ Dark mode deployed"
else
    echo "❌ Flask failed to start - checking logs:"
    cat app.log
    exit 1
fi

echo "🎉 Deployment completed successfully!"
EOF

# Replace placeholder in script
sed -i.bak "s/DEPLOY_FILE_PLACEHOLDER/$DEPLOY_FILE/g" deploy-script.sh

echo "📤 Uploading deployment script..."
scp -o StrictHostKeyChecking=no deploy-script.sh ec2-user@54.161.222.239:~/deploy-script.sh

echo "🚀 Executing deployment on AWS..."
ssh -o StrictHostKeyChecking=no ec2-user@54.161.222.239 'chmod +x deploy-script.sh && ./deploy-script.sh'

echo "✅ Direct deployment completed!"
echo "🌐 Test URLs:"
echo "  - Main site: http://54.161.222.239/"
echo "  - Flask direct: http://54.161.222.239:5000/"

# Cleanup
rm direct-deploy.zip deploy-script.sh deploy-script.sh.bak