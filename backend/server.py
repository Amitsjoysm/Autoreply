from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import logging
import asyncio

from config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# MongoDB connection
client = AsyncIOMotorClient(config.MONGO_URL)
db = client[config.DB_NAME]

# Create FastAPI app
app = FastAPI(
    title="AI Email Assistant API",
    description="Production-ready AI-powered email automation platform",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=config.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# Startup event - Start background worker
@app.on_event("startup")
async def startup_event():
    logger.info("Starting AI Email Assistant API...")
    
    # Start background worker in separate task
    from workers.email_worker import poll_all_accounts, check_follow_ups, check_reminders
    
    async def background_worker():
        poll_counter = 0
        follow_up_counter = 0
        reminder_counter = 0
        
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
                logger.error(f"Background worker error: {e}")
                await asyncio.sleep(5)
    
    # Start background worker
    asyncio.create_task(background_worker())
    logger.info("Background worker started")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down...")
    client.close()
