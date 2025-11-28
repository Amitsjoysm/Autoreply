# Production Readiness Checklist
## AI Email Assistant - Comprehensive Pre-Deployment Validation

**Last Updated**: November 28, 2025  
**Version**: 1.0  
**Status**: Pre-Production Review Required

---

## Table of Contents
1. [Infrastructure & Deployment](#infrastructure--deployment)
2. [Security Hardening](#security-hardening)
3. [Database & Data Management](#database--data-management)
4. [API & Backend Services](#api--backend-services)
5. [Background Workers](#background-workers)
6. [Monitoring & Observability](#monitoring--observability)
7. [Error Handling & Recovery](#error-handling--recovery)
8. [Performance & Scalability](#performance--scalability)
9. [Documentation & Runbooks](#documentation--runbooks)
10. [Compliance & Legal](#compliance--legal)

---

## 1. Infrastructure & Deployment

### 1.1 Server Configuration
- [ ] **Server Specifications**
  - [ ] Minimum 4 CPU cores
  - [ ] Minimum 8GB RAM
  - [ ] Minimum 100GB SSD storage
  - [ ] Network bandwidth: 1Gbps+
  
- [ ] **Operating System**
  - [ ] Ubuntu 22.04 LTS or newer
  - [ ] Security patches applied
  - [ ] Firewall configured (ufw)
  - [ ] Auto-updates enabled for security patches

- [ ] **Docker Setup** (if containerized)
  - [ ] Docker Engine 24.0+ installed
  - [ ] Docker Compose 2.20+ installed
  - [ ] Docker daemon configured with limits
  - [ ] Log rotation configured

**Configuration Example**:
```bash
# /etc/docker/daemon.json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "storage-driver": "overlay2",
  "default-ulimits": {
    "nofile": {
      "Name": "nofile",
      "Hard": 64000,
      "Soft": 64000
    }
  }
}
```

### 1.2 Network Configuration
- [ ] **Domain & DNS**
  - [ ] Domain registered and configured
  - [ ] SSL certificate installed (Let's Encrypt or commercial)
  - [ ] DNS records properly configured (A, AAAA, CNAME)
  - [ ] CDN configured (optional but recommended)

- [ ] **Load Balancer** (for multiple instances)
  - [ ] Health check endpoint configured
  - [ ] Session persistence configured
  - [ ] SSL termination at load balancer
  - [ ] Rate limiting rules configured

- [ ] **Firewall Rules**
  - [ ] Only necessary ports open (80, 443, 22)
  - [ ] MongoDB port (27017) not exposed to internet
  - [ ] Redis port (6379) not exposed to internet
  - [ ] SSH restricted to specific IPs

**UFW Configuration**:
```bash
# Allow SSH (restrict to your IP)
sudo ufw allow from YOUR_IP to any port 22

# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Deny all other incoming
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Enable firewall
sudo ufw enable
```

### 1.3 Environment Variables
- [ ] **All Secrets in Environment**
  - [ ] No hardcoded credentials in code
  - [ ] .env file properly secured (600 permissions)
  - [ ] Secrets managed via vault (HashiCorp, AWS Secrets Manager)
  - [ ] Environment-specific configs (.env.production, .env.staging)

- [ ] **Required Variables Set**
  ```bash
  # Database
  MONGO_URL=mongodb://localhost:27017
  DB_NAME=email_assistant_db
  
  # Redis
  REDIS_URL=redis://localhost:6379/0
  
  # JWT
  JWT_SECRET=<strong-random-secret-64-chars>
  
  # OAuth
  GOOGLE_CLIENT_ID=<from-google-console>
  GOOGLE_CLIENT_SECRET=<from-google-console>
  GOOGLE_REDIRECT_URI=https://yourdomain.com/api/oauth/google/callback
  
  # AI APIs
  GROQ_API_KEY=<your-groq-key>
  EMERGENT_LLM_KEY=<your-emergent-key>
  
  # Encryption
  ENCRYPTION_KEY=<32-byte-key-for-token-encryption>
  
  # App Config
  APP_URL=https://yourdomain.com
  ENVIRONMENT=production
  ```

- [ ] **Security Validation**
  ```bash
  # Check for weak secrets
  if [ ${#JWT_SECRET} -lt 32 ]; then
    echo "ERROR: JWT_SECRET must be at least 32 characters"
    exit 1
  fi
  
  # Check for default values
  if grep -q "your-secret-key" .env; then
    echo "ERROR: Default secrets detected in .env"
    exit 1
  fi
  ```

### 1.4 Deployment Strategy
- [ ] **Blue-Green Deployment Setup**
  - [ ] Two identical production environments
  - [ ] Instant rollback capability
  - [ ] Traffic switch mechanism
  - [ ] Health check before switching

- [ ] **Rolling Deployment** (alternative)
  - [ ] Deploy to one instance at a time
  - [ ] Health check after each deployment
  - [ ] Automatic rollback on failure

- [ ] **Backup Before Deployment**
  - [ ] Database backup taken
  - [ ] Configuration files backed up
  - [ ] Rollback plan documented

**Deployment Script**:
```bash
#!/bin/bash
# deploy.sh

set -e  # Exit on error

echo "🚀 Starting deployment..."

# 1. Backup database
echo "📦 Creating database backup..."
mongodump --uri="$MONGO_URL" --out="/backups/pre-deploy-$(date +%Y%m%d_%H%M%S)"

# 2. Pull latest code
echo "📥 Pulling latest code..."
git pull origin main

# 3. Install dependencies
echo "📚 Installing dependencies..."
cd backend && pip install -r requirements.txt
cd ../frontend && yarn install

# 4. Run database migrations (if any)
echo "🔄 Running migrations..."
# python backend/migrate.py

# 5. Build frontend
echo "🏗️ Building frontend..."
cd frontend && yarn build

# 6. Restart services
echo "♻️ Restarting services..."
sudo supervisorctl restart all

# 7. Wait for services to be ready
echo "⏳ Waiting for services..."
sleep 10

# 8. Health check
echo "🏥 Running health check..."
HEALTH=$(curl -s http://localhost:8001/api/health | jq -r '.status')
if [ "$HEALTH" != "healthy" ]; then
  echo "❌ Health check failed! Rolling back..."
  git checkout HEAD~1
  sudo supervisorctl restart all
  exit 1
fi

echo "✅ Deployment successful!"
```

### 1.5 High Availability
- [ ] **Multiple Instances**
  - [ ] At least 2 backend instances
  - [ ] Load balanced traffic
  - [ ] Shared session storage (Redis)

- [ ] **Database Replication**
  - [ ] MongoDB replica set (minimum 3 nodes)
  - [ ] Automatic failover configured
  - [ ] Read replicas for scaling

- [ ] **Redis High Availability**
  - [ ] Redis Sentinel or Cluster mode
  - [ ] Automatic failover
  - [ ] Persistence enabled (AOF + RDB)

---

## 2. Security Hardening

### 2.1 Authentication & Authorization
- [ ] **JWT Token Security**
  - [ ] Strong secret (64+ characters)
  - [ ] Appropriate expiration time (7 days max)
  - [ ] Refresh token mechanism
  - [ ] Token revocation capability

```python
# backend/config.py - Secure JWT Configuration
class Config:
    JWT_SECRET = os.environ.get('JWT_SECRET')  # Must be 64+ chars
    JWT_ALGORITHM = 'HS256'
    JWT_EXPIRATION_HOURS = 24 * 7  # 7 days
    JWT_REFRESH_EXPIRATION_DAYS = 30  # 30 days
    
    @staticmethod
    def validate_jwt_secret():
        if not Config.JWT_SECRET or len(Config.JWT_SECRET) < 64:
            raise ValueError("JWT_SECRET must be at least 64 characters")
        if Config.JWT_SECRET == "your-secret-key-change-in-production":
            raise ValueError("JWT_SECRET must be changed from default")
```

- [ ] **Password Security**
  - [ ] Bcrypt with cost factor 12+
  - [ ] Password strength requirements enforced
  - [ ] Password reset mechanism secure
  - [ ] Account lockout after failed attempts

```python
# Secure password hashing
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # Cost factor
)

# Password validation
def validate_password_strength(password: str) -> tuple[bool, str]:
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not any(c.isupper() for c in password):
        return False, "Password must contain uppercase letter"
    if not any(c.islower() for c in password):
        return False, "Password must contain lowercase letter"
    if not any(c.isdigit() for c in password):
        return False, "Password must contain number"
    if not any(c in "!@#$%^&*" for c in password):
        return False, "Password must contain special character"
    return True, ""
```

- [ ] **OAuth Token Security**
  - [ ] Tokens encrypted at rest
  - [ ] Automatic token refresh
  - [ ] Token expiry handling
  - [ ] Scope validation

```python
# Encrypt OAuth tokens before storing
from cryptography.fernet import Fernet
import base64

class TokenEncryption:
    def __init__(self):
        key = os.environ.get('ENCRYPTION_KEY', '').encode()
        if len(key) != 32:
            raise ValueError("ENCRYPTION_KEY must be exactly 32 bytes")
        self.cipher = Fernet(base64.urlsafe_b64encode(key))
    
    def encrypt_token(self, token: str) -> str:
        return self.cipher.encrypt(token.encode()).decode()
    
    def decrypt_token(self, encrypted_token: str) -> str:
        return self.cipher.decrypt(encrypted_token.encode()).decode()

# Usage
token_enc = TokenEncryption()
encrypted = token_enc.encrypt_token(access_token)

# Store encrypted token in database
await db.email_accounts.update_one(
    {"id": account_id},
    {"$set": {
        "access_token_encrypted": encrypted,
        "is_encrypted": True
    }}
)
```

### 2.2 API Security
- [ ] **Rate Limiting**
  - [ ] Per-user rate limits
  - [ ] Per-IP rate limits
  - [ ] Endpoint-specific limits
  - [ ] Rate limit headers exposed

```python
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request, HTTPException

limiter = Limiter(key_func=get_remote_address)

# Global rate limit
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # 1000 requests per hour per IP
    # Implementation here
    response = await call_next(request)
    return response

# Endpoint-specific limits
@app.post("/api/auth/login")
@limiter.limit("5/minute")  # Only 5 login attempts per minute
async def login(request: Request, credentials: LoginRequest):
    pass

@app.post("/api/emails/send")
@limiter.limit("100/hour")  # 100 emails per hour
async def send_email(request: Request, email: EmailSend):
    pass
```

- [ ] **CORS Configuration**
  - [ ] Specific origins whitelisted (no wildcard in production)
  - [ ] Credentials allowed only for trusted origins
  - [ ] Appropriate headers configured

```python
from fastapi.middleware.cors import CORSMiddleware

# PRODUCTION CORS - Strict
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yourdomain.com",
        "https://app.yourdomain.com"
    ],  # NO "*" in production!
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
    max_age=3600
)
```

- [ ] **Input Validation**
  - [ ] All inputs validated with Pydantic
  - [ ] SQL injection prevention (using parameterized queries)
  - [ ] XSS prevention (HTML sanitization)
  - [ ] File upload validation

```python
from pydantic import BaseModel, validator, EmailStr
from typing import Optional

class EmailSendRequest(BaseModel):
    to_email: EmailStr  # Validates email format
    subject: str
    body: str
    
    @validator('subject')
    def subject_length(cls, v):
        if len(v) > 200:
            raise ValueError('Subject too long')
        return v
    
    @validator('body')
    def sanitize_body(cls, v):
        # Remove potentially dangerous HTML
        import bleach
        allowed_tags = ['p', 'br', 'strong', 'em', 'ul', 'li']
        return bleach.clean(v, tags=allowed_tags, strip=True)
```

### 2.3 Data Protection
- [ ] **Encryption at Rest**
  - [ ] Database encryption enabled
  - [ ] File storage encrypted
  - [ ] Backup encryption enabled
  - [ ] Encryption keys rotated regularly

- [ ] **Encryption in Transit**
  - [ ] HTTPS enforced (no HTTP)
  - [ ] TLS 1.2+ only
  - [ ] HSTS header enabled
  - [ ] Certificate pinning (for mobile apps)

```python
# Force HTTPS in production
from fastapi import Request, HTTPException

@app.middleware("http")
async def force_https(request: Request, call_next):
    if request.url.scheme == "http" and os.getenv("ENVIRONMENT") == "production":
        https_url = str(request.url).replace("http://", "https://", 1)
        return RedirectResponse(https_url, status_code=301)
    
    response = await call_next(request)
    
    # Add security headers
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    
    return response
```

- [ ] **PII Protection**
  - [ ] Email addresses masked in logs
  - [ ] Sensitive data not logged
  - [ ] Database fields encrypted where needed
  - [ ] Data minimization principle applied

```python
import re

def mask_email(email: str) -> str:
    """Mask email for logging: user@example.com -> u***@e*****e.com"""
    if not email or '@' not in email:
        return "***"
    
    local, domain = email.split('@')
    domain_parts = domain.split('.')
    
    masked_local = local[0] + "***" if len(local) > 1 else "***"
    masked_domain = domain_parts[0][0] + "*****" + domain_parts[0][-1] if len(domain_parts[0]) > 2 else "***"
    masked_tld = domain_parts[-1] if len(domain_parts) > 1 else ""
    
    return f"{masked_local}@{masked_domain}.{masked_tld}"

def mask_sensitive_data(data: dict) -> dict:
    """Recursively mask sensitive fields in dict"""
    sensitive_fields = ['password', 'token', 'secret', 'api_key', 'access_token', 'refresh_token']
    
    masked = data.copy()
    for key, value in masked.items():
        if any(field in key.lower() for field in sensitive_fields):
            masked[key] = "***REDACTED***"
        elif isinstance(value, dict):
            masked[key] = mask_sensitive_data(value)
        elif key.lower() == 'email' and isinstance(value, str):
            masked[key] = mask_email(value)
    
    return masked

# Usage in logging
logger.info(f"Processing email", extra=mask_sensitive_data({
    "email": email.from_email,
    "user_id": user_id
}))
```

### 2.4 Access Control
- [ ] **Role-Based Access Control (RBAC)**
  - [ ] User roles defined (admin, user, viewer)
  - [ ] Permissions mapped to roles
  - [ ] Endpoint access controlled by role
  - [ ] Resource ownership verified

```python
from enum import Enum
from functools import wraps

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"

# Permission decorator
def require_role(*allowed_roles: UserRole):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: User = Depends(get_current_user), **kwargs):
            if current_user.role not in allowed_roles:
                raise HTTPException(
                    status_code=403,
                    detail=f"Permission denied. Required roles: {allowed_roles}"
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

# Usage
@app.delete("/api/users/{user_id}")
@require_role(UserRole.ADMIN)
async def delete_user(user_id: str, current_user: User = Depends(get_current_user)):
    # Only admins can delete users
    pass

@app.get("/api/emails")
@require_role(UserRole.ADMIN, UserRole.USER)
async def get_emails(current_user: User = Depends(get_current_user)):
    # Admins and users can view emails, but not viewers
    pass
```

- [ ] **Resource Ownership**
  - [ ] Users can only access their own data
  - [ ] Tenant isolation enforced
  - [ ] Cross-user access prevented

```python
async def verify_resource_ownership(
    resource_id: str,
    resource_type: str,
    user_id: str,
    db
) -> bool:
    """Verify user owns the resource"""
    collection = getattr(db, resource_type)
    resource = await collection.find_one({"id": resource_id})
    
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    if resource.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return True

# Usage
@app.get("/api/emails/{email_id}")
async def get_email(
    email_id: str,
    current_user: User = Depends(get_current_user)
):
    await verify_resource_ownership(email_id, "emails", current_user.id, db)
    # Proceed with fetching email
```

### 2.5 Security Monitoring
- [ ] **Audit Logging**
  - [ ] All authentication attempts logged
  - [ ] All data access logged
  - [ ] All configuration changes logged
  - [ ] Logs immutable and tamper-proof

```python
async def audit_log(
    user_id: str,
    action: str,
    resource_type: str,
    resource_id: str,
    details: dict,
    ip_address: str,
    user_agent: str
):
    """Create immutable audit log entry"""
    entry = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_id": user_id,
        "action": action,  # create, read, update, delete, login, logout
        "resource_type": resource_type,
        "resource_id": resource_id,
        "details": details,
        "ip_address": ip_address,
        "user_agent": user_agent,
        "hash": ""  # Computed hash for integrity
    }
    
    # Compute hash for tamper detection
    import hashlib
    hash_input = f"{entry['timestamp']}{entry['user_id']}{entry['action']}{entry['resource_id']}"
    entry["hash"] = hashlib.sha256(hash_input.encode()).hexdigest()
    
    await db.audit_logs.insert_one(entry)
    
    # Also log to separate audit system (immutable storage)
    # await send_to_audit_system(entry)
```

- [ ] **Intrusion Detection**
  - [ ] Failed login attempt monitoring
  - [ ] Unusual access pattern detection
  - [ ] API abuse detection
  - [ ] Automated blocking of suspicious IPs

```python
class SecurityMonitor:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.failed_login_threshold = 5
        self.lockout_duration = 900  # 15 minutes
    
    async def record_failed_login(self, identifier: str):
        """Record failed login attempt"""
        key = f"failed_login:{identifier}"
        count = await self.redis.incr(key)
        await self.redis.expire(key, 300)  # 5 minutes window
        
        if count >= self.failed_login_threshold:
            await self.lockout_account(identifier)
            await self.send_alert(f"Account locked: {identifier}")
    
    async def lockout_account(self, identifier: str):
        """Temporarily lock account"""
        key = f"lockout:{identifier}"
        await self.redis.setex(key, self.lockout_duration, "locked")
    
    async def is_locked_out(self, identifier: str) -> bool:
        """Check if account is locked out"""
        key = f"lockout:{identifier}"
        return await self.redis.exists(key)
    
    async def detect_anomalous_access(self, user_id: str, ip_address: str):
        """Detect unusual access patterns"""
        # Check if IP is from unusual location
        # Check if access time is unusual
        # Check if access frequency is high
        pass
```

---

## 3. Database & Data Management

### 3.1 MongoDB Configuration
- [ ] **Performance Tuning**
  - [ ] Indexes created on all query fields
  - [ ] Connection pooling configured
  - [ ] Query timeout set
  - [ ] Slow query logging enabled

```javascript
// Create indexes for performance
// Run this script: mongo email_assistant_db < create_indexes.js

// Emails collection
db.emails.createIndex(
    { "user_id": 1, "processed": 1 },
    { name: "user_processed_idx" }
);
db.emails.createIndex(
    { "email_account_id": 1, "message_id": 1 },
    { unique: true, name: "unique_message_idx" }
);
db.emails.createIndex(
    { "thread_id": 1, "received_at": -1 },
    { name: "thread_chronological_idx" }
);
db.emails.createIndex(
    { "status": 1, "updated_at": -1 },
    { name: "status_updated_idx" }
);
db.emails.createIndex(
    { "intent_detected": 1 },
    { name: "intent_idx" }
);

// Follow-ups collection
db.follow_ups.createIndex(
    { "status": 1, "scheduled_at": 1 },
    { name: "status_scheduled_idx" }
);
db.follow_ups.createIndex(
    { "thread_id": 1 },
    { name: "thread_idx" }
);

// Calendar events
db.calendar_events.createIndex(
    { "user_id": 1, "start_time": 1 },
    { name: "user_start_idx" }
);
db.calendar_events.createIndex(
    { "start_time": 1, "reminder_sent": 1 },
    { name: "reminder_idx" }
);

// Intents
db.intents.createIndex(
    { "user_id": 1, "is_active": 1, "priority": -1 },
    { name: "user_active_priority_idx" }
);

// Inbound leads
db.inbound_leads.createIndex(
    { "user_id": 1, "lead_email": 1 },
    { name: "user_email_idx" }
);
db.inbound_leads.createIndex(
    { "user_id": 1, "stage": 1, "priority": 1 },
    { name: "user_stage_priority_idx" }
);

// Email accounts
db.email_accounts.createIndex(
    { "user_id": 1, "is_active": 1 },
    { name: "user_active_idx" }
);
```

```python
# Python: MongoDB connection with pooling
from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient(
    config.MONGO_URL,
    maxPoolSize=50,  # Maximum connections in pool
    minPoolSize=10,  # Minimum connections in pool
    maxIdleTimeMS=45000,  # Close idle connections after 45s
    serverSelectionTimeoutMS=5000,  # Timeout for server selection
    connectTimeoutMS=10000,  # Timeout for initial connection
    socketTimeoutMS=45000,  # Timeout for socket operations
    retryWrites=True,  # Retry writes on network errors
    retryReads=True  # Retry reads on network errors
)

db = client[config.DB_NAME]

# Enable slow query logging
db.command({
    "profile": 1,  # Log slow queries
    "slowms": 100  # Queries slower than 100ms
})
```

- [ ] **Backup Strategy**
  - [ ] Automated daily backups
  - [ ] Point-in-time recovery enabled
  - [ ] Backups tested regularly
  - [ ] Backups stored off-site

```bash
#!/bin/bash
# backup_mongodb.sh - Automated MongoDB Backup

BACKUP_DIR="/backups/mongodb"
RETENTION_DAYS=30
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
S3_BUCKET="s3://your-backup-bucket/mongodb"

echo "Starting MongoDB backup at $TIMESTAMP"

# Create backup directory
mkdir -p $BACKUP_DIR/$TIMESTAMP

# Dump database
mongodump \
    --uri="$MONGO_URL" \
    --out="$BACKUP_DIR/$TIMESTAMP" \
    --gzip \
    --numParallelCollections=4

# Verify backup
if [ $? -eq 0 ]; then
    echo "✅ Backup successful"
    
    # Compress
    tar -czf "$BACKUP_DIR/${TIMESTAMP}.tar.gz" -C "$BACKUP_DIR" "$TIMESTAMP"
    rm -rf "$BACKUP_DIR/$TIMESTAMP"
    
    # Upload to S3
    aws s3 cp "$BACKUP_DIR/${TIMESTAMP}.tar.gz" "$S3_BUCKET/" --storage-class GLACIER
    
    # Verify upload
    if [ $? -eq 0 ]; then
        echo "✅ Backup uploaded to S3"
        
        # Remove local backup (keep S3 only)
        rm "$BACKUP_DIR/${TIMESTAMP}.tar.gz"
    else
        echo "❌ S3 upload failed, keeping local backup"
    fi
else
    echo "❌ Backup failed"
    exit 1
fi

# Clean old backups (local)
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

# Clean old backups (S3 - older than retention period)
# Note: Use S3 lifecycle policies for this

echo "Backup completed"

# Crontab entry:
# 0 2 * * * /usr/local/bin/backup_mongodb.sh >> /var/log/mongodb_backup.log 2>&1
```

### 3.2 Data Integrity
- [ ] **Data Validation**
  - [ ] Schema validation enabled
  - [ ] Required fields enforced
  - [ ] Data types validated
  - [ ] Constraints enforced

```javascript
// MongoDB schema validation
db.createCollection("emails", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["id", "user_id", "from_email", "subject", "received_at"],
            properties: {
                id: {
                    bsonType: "string",
                    description: "must be a string and is required"
                },
                user_id: {
                    bsonType: "string",
                    description: "must be a string and is required"
                },
                from_email: {
                    bsonType: "string",
                    pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
                    description: "must be a valid email and is required"
                },
                status: {
                    enum: ["received", "classifying", "drafting", "validating", "draft_ready", "sending", "sent", "error", "escalated"],
                    description: "must be one of the enum values"
                }
            }
        }
    }
});
```

- [ ] **Data Cleanup**
  - [ ] Orphaned records cleaned up
  - [ ] Expired data deleted
  - [ ] Archive strategy implemented
  - [ ] Retention policy enforced

```python
async def cleanup_orphaned_data():
    """Clean up orphaned records"""
    # Delete follow-ups for deleted emails
    orphaned_followups = await db.follow_ups.delete_many({
        "email_id": {"$nin": await db.emails.distinct("id")}
    })
    logger.info(f"Deleted {orphaned_followups.deleted_count} orphaned follow-ups")
    
    # Delete calendar events for deleted users
    orphaned_events = await db.calendar_events.delete_many({
        "user_id": {"$nin": await db.users.distinct("id")}
    })
    logger.info(f"Deleted {orphaned_events.deleted_count} orphaned events")

async def archive_old_data():
    """Archive data older than retention period"""
    retention_days = 90
    cutoff_date = (datetime.now(timezone.utc) - timedelta(days=retention_days)).isoformat()
    
    # Find old emails
    old_emails = await db.emails.find({
        "received_at": {"$lt": cutoff_date},
        "archived": {"$ne": True}
    }).to_list(1000)
    
    # Archive to cold storage
    for email in old_emails:
        # Upload to S3 Glacier or similar
        await archive_to_cold_storage(email)
        
        # Mark as archived
        await db.emails.update_one(
            {"id": email['id']},
            {"$set": {"archived": True, "archived_at": datetime.now(timezone.utc).isoformat()}}
        )
    
    logger.info(f"Archived {len(old_emails)} old emails")

# Run daily
# 0 3 * * * python cleanup_script.py
```

### 3.3 Redis Configuration
- [ ] **Persistence**
  - [ ] AOF enabled (appendonly yes)
  - [ ] RDB snapshots configured
  - [ ] fsync policy set (everysec)
  
```bash
# /etc/redis/redis.conf

# Persistence
appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec

# RDB Snapshots
save 900 1      # Save if 1 key changed in 900 seconds
save 300 10     # Save if 10 keys changed in 300 seconds
save 60 10000   # Save if 10000 keys changed in 60 seconds

# Memory management
maxmemory 2gb
maxmemory-policy allkeys-lru

# Security
requirepass YOUR_STRONG_PASSWORD
bind 127.0.0.1
protected-mode yes
```

---

## 4. API & Backend Services

### 4.1 API Documentation
- [ ] **OpenAPI/Swagger**
  - [ ] All endpoints documented
  - [ ] Request/response schemas defined
  - [ ] Authentication documented
  - [ ] Examples provided

```python
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

app = FastAPI(
    title="AI Email Assistant API",
    description="Comprehensive email automation with AI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="AI Email Assistant API",
        version="1.0.0",
        description="Production API for AI-powered email management",
        routes=app.routes,
    )
    
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

### 4.2 Error Handling
- [ ] **Standardized Error Responses**
  - [ ] Consistent error format
  - [ ] Error codes defined
  - [ ] Helpful error messages
  - [ ] No sensitive info in errors

```python
from fastapi import HTTPException
from pydantic import BaseModel

class ErrorResponse(BaseModel):
    error_code: str
    message: str
    details: dict = {}
    timestamp: str
    request_id: str

class APIError(HTTPException):
    def __init__(self, status_code: int, error_code: str, message: str, details: dict = {}):
        self.status_code = status_code
        self.error_code = error_code
        self.message = message
        self.details = details
        super().__init__(status_code=status_code, detail=message)

# Error handler
@app.exception_handler(APIError)
async def api_error_handler(request: Request, exc: APIError):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error_code=exc.error_code,
            message=exc.message,
            details=exc.details,
            timestamp=datetime.now(timezone.utc).isoformat(),
            request_id=request.headers.get("X-Request-ID", "unknown")
        ).dict()
    )

# Usage
@app.post("/api/emails/send")
async def send_email(email: EmailSend):
    if not email.to_email:
        raise APIError(
            status_code=400,
            error_code="INVALID_EMAIL",
            message="Recipient email is required",
            details={"field": "to_email"}
        )
```

### 4.3 Request/Response Handling
- [ ] **Request ID Tracking**
  - [ ] Unique ID for each request
  - [ ] ID in all logs
  - [ ] ID in response headers

```python
import uuid

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request.state.request_id = request_id
    
    # Add to logging context
    with logger.contextualize(request_id=request_id):
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
```

- [ ] **Response Compression**
  - [ ] Gzip enabled
  - [ ] Minimum size threshold
  - [ ] Content types configured

```python
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)  # 1KB minimum
```

### 4.4 Performance
- [ ] **Response Caching**
  - [ ] Cache headers set
  - [ ] ETag support
  - [ ] Redis caching for expensive queries

```python
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

# Initialize cache
@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

# Cache expensive endpoint
@app.get("/api/intents")
@cache(expire=300)  # Cache for 5 minutes
async def get_intents(user_id: str = Depends(get_current_user)):
    return await db.intents.find({"user_id": user_id}).to_list(100)
```

- [ ] **Query Optimization**
  - [ ] N+1 queries eliminated
  - [ ] Projection used (select only needed fields)
  - [ ] Pagination implemented

```python
@app.get("/api/emails")
async def get_emails(
    page: int = 1,
    limit: int = 50,
    user_id: str = Depends(get_current_user)
):
    # Pagination
    skip = (page - 1) * limit
    
    # Projection - only select needed fields
    cursor = db.emails.find(
        {"user_id": user_id},
        {
            "id": 1,
            "from_email": 1,
            "subject": 1,
            "received_at": 1,
            "status": 1,
            "_id": 0
        }
    ).sort("received_at", -1).skip(skip).limit(limit)
    
    emails = await cursor.to_list(limit)
    
    # Get total count for pagination
    total = await db.emails.count_documents({"user_id": user_id})
    
    return {
        "emails": emails,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit
        }
    }
```

---

## 5. Background Workers

### 5.1 Worker Reliability
- [ ] **Process Management**
  - [ ] Supervisor configured
  - [ ] Auto-restart on crash
  - [ ] Resource limits set
  - [ ] Log rotation configured

```ini
# /etc/supervisor/conf.d/email_worker.conf

[program:email_worker]
command=/root/.venv/bin/python /app/backend/run_email_worker.py
directory=/app/backend
user=root
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/email_worker.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=10
stderr_logfile=/var/log/email_worker_error.log
stopwaitsecs=30
stopsignal=TERM
killasgroup=true
stopasgroup=true

# Resource limits
numprocs=1
priority=999
startsecs=10
startretries=3

# Environment
environment=PYTHONUNBUFFERED=1
```

- [ ] **Health Monitoring**
  - [ ] Heartbeat mechanism
  - [ ] Stuck detection
  - [ ] Automatic recovery
  - [ ] Alerting on failure

```python
import signal
import sys
from datetime import datetime, timezone

class WorkerHealthCheck:
    def __init__(self, health_file="/tmp/worker_health.txt"):
        self.health_file = health_file
        self.last_heartbeat = datetime.now(timezone.utc)
    
    def heartbeat(self):
        """Update heartbeat"""
        self.last_heartbeat = datetime.now(timezone.utc)
        with open(self.health_file, 'w') as f:
            f.write(f"{self.last_heartbeat.isoformat()}\n")
    
    def is_healthy(self) -> bool:
        """Check if worker is healthy"""
        age = (datetime.now(timezone.utc) - self.last_heartbeat).seconds
        return age < 300  # Consider unhealthy if no heartbeat for 5 minutes
    
    async def recovery_check(self):
        """Check health and recover if needed"""
        if not self.is_healthy():
            logger.error("Worker appears stuck! Attempting recovery...")
            await self.attempt_recovery()
    
    async def attempt_recovery(self):
        """Attempt to recover from stuck state"""
        # Cancel stuck tasks
        # Clear queues
        # Restart connections
        # If all fails, exit (supervisor will restart)
        logger.critical("Recovery failed, exiting for supervisor restart")
        sys.exit(1)

# Usage in worker
health = WorkerHealthCheck()

async def run_worker():
    while True:
        try:
            # Do work
            await poll_all_accounts()
            
            # Update heartbeat
            health.heartbeat()
            
            # Check health
            await health.recovery_check()
            
        except Exception as e:
            logger.error(f"Worker error: {e}")
            await asyncio.sleep(5)

# External health check script
#!/bin/bash
# check_worker_health.sh

HEALTH_FILE="/tmp/worker_health.txt"
MAX_AGE=300  # 5 minutes

if [ ! -f "$HEALTH_FILE" ]; then
    echo "❌ Health file not found"
    supervisorctl restart email_worker
    exit 1
fi

LAST_HEARTBEAT=$(cat "$HEALTH_FILE")
CURRENT_TIME=$(date +%s)
HEARTBEAT_TIME=$(date -d "$LAST_HEARTBEAT" +%s)
AGE=$((CURRENT_TIME - HEARTBEAT_TIME))

if [ $AGE -gt $MAX_AGE ]; then
    echo "❌ Worker stuck (no heartbeat for ${AGE}s)"
    supervisorctl restart email_worker
    exit 1
else
    echo "✅ Worker healthy (last heartbeat ${AGE}s ago)"
    exit 0
fi

# Run every minute
# * * * * * /usr/local/bin/check_worker_health.sh >> /var/log/worker_health_check.log 2>&1
```

### 5.2 Queue Management
- [ ] **Task Queue**
  - [ ] Redis queue for tasks
  - [ ] Priority queue support
  - [ ] Task retry mechanism
  - [ ] Dead letter queue

```python
from rq import Queue, Worker
from redis import Redis

redis_conn = Redis.from_url(config.REDIS_URL)
task_queue = Queue('email_processing', connection=redis_conn)

# Enqueue task
job = task_queue.enqueue(
    process_email,
    email_id,
    retry=Retry(max=3, interval=[10, 30, 60]),  # Retry with backoff
    job_timeout='5m',
    result_ttl=3600
)

# Priority queue
high_priority_queue = Queue('high_priority', connection=redis_conn)
high_priority_queue.enqueue(process_urgent_email, email_id)
```

---

This is a comprehensive Production Readiness Checklist. Due to length, I'll create additional files for continued sections.

**CHECKLIST STATUS: 60% Complete (Sections 1-5)**

Next sections to add:
- Section 6: Monitoring & Observability
- Section 7: Error Handling & Recovery
- Section 8: Performance & Scalability
- Section 9: Documentation & Runbooks
- Section 10: Compliance & Legal

Would you like me to continue with the remaining sections?
