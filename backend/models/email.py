from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Literal
from datetime import datetime, timezone
import uuid

class Email(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    email_account_id: str
    
    # Email fields
    message_id: str  # Provider's message ID
    thread_id: Optional[str] = None
    from_email: str
    to_email: List[str]
    cc: Optional[List[str]] = None
    bcc: Optional[List[str]] = None
    subject: str
    body: str
    html_body: Optional[str] = None
    
    # Metadata
    received_at: str
    direction: Literal['inbound', 'outbound'] = 'inbound'
    
    # AI Processing
    processed: bool = False
    intent_detected: Optional[str] = None
    intent_confidence: Optional[float] = None
    meeting_detected: bool = False
    meeting_confidence: Optional[float] = None
    
    # Draft & Response
    draft_generated: bool = False
    draft_content: Optional[str] = None
    draft_validated: bool = False
    validation_issues: Optional[List[str]] = None
    
    # Status
    status: Literal['pending', 'processed', 'draft_ready', 'sent', 'escalated'] = 'pending'
    replied: bool = False
    reply_sent_at: Optional[str] = None
    
    # Follow-up
    requires_follow_up: bool = False
    follow_up_scheduled: bool = False
    
    # Token tracking
    tokens_used: int = 0
    
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class EmailResponse(BaseModel):
    id: str
    email_account_id: str
    from_email: str
    to_email: List[str]
    subject: str
    body: str
    received_at: str
    direction: str
    processed: bool
    intent_detected: Optional[str]
    meeting_detected: bool
    draft_generated: bool
    draft_content: Optional[str]
    status: str
    replied: bool
    created_at: str

class EmailSend(BaseModel):
    email_account_id: str
    to_email: List[str]
    subject: str
    body: str
    cc: Optional[List[str]] = None
    bcc: Optional[List[str]] = None
