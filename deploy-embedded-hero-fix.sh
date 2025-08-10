#!/bin/bash
set -e

echo "🚀 DEPLOYING CURRENT VERSION WITH EMBEDDED HERO BACKGROUNDS"
echo "This script will deploy the local version with embedded hero styles to AWS"

# Verify we have the embedded styles in our template
if grep -q "body.hero-page.hero-learning" templates/base.html; then
    echo "✅ Embedded hero styles detected in base.html"
else
    echo "❌ Embedded hero styles not found! Cannot deploy."
    exit 1
fi

# Create deployment package with current files
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
DEPLOY_FILE="bolaquent-embedded-hero-${TIMESTAMP}.zip"

echo "📦 Creating deployment package: $DEPLOY_FILE"

# Create clean deployment package
zip -r "$DEPLOY_FILE" . \
    -x ".git/*" \
    -x "__pycache__/*" \
    -x "*.pyc" \
    -x "venv/*" \
    -x "*.pid" \
    -x "*.log" \
    -x "*deploy*.sh" \
    -x "emergency-deploy.zip" \
    -x "*.zip" \
    -x "htmlcov/*" \
    -x ".pytest_cache/*"

echo "✅ Package created: $(du -h $DEPLOY_FILE | cut -f1)"

# Upload to S3
echo "📤 Uploading to S3..."
aws s3 cp "$DEPLOY_FILE" "s3://bolaquent-deployments/$DEPLOY_FILE" || {
    echo "❌ S3 upload failed. Trying alternative approach..."
    # Create local deployment script for manual execution
    echo "Creating manual deployment script instead..."
    
cat > deploy-manual.sh << MANUALEOF
#!/bin/bash
echo "🚀 Manual deployment of embedded hero version"
echo "Run this script on the AWS server:"
echo ""
echo "# 1. Stop existing processes"
echo "sudo pkill -f python.*app.py || true"
echo "sudo lsof -ti:5000 | xargs -r sudo kill -9 || true"
echo ""
echo "# 2. Backup and clean"
echo "sudo mv /home/ec2-user/bolaquent-app /home/ec2-user/bolaquent-app-backup-\$(date +%s) || true"
echo "mkdir -p /home/ec2-user/bolaquent-app"
echo ""
echo "# 3. Upload this package to the server:"
echo "scp $DEPLOY_FILE ec2-user@54.161.222.239:/home/ec2-user/"
echo ""
echo "# 4. Then run on server:"
echo "cd /home/ec2-user/bolaquent-app"
echo "unzip -o ../$DEPLOY_FILE"
echo "python3 -m venv venv"
echo "source venv/bin/activate"
echo "pip install -r requirements-prod.txt"
echo "export FLASK_ENV=production"
echo "export PORT=5000"
echo "nohup python app.py > app.log 2>&1 &"
echo "echo \$! > app.pid"
MANUALEOF

    chmod +x deploy-manual.sh
    echo "✅ Created deploy-manual.sh with instructions"
    echo "❌ S3 failed, but you can deploy manually using deploy-manual.sh"
    exit 1
}

echo "✅ S3 upload successful"

# Deploy to AWS
echo "🚀 Deploying to AWS server..."

cat > /tmp/aws-deploy.sh << AWSEOF
#!/bin/bash
set -e

echo "🔄 Starting deployment with embedded hero backgrounds..."

# Stop existing Flask applications
echo "🛑 Stopping existing applications..."
sudo pkill -f "python.*app.py" || true
sudo pkill -f "Flask" || true
sudo lsof -ti:5000 | xargs -r sudo kill -9 || true
sudo lsof -ti:5001 | xargs -r sudo kill -9 || true
sleep 5

# Backup existing installation
echo "💾 Backing up existing installation..."
if [ -d "/home/ec2-user/bolaquent-app" ]; then
    sudo mv /home/ec2-user/bolaquent-app /home/ec2-user/bolaquent-app-backup-\$(date +%s)
fi

# Create fresh directory
echo "📁 Creating fresh deployment directory..."
mkdir -p /home/ec2-user/bolaquent-app
cd /home/ec2-user/bolaquent-app

# Download and extract
echo "📥 Downloading deployment package..."
aws configure set region us-east-1
aws s3 cp "s3://bolaquent-deployments/$DEPLOY_FILE" ./app.zip
unzip -o app.zip

# Verify embedded hero styles are present
echo "🔍 Verifying embedded hero styles..."
if grep -q "body.hero-page.hero-learning" templates/base.html; then
    echo "✅ Embedded hero styles confirmed in deployed version"
else
    echo "❌ Embedded hero styles missing! Deployment failed."
    exit 1
fi

# Setup Python environment
echo "🐍 Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-prod.txt

# Start application
echo "🚀 Starting Flask application..."
export FLASK_ENV=production
export PORT=5000
export FLASK_HOST=0.0.0.0
nohup python app.py > app.log 2>&1 &
APP_PID=\$!
echo \$APP_PID > app.pid
echo "📝 Started Flask app with PID: \$APP_PID"

# Wait and verify
sleep 10
if ps -p \$APP_PID > /dev/null; then
    echo "✅ Flask process \$APP_PID is running"
    curl -s http://localhost:5000/ | grep -q "hero-learning" && echo "✅ Embedded hero styles working!" || echo "⚠️ Hero styles verification failed"
else
    echo "❌ Flask process died - checking logs:"
    cat app.log
    exit 1
fi

echo "🎉 Deployment with embedded hero backgrounds complete!"
AWSEOF

# Execute deployment on AWS
ssh -i bolaquent-key.pem -o StrictHostKeyChecking=no ec2-user@54.161.222.239 "bash -s" < /tmp/aws-deploy.sh || {
    echo "❌ SSH deployment failed"
    echo "📋 Manual deployment package ready: $DEPLOY_FILE"
    echo "You can upload this package manually to the server"
    exit 1
}

echo "✅ Deployment complete!"
echo "🌐 Testing AWS site..."

# Wait for deployment to settle
sleep 15

# Test the deployment
if curl -s http://54.161.222.239/ | grep -q "hero-learning"; then
    echo "🎉 SUCCESS! Embedded hero backgrounds are now live on AWS!"
    echo "🔗 URL: http://54.161.222.239/"
else
    echo "⚠️ Deployment completed but hero styles verification failed"
    echo "Manual verification may be needed"
fi