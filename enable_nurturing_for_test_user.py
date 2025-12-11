import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def enable_nurturing():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["email_assistant_db"]
    
    # Update test user
    result = await db.users.update_one(
        {"email": "testuser_interactive@example.com"},
        {"$set": {
            "global_lead_nurturing_enabled": True,
            "global_lead_qualification_enabled": True
        }}
    )
    
    if result.modified_count > 0:
        print("✅ Enabled nurturing and qualification for test user")
    else:
        print("⚠️  User not found or already enabled")
    
    client.close()

asyncio.run(enable_nurturing())
