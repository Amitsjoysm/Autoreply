# GitHub Codespaces Manual Deployment Guide

## 🚀 Complete Step-by-Step Deployment

### Prerequisites
- GitHub Codespace running
- Terminal access

---

## Step 1: Install and Verify Redis

```bash
# Install Redis
sudo apt-get update
sudo apt-get install -y redis-server

# Start Redis server
redis-server --daemonize yes

# Wait a moment for Redis to start
sleep 2

# Verify Redis is running
redis-cli ping
# Expected output: PONG

# Check Redis is listening
netstat -tulpn | grep 6379
# Expected: tcp 0.0.0.0:6379

# Test Redis connection
redis-cli SET test "hello"
redis-cli GET test
# Expected: "hello"

echo "✅ Redis is installed and listening on port 6379"
```

---

## Step 2: Start MongoDB in Docker

```bash
# Pull MongoDB image (if not already present)
docker pull mongo:7.0

# Stop and remove any existing MongoDB container
docker stop mongodb 2>/dev/null || true
docker rm mongodb 2>/dev/null || true

# Start MongoDB container
docker run -d \
  --name mongodb \
  -p 27017:27017 \
  -v mongodb_data:/data/db \
  mongo:7.0

# Wait for MongoDB to be ready
sleep 5

# Verify MongoDB is running
docker ps | grep mongodb

# Test MongoDB connection
docker exec mongodb mongosh --eval "db.adminCommand('ping')"
# Expected: { ok: 1 }

# Create database (optional - will be created automatically)
docker exec mongodb mongosh --eval "use email_assistant_db"

echo "✅ MongoDB is running in Docker on port 27017"
```

---

## Step 3: Configure Backend for Codespace

```bash
# Get your Codespace URL
CODESPACE_NAME=$(hostname)
GITHUB_CODESPACE_URL="https://${CODESPACE_NAME}-3000.preview.app.github.dev"

echo "Your Codespace URL: $GITHUB_CODESPACE_URL"

# Navigate to backend
cd /app/backend

# Update .env file with Codespace-specific settings
cat > .env << EOF
MONGO_URL="mongodb://localhost:27017"
DB_NAME="email_assistant_db"
CORS_ORIGINS="*"

# JWT
JWT_SECRET="your-secret-key-change-in-production-use-strong-secret"

# Google OAuth - UPDATE REDIRECT URI FOR CODESPACE
GOOGLE_CLIENT_ID="387382505084-m1tg4q71lulso2m33mr9a7ni8p6qddlt.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET="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"
GOOGLE_REDIRECT_URI="https://${CODESPACE_NAME}-8001.preview.app.github.dev/api/oauth/google/callback"

# Microsoft OAuth - UPDATE REDIRECT URI FOR CODESPACE
MICROSOFT_CLIENT_ID="41370f61-416c-4f33-ae52-70468b1c1927"
MICROSOFT_CLIENT_SECRET="ZA-8Q~HalBnl3OkxnxyrDjqnzDheedqc-Z6fvc74"
MICROSOFT_TENANT_ID="cf93f5c7-89b8-4808-b550-b61a85422828"
MICROSOFT_REDIRECT_URI="https://${CODESPACE_NAME}-8001.preview.app.github.dev/api/oauth/microsoft/callback"

# AI APIs
GROQ_API_KEY=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
COHERE_API_KEY="4OErktX9UD4NRNsr3IeiOAU06zzNuWChfp0yybS6"

# Redis
REDIS_URL="redis://localhost:6379/0"

# Encryption key for passwords
ENCRYPTION_KEY="your-encryption-key-32-bytes-long"
EMERGENT_LLM_KEY=sk-emergent-c4cD4De0725A81c6a8
EOF

echo "✅ Backend .env configured for Codespace"
echo "⚠️  IMPORTANT: OAuth redirect URIs updated to: https://${CODESPACE_NAME}-8001.preview.app.github.dev"
```

---

## Step 4: Install Backend Requirements

```bash
cd /app/backend

# Create virtual environment (if not exists)
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt

# Install emergentintegrations
pip install emergentintegrations --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/

# Verify key packages
echo "Verifying installations:"
pip show fastapi
pip show redis
pip show pymongo
pip show emergentintegrations

echo "✅ Backend requirements installed"
```

---

## Step 5: Start Backend Server

```bash
cd /app/backend

# Activate virtual environment
source venv/bin/activate

# Start backend server in background
nohup python server.py > /tmp/backend.log 2>&1 &

# Save backend PID
BACKEND_PID=$!
echo $BACKEND_PID > /tmp/backend.pid

echo "Backend started with PID: $BACKEND_PID"

# Wait for server to start
sleep 5

# Check backend logs
tail -20 /tmp/backend.log

# Verify backend is running
curl -s http://localhost:8001/api/health | python3 -m json.tool

echo "✅ Backend is running on http://localhost:8001"
```

---

## Step 6: Verify Workers are Running

```bash
# Check backend logs for worker startup
echo "Checking for worker activity..."

grep -i "worker" /tmp/backend.log | tail -10

# You should see lines like:
# "✓ Background worker started"
# "Polling X active accounts"
# "Found X follow-ups to send"
# "Found X events needing reminders"

# Check if workers are polling
sleep 65  # Wait for first poll cycle (60s)

echo "Recent worker activity:"
tail -30 /tmp/backend.log | grep -E "(Polling|follow-up|reminder)"

echo "✅ Workers are running"
echo "   - Email Worker: Polls every 60 seconds"
echo "   - Follow-up Worker: Checks every 5 minutes"
echo "   - Reminder Worker: Checks every 1 hour"
```

---

## Step 7: Add Seed Data

```bash
cd /app/backend

# Activate virtual environment
source venv/bin/activate

# Check if user exists
USER_EMAIL="amits.joys@gmail.com"

# Get user ID
USER_ID=$(python3 << EOF
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from config import config

async def get_user():
    client = AsyncIOMotorClient(config.MONGO_URL)
    db = client[config.DB_NAME]
    user = await db.users.find_one({"email": "$USER_EMAIL"})
    if user:
        print(user['id'])
    client.close()

asyncio.run(get_user())
EOF
)

if [ -z "$USER_ID" ]; then
    echo "⚠️  User not found. Creating user first..."
    
    # Create user via API
    curl -X POST http://localhost:8001/api/auth/register \
      -H "Content-Type: application/json" \
      -d '{
        "email": "amits.joys@gmail.com",
        "password": "ij@123",
        "full_name": "Amit"
      }'
    
    sleep 2
    
    # Get user ID again
    USER_ID=$(python3 << EOF
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from config import config

async def get_user():
    client = AsyncIOMotorClient(config.MONGO_URL)
    db = client[config.DB_NAME]
    user = await db.users.find_one({"email": "$USER_EMAIL"})
    if user:
        print(user['id'])
    client.close()

asyncio.run(get_user())
EOF
)
fi

echo "User ID: $USER_ID"

# Run seed data script
python3 << EOF
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from config import config
from datetime import datetime, timezone

async def seed_data():
    client = AsyncIOMotorClient(config.MONGO_URL)
    db = client[config.DB_NAME]
    
    user_id = "$USER_ID"
    
    # Delete existing seed data for this user
    await db.intents.delete_many({"user_id": user_id})
    await db.knowledge_base.delete_many({"user_id": user_id})
    
    # Create intents
    intents = [
        {
            "id": "intent_meeting_001",
            "user_id": user_id,
            "name": "Meeting Request",
            "keywords": ["meeting", "schedule", "calendar", "appointment", "call", "zoom", "teams", "discuss"],
            "priority": 10,
            "auto_send": True,
            "is_default": False,
            "prompt": "Handle meeting and scheduling requests professionally. Confirm availability, suggest times, and create calendar events.",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "is_active": True
        },
        {
            "id": "intent_support_001",
            "user_id": user_id,
            "name": "Support Request",
            "keywords": ["issue", "problem", "error", "help", "support", "not working", "bug", "fix"],
            "priority": 8,
            "auto_send": True,
            "is_default": False,
            "prompt": "Provide empathetic support. Acknowledge the issue, offer troubleshooting steps, and provide clear next steps.",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "is_active": True
        },
        {
            "id": "intent_inquiry_001",
            "user_id": user_id,
            "name": "General Inquiry",
            "keywords": ["question", "inquiry", "information", "how", "what", "when", "where", "why"],
            "priority": 5,
            "auto_send": True,
            "is_default": False,
            "prompt": "Answer questions clearly using the knowledge base. Be informative and helpful.",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "is_active": True
        },
        {
            "id": "intent_default_001",
            "user_id": user_id,
            "name": "Default",
            "keywords": [],
            "priority": 1,
            "auto_send": True,
            "is_default": True,
            "prompt": "Respond to emails that don't match any specific category. Use knowledge base and persona to craft helpful responses.",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "is_active": True
        }
    ]
    
    await db.intents.insert_many(intents)
    
    # Create knowledge base
    kb_entries = [
        {
            "id": "kb_company_001",
            "user_id": user_id,
            "title": "Company Overview",
            "content": "We are an AI-powered email assistant service helping professionals manage their inbox efficiently.",
            "category": "Company",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "is_active": True
        },
        {
            "id": "kb_product_001",
            "user_id": user_id,
            "title": "Product Features",
            "content": "Features include: AI-powered email responses, calendar integration, meeting scheduling, follow-up management, and smart intent detection.",
            "category": "Product",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "is_active": True
        },
        {
            "id": "kb_support_001",
            "user_id": user_id,
            "title": "Support Information",
            "content": "For support, contact us at support@example.com. We provide 24/7 assistance.",
            "category": "Support",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "is_active": True
        }
    ]
    
    await db.knowledge_base.insert_many(kb_entries)
    
    print(f"✅ Created {len(intents)} intents")
    print(f"✅ Created {len(kb_entries)} knowledge base entries")
    
    client.close()

asyncio.run(seed_data())
EOF

echo "✅ Seed data added successfully"
```

---

## Step 8: Configure Frontend for Codespace

```bash
cd /app/frontend

# Get Codespace name
CODESPACE_NAME=$(hostname)

# Create .env file for frontend
cat > .env << EOF
# Backend API URL for Codespace
REACT_APP_BACKEND_URL=https://${CODESPACE_NAME}-8001.preview.app.github.dev
EOF

echo "✅ Frontend .env configured"
echo "Backend URL: https://${CODESPACE_NAME}-8001.preview.app.github.dev"
```

---

## Step 9: Install Frontend Dependencies

```bash
cd /app/frontend

# Install dependencies with yarn
yarn install

# This may take 2-3 minutes
# Wait for completion

echo "✅ Frontend dependencies installed"
```

---

## Step 10: Build and Start Frontend

```bash
cd /app/frontend

# Start frontend development server in background
nohup yarn start > /tmp/frontend.log 2>&1 &

# Save frontend PID
FRONTEND_PID=$!
echo $FRONTEND_PID > /tmp/frontend.pid

echo "Frontend started with PID: $FRONTEND_PID"

# Wait for frontend to compile
echo "Waiting for frontend to compile (this may take 30-60 seconds)..."
sleep 40

# Check frontend logs
tail -30 /tmp/frontend.log

# Frontend should be accessible on port 3000
echo "✅ Frontend is building/running on port 3000"
```

---

## Step 11: OAuth Redirect Configuration Fix

### The Problem
When you click OAuth buttons in Codespace, the callback doesn't redirect back to the correct page.

### The Solution

Update the OAuth callback handler to use the Codespace frontend URL:

```bash
cd /app/backend

# Get Codespace URL
CODESPACE_NAME=$(hostname)
FRONTEND_URL="https://${CODESPACE_NAME}-3000.preview.app.github.dev"

# Create a patch for oauth_routes.py
cat > /tmp/oauth_patch.py << 'PATCH_EOF'
import sys

# Read the file
with open('/app/backend/routes/oauth_routes.py', 'r') as f:
    content = f.read()

# Get frontend URL from command line
frontend_url = sys.argv[1]

# Replace the get_frontend_base_url function
old_function = '''def get_frontend_base_url() -> str:
    """Extract base URL from redirect URI for frontend redirects"""
    parsed = urlparse(config.GOOGLE_REDIRECT_URI)
    return f"{parsed.scheme}://{parsed.netloc}"'''

new_function = f'''def get_frontend_base_url() -> str:
    """Get frontend URL for Codespace environment"""
    # For Codespace: use frontend port directly
    import os
    codespace_name = os.environ.get('CODESPACE_NAME') or os.popen('hostname').read().strip()
    if codespace_name:
        return f"https://{{codespace_name}}-3000.preview.app.github.dev"
    # Fallback to redirect URI parsing
    parsed = urlparse(config.GOOGLE_REDIRECT_URI)
    return f"{{parsed.scheme}}://{{parsed.netloc}}"'''

content = content.replace(old_function, new_function)

# Write back
with open('/app/backend/routes/oauth_routes.py', 'w') as f:
    f.write(content)

print("✅ OAuth redirect patched successfully")
PATCH_EOF

# Apply the patch
python3 /tmp/oauth_patch.py "$FRONTEND_URL"

# Restart backend to apply changes
kill $(cat /tmp/backend.pid)
sleep 2

cd /app/backend
source venv/bin/activate
nohup python server.py > /tmp/backend.log 2>&1 &
echo $! > /tmp/backend.pid

echo "✅ Backend restarted with OAuth redirect fix"
```

---

## Step 12: Update Google OAuth Configuration

### IMPORTANT: Update OAuth Redirect URIs in Google Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project
3. Navigate to: **APIs & Services** → **Credentials**
4. Click on your OAuth 2.0 Client ID
5. Add the following to **Authorized redirect URIs**:

```
https://[YOUR-CODESPACE-NAME]-8001.preview.app.github.dev/api/oauth/google/callback
```

Replace `[YOUR-CODESPACE-NAME]` with your actual codespace hostname:

```bash
echo "Add this to Google OAuth Console:"
echo "https://$(hostname)-8001.preview.app.github.dev/api/oauth/google/callback"
```

6. Save changes

---

## Step 13: Verify Complete Deployment

```bash
# Create verification script
cat > /tmp/verify_deployment.sh << 'VERIFY_EOF'
#!/bin/bash

echo "=================================="
echo "   DEPLOYMENT VERIFICATION"
echo "=================================="
echo ""

# Check Redis
echo "1. Redis Status:"
if redis-cli ping > /dev/null 2>&1; then
    echo "   ✅ Redis is running"
else
    echo "   ❌ Redis is NOT running"
fi
echo ""

# Check MongoDB
echo "2. MongoDB Status:"
if docker ps | grep mongodb > /dev/null 2>&1; then
    echo "   ✅ MongoDB container is running"
else
    echo "   ❌ MongoDB container is NOT running"
fi
echo ""

# Check Backend
echo "3. Backend Status:"
if curl -s http://localhost:8001/api/health > /dev/null 2>&1; then
    echo "   ✅ Backend is responding"
    curl -s http://localhost:8001/api/health | python3 -m json.tool
else
    echo "   ❌ Backend is NOT responding"
fi
echo ""

# Check Frontend
echo "4. Frontend Status:"
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "   ✅ Frontend is serving"
else
    echo "   ❌ Frontend is NOT serving"
fi
echo ""

# Check Workers
echo "5. Background Workers:"
if grep -q "Background worker started" /tmp/backend.log 2>/dev/null; then
    echo "   ✅ Workers started"
    echo "   Recent activity:"
    tail -5 /tmp/backend.log | grep -E "(Polling|worker)" | sed 's/^/   /'
else
    echo "   ⚠️  Worker status unclear"
fi
echo ""

# Check Seed Data
echo "6. Seed Data:"
INTENT_COUNT=$(docker exec mongodb mongosh email_assistant_db --quiet --eval "db.intents.countDocuments({})" 2>/dev/null)
KB_COUNT=$(docker exec mongodb mongosh email_assistant_db --quiet --eval "db.knowledge_base.countDocuments({})" 2>/dev/null)
echo "   Intents: $INTENT_COUNT"
echo "   Knowledge Base: $KB_COUNT"
echo ""

# URLs
CODESPACE_NAME=$(hostname)
echo "=================================="
echo "   ACCESS URLS"
echo "=================================="
echo "Frontend: https://${CODESPACE_NAME}-3000.preview.app.github.dev"
echo "Backend:  https://${CODESPACE_NAME}-8001.preview.app.github.dev"
echo ""
echo "Login Credentials:"
echo "  Email: amits.joys@gmail.com"
echo "  Password: ij@123"
echo ""
echo "=================================="
VERIFY_EOF

chmod +x /tmp/verify_deployment.sh
/tmp/verify_deployment.sh
```

---

## Quick Reference Commands

### Start/Stop Services

```bash
# Start Redis
redis-server --daemonize yes

# Start MongoDB
docker start mongodb

# Start Backend
cd /app/backend && source venv/bin/activate
nohup python server.py > /tmp/backend.log 2>&1 &
echo $! > /tmp/backend.pid

# Start Frontend
cd /app/frontend
nohup yarn start > /tmp/frontend.log 2>&1 &
echo $! > /tmp/frontend.pid

# Stop Backend
kill $(cat /tmp/backend.pid)

# Stop Frontend
kill $(cat /tmp/frontend.pid)

# Stop MongoDB
docker stop mongodb
```

### Check Logs

```bash
# Backend logs
tail -f /tmp/backend.log

# Frontend logs
tail -f /tmp/frontend.log

# Backend errors only
tail -f /tmp/backend.log | grep -i error

# Worker activity
tail -f /tmp/backend.log | grep -E "(Polling|worker|follow-up|reminder)"
```

### Check Status

```bash
# All services
/tmp/verify_deployment.sh

# Backend health
curl http://localhost:8001/api/health

# Redis
redis-cli ping

# MongoDB
docker exec mongodb mongosh --eval "db.adminCommand('ping')"

# Worker status
ps aux | grep -E "(server.py|yarn start)" | grep -v grep
```

---

## Troubleshooting

### OAuth Redirect Issues

**Problem**: After OAuth, page doesn't redirect to email-accounts or calendar-providers

**Solution**:
1. Verify .env has correct Codespace URLs
2. Check Google Console has correct redirect URI
3. Verify oauth_routes.py uses correct frontend URL
4. Restart backend after changes

### Backend Not Starting

```bash
# Check logs
cat /tmp/backend.log

# Common issues:
# - MongoDB not running: docker start mongodb
# - Redis not running: redis-server --daemonize yes
# - Missing dependencies: pip install -r requirements.txt
```

### Workers Not Running

```bash
# Check backend logs
grep -i worker /tmp/backend.log

# Workers start automatically with backend
# If not running, restart backend
```

### Frontend Build Issues

```bash
# Clear cache and rebuild
cd /app/frontend
rm -rf node_modules
yarn install
yarn start
```

---

## Environment Variables Summary

### Backend (.env)
- `MONGO_URL`: MongoDB connection
- `REDIS_URL`: Redis connection
- `GOOGLE_REDIRECT_URI`: Must match Codespace backend URL
- `MICROSOFT_REDIRECT_URI`: Must match Codespace backend URL

### Frontend (.env)
- `REACT_APP_BACKEND_URL`: Must point to Codespace backend URL

### Critical for OAuth
Both redirect URIs must use your Codespace name and port 8001:
```
https://[CODESPACE-NAME]-8001.preview.app.github.dev/api/oauth/google/callback
```

---

## Complete Deployment Script

Save this as `/tmp/deploy_all.sh`:

```bash
#!/bin/bash
set -e

echo "🚀 Starting complete deployment..."

# Step 1: Redis
echo "Step 1: Installing Redis..."
sudo apt-get update -qq
sudo apt-get install -y redis-server > /dev/null 2>&1
redis-server --daemonize yes
sleep 2
redis-cli ping

# Step 2: MongoDB
echo "Step 2: Starting MongoDB..."
docker stop mongodb 2>/dev/null || true
docker rm mongodb 2>/dev/null || true
docker run -d --name mongodb -p 27017:27017 -v mongodb_data:/data/db mongo:7.0
sleep 5

# Step 3: Backend config
echo "Step 3: Configuring backend..."
CODESPACE_NAME=$(hostname)
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

# Step 4: Install backend
echo "Step 4: Installing backend dependencies..."
python3 -m venv venv
source venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt
pip install -q emergentintegrations --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/

# Step 5: Start backend
echo "Step 5: Starting backend..."
nohup python server.py > /tmp/backend.log 2>&1 &
echo $! > /tmp/backend.pid
sleep 5

# Step 6: Frontend config
echo "Step 6: Configuring frontend..."
cd /app/frontend
cat > .env << EOF
REACT_APP_BACKEND_URL=https://${CODESPACE_NAME}-8001.preview.app.github.dev
EOF

# Step 7: Install frontend
echo "Step 7: Installing frontend dependencies..."
yarn install > /tmp/yarn_install.log 2>&1

# Step 8: Start frontend
echo "Step 8: Starting frontend..."
nohup yarn start > /tmp/frontend.log 2>&1 &
echo $! > /tmp/frontend.pid

echo ""
echo "✅ Deployment complete!"
echo ""
echo "Frontend: https://${CODESPACE_NAME}-3000.preview.app.github.dev"
echo "Backend:  https://${CODESPACE_NAME}-8001.preview.app.github.dev"
echo ""
echo "⚠️  Remember to update Google OAuth redirect URI:"
echo "https://${CODESPACE_NAME}-8001.preview.app.github.dev/api/oauth/google/callback"
```

Run it with:
```bash
chmod +x /tmp/deploy_all.sh
/tmp/deploy_all.sh
```

---

## Success Checklist

- [ ] Redis responding to PING
- [ ] MongoDB container running
- [ ] Backend returning healthy status
- [ ] Frontend serving on port 3000
- [ ] Workers logging activity
- [ ] Seed data in database
- [ ] OAuth redirect URIs updated in Google Console
- [ ] .env files configured for Codespace
- [ ] Can access frontend via Codespace URL
- [ ] Can login with test credentials

---

**🎉 Your app is now deployed and running in GitHub Codespaces!**
