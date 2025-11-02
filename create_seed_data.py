"""Create seed data for user amits.joys@gmail.com"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime, timezone
import uuid

# User ID for amits.joys@gmail.com
USER_ID = "1086e721-86cf-4c3d-b567-329b20bc29de"
USER_EMAIL = "amits.joys@gmail.com"

async def create_seed_data():
    """Create intents and knowledge base for the user"""
    client = AsyncIOMotorClient(os.environ.get('MONGO_URL', 'mongodb://localhost:27017'))
    db = client['email_assistant_db']
    
    print(f"Creating seed data for user: {USER_EMAIL} ({USER_ID})")
    
    # ============= CREATE INTENTS =============
    intents = [
        {
            "id": str(uuid.uuid4()),
            "user_id": USER_ID,
            "name": "Meeting Request",
            "description": "Handles meeting and scheduling requests",
            "keywords": ["meeting", "schedule", "calendar", "appointment", "call", "zoom", "teams", "meet", "discussion", "catch up"],
            "priority": 10,
            "auto_send": True,
            "custom_prompt": """You are responding to a meeting request. Be professional and accommodating.
- Confirm availability or suggest alternative times
- If a calendar event was created, include all event details (date, time, timezone, and meeting link)
- Keep the tone warm and professional
- Be concise but informative""",
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": USER_ID,
            "name": "Meeting Reschedule",
            "description": "Handles meeting reschedule and change requests",
            "keywords": ["reschedule", "change meeting", "move meeting", "different time", "postpone", "cancel meeting"],
            "priority": 9,
            "auto_send": True,
            "custom_prompt": """You are responding to a meeting reschedule request. Be understanding and flexible.
- Acknowledge the need to reschedule
- Confirm the new meeting details if updated
- If a calendar event was updated, include the new event details with links
- Keep the tone professional and accommodating""",
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": USER_ID,
            "name": "Support Request",
            "description": "Handles technical support and help requests",
            "keywords": ["issue", "problem", "error", "help", "support", "not working", "bug", "broken", "fix"],
            "priority": 8,
            "auto_send": True,
            "custom_prompt": """You are providing technical support. Be empathetic and helpful.
- Acknowledge the issue
- Provide troubleshooting steps or solutions from knowledge base
- Offer to escalate if needed
- Keep the tone supportive and professional""",
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": USER_ID,
            "name": "Follow-up Request",
            "description": "Handles status updates and follow-up inquiries",
            "keywords": ["follow up", "followup", "checking in", "status", "update", "progress", "any news"],
            "priority": 7,
            "auto_send": True,
            "custom_prompt": """You are providing a status update or follow-up. Be informative and proactive.
- Provide current status
- Include any relevant updates or progress
- Set expectations for next steps
- Keep the tone professional and helpful""",
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": USER_ID,
            "name": "Introduction",
            "description": "Handles introductions and networking requests",
            "keywords": ["introduction", "introduce", "connection", "network", "nice to meet", "pleasure to meet"],
            "priority": 6,
            "auto_send": True,
            "custom_prompt": """You are responding to an introduction. Be warm and welcoming.
- Express pleasure in connecting
- Share relevant background from knowledge base
- Offer to discuss further or schedule a call
- Keep the tone friendly and professional""",
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": USER_ID,
            "name": "General Inquiry",
            "description": "Handles general questions and information requests",
            "keywords": ["question", "inquiry", "information", "help", "how", "what", "when", "where", "tell me about"],
            "priority": 5,
            "auto_send": True,
            "custom_prompt": """You are answering a general inquiry. Be informative and helpful.
- Answer questions using knowledge base information
- Provide relevant details
- Offer additional resources or assistance
- Keep the tone professional and informative""",
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": USER_ID,
            "name": "Thank You",
            "description": "Handles thank you messages and appreciation",
            "keywords": ["thank you", "thanks", "appreciate", "grateful", "awesome", "great job"],
            "priority": 4,
            "auto_send": True,
            "custom_prompt": """You are responding to a thank you message. Be gracious and warm.
- Acknowledge their appreciation
- Express willingness to help further
- Keep the response brief and sincere
- Keep the tone warm and professional""",
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": USER_ID,
            "name": "Urgent Request",
            "description": "Handles urgent and time-sensitive requests - requires manual review",
            "keywords": ["urgent", "asap", "immediately", "emergency", "critical", "right now", "time sensitive"],
            "priority": 10,
            "auto_send": False,  # Requires manual review
            "custom_prompt": """This is an urgent request that requires manual review.
- Acknowledge the urgency
- Indicate you will prioritize this
- Provide immediate next steps if possible
- Keep the tone professional and reassuring""",
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    # Insert intents
    if intents:
        await db.intents.insert_many(intents)
        print(f"✓ Created {len(intents)} intents")
        for intent in intents:
            print(f"  - {intent['name']} (auto_send: {intent['auto_send']}, priority: {intent['priority']})")
    
    # ============= CREATE KNOWLEDGE BASE =============
    knowledge_base = [
        {
            "id": str(uuid.uuid4()),
            "user_id": USER_ID,
            "title": "Company Overview",
            "content": """We are a cutting-edge AI-powered email management platform that helps professionals automate their email workflows.

Our mission is to save time and improve communication efficiency through intelligent automation.

Founded in 2024, we serve businesses and professionals who want to focus on what matters most while AI handles routine email tasks.

Key Features:
- AI-powered email classification and drafting
- Smart meeting detection and calendar integration
- Automated follow-ups and reminders
- Knowledge base integration for consistent responses
- Multi-account support""",
            "category": "Company Information",
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": USER_ID,
            "title": "Product Features",
            "content": """Our AI Email Assistant includes:

1. **Smart Email Classification**
   - Automatically categorizes incoming emails by intent
   - Prioritizes emails based on importance
   - Filters spam and low-priority messages

2. **AI Draft Generation**
   - Creates professional email responses
   - Maintains your communication style
   - Uses knowledge base for accurate information
   - Thread-aware responses that avoid repetition

3. **Meeting Management**
   - Detects meeting requests automatically
   - Creates Google Calendar events with Meet links
   - Sends confirmation emails with all event details
   - Manages meeting updates and reschedules

4. **Automated Follow-ups**
   - Schedules follow-up emails automatically
   - Cancels follow-ups when replies are received
   - Customizable follow-up timing

5. **Calendar Integration**
   - Google Calendar sync
   - Conflict detection
   - Event reminders
   - Virtual meeting links included

6. **Multi-Account Support**
   - Connect multiple email accounts
   - OAuth Gmail integration
   - Centralized management""",
            "category": "Product",
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": USER_ID,
            "title": "Meeting and Calendar Features",
            "content": """Our meeting detection and calendar features include:

**Automatic Meeting Detection:**
- AI analyzes emails to detect meeting requests
- Extracts date, time, location, and attendees
- Detects timezone information automatically
- Works with natural language ("tomorrow at 2pm", "next Tuesday")

**Calendar Event Creation:**
- Automatically creates Google Calendar events
- Generates Google Meet links for virtual meetings
- Includes all event details (date, time, location, attendees)
- Sends confirmation email with meeting details and links in the SAME email thread
- All event information included in the reply (no separate emails)

**Meeting Confirmation:**
When a meeting is detected and calendar event is created, your reply email includes:
- Confirmation that the meeting is scheduled
- Date, time, and timezone
- Google Meet joining link (if virtual)
- Calendar link to view/add to personal calendar
- All attendee information

**Event Management:**
- Conflict detection with existing meetings
- Meeting reschedule support
- Automatic reminders sent 1 hour before meeting
- Event updates reflected in both calendar and email

**Single Thread Communication:**
All meeting-related communication happens in the same email thread:
- Initial meeting request received
- AI creates calendar event with Meet link
- Single reply sent with meeting confirmation AND event details
- No separate notification emails - everything in one message""",
            "category": "Meetings",
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": USER_ID,
            "title": "Pricing Information",
            "content": """Our flexible pricing plans:

**Starter Plan - $29/month**
- 1 email account
- Up to 500 emails/month
- Basic AI features
- Email support

**Professional Plan - $79/month**
- 3 email accounts
- Up to 2,000 emails/month
- Full AI features
- Calendar integration
- Priority support
- Custom knowledge base

**Business Plan - $199/month**
- Unlimited email accounts
- Unlimited emails
- Advanced AI features
- Team collaboration
- API access
- Dedicated support
- Custom integrations

**Enterprise Plan - Custom pricing**
- Custom solutions
- On-premise deployment option
- SLA guarantees
- Dedicated account manager
- Custom AI training

All plans include:
- 14-day free trial
- No credit card required
- Cancel anytime
- Data export tools""",
            "category": "Pricing",
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": USER_ID,
            "title": "Getting Started Guide",
            "content": """Quick start guide for new users:

**Step 1: Connect Your Email**
- Click "Email Accounts" in the sidebar
- Choose "Connect Gmail with OAuth" (recommended)
- Authorize access to your Gmail account
- Your account will start syncing automatically

**Step 2: Connect Google Calendar**
- Click "Calendar Providers" in the sidebar
- Choose "Connect Google Calendar"
- Authorize calendar access
- Your calendar will be available for event creation

**Step 3: Set Up Intents**
- Intents are automatically created with default settings
- Review and customize intent prompts if needed
- Enable/disable auto-send for each intent type
- Adjust priority levels

**Step 4: Add Knowledge Base**
- Click "Knowledge Base" in the sidebar
- Add information about your company, products, or services
- AI will use this information in responses
- Keep it updated for best results

**Step 5: Test the System**
- Send a test email to your connected account
- Watch it get processed automatically (within 60 seconds)
- Review the generated draft
- Check the action history for details

**Tips:**
- Emails are polled every 60 seconds
- Auto-send only works for intents with the flag enabled
- Meeting detection requires calendar connection
- Use thread context for better responses""",
            "category": "Documentation",
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": USER_ID,
            "title": "Support and Contact",
            "content": """Need help? We're here for you:

**Email Support:**
- General inquiries: support@yourdomain.com
- Technical issues: tech@yourdomain.com
- Response time: Within 24 hours (weekdays)

**Live Chat:**
- Available during business hours (9 AM - 5 PM EST)
- Instant responses from our support team

**Documentation:**
- Comprehensive guides at docs.yourdomain.com
- Video tutorials available
- FAQ section for common questions

**Community:**
- Join our Slack community
- Share tips and best practices
- Connect with other users

**Troubleshooting:**
Common issues and solutions:
- Email not syncing: Check OAuth permissions
- Drafts not generating: Verify API keys and intents
- Calendar not creating events: Ensure calendar provider is connected
- Auto-send not working: Check intent auto_send flag

**Feature Requests:**
We love feedback! Submit feature requests through:
- In-app feedback form
- Community forum
- Direct email to product@yourdomain.com

**Status Page:**
Check system status at status.yourdomain.com""",
            "category": "Support",
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": USER_ID,
            "title": "Security and Privacy",
            "content": """Your data security is our top priority:

**Data Protection:**
- End-to-end encryption for email data
- OAuth 2.0 for secure authentication
- No storage of email passwords
- Encrypted database storage
- Regular security audits

**Privacy Commitments:**
- We never read your emails beyond processing
- No selling or sharing of user data
- GDPR and CCPA compliant
- Data deletion available on request
- Transparent privacy policy

**Access Control:**
- Role-based access control
- Two-factor authentication available
- Session management and timeout
- Audit logs for all actions

**Compliance:**
- SOC 2 Type II certified
- GDPR compliant
- CCPA compliant
- HIPAA available for Enterprise

**Data Retention:**
- Emails retained for 90 days by default
- Configurable retention policies
- Automatic data cleanup
- Export your data anytime

**OAuth Scopes:**
We only request minimal necessary permissions:
- Gmail: Read and send emails (gmail.readonly, gmail.send)
- Calendar: Manage events (calendar.events)
- We never request full account access

**Questions?**
Contact our security team: security@yourdomain.com""",
            "category": "Security",
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    # Insert knowledge base
    if knowledge_base:
        await db.knowledge_base.insert_many(knowledge_base)
        print(f"\n✓ Created {len(knowledge_base)} knowledge base entries")
        for kb in knowledge_base:
            print(f"  - {kb['title']} ({kb['category']})")
    
    print(f"\n{'='*60}")
    print("✓ Seed data creation complete!")
    print(f"{'='*60}")
    print(f"\nUser: {USER_EMAIL}")
    print(f"Intents: {len(intents)}")
    print(f"Knowledge Base: {len(knowledge_base)}")
    print(f"\nAuto-send enabled intents: {sum(1 for i in intents if i['auto_send'])}")
    print(f"Manual review intents: {sum(1 for i in intents if not i['auto_send'])}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(create_seed_data())
