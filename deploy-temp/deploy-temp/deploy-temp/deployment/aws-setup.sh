#!/bin/bash
# AWS Infrastructure Setup for Bolaquent

set -e

echo "🚀 Setting up AWS infrastructure for Bolaquent deployment..."

# Variables
INSTANCE_ID="i-0332d1b2863b08d95"
BUCKET_NAME="bolaquent-deployments"
KEY_NAME="customer-success-key-east"

# Create S3 bucket for deployments
echo "📦 Creating S3 bucket for deployments..."
aws s3 mb s3://$BUCKET_NAME --region us-east-1 || echo "Bucket may already exist"

# Configure S3 bucket policy for secure access
aws s3api put-bucket-versioning \
    --bucket $BUCKET_NAME \
    --versioning-configuration Status=Enabled

# Install SSM agent on EC2 (if not already installed)
echo "🔧 Configuring EC2 instance for automated deployment..."
aws ssm send-command \
    --instance-ids $INSTANCE_ID \
    --document-name "AWS-ConfigureAWSPackage" \
    --parameters 'action=Install,name=AmazonSSMAgent' \
    --output text

# Create IAM role for EC2 instance (if needed)
echo "🔐 Setting up IAM permissions..."
aws iam create-role \
    --role-name BolaquentEC2Role \
    --assume-role-policy-document '{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "ec2.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }' || echo "Role may already exist"

# Attach policies to role
aws iam attach-role-policy \
    --role-name BolaquentEC2Role \
    --policy-arn arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore || true

aws iam attach-role-policy \
    --role-name BolaquentEC2Role \
    --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess || true

# Create instance profile
aws iam create-instance-profile \
    --instance-profile-name BolaquentEC2Profile || echo "Profile may already exist"

aws iam add-role-to-instance-profile \
    --instance-profile-name BolaquentEC2Profile \
    --role-name BolaquentEC2Role || true

# Associate instance profile with EC2
aws ec2 associate-iam-instance-profile \
    --instance-id $INSTANCE_ID \
    --iam-instance-profile Name=BolaquentEC2Profile || echo "Profile may already be associated"

echo "✅ AWS infrastructure setup complete!"
echo "📋 Summary:"
echo "   - EC2 Instance: $INSTANCE_ID"
echo "   - S3 Bucket: s3://$BUCKET_NAME" 
echo "   - IAM Role: BolaquentEC2Role"
echo "   - Public URL: http://54.89.117.172:5000"
echo ""
echo "🔄 GitHub Actions will now handle automated deployments from main branch"