"""
Production Seed Data Script
Creates comprehensive intents and knowledge base for user
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import uuid
from config import config


async def create_seed_data(user_email: str):
    """Create comprehensive seed data for a user"""
    
    # Connect to database
    client = AsyncIOMotorClient(config.MONGO_URL)
    db = client[config.DB_NAME]
    
    try:
        # Find user
        user = await db.users.find_one({"email": user_email})
        if not user:
            print(f"❌ User not found: {user_email}")
            return
        
        user_id = user['id']
        print(f"✓ Found user: {user_email} (ID: {user_id})")
        
        # Create Intents
        print("\n📝 Creating Intents...")
        intents = [
            {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "name": "Meeting Request",
                "description": "Handle meeting and scheduling requests",
                "keywords": ["meeting", "schedule", "calendar", "appointment", "call", "zoom", "teams", "meet", "discussion", "sync", "catch up"],
                "priority": 10,
                "is_active": True,
                "auto_send": True,
                "prompt": """Handle this meeting request professionally. 
- Confirm availability or suggest alternative times
- Be specific about time zones
- Provide calendar link if meeting is created
- Include any joining links (Zoom, Meet, etc.)
- Keep tone friendly but professional""",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "name": "Meeting Reschedule",
                "description": "Handle meeting reschedule requests",
                "keywords": ["reschedule", "change time", "move meeting", "different time", "postpone", "delay"],
                "priority": 9,
                "is_active": True,
                "auto_send": True,
                "prompt": """Handle the reschedule request professionally.
- Acknowledge the original meeting time
- Confirm the new time or offer alternatives
- Update calendar and provide new link
- Be accommodating and understanding""",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "name": "Support Request",
                "description": "Technical support and problem-solving",
                "keywords": ["issue", "problem", "error", "help", "support", "not working", "bug", "broken", "fix", "trouble", "can't", "cannot"],
                "priority": 8,
                "is_active": True,
                "auto_send": True,
                "prompt": """Provide helpful technical support:
- Show empathy for their issue
- Ask clarifying questions if needed
- Provide step-by-step solutions from knowledge base
- Offer to escalate if issue persists
- Be patient and thorough""",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "name": "Follow-up Request",
                "description": "Follow-up on previous conversations",
                "keywords": ["follow up", "followup", "checking in", "status", "update", "any news", "progress", "heard back"],
                "priority": 7,
                "is_active": True,
                "auto_send": True,
                "prompt": """Provide a helpful status update:
- Reference the previous conversation
- Provide current status or progress
- Be honest about timelines
- Set clear expectations
- Offer next steps""",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "name": "Introduction",
                "description": "New connection or introduction emails",
                "keywords": ["introduce", "introduction", "nice to meet", "reaching out", "connection", "network", "connect"],
                "priority": 6,
                "is_active": True,
                "auto_send": True,
                "prompt": """Respond warmly to introductions:
- Thank them for reaching out
- Share relevant background from knowledge base
- Express interest in connecting
- Suggest next steps (call, meeting, etc.)
- Be friendly and professional""",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "name": "General Inquiry",
                "description": "General questions and information requests",
                "keywords": ["question", "inquiry", "information", "info", "how", "what", "when", "where", "why", "tell me about"],
                "priority": 5,
                "is_active": True,
                "auto_send": True,
                "prompt": """Answer questions using the knowledge base:
- Provide accurate, detailed information
- Use knowledge base as source of truth
- Be clear and concise
- Offer to provide more details if needed
- Never make up information""",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "name": "Thank You",
                "description": "Acknowledgments and thank you messages",
                "keywords": ["thank you", "thanks", "appreciate", "grateful", "thanking"],
                "priority": 4,
                "is_active": True,
                "auto_send": True,
                "prompt": """Respond graciously to thanks:
- Acknowledge their appreciation
- Offer continued assistance
- Be warm and genuine
- Keep it brief but friendly""",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "name": "Urgent Request",
                "description": "Urgent or time-sensitive requests requiring immediate attention",
                "keywords": ["urgent", "asap", "immediately", "emergency", "critical", "time-sensitive", "deadline"],
                "priority": 10,
                "is_active": True,
                "auto_send": False,  # Requires manual review
                "prompt": """Handle urgent requests with care:
- Acknowledge the urgency
- Assess the situation
- Provide immediate next steps
- Set realistic expectations
- This requires manual review before sending""",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "name": "Default",
                "description": "Default handler for emails that don't match specific intents",
                "keywords": [],
                "priority": 1,
                "is_active": True,
                "auto_send": True,
                "is_default": True,
                "prompt": """Respond to this email professionally:
- Use the knowledge base to provide relevant information
- Be helpful and courteous
- Ask clarifying questions if the request is unclear
- Never make up information not in the knowledge base
- Show that you understand their needs""",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        ]
        
        # Delete existing intents for this user
        await db.intents.delete_many({"user_id": user_id})
        
        # Insert new intents
        await db.intents.insert_many(intents)
        print(f"✓ Created {len(intents)} intents")
        
        # Create Knowledge Base
        print("\n📚 Creating Knowledge Base...")
        knowledge_base = [
            {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "title": "Company Overview",
                "content": """We are a technology company specializing in AI-powered solutions. 

Our Mission: To empower businesses with intelligent automation and AI tools that enhance productivity and streamline operations.

Founded: 2023
Location: Global (Remote-first)
Team Size: Growing startup team

Core Values:
- Innovation and excellence
- Customer-first approach
- Transparency and integrity
- Continuous learning
- Work-life balance""",
                "category": "Company Information",
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "title": "AI Email Assistant Features",
                "content": """Our AI Email Assistant is a comprehensive email management solution with the following features:

✉️ CORE FEATURES:
- Automatic email classification using intent recognition
- AI-powered draft generation based on your knowledge base
- Thread context awareness for coherent conversations
- Multi-account support (Gmail, Outlook)
- Auto-send capability for routine responses

📅 CALENDAR INTEGRATION:
- Automatic meeting detection from emails
- Google Calendar event creation
- Meeting reminder notifications
- Reschedule handling
- Virtual meeting link generation

🤖 AI CAPABILITIES:
- Context-aware responses using your knowledge base
- Draft validation and quality checks
- Follow-up management
- Smart reply suggestions
- Thread tracking and conversation history

🔐 SECURITY & PRIVACY:
- OAuth 2.0 authentication
- Encrypted token storage
- No email content stored permanently
- GDPR compliant
- User data isolation""",
                "category": "Product",
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "title": "Meeting and Calendar Features",
                "content": """MEETING DETECTION:
Our AI automatically detects meeting requests in emails and extracts:
- Date and time (with timezone handling)
- Meeting duration
- Location (physical or virtual)
- Attendee information
- Meeting purpose/title

CALENDAR INTEGRATION:
- Automatic Google Calendar event creation
- Google Meet link generation for virtual meetings
- Calendar conflict detection
- Event update capabilities
- Meeting reminders (sent 1 hour before)

MEETING WORKFLOW:
1. Email with meeting request arrives
2. AI detects meeting and extracts details
3. Calendar event created automatically
4. Confirmation email sent with:
   - Meeting details
   - Google Meet link
   - Calendar view link
   - Add to calendar option
5. Reminder sent 1 hour before meeting

SUPPORTED FORMATS:
- "Let's meet tomorrow at 3pm"
- "Can we schedule a call next Tuesday at 2:30pm EST?"
- "I'm free on Jan 15th at 14:00"
- And many more natural language formats""",
                "category": "Meetings",
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "title": "Pricing Information",
                "content": """PRICING PLANS:

🆓 FREE PLAN:
- 50 emails per month
- Single email account
- Basic AI responses
- Email classification
- Perfect for individuals

💼 PROFESSIONAL PLAN - $29/month:
- 500 emails per month
- Up to 5 email accounts
- Advanced AI responses with knowledge base
- Calendar integration
- Auto-send capability
- Follow-up management
- Priority support
- Ideal for freelancers and small businesses

🏢 BUSINESS PLAN - $99/month:
- Unlimited emails
- Unlimited email accounts
- Team collaboration features
- Custom AI training
- API access
- Advanced analytics
- Dedicated support
- SLA guarantee
- Best for teams and enterprises

🎓 EDUCATION DISCOUNT:
- 50% off Professional and Business plans
- Valid .edu email required
- Annual commitment

💰 ANNUAL BILLING:
- Save 20% with annual payment
- Professional: $278/year (save $70)
- Business: $950/year (save $238)

All plans include:
- 14-day free trial
- No credit card required for trial
- Cancel anytime
- Money-back guarantee (30 days)""",
                "category": "Pricing",
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "title": "Getting Started Guide",
                "content": """QUICK START GUIDE:

STEP 1: CONNECT EMAIL ACCOUNT
1. Go to Settings > Email Accounts
2. Click "Connect Gmail" or "Connect Outlook"
3. Complete OAuth authorization
4. Your account will appear in the list

STEP 2: SET UP PERSONA (Optional but Recommended)
1. Go to your email account settings
2. Add a persona describing your communication style
3. Example: "Professional but friendly, tech startup founder, helpful and concise"
4. This helps AI match your voice

STEP 3: ADD KNOWLEDGE BASE
1. Go to Knowledge Base
2. Click "Add Entry"
3. Add information you frequently share:
   - Company info
   - Product details
   - Pricing
   - FAQs
   - Policies
4. AI will use this to answer questions accurately

STEP 4: CONFIGURE INTENTS
1. Go to Intents
2. Review default intents (meeting, support, inquiry, etc.)
3. Customize keywords and prompts
4. Enable auto-send for intents you trust
5. Set priorities

STEP 5: CONNECT CALENDAR (For Meeting Features)
1. Go to Settings > Calendar
2. Click "Connect Google Calendar"
3. Complete authorization
4. Meeting detection will now create calendar events

STEP 6: TEST THE SYSTEM
1. Send a test email to your connected account
2. Wait 60 seconds for polling
3. Check Dashboard to see:
   - Email received
   - Intent classified
   - Draft generated
   - Auto-sent (if enabled)

TIPS:
- Start with auto-send disabled to review drafts
- Gradually enable auto-send for trusted intents
- Keep knowledge base updated
- Review action history to improve intents""",
                "category": "Documentation",
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "title": "Support and Contact",
                "content": """SUPPORT CHANNELS:

📧 Email Support:
- Email: support@aiemailassistant.com
- Response time: Within 24 hours
- Available 24/7

💬 Live Chat:
- Available on website
- Monday-Friday, 9am-5pm EST
- Instant responses during business hours

📚 Documentation:
- Knowledge base: docs.aiemailassistant.com
- Video tutorials: youtube.com/@aiemailassistant
- API docs: api.aiemailassistant.com

🐛 Bug Reports:
- GitHub: github.com/aiemailassistant/issues
- Include: Steps to reproduce, expected vs actual behavior
- Screenshots helpful

💡 Feature Requests:
- Submit via feedback form
- Vote on existing requests
- Community-driven roadmap

🔧 COMMON ISSUES:

"Emails not being processed"
→ Check: Account connected, OAuth tokens valid, email polling enabled

"Drafts sound wrong"
→ Update: Persona, knowledge base, intent prompts

"Auto-send not working"
→ Check: Intent has auto_send enabled, draft passed validation

"Calendar events not created"
→ Check: Google Calendar connected, meeting detection enabled

"High API costs"
→ Review: Auto-send settings, enable only for trusted intents

EMERGENCY CONTACT:
- Critical issues: emergency@aiemailassistant.com
- Phone: +1-555-AI-EMAIL (business plan only)
- Response: Within 2 hours""",
                "category": "Support",
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "title": "Security and Privacy",
                "content": """SECURITY MEASURES:

🔐 AUTHENTICATION:
- OAuth 2.0 for email and calendar access
- JWT tokens for API authentication
- Token encryption at rest
- Automatic token refresh
- Session management and expiry

🛡️ DATA PROTECTION:
- Email content not stored permanently
- Only metadata and drafts retained
- Encrypted database storage
- Regular security audits
- Penetration testing quarterly

🌍 COMPLIANCE:
- GDPR compliant
- CCPA compliant
- SOC 2 Type II certified (in progress)
- ISO 27001 aligned
- Regular compliance audits

📊 DATA USAGE:
What we store:
- Email metadata (from, to, subject, date)
- Generated drafts
- User preferences and settings
- Intent and knowledge base data

What we DON'T store:
- Full email bodies (processed and discarded)
- Passwords or credentials
- Credit card numbers (via Stripe)
- Attachments

🔒 USER RIGHTS:
- Right to access your data
- Right to export your data
- Right to delete your account
- Right to opt-out of analytics
- Data portability

🚫 PRIVACY POLICY HIGHLIGHTS:
- No selling of user data
- No third-party advertising
- Minimal data collection
- Transparent data practices
- Regular privacy policy updates

AI PROCESSING:
- AI processing via Groq API
- No training on your emails
- Prompts and responses encrypted in transit
- No data retention by AI provider
- Real-time processing only

INCIDENT RESPONSE:
- 24/7 security monitoring
- Incident response team
- Breach notification within 72 hours
- Public security advisories
- Bug bounty program

BEST PRACTICES:
- Use strong passwords
- Enable 2FA (coming soon)
- Review connected accounts regularly
- Limit auto-send to trusted intents
- Keep knowledge base private""",
                "category": "Security",
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        ]
        
        # Delete existing KB entries for this user
        await db.knowledge_base.delete_many({"user_id": user_id})
        
        # Insert new KB entries
        await db.knowledge_base.insert_many(knowledge_base)
        print(f"✓ Created {len(knowledge_base)} knowledge base entries")
        
        print("\n" + "="*60)
        print("✅ SEED DATA CREATED SUCCESSFULLY!")
        print("="*60)
        print(f"\nUser: {user_email}")
        print(f"Intents: {len(intents)} (including 1 default)")
        print(f"Knowledge Base: {len(knowledge_base)} entries")
        print(f"Auto-send enabled: {len([i for i in intents if i['auto_send']])} intents")
        print(f"Manual review required: {len([i for i in intents if not i['auto_send']])} intents")
        
    finally:
        client.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python create_production_seed.py <user_email>")
        print("Example: python create_production_seed.py amits.joys@gmail.com")
        sys.exit(1)
    
    user_email = sys.argv[1]
    asyncio.run(create_seed_data(user_email))
