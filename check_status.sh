#!/bin/bash

# Quick status check script for Codespaces deployment

echo "╔════════════════════════════════════════════════════════════╗"
echo "║         AI Email Assistant - Status Check                 ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

CODESPACE_NAME=$(hostname)

# Function to check service
check_service() {
    local name=$1
    local check_cmd=$2
    
    echo -n "  $name: "
    if eval $check_cmd > /dev/null 2>&1; then
        echo "✅ Running"
        return 0
    else
        echo "❌ Not Running"
        return 1
    fi
}

# Check all services
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Services Status:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
check_service "Redis      " "redis-cli ping"
check_service "MongoDB    " "docker ps | grep mongodb"
check_service "Backend    " "curl -s http://localhost:8001/api/health"
check_service "Frontend   " "curl -s http://localhost:3000"
echo ""

# Check backend health
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Backend Health:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if curl -s http://localhost:8001/api/health 2>/dev/null; then
    echo ""
else
    echo "  ❌ Backend not responding"
fi
echo ""

# Check workers
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Background Workers:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -f /tmp/backend.log ]; then
    if grep -q "Background worker started" /tmp/backend.log; then
        echo "  ✅ Workers started"
        echo ""
        echo "  Recent activity (last 5 lines):"
        tail -5 /tmp/backend.log | grep -E "(Polling|worker|follow-up|reminder)" | sed 's/^/  /' || echo "  No recent activity"
    else
        echo "  ⚠️  No worker activity detected"
    fi
else
    echo "  ⚠️  Backend log not found"
fi
echo ""

# Check database
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Database Contents:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if docker ps | grep mongodb > /dev/null 2>&1; then
    USERS=$(docker exec mongodb mongosh email_assistant_db --quiet --eval "db.users.countDocuments({})" 2>/dev/null || echo "?")
    INTENTS=$(docker exec mongodb mongosh email_assistant_db --quiet --eval "db.intents.countDocuments({})" 2>/dev/null || echo "?")
    KB=$(docker exec mongodb mongosh email_assistant_db --quiet --eval "db.knowledge_base.countDocuments({})" 2>/dev/null || echo "?")
    EMAILS=$(docker exec mongodb mongosh email_assistant_db --quiet --eval "db.emails.countDocuments({})" 2>/dev/null || echo "?")
    EMAIL_ACCOUNTS=$(docker exec mongodb mongosh email_assistant_db --quiet --eval "db.email_accounts.countDocuments({})" 2>/dev/null || echo "?")
    
    echo "  Users:          $USERS"
    echo "  Intents:        $INTENTS"
    echo "  Knowledge Base: $KB"
    echo "  Emails:         $EMAILS"
    echo "  Email Accounts: $EMAIL_ACCOUNTS"
else
    echo "  ❌ MongoDB not running"
fi
echo ""

# Process info
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Process Information:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -f /tmp/backend.pid ]; then
    BACKEND_PID=$(cat /tmp/backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        echo "  Backend PID:  $BACKEND_PID (running)"
    else
        echo "  Backend PID:  $BACKEND_PID (not running)"
    fi
else
    echo "  Backend PID:  Not found"
fi

if [ -f /tmp/frontend.pid ]; then
    FRONTEND_PID=$(cat /tmp/frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo "  Frontend PID: $FRONTEND_PID (running)"
    else
        echo "  Frontend PID: $FRONTEND_PID (not running)"
    fi
else
    echo "  Frontend PID: Not found"
fi
echo ""

# URLs
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Access URLs:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Frontend: https://${CODESPACE_NAME}-3000.preview.app.github.dev"
echo "  Backend:  https://${CODESPACE_NAME}-8001.preview.app.github.dev"
echo ""
echo "  Login:    amits.joys@gmail.com / ij@123"
echo ""

# OAuth URIs
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "OAuth Configuration:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Add this to Google OAuth Console:"
echo "  https://${CODESPACE_NAME}-8001.preview.app.github.dev/api/oauth/google/callback"
echo ""

# Quick commands
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Quick Commands:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  View backend logs:   tail -f /tmp/backend.log"
echo "  View frontend logs:  tail -f /tmp/frontend.log"
echo "  Restart backend:     kill \$(cat /tmp/backend.pid) && cd /app/backend && source venv/bin/activate && nohup python server.py > /tmp/backend.log 2>&1 & echo \$! > /tmp/backend.pid"
echo "  Restart frontend:    kill \$(cat /tmp/frontend.pid) && cd /app/frontend && nohup yarn start > /tmp/frontend.log 2>&1 & echo \$! > /tmp/frontend.pid"
echo ""
echo "╚════════════════════════════════════════════════════════════╝"
