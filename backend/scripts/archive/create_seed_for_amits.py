"""
Create comprehensive seed data for user: amits.joys@gmail.com
Includes intents, knowledge base, and persona configuration
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config
from models.intent import Intent
from models.knowledge_base import KnowledgeBase

async def create_seed_data():
    """Create seed data for amits.joys@gmail.com"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(config.MONGO_URL)
    db = client[config.DB_NAME]
    
    # Find user
    user = await db.users.find_one({"email": "amits.joys@gmail.com"})
    if not user:
        print("❌ User amits.joys@gmail.com not found!")
        return
    
    user_id = user['id']
    print(f"✓ Found user: {user['email']} (ID: {user_id})")
    
    # Delete existing seed data
    deleted_intents = await db.intents.delete_many({"user_id": user_id})
    deleted_kb = await db.knowledge_base.delete_many({"user_id": user_id})
    print(f"✓ Cleaned up: {deleted_intents.deleted_count} intents, {deleted_kb.deleted_count} KB entries")
    
    # Update persona
    persona = """I am a professional business assistant representing our company. I communicate clearly, professionally, and warmly. I always address recipients by their name when known. I provide helpful, accurate information based on our knowledge base."""
    
    await db.users.update_one(
        {"id": user_id},
        {"$set": {"persona": persona}}
    )
    print("✓ Updated user persona")
    
    # ============================================================================
    # CREATE INTENTS
    # ============================================================================
    
    intents_data = [
        {
            "name": "Meeting Request - Time Confirmation Required",
            "description": "When someone requests a meeting - MUST ask for time confirmation before creating calendar event",
            "keywords": ["meeting", "schedule", "call", "zoom", "meet", "catch up", "sync", "discussion", "chat"],
            "priority": 10,
            "auto_send": True,
            "is_lead": False,
            "is_default": False,
            "ai_prompt": """CRITICAL MEETING PROTOCOL:
1. NEVER create calendar events without explicit time confirmation from user
2. If user suggests a time: Ask "Would [suggested time] work for you? Please confirm."
3. If time is unclear/missing: Ask "What date and time would work best for you?"
4. If there's a scheduling conflict: Propose alternative times
5. ONLY after user confirms specific date/time, the system will create the calendar event

RESPONSE FORMAT:
- Start with personalized greeting using sender's name (e.g., "Hi John,")
- Acknowledge the meeting request warmly
- Confirm or ask about the proposed time
- If time confirmed by user, mention that calendar invite will follow
- End professionally but warmly

DO NOT create calendar events in this response - that happens automatically after confirmation."""
        },
        {
            "name": "Meeting Time Confirmation",
            "description": "When user confirms a specific meeting time",
            "keywords": ["confirm", "works for me", "sounds good", "that time", "perfect", "available", "free at"],
            "priority": 9,
            "auto_send": True,
            "is_lead": False,
            "is_default": False,
            "ai_prompt": """The user has confirmed a meeting time. 

RESPONSE FORMAT:
- Start with personalized greeting (e.g., "Hi [Name],")
- Confirm you've received their confirmation
- Let them know a calendar invite will be sent shortly
- Include any meeting details (agenda, preparation needed, etc.)
- End warmly

The calendar event will be created automatically with the confirmed time."""
        },
        {
            "name": "Support Request",
            "description": "User needs help or has an issue",
            "keywords": ["help", "issue", "problem", "error", "broken", "not working", "trouble", "support"],
            "priority": 8,
            "auto_send": True,
            "is_lead": False,
            "is_default": False,
            "ai_prompt": """Provide helpful support response.

RESPONSE FORMAT:
- Start with personalized greeting (e.g., "Hi [Name],")
- Acknowledge their issue/concern
- Provide solution using knowledge base
- Offer additional help if needed
- End with assurance and availability"""
        },
        {
            "name": "General Inquiry",
            "description": "Questions about products, services, or company",
            "keywords": ["question", "wondering", "curious", "ask", "inquire", "information", "details", "know more"],
            "priority": 7,
            "auto_send": True,
            "is_lead": False,
            "is_default": False,
            "ai_prompt": """Provide informative response to their question.

RESPONSE FORMAT:
- Start with personalized greeting (e.g., "Hi [Name],")
- Answer their question using knowledge base
- Provide additional relevant information
- Offer to answer more questions
- End warmly"""
        },
        {
            "name": "Pricing Inquiry",
            "description": "Questions about pricing, costs, or plans",
            "keywords": ["price", "cost", "pricing", "how much", "fee", "charge", "payment", "plan", "subscription"],
            "priority": 8,
            "auto_send": True,
            "is_lead": True,
            "is_default": False,
            "ai_prompt": """Provide clear pricing information.

RESPONSE FORMAT:
- Start with personalized greeting (e.g., "Hi [Name],")
- Share pricing details from knowledge base
- Explain value and benefits
- Offer to discuss their specific needs
- End with call to action"""
        },
        {
            "name": "Thank You / Appreciation",
            "description": "User expressing gratitude",
            "keywords": ["thank", "thanks", "appreciate", "grateful", "gratitude"],
            "priority": 5,
            "auto_send": True,
            "is_lead": False,
            "is_default": False,
            "ai_prompt": """Respond warmly to their appreciation.

RESPONSE FORMAT:
- Start with personalized greeting (e.g., "Hi [Name],")
- Acknowledge their thanks warmly
- Reinforce availability for future help
- Keep it brief but genuine"""
        },
        {
            "name": "Default - General Response",
            "description": "Catch-all for emails that don't match other intents",
            "keywords": [],
            "priority": 1,
            "auto_send": True,
            "is_lead": False,
            "is_default": True,
            "ai_prompt": """Provide helpful, context-appropriate response.

RESPONSE FORMAT:
- ALWAYS start with personalized greeting using sender's name (e.g., "Hi [Name],")
- Acknowledge their email
- Provide relevant response using knowledge base and persona
- Offer additional assistance
- End warmly"""
        }
    ]
    
    print("\n📋 Creating Intents...")
    for intent_data in intents_data:
        intent = Intent(
            user_id=user_id,
            name=intent_data["name"],
            description=intent_data["description"],
            keywords=intent_data["keywords"],
            priority=intent_data["priority"],
            auto_send=intent_data["auto_send"],
            is_inbound_lead=intent_data["is_lead"],
            is_default=intent_data["is_default"],
            prompt=intent_data["ai_prompt"],
            is_active=True,
            created_at=datetime.now(timezone.utc).isoformat()
        )
        
        await db.intents.insert_one(intent.model_dump())
        print(f"  ✓ {intent.name} (Priority: {intent.priority}, Auto-send: {intent.auto_send})")
    
    # ============================================================================
    # CREATE KNOWLEDGE BASE
    # ============================================================================
    
    kb_data = [
        {
            "title": "Company Overview",
            "content": """We are a leading technology solutions provider specializing in business automation and AI-powered tools. 
Our mission is to help businesses streamline operations and improve productivity through intelligent automation.
We serve clients across various industries including retail, healthcare, finance, and manufacturing.""",
            "category": "Company Information"
        },
        {
            "title": "Product Features",
            "content": """Our AI Email Assistant offers:
- Intelligent email processing and auto-replies
- Meeting scheduling with calendar integration
- Lead management and tracking
- Campaign management with analytics
- Knowledge base integration for accurate responses
- Multi-account support (Gmail, Outlook)
- Background processing with task queue
- Customizable intents and workflows""",
            "category": "Product"
        },
        {
            "title": "Pricing Plans",
            "content": """We offer flexible pricing plans:
- Starter Plan: $29/month - Up to 1,000 emails, 1 email account
- Professional Plan: $79/month - Up to 5,000 emails, 3 email accounts, priority support
- Business Plan: $199/month - Up to 20,000 emails, 10 email accounts, dedicated support
- Enterprise: Custom pricing - Unlimited emails, custom integrations, SLA guarantee

All plans include: AI-powered responses, calendar integration, lead management, and campaign tools.
14-day free trial available for all plans.""",
            "category": "Pricing"
        },
        {
            "title": "Meeting Scheduling Process",
            "content": """Our meeting scheduling works as follows:
1. User requests a meeting via email
2. System asks for time confirmation if not explicitly stated
3. Once user confirms specific date/time, system creates calendar event
4. Calendar invite sent with Google Meet link
5. Automatic reminders sent 1 hour before meeting
6. If scheduling conflicts detected, alternative times are suggested

We support Google Calendar and Microsoft Outlook integration.""",
            "category": "Features"
        },
        {
            "title": "Support and Contact",
            "content": """We provide comprehensive support:
- Email Support: support@company.com (24-48 hour response)
- Live Chat: Available Monday-Friday, 9 AM - 6 PM EST
- Phone Support: +1-555-123-4567 (Business hours)
- Knowledge Base: help.company.com
- Video Tutorials: Available on our website
- Dedicated account manager for Business and Enterprise plans""",
            "category": "Support"
        },
        {
            "title": "Getting Started Guide",
            "content": """Quick start steps:
1. Connect your email account (Gmail or Outlook)
2. Configure your persona and signature
3. Set up intents for different email types
4. Add knowledge base entries about your business
5. Connect calendar for meeting management
6. Test with sample emails
7. Enable auto-send once comfortable

Our onboarding team is available to help you get started.""",
            "category": "Documentation"
        }
    ]
    
    print("\n📚 Creating Knowledge Base...")
    for kb_item in kb_data:
        kb = KnowledgeBase(
            user_id=user_id,
            title=kb_item["title"],
            content=kb_item["content"],
            category=kb_item["category"],
            is_active=True,
            created_at=datetime.now(timezone.utc).isoformat(),
            updated_at=datetime.now(timezone.utc).isoformat()
        )
        
        await db.knowledge_base.insert_one(kb.model_dump())
        print(f"  ✓ {kb.title} ({kb.category})")
    
    # Summary
    print("\n" + "="*60)
    print("✅ SEED DATA CREATION COMPLETE")
    print("="*60)
    print(f"\nUser: amits.joys@gmail.com")
    print(f"User ID: {user_id}")
    print(f"\nCreated:")
    print(f"  • {len(intents_data)} Intents (including meeting confirmation protocol)")
    print(f"  • {len(kb_data)} Knowledge Base entries")
    print(f"  • Updated persona")
    print(f"\n🎯 Key Features:")
    print(f"  • Personalized greetings in all responses")
    print(f"  • Meeting scheduling requires time confirmation")
    print(f"  • Auto-replies based on intents + KB + context + persona")
    print(f"  • Fully autonomous email processing")
    print("\n" + "="*60)

if __name__ == "__main__":
    asyncio.run(create_seed_data())
