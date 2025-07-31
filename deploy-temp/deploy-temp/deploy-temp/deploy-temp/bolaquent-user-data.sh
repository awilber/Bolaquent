#!/bin/bash
# EC2 User Data script for Bolaquent deployment

# Update system
yum update -y

# Install Python 3 and pip
yum install python3 python3-pip git -y

# Install nginx for reverse proxy
amazon-linux-extras install nginx1 -y

# Create app directory
mkdir -p /opt/bolaquent
cd /opt/bolaquent

# Create a basic Flask app structure (will be replaced by real app)
cat > app.py << 'FLASKEOF'
from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return '<h1>Bolaquent is starting up...</h1><p>Deployment in progress</p>'

@app.route('/health')
def health():
    return {'status': 'ok'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
FLASKEOF

# Create requirements.txt
cat > requirements.txt << 'REQEOF'
Flask>=2.3.0
Werkzeug>=2.3.0
REQEOF

# Install Python dependencies
pip3 install -r requirements.txt

# Create systemd service
cat > /etc/systemd/system/bolaquent.service << 'SERVICEEOF'
[Unit]
Description=Bolaquent Flask Application
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/opt/bolaquent
ExecStart=/usr/bin/python3 app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICEEOF

# Set proper ownership
chown -R ec2-user:ec2-user /opt/bolaquent

# Configure nginx
cat > /etc/nginx/conf.d/bolaquent.conf << 'NGINXEOF'
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /health {
        proxy_pass http://127.0.0.1:5000/health;
    }
}
NGINXEOF

# Start services
systemctl enable bolaquent
systemctl start bolaquent
systemctl enable nginx
systemctl start nginx

# Wait a moment and check status
sleep 5
systemctl status bolaquent --no-pager
systemctl status nginx --no-pager

echo "Bolaquent deployment complete!"
