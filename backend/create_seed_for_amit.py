"""
Seed data script for user: amits.joys@gmail.com
Creates comprehensive Intents and Knowledge Base entries
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv('/app/backend/.env')

USER_EMAIL = "amits.joys@gmail.com"

INTENTS = [
    {
        "name": "Meeting Request",
        "description": "Handle meeting and scheduling requests",
        "keywords": ["meeting", "schedule", "calendar", "appointment", "call", "zoom", "teams", "meet", "available", "availability"],
        "prompt": "You are responding to a meeting request. Be professional and accommodating. Check for time, date, and meeting details. If creating a meeting, confirm all details clearly.",
        "priority": 10,
        "auto_send": True
    },
    {
        "name": "Support Request",
        "description": "Technical support and troubleshooting inquiries",
        "keywords": ["issue", "problem", "error", "help", "support", "not working", "bug", "broken", "fix", "trouble"],
        "prompt": "You are responding to a support request. Be empathetic and solution-oriented. Acknowledge the issue and provide clear troubleshooting steps or escalate if needed.",
        "priority": 8,
        "auto_send": True
    },
    {
        "name": "General Inquiry",
        "description": "General questions about products or services",
        "keywords": ["question", "inquiry", "information", "tell me", "how", "what", "when", "where", "why", "details"],
        "prompt": "You are answering a general inquiry. Be informative and helpful. Use knowledge base information to provide accurate answers. Be concise but thorough.",
        "priority": 5,
        "auto_send": True
    },
    {
        "name": "Follow-up Request",
        "description": "Following up on previous conversations",
        "keywords": ["follow up", "followup", "checking in", "status", "update", "any news", "heard back"],
        "prompt": "You are responding to a follow-up request. Reference previous conversations if available. Provide status updates and next steps clearly.",
        "priority": 7,
        "auto_send": True
    },
    {
        "name": "Introduction",
        "description": "New connections and introductions",
        "keywords": ["introduction", "introduce", "connection", "network", "reach out", "connect", "nice to meet"],
        "prompt": "You are responding to an introduction. Be warm and professional. Express interest in the connection and suggest next steps for collaboration or conversation.",
        "priority": 6,
        "auto_send": True
    },
    {
        "name": "Thank You",
        "description": "Expressions of gratitude",
        "keywords": ["thank you", "thanks", "appreciate", "grateful", "gratitude", "thank"],
        "prompt": "You are responding to a thank you message. Be gracious and warm. Acknowledge their appreciation and reinforce the positive relationship.",
        "priority": 4,
        "auto_send": True
    },
    {
        "name": "Urgent Request",
        "description": "Time-sensitive or critical matters requiring immediate attention",
        "keywords": ["urgent", "asap", "immediately", "emergency", "critical", "important", "time-sensitive", "priority"],
        "prompt": "You are handling an urgent request. Acknowledge the urgency and provide immediate next steps. Set clear expectations for response time.",
        "priority": 10,
        "auto_send": False  # Manual review for urgent matters
    },
    {
        "name": "Default",
        "description": "Default intent for emails that don't match any specific category",
        "keywords": [],
        "prompt": "You are responding to an email that doesn't match any specific category. Use the knowledge base and persona to craft a helpful, relevant response. Focus on understanding the sender's intent and providing value based on available information. If you're unsure about specific details, acknowledge it professionally and offer to get more information or direct them to the right resource.",
        "priority": 1,
        "auto_send": True,
        "is_default": True
    }
]

KNOWLEDGE_BASE = [
    {
        "title": "Company Overview",
        "content": """AI Email Assistant is an intelligent email management platform that helps professionals automate email responses, schedule meetings, and manage follow-ups efficiently.

Founded in 2024, we leverage cutting-edge AI technology to understand email context, classify intents, and generate personalized responses that maintain your unique voice and style.

Our mission is to save professionals 10+ hours per week on email management while improving response quality and customer satisfaction.""",
        "category": "Company Information",
        "tags": ["company", "about", "mission", "overview"]
    },
    {
        "title": "Product Features",
        "content": """Key features of AI Email Assistant:

1. **Intelligent Email Classification**: Automatically categorizes incoming emails by intent (meetings, support, inquiries, etc.)

2. **AI-Powered Draft Generation**: Creates contextual, personalized email drafts using your knowledge base and communication style

3. **Auto-Reply System**: Automatically sends responses for approved intent categories with validation checks

4. **Meeting Detection & Scheduling**: Detects meeting requests and automatically creates calendar events with Google Calendar integration

5. **Follow-up Management**: Tracks conversations and sends timely follow-ups when no response is received

6. **Knowledge Base Integration**: Uses your company information to provide accurate, consistent responses

7. **Thread Context Awareness**: Maintains conversation history to avoid repetitive information

8. **OAuth Integration**: Secure Gmail and Google Calendar integration with automatic token refresh""",
        "category": "Product",
        "tags": ["features", "capabilities", "product", "functionality"]
    },
    {
        "title": "Pricing Information",
        "content": """AI Email Assistant Pricing Plans:

**Starter Plan - $29/month**
- 500 emails/month
- Basic intent classification
- Manual draft review
- Email thread tracking
- 1 email account
- Email support

**Professional Plan - $79/month** (Most Popular)
- 2,000 emails/month
- Advanced AI classification
- Auto-reply for approved intents
- Meeting detection & calendar sync
- Follow-up automation
- 3 email accounts
- Priority support
- Custom intents & knowledge base

**Business Plan - $199/month**
- 10,000 emails/month
- All Professional features
- Advanced analytics
- Team collaboration
- Unlimited email accounts
- Custom AI training
- Dedicated account manager
- API access

**Enterprise Plan - Custom Pricing**
- Unlimited emails
- On-premise deployment option
- Custom integrations
- SLA guarantee
- White-label options
- Advanced security features

All plans include a 14-day free trial. Annual billing saves 20%.""",
        "category": "Pricing",
        "tags": ["pricing", "plans", "cost", "subscription"]
    },
    {
        "title": "Getting Started Guide",
        "content": """How to Get Started with AI Email Assistant:

**Step 1: Connect Your Email**
- Click "Email Accounts" in the sidebar
- Select "Connect Gmail"
- Authorize access via Google OAuth
- Your emails will start syncing automatically

**Step 2: Connect Calendar (Optional)**
- Click "Calendar Providers" in the sidebar
- Select "Connect Google Calendar"
- Authorize calendar access
- Meeting detection will now create calendar events

**Step 3: Set Up Intents**
- Navigate to "Intents" page
- Review pre-configured intents
- Customize keywords and prompts for your use case
- Enable auto-send for intents you trust

**Step 4: Build Your Knowledge Base**
- Go to "Knowledge Base" page
- Add information about your company, products, services
- Include FAQs, policies, and common information
- Tag entries for easy retrieval

**Step 5: Test the System**
- Send a test email to your connected account
- Watch as it gets classified, drafted, and processed
- Review the draft in the "Emails" page
- Adjust intents and knowledge base as needed

**Step 6: Enable Auto-Reply**
- Once comfortable with draft quality
- Enable auto-send for specific intents
- System will automatically respond within 60 seconds
- You maintain full control and visibility""",
        "category": "Documentation",
        "tags": ["getting started", "setup", "tutorial", "onboarding"]
    },
    {
        "title": "Support and Contact",
        "content": """Getting Help with AI Email Assistant:

**Documentation**
- User Guide: docs.aiemailassistant.com
- Video Tutorials: youtube.com/aiemailassistant
- FAQ: help.aiemailassistant.com

**Support Channels**
- Email: support@aiemailassistant.com (Response within 24 hours)
- Live Chat: Available Mon-Fri 9am-6pm EST
- Priority Support: For Professional+ plans (Response within 4 hours)
- Emergency Support: For Business+ plans (24/7 availability)

**Common Issues**
- **OAuth Connection Failed**: Ensure you've granted all required permissions. Try disconnecting and reconnecting.
- **Emails Not Syncing**: Check that your email account is active in settings. Worker runs every 60 seconds.
- **Drafts Not Generated**: Verify you have intents configured and knowledge base populated.
- **Auto-send Not Working**: Check that the intent has auto_send enabled and draft passes validation.

**Community**
- Discord: discord.gg/aiemailassistant
- Community Forum: community.aiemailassistant.com
- Feature Requests: feedback.aiemailassistant.com

**Technical Support**
For API integration, webhook setup, or custom development needs, contact: dev@aiemailassistant.com""",
        "category": "Support",
        "tags": ["support", "help", "contact", "troubleshooting"]
    },
    {
        "title": "Security and Privacy",
        "content": """AI Email Assistant Security & Privacy:

**Data Security**
- End-to-end encryption for all data in transit (TLS 1.3)
- AES-256 encryption for data at rest
- OAuth 2.0 secure authentication
- No storage of email passwords
- Regular security audits and penetration testing
- SOC 2 Type II certified

**Privacy Commitments**
- We never read your emails for marketing purposes
- AI processing happens in secure, isolated environments
- No data sharing with third parties
- No training on your private data
- GDPR and CCPA compliant
- Right to deletion honored within 30 days

**Data Access**
- Only you can access your email data
- Our AI processes emails only for generating drafts
- Staff access requires explicit user permission
- All access is logged and auditable
- Multi-factor authentication available

**OAuth Permissions**
- Gmail: Read emails, send emails (required for core functionality)
- Calendar: Read/write events (required for meeting scheduling)
- Tokens stored encrypted and refreshed automatically
- You can revoke access anytime via Google account settings

**Compliance**
- HIPAA compliant (Business plan+)
- GDPR compliant (all regions)
- CCPA compliant (California users)
- Regular third-party audits
- Data Processing Agreements available

**Data Retention**
- Active emails retained for 90 days
- Archived emails retained per your settings
- Knowledge base retained until deleted
- Account deletion removes all data within 30 days

For security inquiries: security@aiemailassistant.com""",
        "category": "Security",
        "tags": ["security", "privacy", "compliance", "gdpr", "encryption"]
    }
]


async def create_seed_data():
    """Create seed data for the specified user"""
    
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client.email_assistant_db
    
    try:
        # Find user
        user = await db.users.find_one({"email": USER_EMAIL})
        if not user:
            print(f"❌ User {USER_EMAIL} not found")
            return
        
        user_id = user['id']
        print(f"✓ Found user: {user_id}")
        
        # Delete existing intents and knowledge base
        deleted_intents = await db.intents.delete_many({"user_id": user_id})
        print(f"✓ Deleted {deleted_intents.deleted_count} existing intents")
        
        deleted_kb = await db.knowledge_base.delete_many({"user_id": user_id})
        print(f"✓ Deleted {deleted_kb.deleted_count} existing knowledge base entries")
        
        # Create intents
        print("\n📋 Creating Intents...")
        for intent_data in INTENTS:
            intent = {
                "id": f"intent_{intent_data['name'].lower().replace(' ', '_')}_{user_id[:8]}",
                "user_id": user_id,
                "name": intent_data["name"],
                "description": intent_data["description"],
                "prompt": intent_data["prompt"],
                "keywords": intent_data["keywords"],
                "auto_send": intent_data["auto_send"],
                "priority": intent_data["priority"],
                "is_default": intent_data.get("is_default", False),
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            await db.intents.insert_one(intent)
            print(f"  ✓ {intent['name']} (Priority: {intent['priority']}, Auto-send: {intent['auto_send']})")
        
        # Create knowledge base entries
        print("\n📚 Creating Knowledge Base Entries...")
        for kb_data in KNOWLEDGE_BASE:
            kb_entry = {
                "id": f"kb_{kb_data['title'].lower().replace(' ', '_')}_{user_id[:8]}",
                "user_id": user_id,
                "title": kb_data["title"],
                "content": kb_data["content"],
                "category": kb_data["category"],
                "tags": kb_data["tags"],
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            await db.knowledge_base.insert_one(kb_entry)
            print(f"  ✓ {kb_entry['title']} ({kb_entry['category']})")
        
        # Verify creation
        intents_count = await db.intents.count_documents({"user_id": user_id})
        kb_count = await db.knowledge_base.count_documents({"user_id": user_id})
        
        print(f"\n🎉 Seed Data Created Successfully!")
        print(f"   • {intents_count} Intents")
        print(f"   • {kb_count} Knowledge Base Entries")
        print(f"\n✅ User {USER_EMAIL} is ready to use the system!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(create_seed_data())
