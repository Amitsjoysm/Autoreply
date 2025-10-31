from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import RedirectResponse
from motor.motor_asyncio import AsyncIOMotorDatabase
import uuid
import jwt
from datetime import datetime, timezone

from routes.auth_routes import get_current_user_from_token, get_db
from services.oauth_service import OAuthService
from models.email_account import EmailAccount
from models.calendar import CalendarProvider
from models.user import User
from config import config

router = APIRouter(prefix="/oauth", tags=["oauth"])

@router.get("/google/url")
async def get_google_oauth_url(
    user: User = Depends(get_current_user_from_token),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get Google OAuth URL"""
    oauth_service = OAuthService(db)
    state = str(uuid.uuid4())
    
    # Store state in DB for verification
    await db.oauth_states.insert_one({
        "state": state,
        "user_id": user.id,
        "provider": "google"
    })
    
    url = oauth_service.get_google_auth_url(state)
    return {"url": url, "state": state}

@router.get("/google/authorize")
async def google_oauth_authorize(
    request: Request,
    account_type: str = Query('email', description='email or calendar'),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Initiate Google OAuth flow - redirects to Google"""
    # Extract user from Authorization header
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    oauth_service = OAuthService(db)
    state = str(uuid.uuid4())
    
    # Store state with account_type in DB for verification
    await db.oauth_states.insert_one({
        "state": state,
        "user_id": user_id,
        "provider": "google",
        "account_type": account_type,
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    url = oauth_service.get_google_auth_url(state)
    return RedirectResponse(url=url)

@router.get("/microsoft/url")
async def get_microsoft_oauth_url(
    user: User = Depends(get_current_user_from_token),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get Microsoft OAuth URL"""
    oauth_service = OAuthService(db)
    state = str(uuid.uuid4())
    
    await db.oauth_states.insert_one({
        "state": state,
        "user_id": user.id,
        "provider": "microsoft"
    })
    
    url = oauth_service.get_microsoft_auth_url(state)
    return {"url": url, "state": state}

@router.get("/microsoft/authorize")
async def microsoft_oauth_authorize(
    request: Request,
    account_type: str = Query('email', description='email or calendar'),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Initiate Microsoft OAuth flow - redirects to Microsoft"""
    # Extract user from Authorization header
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    oauth_service = OAuthService(db)
    state = str(uuid.uuid4())
    
    # Store state with account_type in DB for verification
    await db.oauth_states.insert_one({
        "state": state,
        "user_id": user_id,
        "provider": "microsoft",
        "account_type": account_type,
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    url = oauth_service.get_microsoft_auth_url(state)
    return RedirectResponse(url=url)

@router.get("/google/callback")
async def google_oauth_callback_get(
    code: str = Query(...),
    state: str = Query(...),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Handle Google OAuth callback (GET redirect from Google)"""
    # Verify state
    state_doc = await db.oauth_states.find_one({"state": state})
    if not state_doc:
        return RedirectResponse(url=f"{config.GOOGLE_REDIRECT_URI.replace('/oauth/google/callback', '')}?error=invalid_state")
    
    user_id = state_doc['user_id']
    account_type = state_doc.get('account_type', 'email')
    
    # Delete state
    await db.oauth_states.delete_one({"state": state})
    
    oauth_service = OAuthService(db)
    
    # Exchange code for tokens
    tokens = await oauth_service.exchange_google_code(code)
    if not tokens:
        return RedirectResponse(url=f"{config.GOOGLE_REDIRECT_URI.replace('/oauth/google/callback', '')}?error=token_exchange_failed")
    
    # Get user email
    email = await oauth_service.get_google_user_email(tokens['access_token'])
    if not email:
        return RedirectResponse(url=f"{config.GOOGLE_REDIRECT_URI.replace('/oauth/google/callback', '')}?error=email_fetch_failed")
    
    if account_type == 'email':
        # Create email account
        account = EmailAccount(
            user_id=user_id,
            email=email,
            account_type='oauth_gmail',
            access_token=tokens['access_token'],
            refresh_token=tokens['refresh_token'],
            token_expires_at=tokens['token_expires_at']
        )
        
        doc = account.model_dump()
        await db.email_accounts.insert_one(doc)
        
        return RedirectResponse(url=f"{config.GOOGLE_REDIRECT_URI.replace('/oauth/google/callback', '')}/email-accounts?success=true&email={email}")
    else:
        # Create calendar provider
        provider = CalendarProvider(
            user_id=user_id,
            provider='google',
            email=email,
            access_token=tokens['access_token'],
            refresh_token=tokens['refresh_token'],
            token_expires_at=tokens['token_expires_at']
        )
        
        doc = provider.model_dump()
        await db.calendar_providers.insert_one(doc)
        
        return RedirectResponse(url=f"{config.GOOGLE_REDIRECT_URI.replace('/oauth/google/callback', '')}/calendar-providers?success=true&email={email}")

@router.post("/google/callback")
async def google_oauth_callback(
    code: str = Query(...),
    state: str = Query(...),
    account_type: str = Query('email', description='email or calendar'),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Handle Google OAuth callback"""
    # Verify state
    state_doc = await db.oauth_states.find_one({"state": state})
    if not state_doc:
        raise HTTPException(status_code=400, detail="Invalid state")
    
    user_id = state_doc['user_id']
    
    # Delete state
    await db.oauth_states.delete_one({"state": state})
    
    oauth_service = OAuthService(db)
    
    # Exchange code for tokens
    tokens = await oauth_service.exchange_google_code(code)
    if not tokens:
        raise HTTPException(status_code=400, detail="Failed to exchange code")
    
    # Get user email
    email = await oauth_service.get_google_user_email(tokens['access_token'])
    if not email:
        raise HTTPException(status_code=400, detail="Failed to get user email")
    
    if account_type == 'email':
        # Create email account
        account = EmailAccount(
            user_id=user_id,
            email=email,
            account_type='oauth_gmail',
            access_token=tokens['access_token'],
            refresh_token=tokens['refresh_token'],
            token_expires_at=tokens['token_expires_at']
        )
        
        doc = account.model_dump()
        await db.email_accounts.insert_one(doc)
        
        return {"success": True, "account_id": account.id, "email": email}
    else:
        # Create calendar provider
        provider = CalendarProvider(
            user_id=user_id,
            provider='google',
            email=email,
            access_token=tokens['access_token'],
            refresh_token=tokens['refresh_token'],
            token_expires_at=tokens['token_expires_at']
        )
        
        doc = provider.model_dump()
        await db.calendar_providers.insert_one(doc)
        
        return {"success": True, "provider_id": provider.id, "email": email}

@router.post("/microsoft/callback")
async def microsoft_oauth_callback(
    code: str = Query(...),
    state: str = Query(...),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Handle Microsoft OAuth callback"""
    state_doc = await db.oauth_states.find_one({"state": state})
    if not state_doc:
        raise HTTPException(status_code=400, detail="Invalid state")
    
    _ = state_doc['user_id']  # user_id for future use
    
    await db.oauth_states.delete_one({"state": state})
    
    oauth_service = OAuthService(db)
    
    tokens = await oauth_service.exchange_microsoft_code(code)
    if not tokens:
        raise HTTPException(status_code=400, detail="Failed to exchange code")
    
    # For now, we'll ask user to provide email separately
    # In production, fetch from Microsoft Graph API
    
    return {
        "success": True,
        "message": "OAuth successful. Please provide your email to complete setup.",
        "tokens": tokens
    }
