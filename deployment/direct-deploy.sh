#!/bin/bash

# Direct deployment script for Bolaquent - similar to CustomerSuccess pattern
# This deploys directly to the existing EC2 instance using SSM

set -e

echo "🚀 Starting direct deployment to AWS EC2..."

# Configuration
INSTANCE_ID="i-0332d1b2863b08d95"
BUCKET_NAME="bolaquent-deployments"
REGION="us-east-1"
APP_NAME="bolaquent"

# Check AWS CLI configuration
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo "❌ AWS CLI not configured. Please run 'aws configure' first."
    exit 1
fi

echo "✅ AWS CLI configured"

# Create deployment package locally
echo "📦 Creating deployment package..."
mkdir -p deploy-temp
cp -r . deploy-temp/
cd deploy-temp

# Clean up unnecessary files
rm -rf .git .github __pycache__ *.pyc venv htmlcov deploy-temp backup cookies.txt
rm -f *.pid *.log CLAUDE.md.bak-*

# Skip local pip install - will install on server

# Create zip
zip -r ../bolaquent-deploy-$(date +%Y%m%d-%H%M%S).zip .
cd ..
rm -rf deploy-temp

DEPLOY_FILE="bolaquent-deploy-$(date +%Y%m%d-%H%M%S).zip"

echo "✅ Deployment package created: $DEPLOY_FILE"

# Upload to S3 for backup
echo "☁️ Uploading to S3..."
aws s3 cp $DEPLOY_FILE s3://$BUCKET_NAME/ --region $REGION

# Deploy to EC2 using SSM
echo "🖥️ Deploying to EC2 instance $INSTANCE_ID..."
COMMAND_ID=$(aws ssm send-command \
    --instance-ids $INSTANCE_ID \
    --document-name "AWS-RunShellScript" \
    --parameters "commands=[
        'echo \"🛑 Stopping existing application...\"',
        'pkill -f \"python.*app.py\" || true',
        'sleep 3',
        'echo \"📁 Setting up deployment directory...\"',
        'cd /home/ec2-user',
        'rm -rf bolaquent-app',
        'mkdir -p bolaquent-app',
        'cd bolaquent-app',
        'echo \"⬇️ Downloading deployment package...\"',
        'aws s3 cp s3://$BUCKET_NAME/$DEPLOY_FILE . --region $REGION',
        'echo \"📂 Extracting application...\"',
        'unzip -o $DEPLOY_FILE',
        'echo \"🐍 Installing Python dependencies...\"',
        'python3 -m pip install --user -r requirements.txt',
        'echo \"🚀 Starting application...\"',
        'nohup python3 app.py > app.log 2>&1 &',
        'echo \$! > app.pid',
        'sleep 10',
        'echo \"🔍 Testing application...\"',
        'curl -f http://localhost:5000/ && echo \"✅ App running on port 5000\" || echo \"⚠️ Port 5000 not responding\"',
        'curl -f http://localhost:5010/ && echo \"✅ App running on port 5010\" || echo \"⚠️ Port 5010 not responding\"',
        'curl -f http://localhost:5020/ && echo \"✅ App running on port 5020\" || echo \"⚠️ Port 5020 not responding\"',
        'echo \"📊 Deployment completed!\"'
    ]" \
    --region $REGION \
    --query 'Command.CommandId' --output text)

echo "⏳ Waiting for deployment to complete..."
echo "📊 Command ID: $COMMAND_ID"

# Wait for command to complete
aws ssm wait command-executed \
    --command-id $COMMAND_ID \
    --instance-id $INSTANCE_ID \
    --region $REGION

# Get command results
echo "📋 Deployment results:"
aws ssm get-command-invocation \
    --command-id $COMMAND_ID \
    --instance-id $INSTANCE_ID \
    --region $REGION \
    --query 'StandardOutputContent' --output text

# Test the deployment
echo ""
echo "🌐 Testing AWS site accessibility..."
sleep 15

if curl -I http://54.89.117.172/ 2>/dev/null | head -1 | grep -q "200\|302"; then
    echo "✅ AWS site is accessible at http://54.89.117.172/"
elif curl -I http://54.89.117.172:5000/ 2>/dev/null | head -1 | grep -q "200\|302"; then
    echo "✅ AWS site is accessible at http://54.89.117.172:5000/"
else
    echo "❌ AWS site not accessible - checking logs..."
    aws ssm get-command-invocation \
        --command-id $COMMAND_ID \
        --instance-id $INSTANCE_ID \
        --region $REGION \
        --query 'StandardErrorContent' --output text
fi

# Clean up local deployment file
rm $DEPLOY_FILE

echo ""
echo "🎉 Deployment process completed!"
echo "🌐 Check: http://54.89.117.172/"
echo "🌐 Alt: http://54.89.117.172:5000/"