#!/bin/bash

echo "🔧 Fixing AWS port conflict and starting Flask app"

ssh -i bolaquent-key.pem -o StrictHostKeyChecking=no ec2-user@54.161.222.239 << 'PORTFIXEOF'
#!/bin/bash
set -e

echo "🛑 Aggressive port cleanup..."

# Kill all processes on port 5000
sudo lsof -ti:5000 | xargs -r sudo kill -9 || true
sudo lsof -ti:5001 | xargs -r sudo kill -9 || true

# Kill all Flask/Python processes
sudo pkill -f "python.*app.py" || true
sudo pkill -f "Flask" || true
sudo pkill -f "bolaquent" || true

# Kill all Python processes related to web
sudo ps aux | grep -E "(python.*app|Flask)" | grep -v grep | awk '{print $2}' | xargs -r sudo kill -9 || true

# Wait for processes to die
sleep 10

# Double-check port is free
if lsof -i:5000; then
    echo "⚠️ Port 5000 still in use - force killing..."
    sudo lsof -ti:5000 | xargs -r sudo kill -9 || true
    sleep 5
fi

# Now start our Flask app
cd /home/ec2-user/bolaquent-app

echo "🚀 Starting Flask application on clean port..."
source venv/bin/activate

# Set environment variables
export FLASK_ENV=production
export PORT=5000
export FLASK_HOST=0.0.0.0

# Start with nohup and capture PID
nohup python app.py > app.log 2>&1 &
APP_PID=$!
echo $APP_PID > app.pid

echo "📝 Started Flask app with PID: $APP_PID"

# Wait and verify
sleep 15

if ps -p $APP_PID > /dev/null; then
    echo "✅ Flask process $APP_PID is running successfully"
    
    # Test the application
    if curl -f http://localhost:5000/ > /dev/null 2>&1; then
        echo "✅ Flask responding on port 5000"
        
        # Test for embedded hero styles
        if curl -s http://localhost:5000/ | grep -q "hero-learning"; then
            echo "🎉 Embedded hero styles detected!"
        else
            echo "⚠️ Hero styles not detected in response"
        fi
    else
        echo "❌ Flask not responding on port 5000"
        cat app.log
        exit 1
    fi
else
    echo "❌ Flask process died - checking logs:"
    cat app.log
    exit 1
fi

echo "🌐 Application should now be accessible at http://54.161.222.239/"
PORTFIXEOF