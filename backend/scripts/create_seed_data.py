"""
Create comprehensive seed data for Intents and Knowledge Base
Run this script to populate the database with initial data
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import uuid

# User credentials
USER_EMAIL = "amits.joys@gmail.com"

async def create_seed_data():
    """Create seed data for intents and knowledge base"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['email_assistant_db']
    
    # Get user
    user = await db.users.find_one({"email": USER_EMAIL})
    if not user:
        print(f"❌ User {USER_EMAIL} not found. Please register first.")
        return
    
    user_id = user['id']
    print(f"✅ Found user: {USER_EMAIL} (ID: {user_id})")
    
    # Clear existing data
    await db.intents.delete_many({"user_id": user_id})
    await db.knowledge_base.delete_many({"user_id": user_id})
    print("🗑️  Cleared existing seed data")
    
    # ============================================================================
    # INTENTS
    # ============================================================================
    
    intents = [
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Meeting Request",
            "description": "Handle meeting scheduling requests",
            "prompt": "You are responding to a meeting request. Be professional and helpful. If meeting details are provided, confirm them. If details are missing, ask for clarification on date, time, and agenda.",
            "keywords": ["meeting", "schedule", "call", "discuss", "catch up", "zoom", "teams", "meet"],
            "auto_send": True,
            "priority": 10,
            "is_default": False,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Meeting Reschedule",
            "description": "Handle meeting rescheduling requests",
            "prompt": "You are responding to a meeting reschedule request. Be understanding and accommodating. Suggest alternative times or ask for their preferred availability.",
            "keywords": ["reschedule", "change meeting", "postpone", "move meeting", "different time"],
            "auto_send": True,
            "priority": 9,
            "is_default": False,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Support Request",
            "description": "Handle customer support inquiries",
            "prompt": "You are providing customer support. Be helpful, empathetic, and solution-oriented. Ask clarifying questions if needed and provide clear next steps.",
            "keywords": ["help", "issue", "problem", "error", "support", "not working", "bug", "broken"],
            "auto_send": True,
            "priority": 8,
            "is_default": False,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "General Inquiry",
            "description": "Handle general questions about products/services",
            "prompt": "You are responding to a general inquiry. Be informative and helpful. Use the knowledge base to provide accurate information about products, services, and pricing.",
            "keywords": ["question", "inquiry", "info", "information", "details", "tell me", "explain"],
            "auto_send": True,
            "priority": 5,
            "is_default": False,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Follow-up Request",
            "description": "Handle follow-up requests",
            "prompt": "You are responding to a follow-up request. Acknowledge their previous interaction and provide any updates or information they requested.",
            "keywords": ["follow up", "following up", "checking in", "any update", "status"],
            "auto_send": True,
            "priority": 7,
            "is_default": False,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Introduction",
            "description": "Handle introduction emails",
            "prompt": "You are responding to an introduction email. Be warm and welcoming. Introduce yourself and your organization briefly, and express interest in learning more about their needs.",
            "keywords": ["introduction", "introduce", "nice to meet", "pleased to meet", "reaching out"],
            "auto_send": True,
            "priority": 6,
            "is_default": False,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Thank You",
            "description": "Handle thank you messages",
            "prompt": "You are responding to a thank you message. Be gracious and brief. Acknowledge their appreciation and offer continued support if relevant.",
            "keywords": ["thank", "thanks", "appreciate", "grateful"],
            "auto_send": True,
            "priority": 4,
            "is_default": False,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Default Intent",
            "description": "Default intent for unmatched emails",
            "prompt": "You are responding to an email that doesn't match any specific category. Be professional and helpful. Use the knowledge base to provide relevant information. Ask clarifying questions if the sender's intent is unclear.",
            "keywords": [],
            "auto_send": True,
            "priority": 1,
            "is_default": True,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    # Insert intents
    await db.intents.insert_many(intents)
    print(f"✅ Created {len(intents)} intents")
    
    # ============================================================================
    # KNOWLEDGE BASE
    # ============================================================================
    
    knowledge_base = [
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Company Overview",
            "content": """We are a leading AI-powered email assistant company that helps professionals manage their email communication efficiently. Our platform uses advanced AI to automatically respond to emails, schedule meetings, and manage follow-ups. We serve businesses of all sizes, from startups to enterprise organizations.""",
            "category": "Company Information",
            "tags": ["company", "about", "overview"],
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Product Features",
            "content": """Our AI Email Assistant offers:
1. Automatic Email Responses: AI-generated replies based on your communication style
2. Smart Meeting Scheduling: Automatic calendar integration and meeting creation
3. Follow-up Management: Automated follow-up reminders and scheduling
4. Intent Classification: Intelligent categorization of incoming emails
5. Knowledge Base Integration: Responses grounded in your company information
6. Multi-account Support: Manage multiple email accounts from one platform
7. Calendar Integration: Google Calendar and Microsoft Outlook support""",
            "category": "Product",
            "tags": ["features", "product", "capabilities"],
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Pricing Information",
            "content": """Our pricing plans:
- Starter Plan: $29/month - Up to 1000 emails/month, 1 email account
- Professional Plan: $79/month - Up to 5000 emails/month, 3 email accounts, priority support
- Business Plan: $199/month - Unlimited emails, unlimited accounts, dedicated support, custom integrations
- Enterprise: Custom pricing - Volume discounts, SLA guarantees, custom features

All plans include a 14-day free trial. No credit card required for trial.""",
            "category": "Pricing",
            "tags": ["pricing", "plans", "cost", "subscription"],
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Getting Started Guide",
            "content": """To get started:
1. Sign up for an account at our website
2. Connect your email account (Gmail or Outlook)
3. Set up your calendar integration
4. Configure your intents and response templates
5. Add knowledge base entries about your business
6. Test with a few emails before enabling auto-send
7. Review and refine based on initial results

Our onboarding team can help you get set up in under 30 minutes.""",
            "category": "Documentation",
            "tags": ["getting started", "setup", "onboarding"],
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Support and Contact",
            "content": """Support options:
- Email: support@emailassistant.ai (response within 4 hours)
- Live Chat: Available 9 AM - 6 PM EST on our website
- Phone: +1 (555) 123-4567 (Business hours: 9 AM - 6 PM EST)
- Documentation: docs.emailassistant.ai
- Community Forum: community.emailassistant.ai

For urgent issues, Professional and Business plan customers have priority support channels.""",
            "category": "Support",
            "tags": ["support", "contact", "help"],
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Security and Privacy",
            "content": """Security is our top priority:
- All data encrypted in transit (TLS 1.3) and at rest (AES-256)
- SOC 2 Type II certified
- GDPR and CCPA compliant
- Regular security audits and penetration testing
- OAuth 2.0 for email account connections (we never store your password)
- Data retention: 90 days by default, customizable
- Right to data deletion and export anytime

We never share your data with third parties for marketing purposes.""",
            "category": "Security",
            "tags": ["security", "privacy", "compliance", "gdpr"],
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Meeting and Calendar Features",
            "content": """Our meeting and calendar features include:
- Automatic meeting detection from email content
- Calendar event creation with Google Meet links
- Meeting reminders sent 1 hour before
- Conflict detection and resolution
- Meeting rescheduling support
- Multiple timezone support
- Attendee management
- Calendar view integration

When someone requests a meeting, we automatically create the calendar event and include all meeting details (time, date, video link) in the reply.""",
            "category": "Meetings",
            "tags": ["meetings", "calendar", "scheduling"],
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    # Insert knowledge base
    await db.knowledge_base.insert_many(knowledge_base)
    print(f"✅ Created {len(knowledge_base)} knowledge base entries")
    
    # Summary
    print("\n" + "="*60)
    print("✅ SEED DATA CREATION COMPLETE")
    print("="*60)
    print(f"User: {USER_EMAIL}")
    print(f"Intents: {len(intents)}")
    print(f"Knowledge Base: {len(knowledge_base)}")
    print("\nIntents created:")
    for intent in intents:
        print(f"  - {intent['name']} (Priority: {intent['priority']}, Auto-send: {intent['auto_send']})")
    print("\nKnowledge Base categories:")
    for kb in knowledge_base:
        print(f"  - {kb['title']} ({kb['category']})")
    print("="*60)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(create_seed_data())
