#!/bin/bash
# Deployment script for Bolaquent vocabulary learning app

# AWS Configuration
INSTANCE_ID="i-0332d1b2863b08d95"
PUBLIC_IP="54.89.117.172"
SECURITY_GROUP="sg-027bbdda70b9ae03b"
KEY_NAME="customer-success-key-east"

echo "Deploying Bolaquent to AWS EC2 instance: $INSTANCE_ID"
echo "Public IP: $PUBLIC_IP"
echo "GitHub Repository: https://github.com/awilber/Bolaquent"

# SSH connection command
echo "To connect to the instance:"
echo "ssh -i ~/.ssh/$KEY_NAME.pem ec2-user@$PUBLIC_IP"

# Deployment steps would go here once the Flask app is built
echo "Instance is ready for application deployment"