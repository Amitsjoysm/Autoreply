#!/usr/bin/env python3
"""
Setup intents for test user
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import uuid

async def setup_test_user():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.email_assistant_db
    
    # Get test user
    user = await db.users.find_one({"email": "testuser_interactive@example.com"})
    if not user:
        print("❌ Test user not found")
        return
    
    user_id = user['id']
    print(f"✅ Found test user: {user['email']} (ID: {user_id})")
    
    # Delete existing intents
    await db.intents.delete_many({"user_id": user_id})
    print("🗑️  Cleared existing intents")
    
    # Create pricing inquiry intent (LEAD)
    pricing_intent = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "name": "Pricing Inquiry (Lead)",
        "description": "Handle pricing and cost inquiries from potential customers",
        "keywords": ["pricing", "price", "cost", "how much", "quote", "pricing inquiry"],
        "prompt": "You are responding to a pricing inquiry. Be helpful and professional. Provide pricing information and ask qualifying questions to understand their needs better.",
        "priority": 10,
        "auto_send": True,
        "is_lead": True,
        "is_inbound_lead": True,
        "is_default": False,
        "is_active": True,
        "enable_lead_qualification": True,
        "enable_lead_nurturing": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.intents.insert_one(pricing_intent)
    print(f"✅ Created intent: {pricing_intent['name']} (is_inbound_lead=True)")
    
    # Create meeting request intent
    meeting_intent = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "name": "Meeting Request",
        "description": "Handle meeting scheduling requests",
        "keywords": ["meeting", "schedule", "meet", "call", "discussion"],
        "prompt": "You are responding to a meeting request. Be professional and accommodating. Confirm the meeting time and provide details.",
        "priority": 9,
        "auto_send": True,
        "is_lead": False,
        "is_inbound_lead": False,
        "is_default": False,
        "is_active": True,
        "enable_lead_qualification": False,
        "enable_lead_nurturing": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.intents.insert_one(meeting_intent)
    print(f"✅ Created intent: {meeting_intent['name']}")
    
    # Create qualification criteria
    criteria = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "name": "Default Qualification Criteria",
        "description": "Standard B2B lead qualification",
        "criteria": [
            {
                "question_key": "company_size",
                "question_text": "What's your company size?",
                "weight": 30,
                "scoring_rules": [
                    {"condition": ">=100", "points": 30},
                    {"condition": "50-99", "points": 20},
                    {"condition": "10-49", "points": 10},
                    {"condition": "<10", "points": 5}
                ]
            },
            {
                "question_key": "budget",
                "question_text": "What's your monthly budget?",
                "weight": 40,
                "scoring_rules": [
                    {"condition": ">=10000", "points": 40},
                    {"condition": "5000-9999", "points": 30},
                    {"condition": "1000-4999", "points": 15},
                    {"condition": "<1000", "points": 5}
                ]
            },
            {
                "question_key": "industry",
                "question_text": "What industry are you in?",
                "weight": 30,
                "scoring_rules": [
                    {"condition": "technology", "points": 30},
                    {"condition": "finance", "points": 25},
                    {"condition": "healthcare", "points": 20},
                    {"condition": "other", "points": 10}
                ]
            }
        ],
        "qualification_threshold": 60,
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.lead_qualification_criteria.insert_one(criteria)
    print(f"✅ Created qualification criteria: {criteria['name']}")
    
    # Create nurturing config
    nurturing_config = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "name": "Default Nurturing Config",
        "description": "Standard lead nurturing configuration",
        "max_attempts": 3,
        "questions_per_attempt": 2,
        "follow_up_schedule": [2, 4, 6],
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.lead_nurturing_configs.insert_one(nurturing_config)
    print(f"✅ Created nurturing config: {nurturing_config['name']}")
    
    # Create knowledge base entries
    kb_entries = [
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Pricing Information",
            "content": "Our pricing starts at $1,000/month for small teams (up to 10 users), $5,000/month for medium teams (up to 50 users), and $10,000/month for enterprise (unlimited users). We offer customized packages based on your specific needs.",
            "category": "pricing",
            "tags": ["pricing", "cost", "plans"],
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Company Information",
            "content": "We are a leading AI-powered email automation platform that helps businesses streamline their email communications and improve response times.",
            "category": "company",
            "tags": ["company", "about"],
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    for entry in kb_entries:
        await db.knowledge_base.insert_one(entry)
        print(f"✅ Created KB entry: {entry['title']}")
    
    # Create persona
    persona = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "name": "Professional Sales Assistant",
        "description": "Helpful and professional sales assistant",
        "tone": "professional",
        "style": "concise",
        "signature": "Best regards,\nSales Team",
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.personas.insert_one(persona)
    print(f"✅ Created persona: {persona['name']}")
    
    print("\n✅ Test user setup complete!")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(setup_test_user())
