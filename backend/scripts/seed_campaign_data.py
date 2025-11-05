#!/usr/bin/env python3
"""
Seed campaign data for testing:
- Create a list named "rapid"
- Add contacts with provided emails
- Create email templates and follow-up templates
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timezone
import uuid

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from config import Config

# Provided email addresses
TEST_EMAILS = [
    "sandypandit856@gmail.com",
    "vasantm521@gmail.com",
    "gojo4772@gmail.com",
    "getosuguro002@gmail.com"
]

async def seed_campaign_data():
    """Seed campaign data into MongoDB"""
    print("🚀 Starting campaign data seeding...")
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Find user by email (using amits.joys@gmail.com as mentioned in tests)
    user = await db.users.find_one({"email": "amits.joys@gmail.com"})
    
    if not user:
        print("❌ User amits.joys@gmail.com not found!")
        print("Please create the user first or run the application.")
        return
    
    user_id = user['id']
    print(f"✅ Found user: {user['email']} (ID: {user_id})")
    
    # ========================================
    # 1. CREATE CONTACTS
    # ========================================
    print("\n📧 Creating contacts...")
    contact_ids = []
    
    for i, email in enumerate(TEST_EMAILS, 1):
        # Extract name from email
        email_parts = email.split('@')[0]
        first_name = email_parts.capitalize()
        
        contact_data = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'email': email,
            'first_name': first_name,
            'last_name': 'Test',
            'company': f'Company {i}',
            'title': f'Position {i}',
            'linkedin_url': f'https://linkedin.com/in/{email_parts}',
            'company_domain': email.split('@')[1],
            'custom_fields': {},
            'status': 'active',
            'email_verified': False,
            'verification_status': 'unknown',
            'emails_sent': 0,
            'emails_opened': 0,
            'emails_replied': 0,
            'last_contacted': None,
            'tags': ['test', 'rapid'],
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
        print(f"  ✅ Contact: {email} (ID: {contact_data['id']})")
    
    # ========================================
    # 2. CREATE "RAPID" LIST
    # ========================================
    print("\n📋 Creating 'rapid' contact list...")
    
    list_data = {
        'id': str(uuid.uuid4()),
        'user_id': user_id,
        'name': 'rapid',
        'description': 'Test contacts for rapid campaign testing',
        'contact_ids': contact_ids,
        'total_contacts': len(contact_ids),
        'created_at': datetime.now(timezone.utc).isoformat(),
        'updated_at': datetime.now(timezone.utc).isoformat()
    }
    
    result = await db.contact_lists.update_one(
        {'name': 'rapid', 'user_id': user_id},
        {'$set': list_data},
        upsert=True
    )
    
    print(f"  ✅ List 'rapid' created with {len(contact_ids)} contacts (ID: {list_data['id']})")
    
    # ========================================
    # 3. CREATE EMAIL TEMPLATES
    # ========================================
    print("\n📝 Creating email templates...")
    
    templates = [
        {
            'name': 'Initial Outreach',
            'description': 'Initial email template for cold outreach',
            'subject': 'Quick question about {{company}}',
            'body': '''Hi {{first_name}},

I noticed you're working at {{company}} as {{title}}. I wanted to reach out because I think we could help your team with [specific value proposition].

Would you be open to a quick 15-minute call this week to discuss?

Looking forward to hearing from you!''',
            'template_type': 'initial'
        },
        {
            'name': 'Follow-up 1',
            'description': 'First follow-up email',
            'subject': 'Re: Quick question about {{company}}',
            'body': '''Hi {{first_name}},

I wanted to follow up on my previous email. I know you're probably busy, but I genuinely believe we could add value to {{company}}.

Are you available for a brief chat this week?

Best regards!''',
            'template_type': 'follow_up_1'
        },
        {
            'name': 'Follow-up 2',
            'description': 'Second follow-up email',
            'subject': 'Re: Quick question about {{company}}',
            'body': '''Hi {{first_name}},

This is my last follow-up. I understand if now isn't the right time, but I wanted to make sure you had the opportunity to learn about how we're helping companies like {{company}}.

If you're interested, just reply to this email and we'll find a time that works.

Thanks for your time!''',
            'template_type': 'follow_up_2'
        },
        {
            'name': 'Meeting Request',
            'description': 'Template for requesting a meeting',
            'subject': 'Meeting Request - {{company}}',
            'body': '''Hi {{first_name}},

I'd love to schedule a meeting to discuss how we can help {{company}} achieve [specific goal].

Are you available next week for a 30-minute call?

Please let me know what works best for your schedule.

Best regards!''',
            'template_type': 'initial'
        }
    ]
    
    template_ids = []
    for template_data in templates:
        template = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'name': template_data['name'],
            'description': template_data['description'],
            'subject': template_data['subject'],
            'body': template_data['body'],
            'available_tags': [
                'email', 'first_name', 'last_name', 'company',
                'title', 'linkedin_url', 'company_domain'
            ],
            'template_type': template_data['template_type'],
            'times_used': 0,
            'is_active': True,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        
        result = await db.campaign_templates.update_one(
            {'name': template['name'], 'user_id': user_id},
            {'$set': template},
            upsert=True
        )
        
        template_ids.append(template['id'])
        print(f"  ✅ Template: {template['name']} ({template['template_type']}) (ID: {template['id']})")
    
    # ========================================
    # SUMMARY
    # ========================================
    print("\n" + "="*60)
    print("✅ CAMPAIGN DATA SEEDING COMPLETED!")
    print("="*60)
    print(f"📧 Contacts created: {len(contact_ids)}")
    print(f"📋 List 'rapid' created with {len(contact_ids)} contacts")
    print(f"📝 Templates created: {len(template_ids)}")
    print("\nTest Emails in 'rapid' list:")
    for email in TEST_EMAILS:
        print(f"  - {email}")
    print("\nTemplates available:")
    for template_data in templates:
        print(f"  - {template_data['name']} ({template_data['template_type']})")
    print("\n🎉 Ready for campaign testing!")
    print("="*60)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_campaign_data())
