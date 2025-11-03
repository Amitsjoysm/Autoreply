"""
Script to seed Knowledge Base and Intents for a specific user
"""
import asyncio
import sys
sys.path.append('/app/backend')

from motor.motor_asyncio import AsyncIOMotorClient
from config import config
import uuid
from datetime import datetime, timezone

async def seed_data_for_user(user_email: str):
    """Add seed data for a specific user"""
    client = AsyncIOMotorClient(config.MONGO_URL)
    db = client[config.DB_NAME]
    
    # Find user
    user = await db.users.find_one({"email": user_email})
    if not user:
        print(f"❌ User not found: {user_email}")
        return
    
    user_id = user['id']
    print(f"✅ Found user: {user_email} (ID: {user_id})")
    
    # Check existing data
    existing_intents = await db.intents.count_documents({"user_id": user_id})
    existing_kb = await db.knowledge_base.count_documents({"user_id": user_id})
    
    print(f"\n📊 Current Data:")
    print(f"   Intents: {existing_intents}")
    print(f"   Knowledge Base: {existing_kb}")
    
    # Create Intents
    intents = [
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Meeting Request",
            "description": "Handles meeting and scheduling requests",
            "prompt": "You are scheduling a meeting. Be professional, confirm the proposed time, and ask for any additional details needed. Include calendar event details if created.",
            "keywords": ["meeting", "schedule", "calendar", "appointment", "call", "zoom", "teams", "discuss", "sync", "catch up"],
            "auto_send": True,
            "priority": 10,
            "is_active": True,
            "is_default": False,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "General Inquiry",
            "description": "Answers general questions using knowledge base",
            "prompt": "You are answering a general inquiry. Use the knowledge base to provide accurate information. Be helpful and comprehensive.",
            "keywords": ["question", "inquiry", "information", "help", "how", "what", "when", "where", "why", "tell me"],
            "auto_send": True,
            "priority": 5,
            "is_active": True,
            "is_default": False,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Support Request",
            "description": "Handles support and technical issues",
            "prompt": "You are providing support. Be empathetic, acknowledge the issue, and provide troubleshooting steps or escalate if needed.",
            "keywords": ["issue", "problem", "error", "support", "not working", "bug", "broken", "help", "urgent"],
            "auto_send": True,
            "priority": 8,
            "is_active": True,
            "is_default": False,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Follow-up Request",
            "description": "Handles follow-up inquiries",
            "prompt": "You are responding to a follow-up. Provide status updates and be proactive about next steps.",
            "keywords": ["follow up", "followup", "checking in", "status", "update", "any news", "heard back"],
            "auto_send": True,
            "priority": 7,
            "is_active": True,
            "is_default": False,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Introduction",
            "description": "Handles networking and introduction requests",
            "prompt": "You are responding to an introduction or networking request. Be warm, professional, and express interest in connecting.",
            "keywords": ["introduction", "introduce", "connection", "network", "linkedin", "connect", "meet you"],
            "auto_send": True,
            "priority": 6,
            "is_active": True,
            "is_default": False,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Thank You",
            "description": "Handles thank you messages",
            "prompt": "You are responding to a thank you message. Be gracious and maintain the positive relationship.",
            "keywords": ["thank you", "thanks", "appreciate", "grateful", "kudos"],
            "auto_send": True,
            "priority": 4,
            "is_active": True,
            "is_default": False,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Urgent Request",
            "description": "Handles urgent matters - requires manual review",
            "prompt": "You are handling an urgent request. Acknowledge urgency and escalate appropriately.",
            "keywords": ["urgent", "asap", "immediately", "emergency", "critical", "priority"],
            "auto_send": False,  # Manual review for urgent matters
            "priority": 10,
            "is_active": True,
            "is_default": False,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Default",
            "description": "Default intent for unmatched emails - responds using knowledge base and persona",
            "prompt": "You are responding to an email that doesn't match any specific category. Use the knowledge base and persona to craft a helpful, relevant response. Focus on understanding the sender's intent and providing value based on available information. If you're unsure about specific details, acknowledge it professionally and offer to get more information or direct them to the right resource.",
            "keywords": [],  # No keywords - catches everything else
            "auto_send": True,
            "priority": 1,  # Lowest priority - checked last
            "is_active": True,
            "is_default": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
    ]
    
    # Create Knowledge Base entries
    kb_entries = [
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Company Overview",
            "content": """
We are an innovative technology company focused on AI-powered solutions that help businesses automate and optimize their workflows.

Our Mission: To empower businesses with intelligent automation that saves time and increases productivity.

Founded: 2023
Team Size: 50+ employees
Location: Remote-first with offices in San Francisco and New York

Key Differentiators:
- Cutting-edge AI technology
- User-friendly interface
- 24/7 customer support
- Enterprise-grade security
""",
            "category": "Company Information",
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Product Features",
            "content": """
Our AI Email Assistant offers:

1. Smart Email Processing
   - Automatic intent classification
   - Context-aware responses
   - Thread tracking and management

2. Calendar Integration
   - Automatic meeting detection
   - Google Calendar integration
   - Meeting conflict detection
   - Automated reminders

3. AI-Powered Drafting
   - Natural language responses
   - Knowledge base integration
   - Multi-intent support
   - Quality validation

4. Automation
   - Auto-reply for configured intents
   - Follow-up scheduling
   - Reminder management
   - Reply detection and follow-up cancellation

5. Security & Privacy
   - OAuth 2.0 authentication
   - End-to-end encryption
   - GDPR compliant
   - SOC 2 certified
""",
            "category": "Product",
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Meeting and Calendar Features",
            "content": """
Our Meeting and Calendar Management System:

Meeting Detection:
- Automatically detects meeting requests in emails
- Extracts date, time, and location information
- Identifies attendees and meeting purpose

Calendar Integration:
- Seamless Google Calendar integration
- Creates calendar events with Google Meet links
- Includes all event details in email responses
- Conflict detection and warnings

Meeting Communication:
- Single email thread for all meeting-related communication
- Includes Google Meet joining link in responses
- Calendar view link for easy access
- Automatic confirmation emails

Event Management:
- Update and reschedule meetings
- Reminder notifications (1 hour before)
- Cancellation handling
- Attendee management
""",
            "category": "Meetings",
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Pricing Information",
            "content": """
Pricing Plans:

Free Tier:
- 50 emails per month
- Basic AI responses
- Limited knowledge base
- Community support
Price: $0/month

Professional:
- 1,000 emails per month
- Advanced AI responses
- Full knowledge base access
- Calendar integration
- Priority support
Price: $29/month

Business:
- 10,000 emails per month
- Custom AI training
- Unlimited knowledge base
- Multi-calendar support
- Dedicated support
- API access
Price: $99/month

Enterprise:
- Unlimited emails
- Custom deployment
- Advanced security features
- SLA guarantee
- Account manager
Price: Custom pricing

All plans include:
- 14-day free trial
- No credit card required
- Cancel anytime
- Money-back guarantee
""",
            "category": "Pricing",
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Getting Started Guide",
            "content": """
Quick Start Guide:

1. Connect Email Account:
   - Go to Email Accounts page
   - Click "Connect Gmail"
   - Authorize OAuth access
   - Wait for initial sync

2. Connect Calendar (Optional):
   - Go to Calendar Providers page
   - Click "Connect Google Calendar"
   - Authorize OAuth access

3. Configure Intents:
   - Review default intents
   - Enable/disable as needed
   - Customize prompts
   - Set auto-send preferences

4. Add Knowledge Base:
   - Go to Knowledge Base page
   - Add your company information
   - Add product details
   - Add FAQs

5. Configure Persona:
   - Go to Profile/Settings
   - Set your communication style
   - Add signature preferences
   - Set response preferences

6. Test the System:
   - Send a test email
   - Check email processing
   - Review generated drafts
   - Verify auto-send behavior

Support Resources:
- Documentation: docs.example.com
- Video tutorials: youtube.com/example
- Community forum: community.example.com
""",
            "category": "Documentation",
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Support and Contact",
            "content": """
Contact Information:

Customer Support:
- Email: support@example.com
- Response time: Within 24 hours
- Available: Monday-Friday, 9 AM - 6 PM EST

Technical Support:
- Email: tech@example.com
- For technical issues and bugs
- Include error messages and screenshots

Sales Inquiries:
- Email: sales@example.com
- Phone: +1 (555) 123-4567
- For pricing and enterprise plans

General Inquiries:
- Email: hello@example.com
- For partnerships and press

Live Chat:
- Available on website
- Monday-Friday, 9 AM - 6 PM EST

Social Media:
- Twitter: @example
- LinkedIn: linkedin.com/company/example
- Facebook: facebook.com/example

Common Issues:
1. Email not syncing: Check OAuth permissions
2. Calendar not connecting: Re-authorize access
3. Drafts not generating: Check AI credits
4. Auto-send not working: Verify intent configuration
""",
            "category": "Support",
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Security and Privacy",
            "content": """
Security Measures:

Data Protection:
- End-to-end encryption for all data in transit
- AES-256 encryption for data at rest
- Regular security audits
- Penetration testing

Compliance:
- GDPR compliant
- SOC 2 Type II certified
- HIPAA compliant (Enterprise)
- ISO 27001 certified

OAuth Security:
- OAuth 2.0 standard
- Token encryption
- Automatic token refresh
- Scope-limited access

Data Privacy:
- No email content used for training
- Data retention policies
- Right to deletion
- Data export available

Access Control:
- Role-based access control
- Two-factor authentication
- Single sign-on (SSO) available
- Audit logs

Third-party Services:
- We use Google APIs (Calendar, Gmail)
- Groq API for AI processing
- All third parties are GDPR compliant

Your Rights:
- Access your data anytime
- Request data deletion
- Export your data
- Opt-out of analytics
""",
            "category": "Security",
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
    ]
    
    print(f"\n📝 Creating Data...")
    
    # Insert intents
    if existing_intents > 0:
        print(f"\n⚠️  {existing_intents} intents already exist. Skipping intent creation.")
    else:
        result = await db.intents.insert_many(intents)
        print(f"✅ Created {len(result.inserted_ids)} intents")
        for intent in intents:
            print(f"   - {intent['name']} (auto_send: {intent['auto_send']}, priority: {intent['priority']}, default: {intent.get('is_default', False)})")
    
    # Insert knowledge base entries
    if existing_kb > 0:
        print(f"\n⚠️  {existing_kb} knowledge base entries already exist. Skipping KB creation.")
    else:
        result = await db.knowledge_base.insert_many(kb_entries)
        print(f"\n✅ Created {len(result.inserted_ids)} knowledge base entries")
        for kb in kb_entries:
            print(f"   - {kb['title']} ({kb['category']})")
    
    # Final counts
    final_intents = await db.intents.count_documents({"user_id": user_id})
    final_kb = await db.knowledge_base.count_documents({"user_id": user_id})
    
    print(f"\n📊 Final Data:")
    print(f"   Intents: {final_intents}")
    print(f"   Knowledge Base: {final_kb}")
    print(f"\n✅ Seed data setup complete!")
    
    client.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python seed_user_data.py <user_email>")
        sys.exit(1)
    
    user_email = sys.argv[1]
    asyncio.run(seed_data_for_user(user_email))
