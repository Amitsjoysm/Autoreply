"""
Seed data creation script for user amits.joys@gmail.com
Creates comprehensive Intents and Knowledge Base entries
"""
import os
import sys
from pymongo import MongoClient
from datetime import datetime
import uuid

# Connect to MongoDB
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
db_name = os.environ.get('DB_NAME', 'email_assistant_db')
client = MongoClient(mongo_url)
db = client[db_name]

# Find user
user = db.users.find_one({"email": "amits.joys@gmail.com"})
if not user:
    print("❌ User not found!")
    sys.exit(1)

user_id = user["id"]
print(f"✅ Found user: {user['email']} (ID: {user_id})")

# Remove any existing seed data
print("\n🗑️  Removing existing seed data...")
deleted_intents = db.intents.delete_many({"user_id": user_id})
deleted_kb = db.knowledge_base.delete_many({"user_id": user_id})
print(f"   Deleted {deleted_intents.deleted_count} intents")
print(f"   Deleted {deleted_kb.deleted_count} knowledge base entries")

# Create comprehensive Intents
print("\n📋 Creating Intents...")

intents = [
    {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "name": "Meeting Request",
        "description": "Handles meeting scheduling requests and calendar coordination",
        "keywords": ["meeting", "schedule", "calendar", "appointment", "call", "zoom", "teams", "meet", "conference"],
        "prompt": """You are handling a meeting request. The sender wants to schedule a meeting or call.

Key Points:
- Be professional and courteous
- Confirm availability for the proposed time
- If no specific time mentioned, suggest 2-3 time slots
- Include timezone information
- Mention meeting platform (Zoom, Teams, Google Meet) if applicable
- Confirm meeting agenda if provided
- Ask for any additional details needed

Format your response professionally with:
1. Acknowledgment of their request
2. Confirmation or alternative time slots
3. Meeting details summary
4. Next steps

Keep the tone warm yet professional.""",
        "priority": 10,
        "is_active": True,
        "auto_send": True,
        "is_default": False,
        "created_at": datetime.utcnow().isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "name": "Support Request",
        "description": "Handles technical support and troubleshooting inquiries",
        "keywords": ["issue", "problem", "error", "help", "support", "not working", "bug", "broken", "fix", "trouble"],
        "prompt": """You are handling a support request. The sender is experiencing an issue and needs help.

Key Points:
- Show empathy and understanding
- Acknowledge the problem clearly
- Provide step-by-step troubleshooting if applicable
- Offer to escalate if needed
- Include relevant documentation links
- Set expectations for resolution timeline
- Ask for additional details if needed (screenshots, error messages, etc.)

Format your response with:
1. Empathetic acknowledgment
2. Understanding of the issue
3. Initial troubleshooting steps or solution
4. Timeline for resolution
5. Contact information for urgent issues

Keep tone helpful and reassuring.""",
        "priority": 8,
        "is_active": True,
        "auto_send": True,
        "is_default": False,
        "created_at": datetime.utcnow().isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "name": "General Inquiry",
        "description": "Handles general questions about products, services, or company",
        "keywords": ["question", "inquiry", "information", "help", "how", "what", "when", "where", "why", "details"],
        "prompt": """You are handling a general inquiry. The sender wants information about our products, services, or company.

Key Points:
- Provide clear and comprehensive information
- Use knowledge base content to ensure accuracy
- Be informative yet concise
- Offer additional resources or documentation
- Invite further questions
- Maintain professional yet friendly tone

Format your response with:
1. Direct answer to their question
2. Supporting details from knowledge base
3. Additional relevant information
4. Links to more resources if applicable
5. Invitation for follow-up questions

Keep the tone informative and helpful.""",
        "priority": 5,
        "is_active": True,
        "auto_send": True,
        "is_default": False,
        "created_at": datetime.utcnow().isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "name": "Follow-up Request",
        "description": "Handles follow-up inquiries on previous conversations or requests",
        "keywords": ["follow up", "followup", "checking in", "status", "update", "progress", "any news"],
        "prompt": """You are handling a follow-up request. The sender is checking on the status of a previous inquiry or request.

Key Points:
- Reference previous conversation if available
- Provide current status update
- Be transparent about timeline
- Show appreciation for their patience
- Set clear next steps and expectations
- Include relevant updates or progress made

Format your response with:
1. Acknowledgment of their follow-up
2. Current status summary
3. Progress or updates made
4. Expected timeline for completion
5. Next steps and communication plan

Keep tone appreciative and transparent.""",
        "priority": 7,
        "is_active": True,
        "auto_send": True,
        "is_default": False,
        "created_at": datetime.utcnow().isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "name": "Introduction",
        "description": "Handles introduction emails and networking requests",
        "keywords": ["introduction", "introduce", "connection", "network", "reach out", "get to know", "collaborate"],
        "prompt": """You are handling an introduction or networking request. The sender wants to connect or introduce themselves.

Key Points:
- Respond warmly and professionally
- Show interest in the connection
- Mention relevant mutual interests or connections
- Suggest next steps (call, meeting, email exchange)
- Be open to collaboration opportunities
- Share relevant background about yourself/company

Format your response with:
1. Warm greeting and appreciation for reaching out
2. Brief introduction or acknowledgment
3. Expression of interest in connecting
4. Suggested next steps
5. Professional closing

Keep tone friendly, open, and professional.""",
        "priority": 6,
        "is_active": True,
        "auto_send": True,
        "is_default": False,
        "created_at": datetime.utcnow().isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "name": "Thank You",
        "description": "Handles thank you messages and appreciation emails",
        "keywords": ["thank you", "thanks", "appreciate", "grateful", "appreciation", "gratitude"],
        "prompt": """You are handling a thank you message. The sender is expressing gratitude or appreciation.

Key Points:
- Respond graciously and warmly
- Acknowledge their appreciation
- Reciprocate positivity
- Keep response brief but genuine
- Maintain professional relationship
- Offer continued support if relevant

Format your response with:
1. Gracious acknowledgment
2. Brief, genuine response
3. Reciprocal appreciation if applicable
4. Offer of continued support
5. Warm closing

Keep tone warm, genuine, and professional.""",
        "priority": 4,
        "is_active": True,
        "auto_send": True,
        "is_default": False,
        "created_at": datetime.utcnow().isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "name": "Urgent Request",
        "description": "Handles urgent or time-sensitive requests requiring immediate attention",
        "keywords": ["urgent", "asap", "immediately", "emergency", "critical", "important", "now", "right away"],
        "prompt": """You are handling an urgent request. The sender needs immediate attention or response.

Key Points:
- Acknowledge urgency immediately
- Provide immediate next steps
- Set realistic expectations
- Escalate if necessary
- Include emergency contact information
- Be clear about timeline and actions

Format your response with:
1. Immediate acknowledgment of urgency
2. Current status or immediate action taken
3. Expected resolution timeline
4. Emergency contact information if needed
5. Follow-up plan

Keep tone professional, responsive, and reassuring.""",
        "priority": 10,
        "is_active": True,
        "auto_send": False,  # Manual review for urgent requests
        "is_default": False,
        "created_at": datetime.utcnow().isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "name": "Default",
        "description": "Default intent for emails that don't match specific categories",
        "keywords": [],  # No keywords - catches everything else
        "prompt": """You are responding to an email that doesn't clearly match any specific category.

Key Points:
- Use the knowledge base to provide accurate information
- Be helpful and professional
- Try to understand the sender's underlying need
- Ask clarifying questions if needed
- Provide relevant information based on available context
- Direct to appropriate resources
- Do not make assumptions or provide unverified information

Format your response with:
1. Acknowledgment of their email
2. Best attempt to address their query using available knowledge
3. Request for clarification if needed
4. Relevant resources or next steps
5. Professional closing

Keep tone professional, helpful, and open to clarification.""",
        "priority": 1,
        "is_active": True,
        "auto_send": True,
        "is_default": True,  # This is the default fallback intent
        "created_at": datetime.utcnow().isoformat()
    }
]

# Insert intents
for intent in intents:
    db.intents.insert_one(intent)
    print(f"   ✓ Created intent: {intent['name']} (Priority: {intent['priority']}, Auto-send: {intent['auto_send']})")

print(f"\n✅ Created {len(intents)} intents")

# Create comprehensive Knowledge Base
print("\n📚 Creating Knowledge Base entries...")

knowledge_base = [
    {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "title": "Company Overview",
        "content": """Our company is an AI-powered email management and assistant platform that helps professionals and businesses automate email responses, schedule meetings, and manage their inbox efficiently.

Founded in 2024, we specialize in intelligent email processing using advanced AI models to understand context, classify intents, and generate professional responses.

Key Features:
- Automated email classification and intent detection
- AI-generated draft responses with validation
- Smart calendar integration and meeting scheduling
- Follow-up management and reminders
- Knowledge base integration for accurate responses
- Multi-account email management
- OAuth-based secure authentication

Our mission is to help professionals reclaim their time by automating routine email tasks while maintaining personalization and professionalism in every response.

Contact Information:
- Email: support@emailassistant.com
- Website: www.emailassistant.com
- Support Hours: 24/7 automated, Business hours for human support""",
        "category": "Company Information",
        "tags": ["about", "company", "overview", "mission", "contact"],
        "is_active": True,
        "created_at": datetime.utcnow().isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "title": "Product Features",
        "content": """Email Assistant Platform - Complete Feature List

1. INTELLIGENT EMAIL PROCESSING
   - Automatic email classification by intent
   - Context-aware response generation
   - Multi-language support
   - Thread tracking and conversation management
   - Spam and priority detection

2. AI-POWERED RESPONSES
   - GPT-4 powered draft generation
   - Response validation before sending
   - Tone and style customization
   - Knowledge base integration for accuracy
   - Retry logic with improvement feedback

3. CALENDAR INTEGRATION
   - Google Calendar sync
   - Microsoft Calendar support
   - Automatic meeting detection from emails
   - Smart scheduling with conflict detection
   - Meeting link generation (Zoom, Google Meet)
   - Reminder notifications

4. AUTOMATION & WORKFLOWS
   - Auto-send based on confidence and intent
   - Follow-up management and scheduling
   - Email polling and real-time processing
   - Background workers for continuous operation
   - Customizable automation rules

5. SECURITY & PRIVACY
   - OAuth 2.0 authentication
   - Encrypted credential storage
   - Token auto-refresh
   - Secure API endpoints
   - GDPR compliant data handling

6. KNOWLEDGE BASE
   - Custom knowledge repository
   - Category-based organization
   - Tag-based search
   - Integration with response generation
   - Regular updates and versioning

7. USER INTERFACE
   - Modern, intuitive dashboard
   - Real-time email status tracking
   - Action history timeline
   - Detailed analytics and metrics
   - Mobile-responsive design""",
        "category": "Product",
        "tags": ["features", "capabilities", "functions", "what we do"],
        "is_active": True,
        "created_at": datetime.utcnow().isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "title": "Meeting and Calendar Features",
        "content": """Meeting Scheduling & Calendar Management

AUTOMATIC MEETING DETECTION:
- Detects meeting requests from email content
- Extracts date, time, and timezone information
- Identifies meeting participants
- Recognizes meeting types (call, in-person, video conference)

CALENDAR INTEGRATION:
- Google Calendar synchronization
- Microsoft Calendar support
- Real-time availability checking
- Conflict detection and warnings
- Multi-calendar management

MEETING COORDINATION:
- Automatic calendar event creation
- Google Meet link generation
- Zoom integration support
- Meeting invitation emails
- Attendee management
- Location details

SMART SCHEDULING:
- Timezone-aware scheduling
- Business hours consideration
- Buffer time between meetings
- Recurring meeting support
- Meeting rescheduling capability

NOTIFICATIONS & REMINDERS:
- Email reminders 1 hour before meetings
- Calendar notifications
- Follow-up emails after meetings
- Meeting change notifications

MEETING RESPONSE FORMAT:
All meeting confirmations include:
- Meeting title and agenda
- Date and time with timezone
- Duration
- Meeting link (Google Meet, Zoom, etc.)
- Calendar link for direct addition
- Attendee information
- Location details if applicable

Note: Meeting details are sent in the SAME thread as the original email request, maintaining conversation context.""",
        "category": "Meetings",
        "tags": ["meetings", "calendar", "scheduling", "appointments"],
        "is_active": True,
        "created_at": datetime.utcnow().isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "title": "Pricing Information",
        "content": """Email Assistant Platform - Pricing Plans

FREE TIER (Beta)
- Up to 100 emails per month
- 1 email account
- Basic intent classification
- Manual approval for all responses
- Community support
- Price: $0/month

PROFESSIONAL PLAN
- Up to 1,000 emails per month
- 3 email accounts
- Advanced AI responses
- Auto-send capability
- Calendar integration
- Knowledge base (10 entries)
- Email support
- Price: $29/month

BUSINESS PLAN
- Up to 5,000 emails per month
- 10 email accounts
- Priority AI processing
- Advanced automation rules
- Unlimited knowledge base
- Team collaboration features
- Priority support
- API access
- Price: $99/month

ENTERPRISE PLAN
- Unlimited emails
- Unlimited accounts
- Custom AI model training
- White-label option
- Dedicated support
- SLA guarantees
- Custom integrations
- On-premise deployment option
- Price: Custom (Contact sales)

ALL PLANS INCLUDE:
- 14-day free trial
- No credit card required for trial
- Cancel anytime
- Monthly or annual billing (20% discount on annual)
- Free migration assistance
- Regular updates and new features

CONTACT SALES:
- Email: sales@emailassistant.com
- Phone: +1 (555) 123-4567
- Schedule a demo: www.emailassistant.com/demo""",
        "category": "Pricing",
        "tags": ["pricing", "plans", "cost", "subscription", "payment"],
        "is_active": True,
        "created_at": datetime.utcnow().isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "title": "Getting Started Guide",
        "content": """Getting Started with Email Assistant

STEP 1: ACCOUNT SETUP
1. Sign up at www.emailassistant.com
2. Verify your email address
3. Complete your profile
4. Choose your plan (or start with free trial)

STEP 2: CONNECT EMAIL ACCOUNTS
1. Navigate to Settings > Email Accounts
2. Click "Connect Email Account"
3. Choose provider (Gmail, Outlook, etc.)
4. Complete OAuth authentication
5. Grant necessary permissions
6. Wait for initial sync (may take a few minutes)

STEP 3: CALENDAR INTEGRATION
1. Go to Settings > Calendar
2. Click "Connect Calendar"
3. Authenticate with Google/Microsoft
4. Select calendars to sync
5. Set scheduling preferences

STEP 4: CONFIGURE INTENTS
1. Navigate to Intents page
2. Review default intents
3. Customize prompts as needed
4. Add custom intents for your specific needs
5. Set priorities and auto-send preferences

STEP 5: BUILD KNOWLEDGE BASE
1. Go to Knowledge Base page
2. Add entries about your:
   - Company information
   - Products/services
   - Common questions and answers
   - Policies and procedures
3. Organize with categories and tags
4. Keep entries updated

STEP 6: TEST THE SYSTEM
1. Send a test email to your connected account
2. Watch it process in the dashboard
3. Review generated draft
4. Make adjustments to intents/knowledge base
5. Enable auto-send when confident

BEST PRACTICES:
- Start with manual approval for all emails
- Review and refine AI responses
- Build comprehensive knowledge base
- Use specific keywords for intents
- Monitor email processing regularly
- Keep intents and KB updated

NEED HELP?
- Documentation: docs.emailassistant.com
- Video tutorials: youtube.com/emailassistant
- Support: support@emailassistant.com
- Live chat: Available in dashboard""",
        "category": "Documentation",
        "tags": ["setup", "getting started", "onboarding", "guide", "tutorial"],
        "is_active": True,
        "created_at": datetime.utcnow().isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "title": "Support and Contact",
        "content": """Support and Contact Information

SUPPORT CHANNELS:

1. EMAIL SUPPORT
   - General inquiries: support@emailassistant.com
   - Technical issues: tech@emailassistant.com
   - Billing questions: billing@emailassistant.com
   - Response time: Within 24 hours (Business days)
   - Priority support: Within 4 hours (Business/Enterprise plans)

2. LIVE CHAT
   - Available in dashboard (bottom right)
   - Hours: Monday-Friday, 9 AM - 6 PM EST
   - Weekend: Automated responses with Monday follow-up

3. KNOWLEDGE BASE
   - Self-service documentation
   - Video tutorials
   - FAQs and troubleshooting guides
   - Access: docs.emailassistant.com

4. COMMUNITY FORUM
   - User discussions
   - Tips and best practices
   - Feature requests
   - Access: community.emailassistant.com

5. PHONE SUPPORT (Business/Enterprise only)
   - Phone: +1 (555) 123-4567
   - Hours: Monday-Friday, 9 AM - 6 PM EST
   - Schedule callback: support.emailassistant.com/callback

COMMON ISSUES & SOLUTIONS:

Email Sync Issues:
- Check OAuth token expiration
- Re-authenticate email account
- Verify permissions granted
- Check email provider status

Calendar Not Syncing:
- Re-connect calendar provider
- Check calendar permissions
- Verify timezone settings
- Review calendar selection

AI Response Quality:
- Update knowledge base entries
- Refine intent prompts
- Review and provide feedback
- Check intent priority settings

Auto-send Not Working:
- Verify auto_send enabled on intent
- Check draft validation status
- Review confidence threshold
- Check email account status

EMERGENCY SUPPORT:
For critical production issues:
- Email: emergency@emailassistant.com
- Subject line: [URGENT] + description
- Include: account email, error details
- Available: 24/7 for Enterprise plans

FEEDBACK & FEATURE REQUESTS:
- Email: feedback@emailassistant.com
- Feature requests: features.emailassistant.com
- Bug reports: bugs.emailassistant.com

SOCIAL MEDIA:
- Twitter: @EmailAssistant
- LinkedIn: Email Assistant Platform
- YouTube: Email Assistant Channel""",
        "category": "Support",
        "tags": ["support", "help", "contact", "troubleshooting", "assistance"],
        "is_active": True,
        "created_at": datetime.utcnow().isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "title": "Security and Privacy",
        "content": """Security and Privacy Policy

DATA SECURITY:

1. ENCRYPTION
   - All data encrypted in transit (TLS 1.3)
   - Encryption at rest for sensitive data
   - Database encryption enabled
   - Secure credential storage with encryption keys

2. AUTHENTICATION
   - OAuth 2.0 for email/calendar access
   - JWT tokens for API authentication
   - Automatic token refresh
   - Secure session management
   - 2FA support (coming soon)

3. ACCESS CONTROL
   - User-level data isolation
   - Role-based access control
   - API rate limiting
   - IP whitelisting (Enterprise)
   - Audit logging enabled

PRIVACY COMMITMENTS:

1. DATA USAGE
   - We ONLY access emails you explicitly connect
   - Email content used ONLY for processing and response generation
   - No email content used for AI training without consent
   - No data sharing with third parties
   - No selling of user data

2. DATA RETENTION
   - Emails: Retained for 90 days (configurable)
   - Drafts: Retained for 30 days
   - Knowledge base: Retained while active
   - Deleted data: Permanently removed within 30 days
   - Export your data anytime

3. DATA LOCATION
   - Primary servers: AWS US-East region
   - Backups: Encrypted and geo-redundant
   - EU data residency option (Enterprise)
   - Compliant data centers

COMPLIANCE:

- GDPR compliant
- SOC 2 Type II certified (in progress)
- CCPA compliant
- HIPAA available (Enterprise)
- Regular security audits
- Penetration testing quarterly

USER RIGHTS:

You have the right to:
- Access your data
- Export your data
- Delete your data
- Opt-out of features
- Data portability
- Lodge complaints

THIRD-PARTY SERVICES:

We integrate with:
- Google (Gmail, Calendar) - OAuth only
- Microsoft (Outlook, Calendar) - OAuth only
- AI Providers (OpenAI, Anthropic) - No PII shared
- Stripe (Payment processing) - PCI compliant

SECURITY BEST PRACTICES:

For users:
- Use strong, unique passwords
- Enable 2FA when available
- Review connected accounts regularly
- Report suspicious activity immediately
- Keep recovery email updated
- Review app permissions granted

INCIDENT RESPONSE:

In case of security incident:
- Immediate investigation initiated
- Affected users notified within 72 hours
- Detailed incident report provided
- Remediation steps implemented
- External audit if required

CONTACT SECURITY TEAM:

- Email: security@emailassistant.com
- PGP Key: Available at emailassistant.com/pgp
- Bug Bounty: security.emailassistant.com/bounty
- Responsible disclosure encouraged

Last Updated: November 2024
Policy Version: 2.0""",
        "category": "Security",
        "tags": ["security", "privacy", "data protection", "compliance", "gdpr"],
        "is_active": True,
        "created_at": datetime.utcnow().isoformat()
    }
]

# Insert knowledge base entries
for kb in knowledge_base:
    db.knowledge_base.insert_one(kb)
    print(f"   ✓ Created KB entry: {kb['title']} (Category: {kb['category']})")

print(f"\n✅ Created {len(knowledge_base)} knowledge base entries")

print("\n" + "="*60)
print("✨ SEED DATA CREATION COMPLETE ✨")
print("="*60)
print(f"\nSummary:")
print(f"  User: {user['email']}")
print(f"  Intents: {len(intents)}")
print(f"  Knowledge Base: {len(knowledge_base)}")
print(f"  Auto-send Intents: {sum(1 for i in intents if i['auto_send'])}")
print(f"  Manual Review Intents: {sum(1 for i in intents if not i['auto_send'])}")
print(f"  Default Intent: {'✓' if any(i['is_default'] for i in intents) else '✗'}")
print("\n" + "="*60)
