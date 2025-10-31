from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime, timezone
import uuid

class Intent(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    name: str
    description: Optional[str] = None
    prompt: str  # Custom prompt for this intent
    keywords: List[str] = []  # Keywords to help detect this intent
    auto_send: bool = False  # Auto-send replies for this intent
    priority: int = 0  # Higher priority intents checked first
    
    is_active: bool = True
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class IntentCreate(BaseModel):
    name: str
    description: Optional[str] = None
    prompt: str
    keywords: List[str] = []
    auto_send: bool = False
    priority: int = 0

class IntentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    prompt: Optional[str] = None
    keywords: Optional[List[str]] = None
    auto_send: Optional[bool] = None
    priority: Optional[int] = None
    is_active: Optional[bool] = None

class IntentResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    prompt: str
    keywords: List[str]
    auto_send: bool
    priority: int
    is_active: bool
    created_at: str
