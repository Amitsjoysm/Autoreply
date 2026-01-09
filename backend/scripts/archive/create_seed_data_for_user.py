#!/usr/bin/env python3
"""
Create seed data for user: amits.joys@gmail.com
"""
from pymongo import MongoClient
from datetime import datetime, timezone
import uuid

USER_EMAIL = "amits.joys@gmail.com"

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client["email_assistant_db"]

# Find user
user = db.users.find_one({"email": USER_EMAIL})
if not user:
    print(f"❌ User {USER_EMAIL} not found!")
    exit(1)

user_id = user.get('id') or user.get('_id')
print(f"✅ Found user: {USER_EMAIL}")
print(f"   User ID: {user_id}\n")

# Delete existing data for this user
print("🗑️  Cleaning up old data...")
db.intents.delete_many({"user_id": user_id})
db.knowledge_base.delete_many({"user_id": user_id})
print("✅ Old data removed\n")

# Create Intents
print("📋 Creating Intents...")
intents = [
    {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "name": "Meeting Request",
        "description": "Handle meeting requests and scheduling",
        "prompt": "You are scheduling a meeting. Be professional, propose times, and confirm availability. Always ask for preferred date/time if not mentioned.",
        "keywords": ["meeting", "schedule", "call", "zoom", "teams", "appointment", "catch up", "discuss", "meet", "demo", "presentation"],
        "auto_send": True,
        "priority": 10,
        "is_default": False,
        "is_inbound_lead": False,
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "name": "Urgent Request",
        "description": "Urgent issues requiring immediate attention",
        "prompt": "This is an urgent matter. Acknowledge immediately, provide timeline, and escalate if needed. Show empathy and commitment to quick resolution.",
        "keywords": ["urgent", "asap", "emergency", "critical", "important", "immediately", "right away", "priority"],
        "auto_send": False,  # Manual review for urgent
        "priority": 10,
        "is_default": False,
        "is_inbound_lead": False,
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "name": "Support Request",
        "description": "Technical support and help requests",
        "prompt": "You are providing customer support. Be helpful, patient, and thorough. Ask clarifying questions and provide step-by-step solutions.",
        "keywords": ["help", "issue", "problem", "error", "bug", "not working", "broken", "support", "assistance", "trouble"],
        "auto_send": True,
        "priority": 8,
        "is_default": False,
        "is_inbound_lead": False,
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "name": "Sales Inquiry",
        "description": "Sales and business inquiries - potential leads",
        "prompt": "You are handling a sales inquiry. Be professional, highlight value, and guide toward next steps. Ask about their needs and timeline.",
        "keywords": ["pricing", "cost", "buy", "purchase", "quote", "proposal", "interested in", "sales", "demo", "trial", "subscription"],
        "auto_send": True,
        "priority": 9,
        "is_default": False,
        "is_inbound_lead": True,  # Mark as lead
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "name": "Partnership Opportunity",
        "description": "Business partnership and collaboration inquiries",
        "prompt": "You are exploring a partnership opportunity. Be professional, show interest, and suggest a call to discuss further.",
        "keywords": ["partnership", "collaboration", "collaborate", "work together", "joint venture", "affiliate", "integration"],
        "auto_send": True,
        "priority": 8,
        "is_default": False,
        "is_inbound_lead": True,  # Mark as lead
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "name": "Introduction",
        "description": "Introductions and networking",
        "prompt": "Respond warmly to introductions. Show interest, ask about their background, and suggest ways to stay connected.",
        "keywords": ["introduction", "introduce", "meet", "connect", "networking", "hello", "reaching out"],
        "auto_send": True,
        "priority": 6,
        "is_default": False,
        "is_inbound_lead": False,
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "name": "General Inquiry",
        "description": "General questions and information requests",
        "prompt": "Provide helpful, accurate information. Be friendly and offer to provide more details if needed.",
        "keywords": ["question", "information", "inquiry", "wondering", "curious", "ask", "know more", "tell me"],
        "auto_send": True,
        "priority": 5,
        "is_default": False,
        "is_inbound_lead": False,
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "name": "Thank You",
        "description": "Acknowledgments and thank you messages",
        "prompt": "Respond graciously to thank you messages. Keep it brief and warm.",
        "keywords": ["thanks", "thank you", "appreciate", "grateful"],
        "auto_send": True,
        "priority": 4,
        "is_default": False,
        "is_inbound_lead": False,
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "name": "Default Intent",
        "description": "Default handler for unmatched emails",
        "prompt": "Respond professionally and helpfully. Acknowledge the email and offer assistance.",
        "keywords": [],
        "auto_send": True,
        "priority": 1,
        "is_default": True,  # Default intent
        "is_inbound_lead": False,
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
]

result = db.intents.insert_many(intents)
print(f"✅ Created {len(result.inserted_ids)} intents")
for intent in intents:
    lead_marker = " [LEAD]" if intent['is_inbound_lead'] else ""
    auto_marker = " [AUTO]" if intent['auto_send'] else " [MANUAL]"
    default_marker = " [DEFAULT]" if intent['is_default'] else ""
    print(f"   - {intent['name']} (P:{intent['priority']}){auto_marker}{lead_marker}{default_marker}")

# Create Knowledge Base
print("\n📚 Creating Knowledge Base...")
knowledge_base = [
    {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "title": "Company Overview",
        "content": """Our company is a leading provider of AI-powered email automation solutions. 
We help businesses streamline their email communication, automate responses, and improve customer engagement. 
Founded in 2024, we serve clients across various industries including technology, healthcare, and e-commerce.
Our mission is to make email communication more efficient and intelligent.""",
        "category": "Company",
        "tags": ["company", "overview", "about"],
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "title": "Product Features",
        "content": """Our AI Email Assistant includes:
- Automated email classification and intent detection
- AI-powered draft generation with customizable prompts
- Smart follow-up scheduling with time-based automation
- Meeting detection and calendar integration
- Lead tracking and management
- Campaign management with personalized templates
- Email thread management
- Knowledge base integration for accurate responses
- Multi-account support (Gmail, Outlook)
- Real-time email polling and processing""",
        "category": "Product",
        "tags": ["features", "product", "capabilities"],
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "title": "Pricing Plans",
        "content": """We offer flexible pricing plans:

Starter Plan - $49/month:
- 1 email account
- 1,000 emails/month
- Basic AI features
- 7-day follow-up history

Professional Plan - $99/month:
- 3 email accounts
- 5,000 emails/month
- Advanced AI features
- Unlimited follow-ups
- Lead tracking
- Priority support

Enterprise Plan - Custom pricing:
- Unlimited email accounts
- Unlimited emails
- Custom AI training
- Dedicated support
- API access
- SLA guarantee

All plans include 14-day free trial. Contact sales@example.com for custom quotes.""",
        "category": "Pricing",
        "tags": ["pricing", "plans", "cost"],
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "title": "Getting Started Guide",
        "content": """Quick Start Guide:

1. Connect Your Email Account
   - Click "Email Accounts" in the sidebar
   - Click "Connect with Google"
   - Authorize OAuth access

2. Set Up Intents
   - Navigate to "Intents"
   - Review default intents
   - Customize prompts and keywords

3. Add Knowledge Base
   - Go to "Knowledge Base"
   - Add company information
   - Add product details
   - Add FAQs

4. Test the System
   - Send a test email to your connected account
   - Check "Emails" to see processing
   - Review generated drafts

5. Configure Follow-ups
   - Set up follow-up schedules
   - Enable auto-send for specific intents
   - Monitor follow-up status

Need help? Contact support@example.com""",
        "category": "Documentation",
        "tags": ["getting started", "setup", "tutorial"],
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "title": "Support and Contact",
        "content": """Contact Information:

Email Support: support@example.com
Sales Inquiries: sales@example.com
Technical Support: tech@example.com

Phone: +1 (555) 123-4567
Hours: Monday-Friday, 9 AM - 6 PM EST

Live Chat: Available on our website during business hours

Response Times:
- Critical issues: Within 1 hour
- High priority: Within 4 hours
- Normal priority: Within 24 hours

Documentation: docs.example.com
Community Forum: community.example.com
Status Page: status.example.com""",
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
        "content": """Security & Privacy:

Data Security:
- End-to-end encryption for all email data
- SOC 2 Type II certified
- GDPR and CCPA compliant
- Regular security audits
- Data hosted in secure AWS facilities

Privacy Policy:
- We never sell your data
- Your emails are processed only for automation
- You retain full ownership of your data
- Data can be exported or deleted anytime
- We use AI models that don't train on your data

OAuth Security:
- We use OAuth 2.0 for secure authentication
- Tokens are encrypted at rest
- Automatic token refresh
- Revoke access anytime from your Google account

Compliance:
- GDPR compliant
- CCPA compliant
- HIPAA available for Enterprise plans
- SOC 2 Type II certified

Questions? privacy@example.com""",
        "category": "Security",
        "tags": ["security", "privacy", "compliance"],
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "title": "API and Integrations",
        "content": """API & Integrations:

REST API:
- Full-featured REST API
- OAuth 2.0 authentication
- Rate limiting: 1000 requests/hour
- Webhooks for real-time updates
- Comprehensive documentation

Supported Integrations:
- Email: Gmail, Outlook, IMAP
- Calendar: Google Calendar, Outlook Calendar
- CRM: Salesforce, HubSpot, Pipedrive (coming soon)
- Slack notifications
- Zapier integration
- Webhooks for custom integrations

Developer Resources:
- API Documentation: api.example.com
- Code examples (Python, JavaScript, Ruby)
- Postman collection
- SDKs available

Enterprise customers get:
- Custom integrations
- Dedicated API support
- Higher rate limits
- SLA guarantee

Developer support: developers@example.com""",
        "category": "Technical",
        "tags": ["api", "integrations", "webhooks"],
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
]

result = db.knowledge_base.insert_many(knowledge_base)
print(f"✅ Created {len(result.inserted_ids)} knowledge base entries")
for kb in knowledge_base:
    print(f"   - {kb['title']} ({kb['category']})")

print("\n" + "="*70)
print("✅ SEED DATA CREATED SUCCESSFULLY!")
print("="*70)
print(f"\nUser: {USER_EMAIL}")
print(f"Intents: {len(intents)}")
print(f"  - {sum(1 for i in intents if i['is_inbound_lead'])} marked as lead intents")
print(f"  - {sum(1 for i in intents if i['auto_send'])} with auto-send enabled")
print(f"Knowledge Base: {len(knowledge_base)}")
print("\nFrontend should now load data successfully! 🎉")

client.close()
