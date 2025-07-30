#!/bin/bash

# Manual AWS deployment for Bolaquent
# Uses existing simple package and AWS credentials

set -e

echo "🚀 Starting manual AWS deployment for Bolaquent..."

# Configuration
INSTANCE_ID="i-0332d1b2863b08d95"
BUCKET_NAME="bolaquent-deployments"
REGION="us-east-1"
PACKAGE_FILE="bolaquent-simple.zip"

# Check if package exists
if [ ! -f "$PACKAGE_FILE" ]; then
    echo "❌ Package file $PACKAGE_FILE not found"
    exit 1
fi

echo "✅ Found deployment package: $PACKAGE_FILE"

# Upload to S3 with timestamp
DEPLOY_FILE="bolaquent-manual-$(date +%Y%m%d-%H%M%S).zip"
echo "☁️ Uploading to S3 as $DEPLOY_FILE..."
aws s3 cp $PACKAGE_FILE s3://$BUCKET_NAME/$DEPLOY_FILE --region $REGION

echo "✅ Package uploaded to S3"

# Since SSM is not available, we need to use alternative approach
# Check if SSH access is available
echo "🔍 Attempting SSH connection test..."
if timeout 10 ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no ec2-user@54.89.117.172 'echo "SSH connection successful"' 2>/dev/null; then
    echo "✅ SSH connection successful"
    
    echo "🚀 Deploying via SSH..."
    ssh -o StrictHostKeyChecking=no ec2-user@54.89.117.172 << EOF
        echo "🛑 Stopping existing applications..."
        pkill -f "python.*app.py" || true
        sleep 3
        
        echo "📁 Setting up deployment directory..."
        rm -rf bolaquent-app
        mkdir -p bolaquent-app
        cd bolaquent-app
        
        echo "⬇️ Downloading from S3..."
        aws s3 cp s3://$BUCKET_NAME/$DEPLOY_FILE ./bolaquent-deploy.zip --region $REGION
        
        echo "📂 Extracting application..."
        unzip -o bolaquent-deploy.zip
        
        echo "🐍 Installing dependencies..."
        python3 -m pip install --user -r requirements.txt
        
        echo "🚀 Starting application..."
        nohup python3 app.py > app.log 2>&1 &
        echo \$! > app.pid
        
        echo "⏳ Waiting for startup..."
        sleep 10
        
        echo "🔍 Testing application..."
        curl -f http://localhost:5000/ && echo "✅ App running on port 5000" || echo "⚠️ Port 5000 not responding"
        curl -f http://localhost:5010/ && echo "✅ App running on port 5010" || echo "⚠️ Port 5010 not responding"
        curl -f http://localhost:5020/ && echo "✅ App running on port 5020" || echo "⚠️ Port 5020 not responding"
        
        echo "📊 Deployment completed!"
EOF
    
    echo ""
    echo "🌐 Testing external accessibility..."
    sleep 5
    
    if curl -I http://54.89.117.172/ 2>/dev/null | head -1 | grep -q "200\|302"; then
        echo "✅ AWS site accessible at http://54.89.117.172/"
    elif curl -I http://54.89.117.172:5000/ 2>/dev/null | head -1 | grep -q "200\|302"; then
        echo "✅ AWS site accessible at http://54.89.117.172:5000/"
    else
        echo "❌ AWS site not externally accessible"
        echo "🔍 Checking SSH connection for logs..."
        ssh -o StrictHostKeyChecking=no ec2-user@54.89.117.172 'cd bolaquent-app && tail -20 app.log'
    fi
    
else
    echo "❌ SSH connection failed"
    echo "🔍 Instance may not be properly configured for SSH access"
    echo "💡 You may need to:"
    echo "   1. Check security groups allow SSH (port 22)"
    echo "   2. Verify SSH key is correct"
    echo "   3. Ensure instance is running and accessible"
    
    # Alternative: Try to check if instance is running
    echo ""
    echo "📊 Checking instance status..."
    aws ec2 describe-instances --instance-ids $INSTANCE_ID --region $REGION --query 'Reservations[0].Instances[0].State.Name' --output text
fi

echo ""
echo "🎉 Manual deployment process completed!"
echo "📋 Summary:"
echo "   S3 Package: s3://$BUCKET_NAME/$DEPLOY_FILE"
echo "   Instance: $INSTANCE_ID"
echo "   Test URLs:"
echo "     http://54.89.117.172/"
echo "     http://54.89.117.172:5000/"