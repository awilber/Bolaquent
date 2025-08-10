#!/bin/bash
# AWS Deployment Script for Bolaquent Flask Application
# Ensures proper external access configuration for mobile devices

set -e  # Exit on any error

echo "🚀 Starting Bolaquent AWS deployment..."
echo "📱 Configuring for mobile device access from iPhone..."

# Configuration
AWS_IP="54.89.117.172"
AWS_USER="ec2-user"
SSH_KEY="summerquest-key.pem"
APP_DIR="/home/ec2-user/bolaquent"
SERVICE_NAME="bolaquent"
PORT=5000

echo "📋 Deployment Configuration:"
echo "   AWS Instance: $AWS_IP"
echo "   Application Port: $PORT"
echo "   Service Name: $SERVICE_NAME"
echo "   Target Directory: $APP_DIR"

# Check if SSH key exists
if [ ! -f ~/.ssh/$SSH_KEY ]; then
    echo "❌ SSH key not found: ~/.ssh/$SSH_KEY"
    echo "📝 Please ensure your AWS SSH key is available"
    exit 1
fi

echo "🔑 SSH key found: ~/.ssh/$SSH_KEY"

# Test SSH connectivity
echo "🔗 Testing SSH connection to AWS instance..."
if ! ssh -i ~/.ssh/$SSH_KEY -o ConnectTimeout=10 -o StrictHostKeyChecking=no $AWS_USER@$AWS_IP "echo 'SSH connection successful'" > /dev/null 2>&1; then
    echo "❌ SSH connection failed to $AWS_IP"
    echo "💡 Possible solutions:"
    echo "   - Check AWS instance is running"
    echo "   - Verify security group allows SSH (port 22)"
    echo "   - Confirm SSH key permissions: chmod 400 ~/.ssh/$SSH_KEY"
    exit 1
fi

echo "✅ SSH connection established successfully"

# Create deployment package
echo "📦 Creating deployment package..."
DEPLOY_DIR="/tmp/bolaquent-deploy-$(date +%Y%m%d-%H%M%S)"
mkdir -p $DEPLOY_DIR

# Copy application files (exclude .git, __pycache__, etc.)
rsync -av --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' --exclude='.DS_Store' --exclude='venv' --exclude='env' . $DEPLOY_DIR/

echo "✅ Deployment package created: $DEPLOY_DIR"

# Upload application files
echo "📤 Uploading application to AWS instance..."
ssh -i ~/.ssh/$SSH_KEY $AWS_USER@$AWS_IP "mkdir -p $APP_DIR"
rsync -avz -e "ssh -i ~/.ssh/$SSH_KEY -o StrictHostKeyChecking=no" $DEPLOY_DIR/ $AWS_USER@$AWS_IP:$APP_DIR/

echo "✅ Application files uploaded successfully"

# Install dependencies and configure service
echo "⚙️ Installing dependencies and configuring service on AWS..."
ssh -i ~/.ssh/$SSH_KEY $AWS_USER@$AWS_IP << 'REMOTE_COMMANDS'
    # Navigate to application directory
    cd /home/ec2-user/bolaquent
    
    # Install Python 3 and pip if needed
    sudo yum update -y
    sudo yum install -y python3 python3-pip
    
    # Create virtual environment
    python3 -m venv venv
    source venv/bin/activate
    
    # Install application dependencies
    pip install --upgrade pip
    pip install flask flask-cors flask-sqlalchemy python-dotenv
    
    # Make sure app.py is executable
    chmod +x app.py
    
    echo "✅ Dependencies installed successfully"
REMOTE_COMMANDS

# Create systemd service for automatic startup
echo "🔧 Creating systemd service for automatic startup..."
ssh -i ~/.ssh/$SSH_KEY $AWS_USER@$AWS_IP << REMOTE_SERVICE
    # Create systemd service file
    sudo tee /etc/systemd/system/${SERVICE_NAME}.service > /dev/null << 'SERVICE_FILE'
[Unit]
Description=Bolaquent Flask Application
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=${APP_DIR}
Environment=FLASK_ENV=production
Environment=PORT=${PORT}
ExecStart=${APP_DIR}/venv/bin/python ${APP_DIR}/app.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SERVICE_FILE

    # Reload systemd and enable service
    sudo systemctl daemon-reload
    sudo systemctl enable ${SERVICE_NAME}
    
    echo "✅ Systemd service created and enabled"
REMOTE_SERVICE

# Configure security group and firewall
echo "🔒 Configuring security and firewall..."
ssh -i ~/.ssh/$SSH_KEY $AWS_USER@$AWS_IP << 'SECURITY_COMMANDS'
    # Configure firewall to allow port 5000
    if command -v firewall-cmd >/dev/null 2>&1; then
        sudo firewall-cmd --permanent --add-port=5000/tcp
        sudo firewall-cmd --reload
        echo "✅ Firewall configured for port 5000"
    else
        echo "ℹ️ No firewall service found, assuming security group handles access"
    fi
SECURITY_COMMANDS

# Stop any existing service and start the new one
echo "🔄 Starting Bolaquent service..."
ssh -i ~/.ssh/$SSH_KEY $AWS_USER@$AWS_IP << REMOTE_START
    # Stop any existing Python processes on port 5000
    sudo pkill -f "python.*app.py" || true
    sudo fuser -k ${PORT}/tcp || true
    
    # Start the service
    sudo systemctl stop ${SERVICE_NAME} || true
    sudo systemctl start ${SERVICE_NAME}
    
    # Check service status
    sudo systemctl status ${SERVICE_NAME} --no-pager
    
    echo "✅ Service started successfully"
REMOTE_START

# Wait a moment for service to fully start
echo "⏳ Waiting for service to fully initialize..."
sleep 5

# Verify service is accessible
echo "🧪 Testing service accessibility..."
if curl -m 10 -s http://$AWS_IP:$PORT/ > /dev/null; then
    echo "✅ Service is accessible at http://$AWS_IP:$PORT/"
    echo "📱 Your iPhone should now be able to access the app!"
else
    echo "⚠️ Service may still be starting up. Checking logs..."
    ssh -i ~/.ssh/$SSH_KEY $AWS_USER@$AWS_IP "sudo journalctl -u $SERVICE_NAME --no-pager -l -n 20"
fi

# Display final instructions
echo ""
echo "🎉 Deployment Complete!"
echo ""
echo "📱 iPhone Access:"
echo "   URL: http://$AWS_IP:$PORT/"
echo "   Test in Safari on your iPhone"
echo ""
echo "🔧 Management Commands:"
echo "   Status:  ssh -i ~/.ssh/$SSH_KEY $AWS_USER@$AWS_IP 'sudo systemctl status $SERVICE_NAME'"
echo "   Logs:    ssh -i ~/.ssh/$SSH_KEY $AWS_USER@$AWS_IP 'sudo journalctl -u $SERVICE_NAME -f'"
echo "   Restart: ssh -i ~/.ssh/$SSH_KEY $AWS_USER@$AWS_IP 'sudo systemctl restart $SERVICE_NAME'"
echo ""
echo "🔍 If iPhone still shows 'disallowed host', check:"
echo "   1. AWS Security Group allows port $PORT from 0.0.0.0/0"
echo "   2. Service logs for any binding errors"
echo "   3. Try restarting the service"

# Cleanup temporary files
rm -rf $DEPLOY_DIR
echo "🧹 Cleanup completed"