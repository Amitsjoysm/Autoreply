#!/usr/bin/env python3
"""
Create Topleaders contact list with specified email addresses
"""
import asyncio
import uuid
import sys
from pathlib import Path
from datetime import datetime, timezone

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from config import Config

USER_EMAIL = "amits.joys@gmail.com"

# Contact emails to add to Topleaders list
TOPLEADERS_EMAILS = [
    "rp4101023@gmail.com",
    "varadshinde2023@gmail.com",
    "rajwarkhade2023@gmail.com",
    "ramshinde789553@gmail.com",
    "sagarshinde15798796456@gmail.com",
    "rohushanshinde@gmail.com"
]


async def create_topleaders_list():
    """Create Topleaders contact list"""
    print("🚀 Creating Topleaders Contact List...")
    print("=" * 70)
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(Config.MONGO_URL)
    db = client[Config.DB_NAME]
    
    # Get user
    user = await db.users.find_one({"email": USER_EMAIL})
    if not user:
        print(f"❌ User {USER_EMAIL} not found!")
        client.close()
        return
    
    user_id = user['id']
    print(f"✅ Found user: {USER_EMAIL} (ID: {user_id})\n")
    
    # ========================================
    # 1. CREATE CAMPAIGN CONTACTS
    # ========================================
    print("📧 Creating Campaign Contacts...")
    contact_ids = []
    
    for i, email in enumerate(TOPLEADERS_EMAILS, 1):
        # Extract name from email
        email_username = email.split('@')[0]
        # Capitalize first letter
        first_name = email_username.capitalize()
        
        contact_data = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'email': email,
            'first_name': first_name,
            'last_name': 'Contact',
            'company': f'Company {i}',
            'title': f'Professional {i}',
            'linkedin_url': f'https://linkedin.com/in/{email_username}',
            'company_domain': email.split('@')[1],
            'custom_fields': {},
            'status': 'active',
            'email_verified': False,
            'verification_status': 'unknown',
            'emails_sent': 0,
            'emails_opened': 0,
            'emails_replied': 0,
            'last_contacted': None,
            'tags': ['topleaders', 'vip'],
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        
        # Insert or update contact
        result = await db.campaign_contacts.update_one(
            {'email': email, 'user_id': user_id},
            {'$set': contact_data},
            upsert=True
        )
        
        contact_ids.append(contact_data['id'])
        status = "✅ Created" if result.upserted_id else "✅ Updated"
        print(f"   {status}: {email} ({first_name})")
    
    # ========================================
    # 2. CREATE TOPLEADERS LIST
    # ========================================
    print("\n📋 Creating 'Topleaders' Contact List...")
    
    list_data = {
        'id': str(uuid.uuid4()),
        'user_id': user_id,
        'name': 'Topleaders',
        'description': 'Top leaders contact list for campaign outreach',
        'contact_ids': contact_ids,
        'total_contacts': len(contact_ids),
        'created_at': datetime.now(timezone.utc).isoformat(),
        'updated_at': datetime.now(timezone.utc).isoformat()
    }
    
    result = await db.contact_lists.update_one(
        {'name': 'Topleaders', 'user_id': user_id},
        {'$set': list_data},
        upsert=True
    )
    
    status = "Created" if result.upserted_id else "Updated"
    print(f"   ✅ {status} 'Topleaders' list with {len(contact_ids)} contacts")
    print(f"   List ID: {list_data['id']}")
    
    # ========================================
    # SUMMARY
    # ========================================
    print("\n" + "=" * 70)
    print("✅ TOPLEADERS LIST CREATION COMPLETED!")
    print("=" * 70)
    print(f"📧 Contacts created: {len(contact_ids)}")
    print(f"📋 List: 'Topleaders' with {len(contact_ids)} contacts")
    print(f"\n📝 Contact Emails:")
    for i, email in enumerate(TOPLEADERS_EMAILS, 1):
        print(f"   {i}. {email}")
    
    print("\n✅ Next Steps:")
    print("   1. Go to Campaigns → Create Campaign")
    print("   2. Select 'Topleaders' list")
    print("   3. Choose campaign templates")
    print("   4. Launch campaign!")
    print("=" * 70)
    
    client.close()


if __name__ == "__main__":
    asyncio.run(create_topleaders_list())
