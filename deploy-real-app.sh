#\!/bin/bash
set -e

cd /opt/bolaquent

# Stop current service
sudo systemctl stop bolaquent || true

# Backup current app
sudo cp app.py app.py.backup 2>/dev/null || true

# Download real app from S3 (using existing package)
aws s3 cp s3://bolaquent-deployments/bolaquent-manual-20250729-182821.zip ./bolaquent-app.zip --region us-east-1
unzip -o bolaquent-app.zip

# Install dependencies
sudo pip3 install -r requirements.txt

# Update ownership
sudo chown -R ec2-user:ec2-user /opt/bolaquent

# Start service
sudo systemctl start bolaquent
sudo systemctl enable bolaquent

# Check status
sleep 5
sudo systemctl status bolaquent --no-pager

# Test locally
curl -f http://localhost:5000/ && echo "✅ App is running locally" || echo "⚠️ App not responding locally"

# Test nginx
sudo systemctl status nginx --no-pager
curl -f http://localhost/ && echo "✅ Nginx is working" || echo "⚠️ Nginx not responding"
EOF < /dev/null