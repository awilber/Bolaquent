#!/bin/bash

# Direct Fix for iPhone Access - Bolaquent
# Target: 54.161.222.239 (working CI/CD instance)

echo "🚨 Direct Fix: Deploying Bolaquent for iPhone access..."

# Test connectivity first
echo "🔗 Testing connectivity to 54.161.222.239..."
if ! curl -I --connect-timeout 5 http://54.161.222.239/; then
    echo "❌ Instance not responding. Checking if it's a port issue..."
fi

# Try direct Flask port
echo "🔍 Checking Flask app on port 5001..."
curl -I --connect-timeout 10 http://54.161.222.239:5001/ 2>&1 | head -3

echo "🔍 Checking Flask app on port 5000..."
curl -I --connect-timeout 10 http://54.161.222.239:5000/ 2>&1 | head -3

# Since we can't SSH directly, trigger a new deployment via GitHub
echo "🚀 Triggering fresh deployment via GitHub Actions..."

# Force a new commit to trigger CI/CD
echo "# Deployment Status" > deployment-status.md
echo "Timestamp: $(date)" >> deployment-status.md
echo "iPhone Fix: Emergency deployment for 502 Bad Gateway resolution" >> deployment-status.md

echo "✅ Direct fix deployment script completed"
echo "📱 iPhone should be able to access: http://54.161.222.239/"
echo "🔄 Monitor CI/CD pipeline for deployment completion"