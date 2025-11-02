"""Create seed data for specific user"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import uuid
from config import config

async def create_seed_data_for_user(email: str):
    """Create seed data for a specific user"""
    
    client = AsyncIOMotorClient(config.MONGO_URL)
    db = client[config.DB_NAME]
    
    # Find user
    user = await db.users.find_one({"email": email})
    if not user:
        print(f"✗ User not found: {email}")
        client.close()
        return
    
    user_id = user['id']
    print(f"✓ Creating seed data for: {email} (ID: {user_id})")
    print("=" * 60)
    
    # ============================================
    # INTENTS - Various email response scenarios
    # ============================================
    intents = [
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Meeting Request",
            "description": "Handle meeting and scheduling requests with calendar integration",
            "prompt": """You are responding to a meeting request. Be professional and courteous.

Guidelines:
- Acknowledge the meeting request warmly
- Confirm you're checking calendar availability
- If meeting details are provided, acknowledge them
- Ask for any missing information (date, time, duration, attendees)
- Keep response concise and professional
- Express willingness to coordinate the meeting

Tone: Professional, helpful, and organized

IMPORTANT: Do not make up availability or suggest times. The system will automatically check the calendar and create the event.""",
            "keywords": ["meeting", "schedule", "calendar", "appointment", "call", "zoom", "teams", "discuss", "available", "availability", "meet", "conference", "video call", "sync up", "catch up", "connect"],
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
- If you don't have information, politely say so
- Maintain a friendly and professional tone
- Keep response focused on the question

Tone: Friendly, professional, and helpful""",
            "keywords": ["question", "inquiry", "information", "help", "how", "what", "when", "where", "why", "who", "could you", "can you"],
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
            "keywords": ["issue", "problem", "error", "help", "support", "not working", "broken", "fix", "bug", "assistance", "trouble"],
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
            "prompt": """You are responding to a follow-up request. Be responsive and thorough.

Guidelines:
- Acknowledge the follow-up request
- Provide status update on the original inquiry
- Reference previous conversation context
- Give clear next steps or timeline
- Be transparent about any delays

Tone: Professional, transparent, and accountable""",
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
            "description": "New contact introductions and networking",
            "prompt": """You are responding to an introduction or networking request. Be warm and professional.

Guidelines:
- Thank them for reaching out
- Express interest in connecting
- Provide brief background about yourself/company
- Suggest next steps for collaboration
- Keep tone welcoming and open

Tone: Warm, professional, and welcoming""",
            "keywords": ["introduction", "introduce", "connection", "network", "nice to meet", "reaching out", "connect"],
            "auto_send": True,
            "priority": 6,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Thank You",
            "description": "Acknowledgment and gratitude",
            "prompt": """You are responding to a thank you message. Be gracious and warm.

Guidelines:
- Acknowledge their gratitude
- Express your pleasure in helping
- Offer continued support if needed
- Keep it brief and genuine
- Maintain positive tone

Tone: Warm, genuine, and professional""",
            "keywords": ["thank you", "thanks", "appreciate", "grateful", "gratitude", "thank"],
            "auto_send": True,
            "priority": 4,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Urgent Request",
            "description": "High-priority or urgent matters requiring immediate attention",
            "prompt": """You are responding to an urgent request. Be prompt and action-oriented.

Guidelines:
- Acknowledge the urgency immediately
- Provide immediate next steps
- Set clear expectations for response time
- Escalate if necessary
- Be concise but thorough

Tone: Professional, urgent, and action-oriented

Note: This requires manual review before sending.""",
            "keywords": ["urgent", "asap", "immediately", "emergency", "critical", "time-sensitive", "high priority"],
            "auto_send": False,  # Manual review required
            "priority": 10,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Meeting Reschedule",
            "description": "Requests to reschedule or update existing meetings",
            "prompt": """You are responding to a meeting reschedule request. Be flexible and accommodating.

Guidelines:
- Acknowledge the reschedule request
- Express understanding and flexibility
- Confirm you'll update the calendar event
- Ask for preferred new time if not provided
- Confirm once the calendar is updated

Tone: Understanding, flexible, and professional

IMPORTANT: The system will automatically update the calendar event if new time is provided.""",
            "keywords": ["reschedule", "change meeting", "update meeting", "move meeting", "different time", "conflict", "can't make it"],
            "auto_send": True,
            "priority": 9,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    # Insert intents
    result = await db.intents.insert_many(intents)
    print(f"✓ Created {len(result.inserted_ids)} intents")
    for intent in intents:
        print(f"  - {intent['name']} (Priority: {intent['priority']}, Auto-send: {intent['auto_send']})")
    
    # ============================================
    # KNOWLEDGE BASE - Company/User Information
    # ============================================
    knowledge_base = [
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Company Overview",
            "content": """AI Email Assistant is a comprehensive email automation platform that helps professionals manage their inbox intelligently.

Key Features:
- AI-powered email classification and intent detection
- Automated draft generation with context awareness
- Calendar integration for automatic meeting scheduling
- Smart follow-up management
- Real-time email monitoring and processing

Our mission is to help professionals focus on high-value work by automating routine email communications while maintaining quality and personalization.""",
            "category": "Company Information",
            "tags": ["company", "overview", "mission", "features"],
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Product Features",
            "content": """AI Email Assistant offers comprehensive email automation capabilities:

EMAIL MANAGEMENT:
- Automatic email classification by intent
- AI-powered draft generation
- Multi-level validation system
- Thread context awareness
- Reply detection and follow-up cancellation

CALENDAR INTEGRATION:
- Automatic meeting detection from emails
- Calendar event creation with conflict detection
- Meeting reminder system
- Event update and rescheduling support
- Timezone-aware scheduling

AI CAPABILITIES:
- Intent classification using advanced NLP
- Context-aware draft generation
- Draft validation with quality checks
- Meeting detail extraction
- Sentiment analysis

AUTOMATION:
- Auto-send for trusted intents
- Scheduled follow-ups
- Reminder notifications
- Background email polling
- Token management and refresh""",
            "category": "Product",
            "tags": ["features", "capabilities", "automation", "ai"],
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Meeting and Calendar Features",
            "content": """Our calendar integration provides seamless meeting management:

MEETING DETECTION:
- Automatically detects meeting requests in emails
- Extracts date, time, duration, and attendees
- Identifies meeting topics and agenda
- Supports multiple timezone formats
- Recognizes various date/time expressions

CALENDAR INTEGRATION:
- Creates events in Google Calendar
- Checks for scheduling conflicts
- Suggests alternative times if conflicts exist
- Updates existing events when rescheduled
- Synchronizes across all connected calendars

REMINDERS & NOTIFICATIONS:
- Sends reminders 1 hour before meetings
- Email notifications with meeting details
- Follow-up reminders for upcoming events
- Cancellation notifications

CONFLICT HANDLING:
- Detects overlapping meetings
- Suggests alternative time slots
- Allows manual override for important meetings
- Updates all attendees on changes""",
            "category": "Calendar",
            "tags": ["calendar", "meetings", "scheduling", "conflicts"],
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Getting Started Guide",
            "content": """Quick start guide for AI Email Assistant:

SETUP STEPS:
1. Create account and log in
2. Connect email account via OAuth (Gmail or Outlook)
3. Connect calendar provider (Google Calendar)
4. Configure intents for different email types
5. Add knowledge base entries for context
6. Set up auto-send rules and priorities

CONNECTING EMAIL:
- Go to Email Accounts page
- Click "Connect Gmail" or "Connect Outlook"
- Authorize OAuth permissions
- Wait for initial email sync (happens automatically)

CONNECTING CALENDAR:
- Go to Calendar Providers page
- Click "Connect Google Calendar"
- Authorize calendar permissions
- System will start detecting meetings

CUSTOMIZATION:
- Create custom intents for your common email types
- Add knowledge base entries about your company/role
- Set auto-send preferences
- Configure follow-up schedules
- Adjust priority levels""",
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
            "content": """Support resources for AI Email Assistant:

GETTING HELP:
- Email: support@aiemailassistant.com
- Response time: 24 hours for standard inquiries
- Priority support available for urgent issues

TROUBLESHOOTING:
- Check OAuth token status in account settings
- Verify calendar permissions are granted
- Review intent keywords for proper matching
- Check email polling logs in Live Monitoring
- Ensure background workers are running

COMMON ISSUES:
- "No emails being processed": Check OAuth connection
- "Meetings not detected": Verify calendar is connected
- "Drafts not auto-sending": Check intent auto_send flag
- "Follow-ups not working": Verify follow-up schedule

DOCUMENTATION:
- Full API documentation available at /api/docs
- User guide and tutorials on our website
- Video walkthroughs for common tasks
- FAQ section for quick answers""",
            "category": "Support",
            "tags": ["support", "help", "troubleshooting", "contact"],
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Security and Privacy",
            "content": """Security and privacy measures in AI Email Assistant:

DATA SECURITY:
- OAuth 2.0 for secure authentication
- Token encryption at rest
- Encrypted database connections
- Regular security audits
- SOC 2 compliant infrastructure

PRIVACY:
- No email content is stored permanently
- AI processing uses encrypted connections
- No third-party data sharing
- GDPR and CCPA compliant
- Data deletion on account closure

ACCESS CONTROL:
- User-specific data isolation
- Role-based permissions
- Secure API authentication
- Rate limiting and abuse prevention
- Audit logging for all actions

OAUTH SCOPES:
- Email: Read and send permissions only
- Calendar: Event creation and read access
- No access to other Google/Microsoft services
- Tokens refreshed automatically
- Revocable at any time through Google/Microsoft""",
            "category": "Security",
            "tags": ["security", "privacy", "compliance", "encryption"],
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    # Insert knowledge base
    result = await db.knowledge_base.insert_many(knowledge_base)
    print(f"\n✓ Created {len(result.inserted_ids)} knowledge base entries")
    for kb in knowledge_base:
        print(f"  - {kb['title']} ({kb['category']})")
    
    print("\n" + "=" * 60)
    print("✓ Seed data creation complete!")
    print("=" * 60)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(create_seed_data_for_user("amits.joys@gmail.com"))
