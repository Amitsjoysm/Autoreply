#!/usr/bin/env python3
"""
Create comprehensive seed data for Intents and Knowledge Base
"""
import asyncio
import uuid
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient

# MongoDB connection
MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "email_assistant_db"
USER_EMAIL = "amits.joys@gmail.com"


async def create_seed_data():
    """Create comprehensive seed data"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Get user
    user = await db.users.find_one({"email": USER_EMAIL})
    if not user:
        print(f"❌ User {USER_EMAIL} not found")
        client.close()
        return
    
    user_id = user['id']
    print(f"✅ Found user: {USER_EMAIL} (ID: {user_id})")
    
    # Clear existing data
    await db.intents.delete_many({"user_id": user_id})
    await db.knowledge_base.delete_many({"user_id": user_id})
    print("✅ Cleared existing seed data")
    
    # Create Intents
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
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Meeting Reschedule",
            "description": "Requests to change or reschedule existing meetings",
            "keywords": ["reschedule", "change meeting", "move meeting", "different time", "postpone"],
            "system_prompt": "You are helping to reschedule a meeting. Be understanding and flexible. Acknowledge the need to reschedule and propose alternative times.",
            "priority": 9,
            "auto_send": True,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Support Request",
            "description": "Technical support or help requests",
            "keywords": ["help", "support", "issue", "problem", "error", "bug", "not working", "assistance"],
            "system_prompt": "You are a technical support specialist. Be helpful, patient, and provide clear solutions. Ask for relevant details if needed.",
            "priority": 8,
            "auto_send": True,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Follow-up Request",
            "description": "Requests for follow-up communication",
            "keywords": ["follow up", "follow-up", "check in", "update", "status", "progress"],
            "system_prompt": "You are providing a follow-up. Be proactive and informative. Reference previous conversations and provide relevant updates.",
            "priority": 7,
            "auto_send": True,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Introduction",
            "description": "Introduction or networking emails",
            "keywords": ["introduction", "introduce", "connect", "networking", "pleasure", "nice to meet"],
            "system_prompt": "You are responding to an introduction. Be warm, professional, and express interest in connecting. Mention relevant background if applicable.",
            "priority": 6,
            "auto_send": True,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "General Inquiry",
            "description": "General questions about products, services, or information",
            "keywords": ["question", "inquiry", "wondering", "curious", "information", "details", "learn more"],
            "system_prompt": "You are answering a general inquiry. Be informative, clear, and helpful. Use knowledge base to provide accurate information.",
            "priority": 5,
            "auto_send": True,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Thank You",
            "description": "Gratitude and appreciation emails",
            "keywords": ["thank you", "thanks", "grateful", "appreciate", "appreciated"],
            "system_prompt": "You are responding to a thank you message. Be gracious and warm. Express that you're happy to help.",
            "priority": 4,
            "auto_send": True,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Default Intent",
            "description": "Catch-all intent for emails that don't match other categories",
            "keywords": [],
            "system_prompt": "You are a professional assistant. Respond appropriately based on the email content. Be helpful and courteous.",
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
    
    # Create Knowledge Base entries
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
            "content": """Our pricing is designed to be transparent and flexible:

Free Tier:
- 100 emails per month
- 1 email account
- Basic AI responses
- Standard support

Professional ($29/month):
- 1,000 emails per month
- 3 email accounts
- Advanced AI with knowledge base
- Priority support
- Calendar integration
- Meeting scheduling

Enterprise (Custom):
- Unlimited emails
- Unlimited accounts
- Custom AI training
- Dedicated support
- API access
- Custom integrations
- SLA guarantees

All plans include:
- Automatic follow-ups
- Multi-language support
- Email templates
- Analytics dashboard

Contact us for volume discounts and custom solutions.""",
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
            "content": """Getting started with our AI Email Assistant is easy:

Step 1: Sign Up
- Create your account at our platform
- Verify your email address

Step 2: Connect Email Account
- Go to Email Accounts page
- Click "Connect Gmail" or "Connect Outlook"
- Authorize OAuth access
- Your account will sync automatically

Step 3: Connect Calendar (Optional)
- Go to Calendar Providers page
- Connect your Google Calendar
- Enable meeting scheduling features

Step 4: Set Up Knowledge Base
- Add company information
- Include product details
- Add FAQs and common responses
- This ensures accurate AI responses

Step 5: Configure Intents
- Review default intents
- Customize system prompts
- Set auto-send preferences
- Adjust priorities as needed

Step 6: Start Receiving Emails
- System polls your email every 60 seconds
- AI automatically classifies and responds
- Review drafts before they're sent (if auto-send disabled)
- Monitor performance in dashboard

Tips:
- Start with manual review (auto-send off)
- Gradually enable auto-send for trusted intents
- Keep knowledge base updated
- Monitor follow-up effectiveness""",
            "category": "Documentation",
            "tags": ["setup", "getting started", "onboarding", "guide"],
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Support and Contact",
            "content": """We're here to help! Here's how to get support:

Email Support:
- support@emailassistant.ai
- Response time: Within 24 hours
- Include your account email for faster service

Live Chat:
- Available Monday-Friday, 9 AM - 6 PM EST
- Access via platform dashboard
- Instant assistance for urgent issues

Documentation:
- Comprehensive guides at docs.emailassistant.ai
- Video tutorials available
- API documentation for developers

Common Issues:
1. Email not syncing: Check OAuth token validity
2. AI not responding: Verify intent configuration
3. Meeting not creating: Ensure calendar is connected
4. Follow-ups not working: Check account settings

Feature Requests:
- Submit via feedback form
- Community voting on roadmap
- Regular feature updates

Enterprise Support:
- Dedicated account manager
- Priority response (< 4 hours)
- Custom training sessions
- Direct phone support""",
            "category": "Support",
            "tags": ["support", "help", "contact", "assistance"],
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Security and Privacy",
            "content": """Your security and privacy are our top priorities:

Data Security:
- End-to-end encryption for all emails
- OAuth 2.0 for secure authentication
- No password storage (OAuth tokens only)
- Regular security audits
- SOC 2 Type II certified

Privacy Policy:
- We never sell your data
- Email content used only for AI responses
- No third-party data sharing
- You own all your data
- GDPR compliant

Data Storage:
- Encrypted at rest and in transit
- Regular backups
- 99.9% uptime SLA
- Data residency options available

Access Control:
- Role-based permissions
- Two-factor authentication available
- Audit logs for all actions
- Session management

Compliance:
- GDPR compliant
- CCPA compliant
- HIPAA available for Enterprise
- ISO 27001 certified

Data Deletion:
- Delete your data anytime
- Complete data removal within 30 days
- Export your data before deletion
- No hidden data retention

For security concerns, contact: security@emailassistant.ai""",
            "category": "Security",
            "tags": ["security", "privacy", "compliance", "data protection"],
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    await db.knowledge_base.insert_many(knowledge_base)
    print(f"✅ Created {len(knowledge_base)} knowledge base entries")
    
    # Summary
    print("\n" + "="*50)
    print("SEED DATA CREATION COMPLETE")
    print("="*50)
    print(f"User: {USER_EMAIL}")
    print(f"User ID: {user_id}")
    print(f"Intents: {len(intents)} created")
    print(f"Knowledge Base: {len(knowledge_base)} entries created")
    print(f"Auto-send enabled: {sum(1 for i in intents if i.get('auto_send', False))} intents")
    print("="*50)
    
    client.close()


if __name__ == "__main__":
    asyncio.run(create_seed_data())
