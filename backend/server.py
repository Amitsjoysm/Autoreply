from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from motor.motor_asyncio import AsyncIOMotorClient
import logging
import asyncio

from config import config
from container import initialize_container
from middleware.error_handler import global_exception_handler, validation_exception_handler
from middleware.security import RateLimitMiddleware, SecurityHeadersMiddleware
from exceptions import EmailAssistantException

# Configure logging with better format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
)
logger = logging.getLogger(__name__)

# MongoDB connection with connection pooling
client = AsyncIOMotorClient(
    config.MONGO_URL,
    maxPoolSize=50,
    minPoolSize=10,
    maxIdleTimeMS=45000,
    serverSelectionTimeoutMS=5000
)
db = client[config.DB_NAME]

# Create FastAPI app
app = FastAPI(
    title="AI Email Assistant API",
    description="Production-ready AI-powered email automation platform with SOLID principles",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Add security middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=config.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add exception handlers
app.add_exception_handler(EmailAssistantException, global_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# Import routes
from routes.auth_routes import router as auth_router
from routes.email_account_routes import router as email_account_router
from routes.email_routes import router as email_router
from routes.intent_routes import router as intent_router
from routes.knowledge_base_routes import router as knowledge_base_router
from routes.oauth_routes import router as oauth_router
from routes.calendar_routes import router as calendar_router
from routes.follow_up_routes import router as follow_up_router
from routes.system_routes import router as system_router

# Include routers under /api prefix
app.include_router(auth_router, prefix="/api")
app.include_router(email_account_router, prefix="/api")
app.include_router(email_router, prefix="/api")
app.include_router(intent_router, prefix="/api")
app.include_router(knowledge_base_router, prefix="/api")
app.include_router(oauth_router, prefix="/api")
app.include_router(calendar_router, prefix="/api")
app.include_router(follow_up_router, prefix="/api")
app.include_router(system_router, prefix="/api")

# Special OAuth callback route (without /api prefix for Google OAuth redirect)
from fastapi import Query
from fastapi.responses import RedirectResponse

@app.get("/oauth/google/callback")
async def oauth_google_callback_public(
    code: str = Query(...),
    state: str = Query(...),
):
    """Public OAuth callback endpoint for Google (redirects from Google don't go through /api)"""
    from routes.oauth_routes import google_oauth_callback_get
    return await google_oauth_callback_get(code=code, state=state, db=db)

# Root endpoint
@app.get("/api")
async def root():
    return {
        "message": "AI Email Assistant API",
        "version": "1.0.0",
        "status": "running"
    }

# Health check
@app.get("/api/health")
async def health_check():
    try:
        await db.command('ping')
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "database": "disconnected"}

# Startup event - Initialize services and start background worker
@app.on_event("startup")
async def startup_event():
    logger.info("=" * 60)
    logger.info("Starting AI Email Assistant API...")
    logger.info("=" * 60)
    
    try:
        # Test database connection
        await db.command('ping')
        logger.info("✓ Database connection established")
        
        # Initialize dependency injection container
        initialize_container(db, config.JWT_SECRET)
        logger.info("✓ Service container initialized")
        
        # Start background worker in separate task
        from workers.email_worker import poll_all_accounts, check_follow_ups, check_reminders
        
        async def background_worker():
            poll_counter = 0
            follow_up_counter = 0
            reminder_counter = 0
            
            logger.info("✓ Background worker started")
            
            while True:
                try:
                    # Poll emails every 60 seconds
                    if poll_counter % config.EMAIL_POLL_INTERVAL == 0:
                        asyncio.create_task(poll_all_accounts())
                        poll_counter = 0
                    
                    # Check follow-ups every 5 minutes
                    if follow_up_counter % config.FOLLOW_UP_CHECK_INTERVAL == 0:
                        asyncio.create_task(check_follow_ups())
                        follow_up_counter = 0
                    
                    # Check reminders every hour
                    if reminder_counter % config.REMINDER_CHECK_INTERVAL == 0:
                        asyncio.create_task(check_reminders())
                        reminder_counter = 0
                    
                    await asyncio.sleep(1)
                    poll_counter += 1
                    follow_up_counter += 1
                    reminder_counter += 1
                except Exception as e:
                    logger.error(f"Background worker error: {e}", exc_info=True)
                    await asyncio.sleep(5)
        
        # Start background worker
        asyncio.create_task(background_worker())
        
        logger.info("=" * 60)
        logger.info("✓ AI Email Assistant API is ready!")
        logger.info("=" * 60)
    except Exception as e:
        logger.error(f"✗ Startup failed: {e}", exc_info=True)
        raise

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down AI Email Assistant API...")
    
    # Close HTTP client pool
    from utils.http_client import http_client_pool
    await http_client_pool.close()
    logger.info("✓ HTTP client pool closed")
    
    # Close database connection
    client.close()
    logger.info("✓ Database connection closed")
    
    logger.info("✓ Shutdown complete")
