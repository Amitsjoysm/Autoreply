from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Literal, Dict, Any
from datetime import datetime, timezone
import uuid

class FollowUpConfig(BaseModel):
    """Configuration for follow-up emails"""
    enabled: bool = True
    count: int = 3  # Number of follow-ups
    intervals: List[int] = [2, 4, 6]  # Days between follow-ups
    template_ids: List[str] = []  # Template IDs for each follow-up

class Campaign(BaseModel):
    """Campaign for outbound email sending"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    
    # Campaign details
    name: str
    description: Optional[str] = None
    
    # Contact selection
    contact_ids: List[str] = []  # List of contact IDs to send to
    contact_tags: List[str] = []  # Or select by tags
    list_ids: List[str] = []  # Or select by contact lists
    
    # Template selection
    initial_template_id: str  # Initial email template
    
    # Follow-up configuration
    follow_up_config: FollowUpConfig = FollowUpConfig()
    
    # Email account selection
    email_account_ids: List[str] = []  # Can use multiple accounts
    
    # Sending configuration
    daily_limit_per_account: int = 100  # User-controlled limit
    random_delay_min: int = 60  # Minimum delay in seconds
    random_delay_max: int = 300  # Maximum delay in seconds
    
    # Scheduling
    scheduled_start: Optional[str] = None  # ISO datetime
    scheduled_end: Optional[str] = None  # ISO datetime
    timezone: str = "UTC"
    
    # Status
    status: Literal["draft", "scheduled", "running", "paused", "completed", "stopped"] = "draft"
    
    # Progress tracking
    total_contacts: int = 0
    emails_sent: int = 0
    emails_pending: int = 0
    emails_failed: int = 0
    
    # Engagement metrics
    emails_opened: int = 0
    emails_replied: int = 0
    emails_bounced: int = 0
    
    # Email verification
    verify_emails: bool = False  # User can enable/disable
    
    # Control
    last_paused_at: Optional[str] = None
    last_resumed_at: Optional[str] = None
    
    # Metadata
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

class CampaignResponse(BaseModel):
    """Response model for campaign"""
    id: str
    name: str
    description: Optional[str] = None
    contact_ids: List[str]
    contact_tags: List[str]
    list_ids: List[str]
    initial_template_id: str
    follow_up_config: FollowUpConfig
    email_account_ids: List[str]
    daily_limit_per_account: int
    random_delay_min: int
    random_delay_max: int
    scheduled_start: Optional[str] = None
    scheduled_end: Optional[str] = None
    timezone: str
    status: str
    total_contacts: int
    emails_sent: int
    emails_pending: int
    emails_failed: int
    emails_opened: int
    emails_replied: int
    emails_bounced: int
    verify_emails: bool
    created_at: str
    updated_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

class CampaignCreate(BaseModel):
    """Create model for campaign"""
    name: str
    description: Optional[str] = None
    contact_ids: List[str] = []
    contact_tags: List[str] = []
    list_ids: List[str] = []
    initial_template_id: str
    follow_up_config: FollowUpConfig = FollowUpConfig()
    email_account_ids: List[str]
    daily_limit_per_account: int = 100
    random_delay_min: int = 60
    random_delay_max: int = 300
    scheduled_start: Optional[str] = None
    scheduled_end: Optional[str] = None
    timezone: str = "UTC"
    verify_emails: bool = False

class CampaignUpdate(BaseModel):
    """Update model for campaign"""
    name: Optional[str] = None
    description: Optional[str] = None
    contact_ids: Optional[List[str]] = None
    contact_tags: Optional[List[str]] = None
    list_ids: Optional[List[str]] = None
    initial_template_id: Optional[str] = None
    follow_up_config: Optional[FollowUpConfig] = None
    email_account_ids: Optional[List[str]] = None
    daily_limit_per_account: Optional[int] = None
    random_delay_min: Optional[int] = None
    random_delay_max: Optional[int] = None
    scheduled_start: Optional[str] = None
    scheduled_end: Optional[str] = None
    timezone: Optional[str] = None
    verify_emails: Optional[bool] = None
