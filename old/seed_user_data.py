"""
Seed data script for user: amits.joys@gmail.com
Creates intents and knowledge base entries
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime, timezone
import uuid

# Get MongoDB connection
MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(MONGO_URL)
db = client['email_assistant_db']

USER_EMAIL = "amits.joys@gmail.com"
USER_ID = "2d41b84c-6be3-4c44-9263-8e14fe2483b6"

async def seed_intents():
    """Create intents for the user"""
    print(f"\n{'='*60}")
    print(f"Creating Intents for {USER_EMAIL}")
    print(f"{'='*60}\n")
    
    intents = [
        {
            "id": str(uuid.uuid4()),
            "user_id": USER_ID,
            "name": "Meeting Request",
            "description": "Handles meeting and scheduling requests professionally",
            "keywords": ["meeting", "schedule", "calendar", "appointment", "call", "zoom", "teams", "meet", "available", "time", "when can we"],
            "prompt": """When responding to meeting requests:
1. Acknowledge the meeting request warmly
2. If a calendar event was created, include ALL event details:
   - Exact date and time with timezone
   - Google Meet joining link (if available)
   - Calendar view link
   - Any attendees
3. Be professional but friendly
4. Keep response concise and clear
5. Include the meeting details in the SAME email reply, not as a separate email""",
            "priority": 10,
            "auto_send": True,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": USER_ID,
            "name": "Meeting Reschedule",
            "description": "Handles requests to reschedule or change meeting times",
            "keywords": ["reschedule", "change meeting", "different time", "move meeting", "postpone", "delay meeting"],
            "prompt": """When handling reschedule requests:
1. Acknowledge the request to reschedule
2. Confirm you'll update the meeting
3. Provide the new meeting details with updated time
4. Include the updated calendar link
5. Be understanding and flexible""",
            "priority": 9,
            "auto_send": True,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": USER_ID,
            "name": "Support Request",
            "description": "Handles technical issues and support questions with empathy",
            "keywords": ["issue", "problem", "error", "help", "support", "not working", "bug", "broken", "trouble", "cannot", "can't", "doesn't work"],
            "prompt": """When handling support requests:
1. Show empathy and understanding
2. Acknowledge the issue clearly
3. Provide step-by-step troubleshooting if possible
4. Offer to escalate if needed
5. Be patient and helpful""",
            "priority": 8,
            "auto_send": True,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": USER_ID,
            "name": "Follow-up Request",
            "description": "Handles follow-up inquiries with context awareness",
            "keywords": ["follow up", "followup", "checking in", "status", "update", "any progress", "heard back"],
            "prompt": """When responding to follow-ups:
1. Reference the previous conversation
2. Provide current status or update
3. Be transparent about any delays
4. Give a clear next step or timeline
5. Maintain professionalism""",
            "priority": 7,
            "auto_send": True,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": USER_ID,
            "name": "Introduction",
            "description": "Handles networking and introduction emails warmly",
            "keywords": ["introduction", "introduce", "connection", "network", "reach out", "connect with", "nice to meet"],
            "prompt": """When responding to introductions:
1. Express enthusiasm about connecting
2. Introduce yourself professionally
3. Highlight relevant experience or interests
4. Suggest a way to continue the conversation
5. Be warm and welcoming""",
            "priority": 6,
            "auto_send": True,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": USER_ID,
            "name": "General Inquiry",
            "description": "Handles general questions using knowledge base",
            "keywords": ["question", "inquiry", "information", "tell me", "help", "how", "what", "when", "where", "why", "explain"],
            "prompt": """When answering general questions:
1. Use knowledge base information when available
2. Be clear and concise
3. Provide relevant details
4. Offer additional resources if helpful
5. Encourage follow-up questions""",
            "priority": 5,
            "auto_send": True,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": USER_ID,
            "name": "Thank You",
            "description": "Responds graciously to appreciation messages",
            "keywords": ["thank you", "thanks", "appreciate", "grateful", "kudos"],
            "prompt": """When responding to thank you messages:
1. Acknowledge their appreciation warmly
2. Express that you're happy to help
3. Keep it brief and genuine
4. Offer continued assistance
5. Be gracious""",
            "priority": 4,
            "auto_send": True,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": USER_ID,
            "name": "Urgent Request",
            "description": "Flags urgent matters for immediate human review",
            "keywords": ["urgent", "asap", "immediately", "emergency", "critical", "right now", "urgent matter"],
            "prompt": """When detecting urgent requests:
1. This should NOT auto-send - requires human review
2. Flag for immediate attention
3. Prepare a draft acknowledging urgency
4. Note the specific urgent matter
5. Wait for human approval before sending""",
            "priority": 10,
            "auto_send": False,  # Manual review required
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    for intent in intents:
        # Check if intent already exists
        existing = await db.intents.find_one({"name": intent["name"], "user_id": USER_ID})
        if existing:
            print(f"✓ Intent '{intent['name']}' already exists (skipping)")
        else:
            await db.intents.insert_one(intent)
            auto_status = "✅ Auto-send" if intent["auto_send"] else "⏸️  Manual review"
            print(f"✓ Created intent: '{intent['name']}' (Priority: {intent['priority']}, {auto_status})")
    
    print(f"\n✅ Intents setup complete!\n")


async def seed_knowledge_base():
    """Create knowledge base entries for the user"""
    print(f"\n{'='*60}")
    print(f"Creating Knowledge Base for {USER_EMAIL}")
    print(f"{'='*60}\n")
    
    kb_entries = [
        {
            "id": str(uuid.uuid4()),
            "user_id": USER_ID,
            "title": "Company Overview",
            "content": """Our company is an AI-powered email assistant service that helps professionals manage their inbox intelligently. We were founded in 2024 with the mission to save people time and improve communication quality through artificial intelligence.

Key Features:
- Automated email responses with AI
- Intent detection and classification
- Meeting scheduling with calendar integration
- Context-aware replies using conversation history
- Smart follow-up management
- Knowledge base integration for accurate responses""",
            "category": "Company Information",
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": USER_ID,
            "title": "Product Features",
            "content": """Complete Feature List:

1. EMAIL MANAGEMENT:
   - Automatic email polling from Gmail
   - Intent classification using AI
   - Draft generation with validation
   - Auto-send for approved intents
   - Thread-aware responses
   - Smart follow-up scheduling

2. CALENDAR INTEGRATION:
   - Google Calendar sync
   - Automatic meeting detection
   - Event creation with Google Meet links
   - Conflict detection and warnings
   - Event reminders
   - Reschedule handling

3. AI CAPABILITIES:
   - Natural language understanding
   - Context-aware responses
   - Knowledge base integration
   - Multi-attempt validation with retry logic
   - Thread context tracking
   - Meeting detail extraction

4. AUTOMATION:
   - Background workers for continuous processing
   - Automatic reply detection and follow-up cancellation
   - Scheduled reminders
   - Token usage tracking""",
            "category": "Product",
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": USER_ID,
            "title": "Meeting and Calendar Features",
            "content": """Calendar and Meeting Management:

AUTOMATIC MEETING DETECTION:
- AI analyzes emails for meeting requests
- Extracts date, time, timezone, location, and attendees
- Detects confidence level (0.8+ for clear requests)
- Provides thread context to avoid duplicate events

GOOGLE CALENDAR INTEGRATION:
- Automatically creates events in Google Calendar
- Generates Google Meet video conferencing links
- Syncs with your calendar in real-time
- Provides calendar view links for attendees

EVENT DETAILS IN REPLIES:
- Meeting confirmation emails include ALL details:
  * Event title and description
  * Date, time, and timezone
  * Google Meet joining link
  * Calendar view link
  * List of attendees
- All details sent in SAME email thread (not separate emails)

CONFLICT HANDLING:
- Detects overlapping calendar events
- Creates events anyway for your review
- Warns about conflicts in confirmation email
- Allows manual resolution

REMINDERS:
- Automatic reminders sent 1 hour before events
- Email notifications with event details
- Helps ensure you never miss a meeting

RESCHEDULING:
- Detects reschedule requests automatically
- Updates events in Google Calendar
- Sends updated details to all attendees
- Maintains event history""",
            "category": "Meetings",
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": USER_ID,
            "title": "Pricing Information",
            "content": """Pricing Tiers:

STARTER PLAN: $29/month
- 1 email account
- 500 emails processed/month
- Basic intent detection
- Knowledge base (up to 10 entries)
- Email support

PROFESSIONAL PLAN: $79/month (Most Popular)
- 3 email accounts
- 2,000 emails processed/month
- Advanced AI features
- Unlimited knowledge base entries
- Calendar integration
- Priority email support
- Custom intents

BUSINESS PLAN: $199/month
- 10 email accounts
- 10,000 emails processed/month
- All Professional features
- Team collaboration
- API access
- Dedicated account manager
- Phone support
- Custom integrations

ENTERPRISE: Custom Pricing
- Unlimited email accounts
- Unlimited emails
- Custom deployment options
- Advanced security features
- SLA guarantees
- Custom AI training
- 24/7 support""",
            "category": "Pricing",
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": USER_ID,
            "title": "Getting Started Guide",
            "content": """Quick Start Guide:

STEP 1: CONNECT EMAIL ACCOUNT
- Go to Email Accounts page
- Click "Connect Email Account"
- Choose Gmail OAuth
- Authorize access
- Email polling starts automatically every 60 seconds

STEP 2: CONNECT GOOGLE CALENDAR (OPTIONAL)
- Go to Calendar Providers page
- Click "Connect Google Calendar"
- Authorize calendar access
- Calendar integration activated

STEP 3: SET UP INTENTS
- Review default intents (Meeting Request, Support, etc.)
- Customize keywords for your needs
- Set auto-send preferences
- Add custom intents if needed

STEP 4: ADD KNOWLEDGE BASE
- Go to Knowledge Base page
- Add information about your company/services
- Include FAQs and common responses
- AI will use this information in replies

STEP 5: TEST THE SYSTEM
- Send a test email to your connected account
- Check Emails page to see processing
- Review draft generation
- Verify auto-send if enabled

STEP 6: CUSTOMIZE SETTINGS
- Set your signature
- Adjust polling frequency if needed
- Configure follow-up timing
- Set reminder preferences""",
            "category": "Documentation",
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": USER_ID,
            "title": "Support and Contact",
            "content": """Customer Support:

SUPPORT CHANNELS:
- Email: support@emailassistant.ai
- Response time: Within 24 hours
- Priority support: Within 4 hours (Pro/Business plans)
- Emergency: Within 1 hour (Enterprise only)

HELP RESOURCES:
- Documentation: docs.emailassistant.ai
- Video tutorials: Available in dashboard
- Knowledge base: kb.emailassistant.ai
- Community forum: community.emailassistant.ai

COMMON ISSUES:

1. Email Not Polling:
   - Check OAuth connection is active
   - Verify email account permissions
   - Check background workers are running
   - Review error logs

2. Calendar Events Not Creating:
   - Ensure Google Calendar is connected
   - Check calendar provider is active
   - Verify meeting detection threshold
   - Review meeting confidence score

3. Auto-Send Not Working:
   - Confirm intent has auto_send enabled
   - Check draft validation passed
   - Verify email account has send permissions
   - Review intent matching keywords

4. Draft Quality Issues:
   - Add more knowledge base entries
   - Customize intent prompts
   - Review thread context settings
   - Adjust AI temperature if needed

REPORTING BUGS:
Include: Error message, timestamp, email ID, expected vs actual behavior""",
            "category": "Support",
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": USER_ID,
            "title": "Security and Privacy",
            "content": """Security & Privacy Policy:

DATA SECURITY:
- End-to-end encryption for all email data
- OAuth 2.0 secure authentication
- No password storage (token-based only)
- Regular security audits
- SOC 2 Type II compliant
- GDPR compliant

YOUR DATA:
- You own all your data
- Data never shared with third parties
- Can export data anytime
- Can delete account and all data instantly
- Email content processed securely
- AI processing done in secure environment

PRIVACY FEATURES:
- Emails processed only for your account
- No cross-customer data sharing
- AI models don't retain your data
- Audit logs available
- Access controls and permissions
- Two-factor authentication available

OAUTH PERMISSIONS:
We request only necessary permissions:
- Gmail: Read and send emails (gmail.readonly, gmail.send)
- Calendar: Read and write events (calendar.events)
- No access to: Contacts, Drive, or other Google services

TOKEN MANAGEMENT:
- Tokens encrypted at rest
- Automatic token refresh
- Secure token storage
- Tokens revocable anytime
- Session timeout after 24 hours

COMPLIANCE:
- GDPR (Europe)
- CCPA (California)
- PIPEDA (Canada)
- SOC 2 Type II
- HIPAA available (Enterprise only)""",
            "category": "Security",
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    for kb in kb_entries:
        # Check if KB entry already exists
        existing = await db.knowledge_base.find_one({"title": kb["title"], "user_id": USER_ID})
        if existing:
            print(f"✓ KB entry '{kb['title']}' already exists (skipping)")
        else:
            await db.knowledge_base.insert_one(kb)
            print(f"✓ Created KB entry: '{kb['title']}' ({kb['category']})")
    
    print(f"\n✅ Knowledge base setup complete!\n")


async def main():
    print(f"\n{'='*60}")
    print(f"SEED DATA SCRIPT")
    print(f"User: {USER_EMAIL}")
    print(f"User ID: {USER_ID}")
    print(f"{'='*60}\n")
    
    try:
        # Verify user exists
        user = await db.users.find_one({"id": USER_ID})
        if not user:
            print(f"❌ Error: User {USER_EMAIL} not found!")
            return
        
        print(f"✅ User verified: {user.get('email')}\n")
        
        # Seed intents
        await seed_intents()
        
        # Seed knowledge base
        await seed_knowledge_base()
        
        # Summary
        intent_count = await db.intents.count_documents({"user_id": USER_ID})
        kb_count = await db.knowledge_base.count_documents({"user_id": USER_ID})
        auto_send_count = await db.intents.count_documents({"user_id": USER_ID, "auto_send": True})
        
        print(f"\n{'='*60}")
        print(f"SEED DATA SUMMARY")
        print(f"{'='*60}")
        print(f"✅ Total Intents: {intent_count}")
        print(f"✅ Auto-send Enabled: {auto_send_count}")
        print(f"✅ Manual Review: {intent_count - auto_send_count}")
        print(f"✅ Knowledge Base Entries: {kb_count}")
        print(f"{'='*60}\n")
        
        print("🎉 Seed data completed successfully!")
        print("The system is now ready for production use.\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(main())
