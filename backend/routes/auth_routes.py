from fastapi import APIRouter, Depends, HTTPException, Header
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel
from datetime import datetime, timezone

from services.auth_service import AuthService
from models.user import UserCreate, UserLogin, TokenResponse, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])

async def get_db():
    from server import db
    return db

async def get_current_user_from_token(authorization: Optional[str] = Header(None), db: AsyncIOMotorDatabase = Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    
    token = authorization.split(" ")[1]
    auth_service = AuthService(db)
    return await auth_service.get_current_user(token)

@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserCreate, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Register new user"""
    auth_service = AuthService(db)
    user = await auth_service.register(user_data)
    token = auth_service.create_access_token(user.id)
    
    return TokenResponse(
        access_token=token,
        user=auth_service.user_to_response(user)
    )

@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Login user"""
    auth_service = AuthService(db)
    token, user = await auth_service.login(credentials)
    
    return TokenResponse(
        access_token=token,
        user=auth_service.user_to_response(user)
    )

@router.get("/me", response_model=UserResponse)
async def get_profile(user = Depends(get_current_user_from_token), db: AsyncIOMotorDatabase = Depends(get_db)):
    """Get current user profile"""
    auth_service = AuthService(db)
    return auth_service.user_to_response(user)

@router.get("/quota")
async def check_quota(user = Depends(get_current_user_from_token), db: AsyncIOMotorDatabase = Depends(get_db)):
    """Check user quota"""
    auth_service = AuthService(db)
    has_quota = await auth_service.check_quota(user.id)
    
    return {
        "has_quota": has_quota,
        "quota": user.quota,
        "quota_used": user.quota_used,
        "quota_remaining": user.quota - user.quota_used
    }

class UserSettingsUpdate(BaseModel):
    """Update user settings (lead qualification & nurturing)"""
    global_lead_qualification_enabled: Optional[bool] = None
    global_lead_nurturing_enabled: Optional[bool] = None
    default_qualification_criteria_id: Optional[str] = None
    default_nurturing_config_id: Optional[str] = None

@router.put("/settings", response_model=UserResponse)
async def update_settings(
    settings: UserSettingsUpdate,
    user = Depends(get_current_user_from_token),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update user settings for lead qualification and nurturing"""
    try:
        users_collection = db['users']
        
        # Prepare update data
        update_data = {
            k: v for k, v in settings.model_dump(exclude_unset=True).items()
            if v is not None
        }
        
        if update_data:
            update_data['updated_at'] = datetime.now(timezone.utc).isoformat()
            
            await users_collection.update_one(
                {"id": user['id']},
                {"$set": update_data}
            )
        
        # Get updated user
        updated_user = await users_collection.find_one({"id": user['id']})
        
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        auth_service = AuthService(db)
        return auth_service.user_to_response(updated_user)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
