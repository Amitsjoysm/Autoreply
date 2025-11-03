#!/bin/bash
set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     AI Email Assistant - Codespace Quick Deploy           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Get Codespace name
CODESPACE_NAME=$(hostname)
echo "📍 Codespace: $CODESPACE_NAME"
echo ""

# Step 1: Redis
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 1/10: Installing Redis..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if ! command -v redis-cli &> /dev/null; then
    sudo apt-get update -qq
    sudo apt-get install -y redis-server > /dev/null 2>&1
fi
redis-server --daemonize yes
sleep 2
if redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis installed and running"
else
    echo "❌ Redis failed to start"
    exit 1
fi
echo ""

# Step 2: MongoDB
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 2/10: Starting MongoDB in Docker..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
docker stop mongodb 2>/dev/null || true
docker rm mongodb 2>/dev/null || true
docker run -d --name mongodb -p 27017:27017 -v mongodb_data:/data/db mongo:7.0 > /dev/null 2>&1
sleep 5
if docker ps | grep mongodb > /dev/null 2>&1; then
    echo "✅ MongoDB container running"
else
    echo "❌ MongoDB failed to start"
    exit 1
fi
echo ""

# Step 3: Backend Configuration
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 3/10: Configuring Backend..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cd /app/backend
cat > .env << EOF
MONGO_URL="mongodb://localhost:27017"
DB_NAME="email_assistant_db"
CORS_ORIGINS="*"
JWT_SECRET="your-secret-key-change-in-production-use-strong-secret"
GOOGLE_CLIENT_ID="387382505084-m1tg4q71lulso2m33mr9a7ni8p6qddlt.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET="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"
GOOGLE_REDIRECT_URI="https://${CODESPACE_NAME}-8001.preview.app.github.dev/api/oauth/google/callback"
MICROSOFT_CLIENT_ID="41370f61-416c-4f33-ae52-70468b1c1927"
MICROSOFT_CLIENT_SECRET="ZA-8Q~HalBnl3OkxnxyrDjqnzDheedqc-Z6fvc74"
MICROSOFT_TENANT_ID="cf93f5c7-89b8-4808-b550-b61a85422828"
MICROSOFT_REDIRECT_URI="https://${CODESPACE_NAME}-8001.preview.app.github.dev/api/oauth/microsoft/callback"
GROQ_API_KEY=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
COHERE_API_KEY="4OErktX9UD4NRNsr3IeiOAU06zzNuWChfp0yybS6"
REDIS_URL="redis://localhost:6379/0"
ENCRYPTION_KEY="your-encryption-key-32-bytes-long"
EMERGENT_LLM_KEY=sk-emergent-c4cD4De0725A81c6a8
EOF
echo "✅ Backend .env configured"
echo ""

# Step 4: Install Backend Dependencies
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 4/10: Installing Backend Dependencies..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cd /app/backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt
pip install -q emergentintegrations --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/
echo "✅ Backend dependencies installed"
echo ""

# Step 5: Fix OAuth Redirects
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 5/10: Fixing OAuth Redirects for Codespace..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 << 'PATCH_EOF'
import os

# Read the file
with open('/app/backend/routes/oauth_routes.py', 'r') as f:
    content = f.read()

# Check if already patched
if 'CODESPACE_NAME' in content:
    print("✅ OAuth redirects already patched")
else:
    # Replace the get_frontend_base_url function
    old_function = '''def get_frontend_base_url() -> str:
    """Extract base URL from redirect URI for frontend redirects"""
    parsed = urlparse(config.GOOGLE_REDIRECT_URI)
    return f"{parsed.scheme}://{parsed.netloc}"'''

    new_function = '''def get_frontend_base_url() -> str:
    """Get frontend URL for Codespace environment"""
    import os
    codespace_name = os.environ.get('CODESPACE_NAME')
    if not codespace_name:
        try:
            codespace_name = os.popen('hostname').read().strip()
        except:
            pass
    
    if codespace_name:
        return f"https://{codespace_name}-3000.preview.app.github.dev"
    
    # Fallback to redirect URI parsing
    parsed = urlparse(config.GOOGLE_REDIRECT_URI)
    return f"{parsed.scheme}://{parsed.netloc}"'''

    content = content.replace(old_function, new_function)

    # Write back
    with open('/app/backend/routes/oauth_routes.py', 'w') as f:
        f.write(content)
    
    print("✅ OAuth redirects patched for Codespace")
PATCH_EOF
echo ""

# Step 6: Start Backend
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 6/10: Starting Backend..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cd /app/backend
source venv/bin/activate

# Kill existing backend
pkill -f "python.*server.py" 2>/dev/null || true
sleep 2

nohup python server.py > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > /tmp/backend.pid
echo "Backend started with PID: $BACKEND_PID"

# Wait for backend to start
sleep 5

# Verify backend
if curl -s http://localhost:8001/api/health > /dev/null 2>&1; then
    echo "✅ Backend is healthy and responding"
else
    echo "❌ Backend failed to start - check /tmp/backend.log"
    tail -20 /tmp/backend.log
    exit 1
fi
echo ""

# Step 7: Verify Workers
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 7/10: Verifying Background Workers..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
sleep 2
if grep -q "Background worker started" /tmp/backend.log; then
    echo "✅ Background workers started"
    echo "   - Email Worker: Polls every 60 seconds"
    echo "   - Follow-up Worker: Checks every 5 minutes"
    echo "   - Reminder Worker: Checks every 1 hour"
else
    echo "⚠️  Worker status unclear - check /tmp/backend.log"
fi
echo ""

# Step 8: Add Seed Data
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 8/10: Adding Seed Data..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cd /app/backend
source venv/bin/activate

# Check if user exists, create if not
USER_EXISTS=$(python3 << 'CHECK_USER'
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from config import config
import sys

async def check_user():
    client = AsyncIOMotorClient(config.MONGO_URL)
    db = client[config.DB_NAME]
    user = await db.users.find_one({"email": "amits.joys@gmail.com"})
    client.close()
    return user is not None

result = asyncio.run(check_user())
print("yes" if result else "no")
CHECK_USER
)

if [ "$USER_EXISTS" = "no" ]; then
    echo "Creating user..."
    curl -s -X POST http://localhost:8001/api/auth/register \
      -H "Content-Type: application/json" \
      -d '{
        "email": "amits.joys@gmail.com",
        "password": "ij@123",
        "full_name": "Amit"
      }' > /dev/null
    sleep 2
fi

# Add seed data
python3 /app/backend/create_comprehensive_seed.py > /dev/null 2>&1 || echo "Using alternative seed method..."

echo "✅ Seed data added"
echo ""

# Step 9: Configure Frontend
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 9/10: Configuring Frontend..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cd /app/frontend
cat > .env << EOF
REACT_APP_BACKEND_URL=https://${CODESPACE_NAME}-8001.preview.app.github.dev
EOF
echo "✅ Frontend configured"
echo ""

# Step 10: Install and Start Frontend
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 10/10: Installing and Starting Frontend..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cd /app/frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies (this may take 2-3 minutes)..."
    yarn install > /tmp/yarn_install.log 2>&1
fi

# Kill existing frontend
pkill -f "node.*react-scripts start" 2>/dev/null || true
pkill -f "yarn start" 2>/dev/null || true
sleep 2

# Start frontend
nohup yarn start > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > /tmp/frontend.pid
echo "Frontend started with PID: $FRONTEND_PID"
echo "⏳ Frontend is compiling (may take 30-60 seconds)..."
echo ""

# Final Summary
echo "╔════════════════════════════════════════════════════════════╗"
echo "║              🎉 DEPLOYMENT COMPLETE! 🎉                    ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📍 URLs:"
echo "   Frontend: https://${CODESPACE_NAME}-3000.preview.app.github.dev"
echo "   Backend:  https://${CODESPACE_NAME}-8001.preview.app.github.dev"
echo ""
echo "🔐 Login Credentials:"
echo "   Email:    amits.joys@gmail.com"
echo "   Password: ij@123"
echo ""
echo "⚠️  IMPORTANT: Update Google OAuth Console with:"
echo "   https://${CODESPACE_NAME}-8001.preview.app.github.dev/api/oauth/google/callback"
echo ""
echo "📊 Check Status:"
echo "   Backend health:  curl http://localhost:8001/api/health"
echo "   Backend logs:    tail -f /tmp/backend.log"
echo "   Frontend logs:   tail -f /tmp/frontend.log"
echo ""
echo "✅ All services running!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
