from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Literal
from datetime import datetime, timezone
import uuid

class FollowUp(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    email_id: str
    email_account_id: str
    
    # Schedule
    scheduled_at: str
    sent_at: Optional[str] = None
    
    # Content
    subject: str
    body: str
    
    # Status
    status: Literal['pending', 'sent', 'cancelled', 'responded'] = 'pending'
    
    # Detection
    response_detected: bool = False
    response_detected_at: Optional[str] = None
    
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class FollowUpCreate(BaseModel):
    email_id: str
    scheduled_at: str
    subject: str
    body: str

class FollowUpResponse(BaseModel):
    id: str
    email_id: str
    scheduled_at: str
    sent_at: Optional[str]
    subject: str
    status: str
    response_detected: bool
    created_at: str
