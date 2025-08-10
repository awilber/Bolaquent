#!/bin/bash
# Quick deployment script for Bolaquent following TogetherQuest pattern

set -e

echo "🚀 Bolaquent AWS Deployment Script (TogetherQuest Style)"
echo "======================================================="

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Please install it first."
    exit 1
fi

# Check if logged in
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ Not logged into AWS. Please run 'aws configure' first."
    exit 1
fi

# Get AWS account ID and region
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION=$(aws configure get region)
echo "✅ AWS Account: $ACCOUNT_ID"
echo "✅ Region: $REGION"

# Variables
INSTANCE_TYPE="t3.micro"  # Free tier eligible
KEY_NAME="bolaquent-key"
SG_NAME="bolaquent-sg"
INSTANCE_NAME="bolaquent-server"

echo ""
echo "1️⃣ Creating Key Pair..."
if ! aws ec2 describe-key-pairs --key-names $KEY_NAME &> /dev/null; then
    aws ec2 create-key-pair --key-name $KEY_NAME --query 'KeyMaterial' --output text > ${KEY_NAME}.pem
    chmod 400 ${KEY_NAME}.pem
    echo "✅ Key pair created: ${KEY_NAME}.pem"
else
    echo "✅ Key pair already exists"
fi

echo ""
echo "2️⃣ Creating Security Group..."
VPC_ID=$(aws ec2 describe-vpcs --filters "Name=is-default,Values=true" --query "Vpcs[0].VpcId" --output text)
if ! aws ec2 describe-security-groups --group-names $SG_NAME &> /dev/null 2>&1; then
    SG_ID=$(aws ec2 create-security-group \
        --group-name $SG_NAME \
        --description "Security group for Bolaquent" \
        --vpc-id $VPC_ID \
        --query 'GroupId' \
        --output text)
    
    # Allow HTTP
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_ID \
        --protocol tcp \
        --port 80 \
        --cidr 0.0.0.0/0
    
    # Allow HTTPS
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_ID \
        --protocol tcp \
        --port 443 \
        --cidr 0.0.0.0/0
    
    # Allow Flask port
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_ID \
        --protocol tcp \
        --port 5000 \
        --cidr 0.0.0.0/0
    
    # Allow SSH from your IP
    MY_IP=$(curl -s https://checkip.amazonaws.com)
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_ID \
        --protocol tcp \
        --port 22 \
        --cidr ${MY_IP}/32
    
    echo "✅ Security group created: $SG_ID"
else
    SG_ID=$(aws ec2 describe-security-groups --group-names $SG_NAME --query 'SecurityGroups[0].GroupId' --output text)
    echo "✅ Security group already exists: $SG_ID"
fi

echo ""
echo "3️⃣ Creating User Data Script..."
cat > bolaquent-user-data.sh << 'EOF'
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
EOF

echo ""
echo "4️⃣ Launching EC2 Instance..."
# Get latest Amazon Linux 2 AMI
AMI_ID=$(aws ec2 describe-images \
    --owners amazon \
    --filters "Name=name,Values=amzn2-ami-hvm-*-x86_64-gp2" \
    --query 'sort_by(Images, &CreationDate)[-1].ImageId' \
    --output text)

# Create instance
INSTANCE_ID=$(aws ec2 run-instances \
    --image-id $AMI_ID \
    --instance-type $INSTANCE_TYPE \
    --key-name $KEY_NAME \
    --security-group-ids $SG_ID \
    --user-data file://bolaquent-user-data.sh \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$INSTANCE_NAME}]" \
    --query 'Instances[0].InstanceId' \
    --output text)

echo "✅ Instance launched: $INSTANCE_ID"
echo "⏳ Waiting for instance to be running..."
aws ec2 wait instance-running --instance-ids $INSTANCE_ID

# Get public IP
PUBLIC_IP=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text)

echo "✅ Instance is running!"

# Wait for user data to complete
echo "⏳ Waiting for initial deployment to complete (60 seconds)..."
sleep 60

echo ""
echo "5️⃣ Deploying Real Bolaquent Application..."

# Create deployment script for the real app
cat > deploy-real-app.sh << 'EOF'
#!/bin/bash
set -e

cd /opt/bolaquent

# Stop current service
sudo systemctl stop bolaquent

# Backup current app
sudo mv app.py app.py.backup 2>/dev/null || true

# Download real app from S3
aws s3 cp s3://bolaquent-deployments/bolaquent-manual-20250729-182821.zip ./bolaquent-app.zip --region us-east-1
unzip -o bolaquent-app.zip

# Install dependencies
pip3 install -r requirements.txt --user

# Start service
sudo systemctl start bolaquent
sudo systemctl status bolaquent --no-pager

# Test
sleep 5
curl -f http://localhost:5000/ && echo "✅ App is running" || echo "⚠️ App may still be starting"
EOF

# Upload and execute real app deployment
echo -e "📤 Uploading real application..."
scp -i "${KEY_NAME}.pem" -o StrictHostKeyChecking=no deploy-real-app.sh ec2-user@$PUBLIC_IP:/tmp/

echo -e "🚀 Deploying real application..."
ssh -i "${KEY_NAME}.pem" -o StrictHostKeyChecking=no ec2-user@$PUBLIC_IP \
    "chmod +x /tmp/deploy-real-app.sh && /tmp/deploy-real-app.sh"

# Clean up local files
rm -f bolaquent-user-data.sh deploy-real-app.sh

echo ""
echo "📋 Deployment Summary"
echo "===================="
echo "Instance ID: $INSTANCE_ID"
echo "Public IP: $PUBLIC_IP"
echo "URL: http://$PUBLIC_IP"
echo ""
echo "🔐 SSH Access:"
echo "ssh -i ${KEY_NAME}.pem ec2-user@$PUBLIC_IP"
echo ""
echo "🔍 Testing Application..."
sleep 10

if curl -I "http://$PUBLIC_IP/" 2>/dev/null | head -1 | grep -q "200\|302"; then
    echo "✅ Application is accessible at http://$PUBLIC_IP/"
else
    echo "⚠️ Application may still be starting up. Check logs with:"
    echo "ssh -i ${KEY_NAME}.pem ec2-user@$PUBLIC_IP 'sudo systemctl status bolaquent'"
fi

# Save deployment info
cat > bolaquent-deployment-info.txt << EOF
Deployment Date: $(date)
Instance ID: $INSTANCE_ID
Public IP: $PUBLIC_IP
Security Group: $SG_ID
Key Name: $KEY_NAME
Region: $REGION
URL: http://$PUBLIC_IP
SSH: ssh -i ${KEY_NAME}.pem ec2-user@$PUBLIC_IP
EOF

echo ""
echo "✅ Deployment info saved to bolaquent-deployment-info.txt"
echo "🎉 Bolaquent deployment complete!"