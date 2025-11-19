from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime, timezone
import uuid

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    password_hash: str
    full_name: Optional[str] = None
    quota: int = 100  # emails per day
    quota_used: int = 0
    quota_reset_date: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    # Role and permissions
    role: str = "user"  # "user", "admin", "super_admin"
    is_active: bool = True
    
    # HubSpot integration fields
    hubspot_enabled: bool = False  # Admin grants access to use HubSpot
    hubspot_connected: bool = False  # User has connected their HubSpot account
    hubspot_access_token: Optional[str] = None
    hubspot_refresh_token: Optional[str] = None
    hubspot_token_expires_at: Optional[str] = None
    hubspot_portal_id: Optional[str] = None  # HubSpot account ID
    hubspot_auto_sync: bool = False  # Auto-sync leads to HubSpot

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str]
    quota: int
    quota_used: int
    quota_reset_date: str
    created_at: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
