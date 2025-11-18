#!/usr/bin/env python3
"""
Create test user and comprehensive seed data
User: amits.joys@gmail.com
Password: ij@123
"""
import asyncio
import uuid
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext

# MongoDB connection
MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "email_assistant_db"

# User details
USER_EMAIL = "amits.joys@gmail.com"
USER_PASSWORD = "ij@123"
USER_NAME = "Amit Joy"

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_test_user_and_seed():
    """Create test user and comprehensive seed data"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("🚀 Creating test user and seed data...")
    print("=" * 60)
    
    # ============ CREATE TEST USER ============
    print(f"\n📋 Step 1: Creating user {USER_EMAIL}...")
    
    # Check if user exists
    existing_user = await db.users.find_one({"email": USER_EMAIL})
    if existing_user:
        user_id = existing_user['id']
        print(f"✅ User already exists: {USER_EMAIL} (ID: {user_id})")
    else:
        user_id = str(uuid.uuid4())
        user_data = {
            "id": user_id,
            "email": USER_EMAIL,
            "full_name": USER_NAME,
            "password_hash": pwd_context.hash(USER_PASSWORD),
            "is_active": True,
            "email_verified": True,
            "persona": "You are a professional AI email assistant helping with business communications. You are knowledgeable, courteous, and efficient.",
            "signature": "Best regards,\nAmit Joy\nEmail Assistant",
            "quota": 1000,
            "quota_used": 0,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        await db.users.insert_one(user_data)
        print(f"✅ Created user: {USER_EMAIL} (ID: {user_id})")
        print(f"   Password: {USER_PASSWORD}")
    
    # ============ CREATE INTENTS ============
    print("\n📋 Step 2: Creating intents...")
    
    # Clear existing intents for this user
    await db.intents.delete_many({"user_id": user_id})
    
    intents = [
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Meeting Request",
            "description": "Emails requesting to schedule a meeting or call",
            "keywords": ["meeting", "schedule", "call", "discuss", "meet", "zoom", "teams", "appointment"],
            "prompt": "You are a professional assistant scheduling meetings. Be courteous, confirm availability, and suggest meeting times if not provided. Always include calendar details if a meeting is being scheduled.",
            "priority": 10,
            "auto_send": True,
            "is_active": True,
            "is_default": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Meeting Reschedule",
            "description": "Requests to change or reschedule existing meetings",
            "keywords": ["reschedule", "change meeting", "move meeting", "different time", "postpone"],
            "prompt": "You are helping to reschedule a meeting. Be understanding and flexible. Acknowledge the need to reschedule and propose alternative times.",
            "priority": 9,
            "auto_send": True,
            "is_active": True,
            "is_default": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Support Request",
            "description": "Technical support or help requests",
            "keywords": ["help", "support", "issue", "problem", "error", "bug", "not working", "assistance"],
            "prompt": "You are a technical support specialist. Be helpful, patient, and provide clear solutions. Ask for relevant details if needed.",
            "priority": 8,
            "auto_send": True,
            "is_active": True,
            "is_default": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Follow-up Request",
            "description": "Requests for follow-up communication",
            "keywords": ["follow up", "follow-up", "check in", "update", "status", "progress"],
            "prompt": "You are providing a follow-up. Be proactive and informative. Reference previous conversations and provide relevant updates.",
            "priority": 7,
            "auto_send": True,
            "is_active": True,
            "is_default": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Introduction",
            "description": "Introduction or networking emails",
            "keywords": ["introduction", "introduce", "connect", "networking", "pleasure", "nice to meet"],
            "prompt": "You are responding to an introduction. Be warm, professional, and express interest in connecting. Mention relevant background if applicable.",
            "priority": 6,
            "auto_send": True,
            "is_active": True,
            "is_default": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "General Inquiry",
            "description": "General questions about products, services, or information",
            "keywords": ["question", "inquiry", "wondering", "curious", "information", "details", "learn more"],
            "prompt": "You are answering a general inquiry. Be informative, clear, and helpful. Use knowledge base to provide accurate information.",
            "priority": 5,
            "auto_send": True,
            "is_active": True,
            "is_default": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Thank You",
            "description": "Gratitude and appreciation emails",
            "keywords": ["thank you", "thanks", "grateful", "appreciate", "appreciated"],
            "prompt": "You are responding to a thank you message. Be gracious and warm. Express that you're happy to help.",
            "priority": 4,
            "auto_send": True,
            "is_active": True,
            "is_default": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Default Intent",
            "description": "Catch-all intent for emails that don't match other categories",
            "keywords": [],
            "prompt": "You are a professional assistant. Respond appropriately based on the email content. Be helpful and courteous. Use the knowledge base to provide accurate information.",
            "priority": 1,
            "auto_send": True,
            "is_default": True,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    await db.intents.insert_many(intents)
    print(f"✅ Created {len(intents)} intents")
    for intent in intents:
        print(f"   - {intent['name']} (Priority: {intent['priority']}, Auto-send: {intent['auto_send']})")
    
    # ============ CREATE KNOWLEDGE BASE ============
    print("\n📋 Step 3: Creating knowledge base entries...")
    
    # Clear existing knowledge base for this user
    await db.knowledge_base.delete_many({"user_id": user_id})
    
    knowledge_base = [
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Company Overview",
            "content": """We are a cutting-edge AI-powered email assistant platform that helps professionals manage their email communication efficiently. Our platform automates email responses, schedules meetings, and ensures no important message goes unanswered.

Key Features:
- AI-powered draft generation
- Automatic email classification
- Meeting scheduling with calendar integration
- Smart follow-up system
- Knowledge base integration for accurate responses
- Multi-account support (Gmail, Outlook, custom SMTP)

Our mission is to save professionals time and improve communication quality through intelligent automation.""",
            "category": "Company Information",
            "tags": ["company", "overview", "about", "platform"],
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Product Features",
            "content": """Our AI Email Assistant includes the following features:

1. Smart Email Classification
   - Automatic intent detection
   - Priority-based handling
   - Context-aware responses

2. AI Draft Generation
   - Uses your knowledge base
   - Maintains your tone and style
   - Includes relevant information automatically

3. Meeting Scheduling
   - Automatic calendar integration
   - Google Meet link generation
   - Conflict detection
   - Meeting reminders

4. Follow-Up System
   - Time-based follow-ups (e.g., "next quarter")
   - Automatic follow-up scheduling
   - Reply detection and cancellation

5. Multi-Account Support
   - Gmail OAuth integration
   - Outlook/Microsoft OAuth
   - Custom SMTP/IMAP support

6. Knowledge Base Integration
   - Ensures accurate information
   - Prevents AI hallucination
   - Company-specific responses""",
            "category": "Product",
            "tags": ["features", "capabilities", "functionality"],
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Meeting and Calendar Features",
            "content": """Our platform provides comprehensive meeting and calendar management:

Meeting Detection:
- Automatically detects meeting requests in emails
- Extracts meeting details (date, time, attendees, agenda)
- High confidence threshold ensures accuracy

Calendar Integration:
- Direct integration with Google Calendar
- Automatic event creation with all details
- Google Meet links generated automatically
- Calendar conflict detection
- Meeting reminders sent 1 hour before

Event Details in Responses:
- Meeting confirmation emails include all details
- Date, time, and timezone clearly stated
- Google Meet joining link provided
- Calendar view link included
- Attendee information listed

Single Thread Communication:
- All meeting-related communication in one thread
- Event details included in the reply email
- No separate notification emails

Calendar Event Updates:
- Reschedule meetings via email
- Automatic calendar synchronization
- Updated details sent to all attendees""",
            "category": "Meetings",
            "tags": ["meetings", "calendar", "scheduling", "google meet"],
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Pricing Information",
            "content": """Our pricing is designed to be flexible and affordable:

Free Plan:
- 100 emails per month
- Basic features
- Email classification
- Manual draft review

Pro Plan ($29/month):
- 1,000 emails per month
- All features included
- Auto-send capability
- Calendar integration
- Priority support

Business Plan ($99/month):
- 5,000 emails per month
- All Pro features
- Multiple team members
- Advanced analytics
- Dedicated account manager
- Custom integrations

Enterprise Plan (Custom):
- Unlimited emails
- Custom features
- On-premise deployment option
- SLA guarantee
- 24/7 support""",
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
            "content": """Quick start guide to using our AI Email Assistant:

Step 1: Connect Your Email
- Go to Settings > Email Accounts
- Click "Connect Gmail" or "Connect Outlook"
- Authorize OAuth access
- Your emails will start syncing automatically

Step 2: Set Up Intents
- Navigate to Intents page
- Review default intents
- Customize keywords and prompts
- Set priority levels
- Enable auto-send for trusted intents

Step 3: Build Your Knowledge Base
- Go to Knowledge Base
- Add company information
- Include product details
- Add FAQs and common responses
- This ensures accurate AI responses

Step 4: Configure Calendar
- Connect your Google Calendar
- Enable meeting detection
- Set your availability preferences
- Auto-create calendar events

Step 5: Test the System
- Send a test email to your connected account
- Watch it get classified
- Review the AI-generated draft
- Approve or edit before sending

You're all set! The system will now automatically handle your emails.""",
            "category": "Documentation",
            "tags": ["getting started", "setup", "onboarding", "guide"],
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Support and Contact",
            "content": """We're here to help! Contact us through:

Email Support:
- support@emailassistant.com
- Response time: Within 24 hours
- Available for all plan types

Live Chat:
- Available in the app (bottom right)
- Hours: Monday-Friday, 9 AM - 6 PM EST
- Instant responses for urgent issues

Help Center:
- Comprehensive documentation
- Video tutorials
- Step-by-step guides
- Troubleshooting tips

Community Forum:
- Ask questions
- Share tips and tricks
- Connect with other users
- Feature requests

For technical issues:
1. Check our status page for known issues
2. Review documentation in Help Center
3. Contact support with detailed description
4. Include error messages and screenshots

We aim to respond to all inquiries within 24 hours on weekdays.""",
            "category": "Support",
            "tags": ["support", "contact", "help", "assistance"],
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Security and Privacy",
            "content": """Your data security and privacy are our top priorities:

Data Encryption:
- All data encrypted in transit (TLS 1.3)
- Data encrypted at rest (AES-256)
- Secure key management
- Regular security audits

OAuth Authentication:
- No password storage
- Token-based authentication
- Automatic token refresh
- Revocable access

Privacy Policies:
- We never read your emails for marketing
- AI processing happens securely
- No data sharing with third parties
- GDPR and CCPA compliant
- Right to data deletion

Access Control:
- Role-based permissions
- Audit logs for all actions
- Two-factor authentication available
- Session management

Data Retention:
- Emails stored for 90 days by default
- Configurable retention policies
- Permanent deletion available
- Export your data anytime

Compliance:
- SOC 2 Type II certified
- GDPR compliant
- HIPAA available for Enterprise
- Regular penetration testing

If you have security concerns, contact: security@emailassistant.com""",
            "category": "Security",
            "tags": ["security", "privacy", "data protection", "compliance"],
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    await db.knowledge_base.insert_many(knowledge_base)
    print(f"✅ Created {len(knowledge_base)} knowledge base entries")
    for kb in knowledge_base:
        print(f"   - {kb['title']} ({kb['category']})")
    
    print("\n" + "=" * 60)
    print("✅ SEED DATA CREATION COMPLETE!")
    print("=" * 60)
    print(f"\n📧 Login Details:")
    print(f"   Email: {USER_EMAIL}")
    print(f"   Password: {USER_PASSWORD}")
    print(f"\n📊 Summary:")
    print(f"   - User ID: {user_id}")
    print(f"   - Intents: {len(intents)}")
    print(f"   - Knowledge Base: {len(knowledge_base)}")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(create_test_user_and_seed())
