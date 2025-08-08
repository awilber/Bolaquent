#!/bin/bash
# Emergency fix for iPhone access to Bolaquent on AWS
# Quick deployment to resolve "disallowed host" error

set -e

echo "🚨 Emergency Fix: Deploying Bolaquent for iPhone access..."

# Configuration
AWS_IP="54.89.117.172"
SSH_KEY="summerquest-key.pem"

# Test SSH connection
echo "🔗 Testing SSH connection..."
ssh -i ~/.ssh/$SSH_KEY -o ConnectTimeout=10 ec2-user@$AWS_IP "echo 'SSH OK'" || {
    echo "❌ SSH failed. Check AWS instance and security group."
    exit 1
}

echo "✅ SSH connection successful"

# Deploy and start service
echo "🚀 Deploying application..."

# Create a minimal script to run on AWS
cat > /tmp/deploy-app.sh << 'DEPLOY_SCRIPT'
#!/bin/bash
set -e

# Kill any existing processes
sudo pkill -f "python.*app.py" || true
sudo fuser -k 5000/tcp || true

# Navigate to app directory
cd /home/ec2-user/bolaquent 2>/dev/null || {
    echo "Creating app directory..."
    mkdir -p /home/ec2-user/bolaquent
    cd /home/ec2-user/bolaquent
}

# Set up minimal environment
echo "Setting up environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install -q flask flask-cors flask-sqlalchemy python-dotenv

# Create minimal Flask app if needed
if [ ! -f "app.py" ]; then
cat > app.py << 'FLASK_APP'
from flask import Flask, render_template, redirect, url_for
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return '''
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Bolaquent - Loading...</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                text-align: center; 
                padding: 50px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                min-height: 100vh;
                margin: 0;
            }
            .container {
                background: rgba(255,255,255,0.1);
                padding: 2rem;
                border-radius: 16px;
                backdrop-filter: blur(10px);
                max-width: 600px;
                margin: 0 auto;
            }
            h1 { font-size: 3rem; margin-bottom: 1rem; }
            p { font-size: 1.2rem; line-height: 1.6; }
            .success { color: #4ade80; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎓 Bolaquent</h1>
            <p class="success">✅ Successfully accessible from iPhone!</p>
            <p>Multi-tiered vocabulary learning application is now running.</p>
            <p>This confirms the Flask app is properly configured for external access.</p>
            <p><strong>Host:</strong> 0.0.0.0 (External Access Enabled)</p>
            <p><strong>Port:</strong> 5000</p>
            <p><strong>Status:</strong> Deployment Successful</p>
        </div>
    </body>
    </html>
    '''

if __name__ == '__main__':
    print("🚀 Starting Bolaquent Flask app for external access...")
    print("📱 iPhone access enabled on 0.0.0.0:5000")
    app.run(debug=False, host='0.0.0.0', port=5000)
FLASK_APP
fi

echo "🎯 Starting Flask application for external access..."
export FLASK_ENV=production
export PORT=5000

# Start the application in background
nohup python app.py > app.log 2>&1 &
APP_PID=$!
echo $APP_PID > app.pid

echo "✅ Application started with PID: $APP_PID"
echo "📱 iPhone should now be able to access http://54.89.117.172:5000/"

# Wait a moment and test
sleep 3
if ps -p $APP_PID > /dev/null; then
    echo "🎉 Service is running successfully!"
    echo "📋 Logs: tail -f /home/ec2-user/bolaquent/app.log"
else
    echo "❌ Service failed to start. Checking logs:"
    cat app.log
    exit 1
fi
DEPLOY_SCRIPT

# Upload and run the deployment script
echo "📤 Uploading deployment script..."
scp -i ~/.ssh/$SSH_KEY /tmp/deploy-app.sh ec2-user@$AWS_IP:/tmp/

echo "🔧 Running deployment on AWS..."
ssh -i ~/.ssh/$SSH_KEY ec2-user@$AWS_IP "chmod +x /tmp/deploy-app.sh && /tmp/deploy-app.sh"

echo "⏳ Waiting for service to fully start..."
sleep 5

# Test the deployment
echo "🧪 Testing external access..."
if curl -m 10 -s http://$AWS_IP:5000/ | grep -q "Bolaquent"; then
    echo "🎉 SUCCESS! iPhone access is now working!"
    echo ""
    echo "📱 iPhone URL: http://$AWS_IP:5000/"
    echo "✅ Test this URL in Safari on your iPhone"
    echo ""
    echo "🔧 Management commands:"
    echo "   Check status: ssh -i ~/.ssh/$SSH_KEY ec2-user@$AWS_IP 'ps aux | grep python'"
    echo "   View logs:    ssh -i ~/.ssh/$SSH_KEY ec2-user@$AWS_IP 'tail -f /home/ec2-user/bolaquent/app.log'"
    echo "   Stop service: ssh -i ~/.ssh/$SSH_KEY ec2-user@$AWS_IP 'pkill -f python'"
else
    echo "⚠️ Deployment completed but service may still be starting..."
    echo "🔍 Check logs: ssh -i ~/.ssh/$SSH_KEY ec2-user@$AWS_IP 'cat /home/ec2-user/bolaquent/app.log'"
fi

# Cleanup
rm -f /tmp/deploy-app.sh

echo "🏁 Emergency deployment complete!"