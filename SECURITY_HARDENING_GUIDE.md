# Security Hardening Guide
## AI Email Assistant - Comprehensive Security Implementation

**Classification**: CONFIDENTIAL  
**Last Updated**: November 28, 2025  
**Version**: 1.0

---

## Table of Contents
1. [Security Threat Model](#security-threat-model)
2. [Authentication & Authorization](#authentication--authorization)
3. [Data Protection](#data-protection)
4. [Network Security](#network-security)
5. [Application Security](#application-security)
6. [Third-Party Security](#third-party-security)
7. [Incident Response](#incident-response)
8. [Security Auditing](#security-auditing)

---

## 1. Security Threat Model

### 1.1 Threat Categories

#### **HIGH SEVERITY THREATS**

**T1: Unauthorized Data Access**
- **Risk**: Attacker gains access to user emails, OAuth tokens, or PII
- **Impact**: Data breach, regulatory fines, reputation damage
- **Likelihood**: MEDIUM
- **Mitigation**:
  - Strong authentication (JWT with secure secrets)
  - Encryption at rest for sensitive data
  - Strict access controls and RBAC
  - Regular security audits

**T2: Account Takeover**
- **Risk**: Attacker compromises user accounts through credential theft or brute force
- **Impact**: Unauthorized access to emails, ability to send malicious emails
- **Likelihood**: MEDIUM
- **Mitigation**:
  - Rate limiting on login endpoints
  - Account lockout after failed attempts
  - Strong password policies
  - Optional 2FA/MFA
  - Session management

**T3: API Abuse**
- **Risk**: Attacker abuses API endpoints for DDoS, data extraction, or resource exhaustion
- **Impact**: Service downtime, increased costs, data leakage
- **Likelihood**: HIGH
- **Mitigation**:
  - Comprehensive rate limiting
  - API authentication required
  - Request size limits
  - WAF (Web Application Firewall)

**T4: Injection Attacks (SQL, NoSQL, XSS)**
- **Risk**: Attacker injects malicious code through input fields
- **Impact**: Data breach, system compromise, client-side attacks
- **Likelihood**: MEDIUM
- **Mitigation**:
  - Input validation and sanitization
  - Parameterized queries
  - Output encoding
  - CSP headers

**T5: OAuth Token Compromise**
- **Risk**: OAuth tokens stolen from database or in transit
- **Impact**: Attacker can access Gmail/Outlook on behalf of users
- **Likelihood**: MEDIUM
- **Mitigation**:
  - Encrypt tokens at rest
  - HTTPS only
  - Token rotation
  - Scope limitation

#### **MEDIUM SEVERITY THREATS**

**T6: Denial of Service**
- **Risk**: Attacker overwhelms system with requests
- **Impact**: Service unavailability
- **Likelihood**: HIGH
- **Mitigation**:
  - Rate limiting
  - Load balancing
  - Auto-scaling
  - CDN

**T7: Information Disclosure**
- **Risk**: Sensitive info leaked through error messages, logs, or responses
- **Impact**: Attacker gains intel for further attacks
- **Likelihood**: MEDIUM
- **Mitigation**:
  - Generic error messages
  - PII masking in logs
  - Security headers
  - Proper exception handling

**T8: Insecure Dependencies**
- **Risk**: Vulnerable third-party libraries
- **Impact**: Various depending on vulnerability
- **Likelihood**: HIGH
- **Mitigation**:
  - Regular dependency updates
  - Vulnerability scanning
  - Dependency pinning
  - Security advisories monitoring

**T9: Privilege Escalation**
- **Risk**: User gains unauthorized elevated privileges
- **Impact**: Access to admin functions or other users' data
- **Likelihood**: LOW
- **Mitigation**:
  - Proper RBAC implementation
  - Resource ownership checks
  - Audit logging
  - Principle of least privilege

**T10: Email Spoofing/Phishing via System**
- **Risk**: Attacker uses system to send phishing emails
- **Impact**: Reputation damage, blacklisting, legal issues
- **Likelihood**: MEDIUM
- **Mitigation**:
  - SPF/DKIM/DMARC validation
  - Content filtering
  - Sending rate limits
  - Abuse detection

---

## 2. Authentication & Authorization

### 2.1 JWT Token Security

#### **Secure JWT Implementation**

```python
# backend/services/auth_service_secure.py

import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional
import secrets
import hashlib

class SecureAuthService:
    def __init__(self):
        # Validate JWT secret
        if not config.JWT_SECRET or len(config.JWT_SECRET) < 64:
            raise ValueError("JWT_SECRET must be at least 64 characters")
        
        self.secret = config.JWT_SECRET
        self.algorithm = "HS256"
        self.access_token_expire = timedelta(hours=24)
        self.refresh_token_expire = timedelta(days=30)
    
    def create_access_token(self, user_id: str, email: str, role: str) -> str:
        """Create JWT access token"""
        now = datetime.now(timezone.utc)
        
        payload = {
            "sub": user_id,  # Standard JWT claim
            "email": email,
            "role": role,
            "type": "access",
            "iat": now,  # Issued at
            "exp": now + self.access_token_expire,  # Expiration
            "jti": secrets.token_urlsafe(16)  # JWT ID for revocation
        }
        
        return jwt.encode(payload, self.secret, algorithm=self.algorithm)
    
    def create_refresh_token(self, user_id: str) -> str:
        """Create JWT refresh token"""
        now = datetime.now(timezone.utc)
        
        payload = {
            "sub": user_id,
            "type": "refresh",
            "iat": now,
            "exp": now + self.refresh_token_expire,
            "jti": secrets.token_urlsafe(16)
        }
        
        token = jwt.encode(payload, self.secret, algorithm=self.algorithm)
        
        # Store refresh token hash in database for revocation
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        await db.refresh_tokens.insert_one({
            "user_id": user_id,
            "token_hash": token_hash,
            "created_at": now.isoformat(),
            "expires_at": (now + self.refresh_token_expire).isoformat(),
            "revoked": False
        })
        
        return token
    
    async def verify_token(self, token: str, token_type: str = "access") -> dict:
        """Verify JWT token"""
        try:
            payload = jwt.decode(
                token,
                self.secret,
                algorithms=[self.algorithm],
                options={"verify_exp": True}
            )
            
            # Verify token type
            if payload.get("type") != token_type:
                raise jwt.InvalidTokenError("Invalid token type")
            
            # Check if token is revoked (for refresh tokens)
            if token_type == "refresh":
                token_hash = hashlib.sha256(token.encode()).hexdigest()
                token_doc = await db.refresh_tokens.find_one({
                    "token_hash": token_hash,
                    "revoked": False
                })
                if not token_doc:
                    raise jwt.InvalidTokenError("Token revoked or invalid")
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError as e:
            raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    
    async def revoke_token(self, token: str):
        """Revoke refresh token"""
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        await db.refresh_tokens.update_one(
            {"token_hash": token_hash},
            {"$set": {"revoked": True, "revoked_at": datetime.now(timezone.utc).isoformat()}}
        )
    
    async def revoke_all_user_tokens(self, user_id: str):
        """Revoke all refresh tokens for user (force logout)"""
        await db.refresh_tokens.update_many(
            {"user_id": user_id, "revoked": False},
            {"$set": {"revoked": True, "revoked_at": datetime.now(timezone.utc).isoformat()}}
        )
    
    async def cleanup_expired_tokens(self):
        """Clean up expired tokens (run daily)"""
        cutoff = datetime.now(timezone.utc).isoformat()
        result = await db.refresh_tokens.delete_many({
            "expires_at": {"$lt": cutoff}
        })
        logger.info(f"Cleaned up {result.deleted_count} expired tokens")
```

#### **Token Refresh Endpoint**

```python
@app.post("/api/auth/refresh")
async def refresh_token(refresh_token: str):
    """Refresh access token using refresh token"""
    auth_service = SecureAuthService()
    
    # Verify refresh token
    payload = await auth_service.verify_token(refresh_token, token_type="refresh")
    
    # Get user
    user = await db.users.find_one({"id": payload["sub"]})
    if not user or not user.get("is_active"):
        raise HTTPException(status_code=401, detail="User not found or inactive")
    
    # Create new access token
    new_access_token = auth_service.create_access_token(
        user_id=user["id"],
        email=user["email"],
        role=user["role"]
    )
    
    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }

@app.post("/api/auth/logout")
async def logout(
    refresh_token: str,
    current_user: User = Depends(get_current_user)
):
    """Logout and revoke refresh token"""
    auth_service = SecureAuthService()
    await auth_service.revoke_token(refresh_token)
    
    return {"message": "Logged out successfully"}

@app.post("/api/auth/logout-all")
async def logout_all_devices(current_user: User = Depends(get_current_user)):
    """Logout from all devices"""
    auth_service = SecureAuthService()
    await auth_service.revoke_all_user_tokens(current_user.id)
    
    return {"message": "Logged out from all devices"}
```

### 2.2 Password Security

#### **Strong Password Hashing**

```python
from passlib.context import CryptContext
from passlib.pwd import genword
import re

class PasswordService:
    def __init__(self):
        self.pwd_context = CryptContext(
            schemes=["bcrypt"],
            deprecated="auto",
            bcrypt__rounds=12,  # Cost factor (higher = more secure but slower)
            bcrypt__ident="2b"  # Use latest bcrypt version
        )
        
        # Password requirements
        self.min_length = 12
        self.require_uppercase = True
        self.require_lowercase = True
        self.require_digit = True
        self.require_special = True
        self.special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    def hash_password(self, password: str) -> str:
        """Hash password with bcrypt"""
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def validate_password_strength(self, password: str) -> tuple[bool, list[str]]:
        """Validate password meets security requirements"""
        errors = []
        
        if len(password) < self.min_length:
            errors.append(f"Password must be at least {self.min_length} characters")
        
        if self.require_uppercase and not re.search(r'[A-Z]', password):
            errors.append("Password must contain uppercase letter")
        
        if self.require_lowercase and not re.search(r'[a-z]', password):
            errors.append("Password must contain lowercase letter")
        
        if self.require_digit and not re.search(r'\d', password):
            errors.append("Password must contain digit")
        
        if self.require_special and not any(c in self.special_chars for c in password):
            errors.append(f"Password must contain special character ({self.special_chars})")
        
        # Check for common weak passwords
        common_passwords = ["password123", "admin123", "welcome123"]
        if password.lower() in common_passwords:
            errors.append("Password is too common")
        
        # Check for sequential or repeated characters
        if re.search(r'(.)\1{2,}', password):  # 3+ repeated chars
            errors.append("Password contains too many repeated characters")
        
        if re.search(r'(012|123|234|345|456|567|678|789|890|abc|bcd|cde)', password.lower()):
            errors.append("Password contains sequential characters")
        
        return len(errors) == 0, errors
    
    def generate_secure_password(self, length: int = 16) -> str:
        """Generate cryptographically secure random password"""
        return genword(
            length=length,
            charset="ascii_62",  # Letters + digits
            entropy=128
        )
    
    async def check_password_breach(self, password: str) -> bool:
        """Check if password appears in breach databases (HIBP API)"""
        import hashlib
        import httpx
        
        # Hash password with SHA-1 for HIBP API
        sha1_hash = hashlib.sha1(password.encode()).hexdigest().upper()
        prefix = sha1_hash[:5]
        suffix = sha1_hash[5:]
        
        # Query HIBP API
        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://api.pwnedpasswords.com/range/{prefix}")
            
            if response.status_code == 200:
                # Check if suffix appears in response
                hashes = response.text.splitlines()
                for hash_line in hashes:
                    hash_suffix, count = hash_line.split(':')
                    if hash_suffix == suffix:
                        return True  # Password found in breach
        
        return False  # Password not found in breach

# Usage in registration
@app.post("/api/auth/register")
async def register(credentials: RegisterRequest):
    password_service = PasswordService()
    
    # Validate password strength
    is_valid, errors = password_service.validate_password_strength(credentials.password)
    if not is_valid:
        raise HTTPException(status_code=400, detail={"errors": errors})
    
    # Check if password is breached
    if await password_service.check_password_breach(credentials.password):
        raise HTTPException(
            status_code=400,
            detail="This password has been found in data breaches. Please choose a different password."
        )
    
    # Hash password
    hashed_password = password_service.hash_password(credentials.password)
    
    # Create user
    # ...
```

### 2.3 Account Security

#### **Brute Force Protection**

```python
from datetime import datetime, timezone, timedelta
import redis

class BruteForceProtection:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.max_attempts = 5
        self.lockout_duration = 900  # 15 minutes in seconds
        self.attempt_window = 300  # 5 minutes
    
    async def record_failed_login(self, identifier: str):
        """Record failed login attempt"""
        key = f"failed_login:{identifier}"
        
        # Increment counter
        attempts = await self.redis.incr(key)
        
        # Set expiry on first attempt
        if attempts == 1:
            await self.redis.expire(key, self.attempt_window)
        
        # Check if should lock out
        if attempts >= self.max_attempts:
            await self.lockout_account(identifier)
            
            # Send alert
            await self.send_security_alert(identifier, "account_locked")
        
        return attempts
    
    async def lockout_account(self, identifier: str):
        """Lock out account temporarily"""
        key = f"lockout:{identifier}"
        await self.redis.setex(key, self.lockout_duration, "locked")
        
        # Log to audit
        await audit_log(
            user_id="system",
            action="account_lockout",
            resource_type="account",
            resource_id=identifier,
            details={"reason": "too_many_failed_attempts"},
            ip_address="system",
            user_agent="system"
        )
    
    async def is_locked_out(self, identifier: str) -> tuple[bool, int]:
        """Check if account is locked out"""
        key = f"lockout:{identifier}"
        ttl = await self.redis.ttl(key)
        
        if ttl > 0:
            return True, ttl
        return False, 0
    
    async def reset_attempts(self, identifier: str):
        """Reset failed login attempts (on successful login)"""
        key = f"failed_login:{identifier}"
        await self.redis.delete(key)
    
    async def send_security_alert(self, identifier: str, alert_type: str):
        """Send security alert to user"""
        # Implementation depends on notification system
        logger.warning(f"Security alert for {identifier}: {alert_type}")
        
        # Could send email, SMS, push notification, etc.
        pass

# Usage in login endpoint
@app.post("/api/auth/login")
async def login(credentials: LoginRequest):
    bf_protection = BruteForceProtection(redis_client)
    
    # Check if account is locked out
    is_locked, ttl = await bf_protection.is_locked_out(credentials.email)
    if is_locked:
        minutes_left = ttl // 60
        raise HTTPException(
            status_code=429,
            detail=f"Account temporarily locked due to too many failed attempts. Try again in {minutes_left} minutes."
        )
    
    # Verify credentials
    user = await db.users.find_one({"email": credentials.email})
    
    if not user:
        # Record failed attempt (even for non-existent users to prevent enumeration)
        await bf_protection.record_failed_login(credentials.email)
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    password_service = PasswordService()
    if not password_service.verify_password(credentials.password, user["hashed_password"]):
        # Record failed attempt
        attempts = await bf_protection.record_failed_login(credentials.email)
        remaining = bf_protection.max_attempts - attempts
        
        if remaining > 0:
            raise HTTPException(
                status_code=401,
                detail=f"Invalid credentials. {remaining} attempts remaining before lockout."
            )
        else:
            raise HTTPException(
                status_code=429,
                detail="Account locked due to too many failed attempts."
            )
    
    # Successful login - reset attempts
    await bf_protection.reset_attempts(credentials.email)
    
    # Generate tokens
    auth_service = SecureAuthService()
    access_token = auth_service.create_access_token(user["id"], user["email"], user["role"])
    refresh_token = await auth_service.create_refresh_token(user["id"])
    
    # Log successful login
    await audit_log(
        user_id=user["id"],
        action="login",
        resource_type="user",
        resource_id=user["id"],
        details={"method": "password"},
        ip_address=request.client.host,
        user_agent=request.headers.get("User-Agent")
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "full_name": user["full_name"]
        }
    }
```

#### **Session Management**

```python
class SessionManager:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.session_ttl = 3600 * 24 * 7  # 7 days
    
    async def create_session(self, user_id: str, ip_address: str, user_agent: str) -> str:
        """Create new session"""
        session_id = secrets.token_urlsafe(32)
        
        session_data = {
            "user_id": user_id,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_activity": datetime.now(timezone.utc).isoformat()
        }
        
        # Store in Redis
        await self.redis.setex(
            f"session:{session_id}",
            self.session_ttl,
            json.dumps(session_data)
        )
        
        # Add to user's active sessions
        await self.redis.sadd(f"user_sessions:{user_id}", session_id)
        
        return session_id
    
    async def get_session(self, session_id: str) -> Optional[dict]:
        """Get session data"""
        data = await self.redis.get(f"session:{session_id}")
        if data:
            return json.loads(data)
        return None
    
    async def update_activity(self, session_id: str):
        """Update last activity timestamp"""
        session = await self.get_session(session_id)
        if session:
            session["last_activity"] = datetime.now(timezone.utc).isoformat()
            await self.redis.setex(
                f"session:{session_id}",
                self.session_ttl,
                json.dumps(session)
            )
    
    async def invalidate_session(self, session_id: str):
        """Invalidate specific session"""
        session = await self.get_session(session_id)
        if session:
            user_id = session["user_id"]
            await self.redis.delete(f"session:{session_id}")
            await self.redis.srem(f"user_sessions:{user_id}", session_id)
    
    async def invalidate_all_user_sessions(self, user_id: str):
        """Invalidate all sessions for user"""
        session_ids = await self.redis.smembers(f"user_sessions:{user_id}")
        for session_id in session_ids:
            await self.redis.delete(f"session:{session_id}")
        await self.redis.delete(f"user_sessions:{user_id}")
    
    async def get_user_sessions(self, user_id: str) -> list:
        """Get all active sessions for user"""
        session_ids = await self.redis.smembers(f"user_sessions:{user_id}")
        sessions = []
        
        for session_id in session_ids:
            session = await self.get_session(session_id)
            if session:
                sessions.append({
                    "session_id": session_id,
                    **session
                })
        
        return sessions
```

---

## 3. Data Protection

### 3.1 Encryption at Rest

#### **OAuth Token Encryption**

```python
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import base64
import os

class DataEncryption:
    def __init__(self):
        # Derive encryption key from environment variable
        password = os.environ.get('ENCRYPTION_KEY', '').encode()
        if not password or len(password) < 32:
            raise ValueError("ENCRYPTION_KEY must be at least 32 characters")
        
        # Use PBKDF2 to derive a proper key
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'email_assistant_salt',  # Should be unique per deployment
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        self.cipher = Fernet(key)
    
    def encrypt(self, data: str) -> str:
        """Encrypt data"""
        if not data:
            return ""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt data"""
        if not encrypted_data:
            return ""
        try:
            return self.cipher.decrypt(encrypted_data.encode()).decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise ValueError("Failed to decrypt data")
    
    def encrypt_dict(self, data: dict, fields: list) -> dict:
        """Encrypt specific fields in dictionary"""
        encrypted = data.copy()
        for field in fields:
            if field in encrypted and encrypted[field]:
                encrypted[field] = self.encrypt(str(encrypted[field]))
                encrypted[f"{field}_encrypted"] = True
        return encrypted
    
    def decrypt_dict(self, data: dict, fields: list) -> dict:
        """Decrypt specific fields in dictionary"""
        decrypted = data.copy()
        for field in fields:
            if f"{field}_encrypted" in decrypted and decrypted.get(f"{field}_encrypted"):
                decrypted[field] = self.decrypt(decrypted[field])
                del decrypted[f"{field}_encrypted"]
        return decrypted

# Usage
encryption = DataEncryption()

# Encrypting OAuth tokens before storing
async def save_oauth_account(user_id: str, account_data: dict):
    """Save OAuth account with encrypted tokens"""
    
    # Encrypt sensitive fields
    encrypted_data = encryption.encrypt_dict(account_data, [
        'access_token',
        'refresh_token',
        'client_secret'
    ])
    
    encrypted_data['user_id'] = user_id
    encrypted_data['created_at'] = datetime.now(timezone.utc).isoformat()
    
    await db.email_accounts.insert_one(encrypted_data)

# Decrypting when retrieving
async def get_oauth_account(account_id: str) -> dict:
    """Get OAuth account with decrypted tokens"""
    account = await db.email_accounts.find_one({"id": account_id})
    
    if account:
        # Decrypt sensitive fields
        decrypted = encryption.decrypt_dict(account, [
            'access_token',
            'refresh_token',
            'client_secret'
        ])
        return decrypted
    
    return None
```

#### **Field-Level Encryption**

```python
# For MongoDB, use client-side field level encryption

from pymongo import MongoClient
from pymongo.encryption import ClientEncryption
from pymongo.encryption_options import AutoEncryptionOpts

# Create encryption key
def create_data_key():
    """Create master encryption key"""
    import os
    from bson.binary import Binary
    
    # Generate random 96-byte key
    local_master_key = os.urandom(96)
    
    kms_providers = {
        "local": {
            "key": local_master_key
        }
    }
    
    # In production, use AWS KMS, Azure Key Vault, or GCP KMS
    # kms_providers = {
    #     "aws": {
    #         "accessKeyId": AWS_ACCESS_KEY_ID,
    #         "secretAccessKey": AWS_SECRET_ACCESS_KEY
    #     }
    # }
    
    return kms_providers

# Configure auto-encryption
def get_encrypted_client():
    """Get MongoDB client with auto-encryption"""
    kms_providers = create_data_key()
    
    # Define schema for encrypted fields
    schema_map = {
        "email_assistant_db.email_accounts": {
            "bsonType": "object",
            "properties": {
                "access_token": {
                    "encrypt": {
                        "bsonType": "string",
                        "algorithm": "AEAD_AES_256_CBC_HMAC_SHA_512-Deterministic"
                    }
                },
                "refresh_token": {
                    "encrypt": {
                        "bsonType": "string",
                        "algorithm": "AEAD_AES_256_CBC_HMAC_SHA_512-Random"
                    }
                }
            }
        }
    }
    
    auto_encryption_opts = AutoEncryptionOpts(
        kms_providers=kms_providers,
        key_vault_namespace="encryption.__keyVault",
        schema_map=schema_map
    )
    
    client = MongoClient(
        config.MONGO_URL,
        auto_encryption_opts=auto_encryption_opts
    )
    
    return client
```

### 3.2 Data Sanitization

#### **PII Masking**

```python
import re

class PIIMasker:
    @staticmethod
    def mask_email(email: str) -> str:
        """Mask email: user@domain.com -> u***@d*****.com"""
        if not email or '@' not in email:
            return "***@***.***"
        
        local, domain = email.split('@', 1)
        domain_parts = domain.split('.')
        
        masked_local = local[0] + '***' if len(local) > 1 else '***'
        
        if len(domain_parts) >= 2:
            masked_domain = domain_parts[0][0] + '*****' if len(domain_parts[0]) > 1 else '***'
            masked_tld = domain_parts[-1]
            return f"{masked_local}@{masked_domain}.{masked_tld}"
        
        return f"{masked_local}@***"
    
    @staticmethod
    def mask_phone(phone: str) -> str:
        """Mask phone: +1234567890 -> +123***7890"""
        if not phone or len(phone) < 6:
            return "***"
        
        return phone[:3] + '***' + phone[-4:]
    
    @staticmethod
    def mask_ip(ip: str) -> str:
        """Mask IP: 192.168.1.1 -> 192.168.*.*"""
        if not ip:
            return "*.*.*.*"
        
        parts = ip.split('.')
        if len(parts) == 4:
            return f"{parts[0]}.{parts[1]}.*.*"
        return "***"
    
    @staticmethod
    def mask_credit_card(cc: str) -> str:
        """Mask credit card: 1234567890123456 -> ****-****-****-3456"""
        if not cc or len(cc) < 8:
            return "****-****-****-****"
        
        return '****-****-****-' + cc[-4:]
    
    @staticmethod
    def mask_sensitive_dict(data: dict) -> dict:
        """Recursively mask sensitive fields in dict"""
        sensitive_patterns = {
            'email': PIIMasker.mask_email,
            'phone': PIIMasker.mask_phone,
            'ip_address': PIIMasker.mask_ip,
            'ip': PIIMasker.mask_ip,
            'credit_card': PIIMasker.mask_credit_card,
            'card_number': PIIMasker.mask_credit_card,
        }
        
        secret_patterns = ['password', 'token', 'secret', 'key', 'api_key']
        
        masked = {}
        for key, value in data.items():
            lower_key = key.lower()
            
            # Check if field should be completely hidden
            if any(pattern in lower_key for pattern in secret_patterns):
                masked[key] = "***REDACTED***"
            
            # Check if field should be masked
            elif any(pattern in lower_key for pattern in sensitive_patterns.keys()):
                for pattern, mask_func in sensitive_patterns.items():
                    if pattern in lower_key and isinstance(value, str):
                        masked[key] = mask_func(value)
                        break
                else:
                    masked[key] = value
            
            # Recursively process nested dicts
            elif isinstance(value, dict):
                masked[key] = PIIMasker.mask_sensitive_dict(value)
            
            # Recursively process lists
            elif isinstance(value, list):
                masked[key] = [
                    PIIMasker.mask_sensitive_dict(item) if isinstance(item, dict) else item
                    for item in value
                ]
            
            else:
                masked[key] = value
        
        return masked

# Usage in logging
import logging

class PIIFilter(logging.Filter):
    """Logging filter to automatically mask PII"""
    
    def filter(self, record):
        # Mask PII in log message
        if hasattr(record, 'msg') and isinstance(record.msg, str):
            # Mask emails
            record.msg = re.sub(
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                lambda m: PIIMasker.mask_email(m.group(0)),
                record.msg
            )
            
            # Mask IPs
            record.msg = re.sub(
                r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
                lambda m: PIIMasker.mask_ip(m.group(0)),
                record.msg
            )
        
        # Mask PII in extra fields
        if hasattr(record, '__dict__'):
            for key in list(record.__dict__.keys()):
                if isinstance(record.__dict__[key], dict):
                    record.__dict__[key] = PIIMasker.mask_sensitive_dict(record.__dict__[key])
        
        return True

# Add filter to logger
logger = logging.getLogger()
logger.addFilter(PIIFilter())
```

---

Due to the comprehensive nature of this guide, I'll continue with additional critical sections. Would you like me to complete the Security Hardening Guide with the remaining sections (Network Security, Application Security, Incident Response, etc.)?
