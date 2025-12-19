"""
Create Test User for Lead Qualification Testing
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import bcrypt
import uuid

async def create_test_user():
    """Create a test user for lead qualification testing"""
    
    # Database connection
    mongo_url = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
    db_name = os.environ.get("DB_NAME", "email_assistant_db")
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    # Test user credentials
    test_email = "amits.joys@gmail.com"
    test_password = "Test@123"
    
    # Check if user already exists
    existing_user = await db.users.find_one({"email": test_email})
    if existing_user:
        print(f"✅ Test user already exists: {test_email}")
        print(f"   User ID: {existing_user['id']}")
        client.close()
        return existing_user['id']
    
    # Hash password
    password_hash = bcrypt.hashpw(test_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Create test user
    user_id = str(uuid.uuid4())
    user_data = {
        "id": user_id,
        "email": test_email,
        "password_hash": password_hash,
        "full_name": "Test User",
        "quota": 5000,
        "quota_used": 0,
        "quota_reset_date": datetime.now(timezone.utc).isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "role": "user",
        "is_active": True,
        
        # Enable lead qualification and nurturing globally
        "global_lead_nurturing_enabled": True,
        "global_lead_qualification_enabled": True,
        
        # Persona settings
        "persona": {
            "role": "Sales Development Representative",
            "tone": "Professional and friendly",
            "communication_style": "Helpful and consultative",
            "company_context": "We provide AI-powered email automation solutions"
        }
    }
    
    # Insert user
    result = await db.users.insert_one(user_data)
    
    print("=" * 60)
    print("✅ TEST USER CREATED SUCCESSFULLY!")
    print("=" * 60)
    print(f"📧 Email: {test_email}")
    print(f"🔑 Password: {test_password}")
    print(f"🆔 User ID: {user_id}")
    print(f"🌐 Global Lead Nurturing: Enabled")
    print(f"🌐 Global Lead Qualification: Enabled")
    print("=" * 60)
    
    client.close()
    return user_id

if __name__ == "__main__":
    asyncio.run(create_test_user())
