"""Seed data script for AI Email Assistant"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

# Database connection
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "email_assistant_db")

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]


async def create_seed_data(user_id: str):
    """Create seed data for intents and knowledge base"""
    
    print("=" * 60)
    print("Creating Seed Data for AI Email Assistant")
    print("=" * 60)
    
    # ============================================
    # INTENTS - Various email response scenarios
    # ============================================
    intents = [
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Meeting Request",
            "description": "Handle meeting and scheduling requests",
            "prompt": """You are responding to a meeting request. Be professional and courteous.
            
Guidelines:
- Confirm availability based on the proposed times
- If calendar shows conflict, suggest alternative times
- Ask for meeting agenda if not provided
- Confirm meeting location (in-person or virtual)
- Keep response concise and professional

Tone: Professional, helpful, and organized""",
            "keywords": ["meeting", "schedule", "calendar", "appointment", "call", "zoom", "teams", "discuss", "available", "availability"],
            "auto_send": True,
            "priority": 10,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "General Inquiry",
            "description": "General questions and inquiries",
            "prompt": """You are responding to a general inquiry. Be helpful and informative.

Guidelines:
- Answer questions clearly and concisely
- Provide relevant information from knowledge base
- If you don't have information, politely say so and offer to escalate
- Maintain a friendly and professional tone
- Keep response focused on the question

Tone: Friendly, professional, and helpful""",
            "keywords": ["question", "inquiry", "information", "help", "how", "what", "when", "where", "why", "who"],
            "auto_send": True,
            "priority": 5,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Support Request",
            "description": "Technical or customer support requests",
            "prompt": """You are responding to a support request. Be empathetic and solution-focused.

Guidelines:
- Acknowledge the issue and show empathy
- Provide step-by-step troubleshooting if applicable
- Reference relevant knowledge base articles
- Offer escalation path if issue is complex
- Set expectations for resolution timeline

Tone: Empathetic, professional, and solution-oriented""",
            "keywords": ["issue", "problem", "error", "help", "support", "not working", "broken", "fix", "bug", "assistance"],
            "auto_send": True,
            "priority": 8,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Follow-up Request",
            "description": "Following up on previous conversations",
            "prompt": """You are responding to a follow-up request. Reference previous context.

Guidelines:
- Reference previous conversation if available
- Provide status update on any pending items
- Be specific about next steps
- Include timeline if applicable
- Maintain continuity in the conversation

Tone: Professional, informative, and contextual""",
            "keywords": ["follow up", "followup", "following up", "checking in", "status", "update", "progress", "any news"],
            "auto_send": True,
            "priority": 7,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Introduction",
            "description": "New connections and introductions",
            "prompt": """You are responding to an introduction or networking email. Be warm and engaging.

Guidelines:
- Thank them for reaching out
- Show interest in their background/company
- Highlight relevant experience or mutual interests
- Suggest next steps (call, meeting, etc.)
- Keep it conversational but professional

Tone: Warm, professional, and engaging""",
            "keywords": ["introduction", "introduce", "connection", "network", "reaching out", "connect", "pleasure", "nice to meet"],
            "auto_send": True,
            "priority": 6,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Urgent Request",
            "description": "Urgent matters requiring immediate attention",
            "prompt": """You are responding to an urgent request. Acknowledge urgency and provide immediate assistance.

Guidelines:
- Acknowledge the urgency immediately
- Provide immediate next steps
- Offer direct contact if needed (phone, urgent meeting)
- Set clear expectations on resolution
- Be concise and action-oriented

Tone: Professional, urgent, and responsive""",
            "keywords": ["urgent", "asap", "immediately", "emergency", "critical", "important", "time-sensitive", "deadline"],
            "auto_send": False,  # Don't auto-send urgent emails - needs human review
            "priority": 10,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Thank You",
            "description": "Acknowledgment and gratitude emails",
            "prompt": """You are responding to a thank you email. Be gracious and professional.

Guidelines:
- Acknowledge their thanks warmly
- Reinforce the positive relationship
- Offer continued support if applicable
- Keep it brief but sincere
- End on a positive note

Tone: Warm, gracious, and professional""",
            "keywords": ["thank you", "thanks", "appreciate", "grateful", "gratitude", "acknowledgment"],
            "auto_send": True,
            "priority": 4,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    # Insert intents
    print(f"\n📝 Creating {len(intents)} intents...")
    for intent in intents:
        await db.intents.insert_one(intent)
        print(f"  ✓ Created intent: {intent['name']} (auto_send: {intent['auto_send']})")
    
    # ============================================
    # KNOWLEDGE BASE - Company information
    # ============================================
    knowledge_base = [
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Company Overview",
            "content": """Our company is a leading AI-powered email assistant platform that helps professionals manage their inbox more efficiently. We use advanced AI technology to automatically classify, draft, and respond to emails based on user preferences and historical context.

Key Features:
- Automatic email classification with intent detection
- AI-powered draft generation using context and knowledge base
- Calendar integration with automatic meeting scheduling
- Smart follow-up management
- Multi-threaded conversation tracking

Founded: 2024
Mission: To help professionals reclaim their time by automating routine email tasks while maintaining personal touch and context.""",
            "category": "Company Information",
            "tags": ["company", "overview", "about", "mission"],
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Product Features",
            "content": """Our AI Email Assistant offers comprehensive email management:

1. INTELLIGENT EMAIL CLASSIFICATION
   - Automatic intent detection with confidence scoring
   - Custom intent creation with keywords and priorities
   - Thread-based conversation management

2. AI-POWERED DRAFT GENERATION
   - Context-aware responses using thread history
   - Knowledge base integration for accurate information
   - Validation system with retry logic for quality assurance

3. CALENDAR INTEGRATION
   - Automatic meeting detection and scheduling
   - Conflict detection and resolution
   - Event reminders and notifications
   - Google Calendar synchronization

4. SMART FOLLOW-UPS
   - Automated follow-up scheduling
   - Reply detection with automatic cancellation
   - Customizable follow-up sequences

5. OAUTH INTEGRATION
   - Secure Gmail integration
   - Automatic token refresh
   - Multi-account support""",
            "category": "Product",
            "tags": ["features", "product", "capabilities", "AI"],
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Pricing Information",
            "content": """Our flexible pricing plans cater to different needs:

STARTER PLAN - $29/month
- Up to 500 emails/month
- 1 email account
- Basic intent detection
- Email drafts and validation
- Standard support

PROFESSIONAL PLAN - $79/month
- Up to 2,000 emails/month
- 3 email accounts
- Advanced intent detection
- Calendar integration
- Priority support
- Custom intents (up to 10)

BUSINESS PLAN - $199/month
- Unlimited emails
- Unlimited email accounts
- Advanced AI features
- Calendar integration
- Dedicated support
- Unlimited custom intents
- API access

ENTERPRISE - Custom Pricing
- Custom deployment options
- Advanced security features
- Dedicated account manager
- Custom integrations
- SLA guarantees

All plans include:
- Secure OAuth integration
- Thread management
- Follow-up automation
- Mobile app access
- 14-day free trial""",
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
            "content": """Quick start guide for new users:

STEP 1: CONNECT YOUR EMAIL ACCOUNT
- Navigate to Email Accounts page
- Click "Connect Gmail Account"
- Authorize OAuth access
- Your emails will start syncing automatically

STEP 2: SET UP INTENTS
- Go to Intents page
- Create custom intents for your common email types
- Add keywords to help AI detect intents
- Enable "auto_send" for intents you want automated

STEP 3: ADD KNOWLEDGE BASE
- Go to Knowledge Base page
- Add information about your company, products, or services
- AI will use this information in drafts
- Keep information up-to-date

STEP 4: CONNECT CALENDAR (Optional)
- Navigate to Calendar Providers page
- Connect Google Calendar
- AI will automatically create events from meeting requests

STEP 5: REVIEW AND REFINE
- Check your dashboard regularly
- Review generated drafts
- Adjust intents and knowledge base as needed
- Monitor auto-sent emails

Tips for Success:
- Start with a few high-priority intents
- Be specific in your intent prompts
- Update knowledge base regularly
- Review drafts before enabling auto-send""",
            "category": "Documentation",
            "tags": ["getting started", "setup", "guide", "tutorial"],
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Support and Contact",
            "content": """We're here to help! Get support through multiple channels:

SUPPORT CHANNELS:
- Email: support@aiemailassistant.com (Response within 24 hours)
- Live Chat: Available Mon-Fri, 9am-6pm EST
- Help Center: help.aiemailassistant.com
- Community Forum: community.aiemailassistant.com

COMMON ISSUES:
1. Email Not Syncing
   - Check OAuth connection status
   - Ensure account is active
   - Verify email permissions

2. Drafts Not Generating
   - Check if intents are configured
   - Verify AI API keys are valid
   - Review knowledge base content

3. Calendar Not Creating Events
   - Ensure calendar provider is connected
   - Check calendar permissions
   - Verify meeting detection threshold

4. Auto-Send Not Working
   - Confirm auto_send is enabled for intent
   - Check draft validation status
   - Verify OAuth tokens are valid

ENTERPRISE SUPPORT:
Enterprise customers receive:
- Dedicated Slack channel
- Priority phone support
- Dedicated account manager
- Custom training sessions
- 99.9% uptime SLA

HOURS OF OPERATION:
Monday - Friday: 9:00 AM - 6:00 PM EST
Saturday - Sunday: Limited support (Email only)""",
            "category": "Support",
            "tags": ["support", "help", "contact", "troubleshooting"],
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Security and Privacy",
            "content": """We take security and privacy seriously:

DATA SECURITY:
- All data encrypted at rest and in transit (AES-256)
- OAuth 2.0 for secure email access
- No password storage - token-based authentication
- Regular security audits and penetration testing
- SOC 2 Type II certified

PRIVACY POLICY:
- We never sell or share your data
- Emails are processed only for AI assistance
- You maintain full ownership of your data
- Data can be exported or deleted anytime
- GDPR and CCPA compliant

EMAIL ACCESS:
- Read-only access to emails (except sending replies)
- Tokens stored encrypted in database
- Automatic token refresh with user consent
- Can revoke access anytime through Google

AI PROCESSING:
- Emails processed with industry-leading AI models
- No data used for model training without consent
- All processing logged for audit trail
- Thread context maintained locally

COMPLIANCE:
- GDPR compliant (EU data privacy)
- CCPA compliant (California privacy)
- HIPAA available for healthcare (Enterprise)
- SOC 2 Type II certified
- ISO 27001 certified

For detailed privacy policy: privacy.aiemailassistant.com
For security inquiries: security@aiemailassistant.com""",
            "category": "Security",
            "tags": ["security", "privacy", "compliance", "data protection"],
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    # Insert knowledge base
    print(f"\n📚 Creating {len(knowledge_base)} knowledge base entries...")
    for kb in knowledge_base:
        await db.knowledge_bases.insert_one(kb)
        print(f"  ✓ Created: {kb['title']} (Category: {kb['category']})")
    
    print("\n" + "=" * 60)
    print("✓ Seed data created successfully!")
    print("=" * 60)
    print(f"\nCreated:")
    print(f"  - {len(intents)} intents ({sum(1 for i in intents if i['auto_send'])} with auto_send enabled)")
    print(f"  - {len(knowledge_base)} knowledge base entries")
    print("\nThe app is now ready for production use!")
    print("=" * 60)


async def get_first_user_id():
    """Get first user from database or create a test user"""
    user = await db.users.find_one()
    
    if user:
        return user['id']
    else:
        # Create a default admin user for seed data
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        user_id = str(uuid.uuid4())
        user_doc = {
            "id": user_id,
            "email": "admin@example.com",
            "username": "admin",
            "hashed_password": pwd_context.hash("admin123"),
            "tokens_used": 0,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.users.insert_one(user_doc)
        print(f"\n✓ Created default admin user (email: admin@example.com, password: admin123)")
        return user_id


async def main():
    """Main function"""
    try:
        # Get or create user
        user_id = await get_first_user_id()
        
        # Check if seed data already exists
        intent_count = await db.intents.count_documents({"user_id": user_id})
        kb_count = await db.knowledge_bases.count_documents({"user_id": user_id})
        
        if intent_count > 0 or kb_count > 0:
            print(f"\nSeed data already exists for user {user_id}:")
            print(f"  - {intent_count} intents")
            print(f"  - {kb_count} knowledge base entries")
            
            response = input("\nDo you want to replace existing seed data? (yes/no): ")
            if response.lower() != 'yes':
                print("Exiting without changes.")
                return
            
            # Delete existing data
            await db.intents.delete_many({"user_id": user_id})
            await db.knowledge_bases.delete_many({"user_id": user_id})
            print("✓ Deleted existing seed data")
        
        # Create seed data
        await create_seed_data(user_id)
        
    except Exception as e:
        print(f"\n✗ Error creating seed data: {e}")
        raise
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(main())
