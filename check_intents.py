import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os

async def check_intents():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["email_assistant_db"]
    
    # Find test user
    user = await db.users.find_one({"email": "testuser_interactive@example.com"})
    if not user:
        print("User not found")
        return
    
    user_id = user['id']
    print(f"User ID: {user_id}")
    
    # Check intents
    intents = await db.intents.find({"user_id": user_id}).to_list(None)
    print(f"\nFound {len(intents)} intents:")
    for intent in intents:
        print(f"  - {intent.get('name')}: is_inbound_lead={intent.get('is_inbound_lead', False)}")
    
    client.close()

asyncio.run(check_intents())
