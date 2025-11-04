#!/usr/bin/env python3
"""
Create comprehensive seed data for AI Email Assistant
Creates intents and knowledge base entries for a specific user
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timezone

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from config import config
from models.intent import Intent
from models.knowledge_base import KnowledgeBase

USER_ID = "0c34b9ea-6740-4aea-afe9-f36c8270a0e8"  # amits.joys@gmail.com

async def create_seed_data():
    """Create seed data for user"""
    # Connect to database
    client = AsyncIOMotorClient(config.MONGO_URL)
    db = client[config.DB_NAME]
    
    print(f"🌱 Creating seed data for user: {USER_ID}")
    print("=" * 60)
    
    # Delete existing seed data for this user
    print("\n🗑️  Removing old seed data...")
    intents_deleted = await db.intents.delete_many({"user_id": USER_ID})
    kb_deleted = await db.knowledge_base.delete_many({"user_id": USER_ID})
    print(f"   Deleted {intents_deleted.deleted_count} old intents")
    print(f"   Deleted {kb_deleted.deleted_count} old KB entries")
    
    # ========== INTENTS ==========
    print("\n📝 Creating Intents...")
    
    intents_data = [
        {
            "name": "Meeting Request",
            "description": "Handle meeting and scheduling requests",
            "keywords": ["meeting", "schedule", "calendar", "appointment", "call", "zoom", "teams", "meet", "catch up", "coffee", "lunch", "available"],
            "prompt": """You are handling a meeting request. Your response should:
1. Acknowledge the meeting request professionally
2. If a specific time is mentioned, confirm availability or suggest alternatives
3. If no time is specified, offer 2-3 specific time slots
4. Include timezone information
5. Keep it brief and professional
6. If creating a calendar event, include all meeting details (date, time, Google Meet link, calendar link)

Remember: The system may have already created a calendar event with meeting details. If so, include those details in your response.""",
            "auto_send": True,
            "priority": 10,
            "is_default": False
        },
        {
            "name": "Meeting Reschedule",
            "description": "Handle meeting reschedule requests",
            "keywords": ["reschedule", "move", "change time", "different time", "cancel meeting", "postpone"],
            "prompt": """You are handling a meeting reschedule request. Your response should:
1. Acknowledge the reschedule request with understanding
2. Confirm that you can accommodate the change
3. If a new time is mentioned, confirm it or suggest alternatives
4. Reference the original meeting if known
5. Keep it professional and accommodating

The system will handle updating the calendar event.""",
            "auto_send": True,
            "priority": 9,
            "is_default": False
        },
        {
            "name": "Support Request",
            "description": "Technical support and problem resolution",
            "keywords": ["issue", "problem", "error", "help", "support", "not working", "bug", "broken", "fix", "trouble"],
            "prompt": """You are handling a support request. Your response should:
1. Acknowledge the issue with empathy
2. Ask clarifying questions if needed
3. Provide troubleshooting steps if applicable
4. Offer to escalate if needed
5. Include relevant documentation links from knowledge base
6. Keep tone helpful and supportive""",
            "auto_send": True,
            "priority": 8,
            "is_default": False
        },
        {
            "name": "Follow-up Request",
            "description": "Status updates and follow-ups",
            "keywords": ["follow up", "followup", "checking in", "status", "update", "progress", "any news"],
            "prompt": """You are handling a follow-up request. Your response should:
1. Acknowledge the follow-up
2. Provide current status
3. Share relevant updates
4. Set expectations for next steps
5. Keep it concise and informative""",
            "auto_send": True,
            "priority": 7,
            "is_default": False
        },
        {
            "name": "Introduction",
            "description": "Networking and introduction emails",
            "keywords": ["introduction", "introduce", "connection", "network", "nice to meet", "pleasure", "heard about"],
            "prompt": """You are responding to an introduction email. Your response should:
1. Express appreciation for the introduction
2. Share brief relevant background
3. Suggest next steps (call, meeting, email exchange)
4. Be warm and professional
5. Keep it concise""",
            "auto_send": True,
            "priority": 6,
            "is_default": False
        },
        {
            "name": "General Inquiry",
            "description": "Questions about products, services, or general information",
            "keywords": ["question", "inquiry", "information", "how", "what", "when", "where", "why", "can you", "could you"],
            "prompt": """You are answering a general inquiry. Your response should:
1. Address the question directly using knowledge base information
2. Be informative but concise
3. Offer additional resources if helpful
4. Invite follow-up questions
5. Stay professional and friendly

Use the knowledge base to provide accurate, factual information.""",
            "auto_send": True,
            "priority": 5,
            "is_default": False
        },
        {
            "name": "Thank You",
            "description": "Appreciation and gratitude emails",
            "keywords": ["thank you", "thanks", "appreciate", "grateful", "appreciation"],
            "prompt": """You are responding to a thank you email. Your response should:
1. Acknowledge their gratitude
2. Express that it was a pleasure to help
3. Offer continued assistance
4. Keep it warm but brief
5. Be genuine and professional""",
            "auto_send": True,
            "priority": 4,
            "is_default": False
        },
        {
            "name": "Urgent Request",
            "description": "High priority issues requiring immediate attention",
            "keywords": ["urgent", "asap", "immediately", "emergency", "critical", "important"],
            "prompt": """You are handling an urgent request. Your response should:
1. Acknowledge the urgency
2. Confirm that you're treating it as high priority
3. Provide immediate next steps
4. Set clear expectations on response time
5. Be professional and reassuring

NOTE: This intent requires manual review before sending.""",
            "auto_send": False,  # Manual review for urgent items
            "priority": 10,
            "is_default": False
        },
        {
            "name": "Default",
            "description": "Fallback for emails that don't match specific categories",
            "keywords": [],
            "prompt": """You are responding to an email that doesn't match any specific category. Your response should:
1. Acknowledge the email professionally
2. Use the knowledge base and persona to craft a helpful, relevant response
3. Focus on understanding the sender's intent
4. Provide value based on available information
5. If unsure about specific details, acknowledge it professionally and offer to get more information or direct them to the right resource
6. Keep the response professional, helpful, and concise

This is a catch-all intent, so be flexible and context-aware.""",
            "auto_send": True,
            "priority": 1,
            "is_default": True
        }
    ]
    
    for intent_data in intents_data:
        intent = Intent(
            user_id=USER_ID,
            name=intent_data["name"],
            description=intent_data["description"],
            prompt=intent_data["prompt"],
            keywords=intent_data["keywords"],
            auto_send=intent_data["auto_send"],
            priority=intent_data["priority"],
            is_default=intent_data.get("is_default", False)
        )
        
        doc = intent.model_dump()
        await db.intents.insert_one(doc)
        
        auto_send_str = "✅ Auto-send" if intent.auto_send else "❌ Manual"
        default_str = " [DEFAULT]" if intent.is_default else ""
        print(f"   ✓ {intent.name} (Priority: {intent.priority}, {auto_send_str}){default_str}")
    
    # ========== KNOWLEDGE BASE ==========
    print("\n📚 Creating Knowledge Base...")
    
    kb_data = [
        {
            "title": "Company Overview",
            "category": "Company Information",
            "content": """Our company is an AI-powered email assistant platform that helps professionals manage their inbox intelligently. 

Founded in 2024, we leverage cutting-edge AI technology to automate email responses, schedule meetings, and provide intelligent follow-ups. Our platform integrates seamlessly with Gmail and Outlook, offering a comprehensive solution for email management.

Key Features:
- Intelligent email classification and routing
- AI-generated draft responses based on context
- Automatic meeting detection and calendar integration
- Smart follow-up system
- Thread-aware conversations
- Knowledge base integration for accurate responses

Our mission is to help professionals focus on what matters by automating routine email tasks while maintaining a personal touch."""
        },
        {
            "title": "Product Features",
            "category": "Product",
            "content": """Complete Feature List:

1. EMAIL PROCESSING:
   - Automatic email polling (every 60 seconds)
   - Intent classification using keywords and AI
   - Thread context tracking
   - Reply detection

2. AI-POWERED RESPONSES:
   - Draft generation using AI (Groq LLM)
   - Draft validation with quality checks
   - Knowledge base grounded responses
   - Persona-based customization
   - Auto-send based on intent configuration

3. MEETING MANAGEMENT:
   - Automatic meeting detection from emails
   - Google Calendar integration
   - Meeting invites with Google Meet links
   - Meeting reminders (1 hour before)
   - Meeting reschedule handling

4. FOLLOW-UP SYSTEM:
   - Automatic follow-up creation
   - Smart scheduling based on business hours
   - Follow-up cancellation when replies received
   - Customizable follow-up templates

5. INTEGRATIONS:
   - Gmail (OAuth)
   - Google Calendar (OAuth)
   - Microsoft Outlook (OAuth)
   - Custom SMTP/IMAP support

6. ANALYTICS & MONITORING:
   - Email processing metrics
   - Intent classification statistics
   - Auto-send success rates
   - Token usage tracking"""
        },
        {
            "title": "Meeting and Calendar Features",
            "category": "Meetings",
            "content": """Meeting Management Capabilities:

MEETING DETECTION:
- Automatically detects meeting requests in emails
- Extracts date, time, timezone, location, and attendees
- Identifies meeting intent with confidence scoring
- Supports relative dates (tomorrow, next week, etc.)

CALENDAR INTEGRATION:
- Creates events in Google Calendar
- Generates Google Meet links automatically
- Checks for scheduling conflicts
- Sends event details in confirmation email
- Updates events when changes requested

MEETING CONFIRMATIONS:
- Single email with all details in same thread
- Includes meeting date, time, timezone
- Provides Google Meet joining link
- Includes calendar view link
- Lists all attendees

REMINDERS:
- Sent 1 hour before meeting start time
- Email notification to all attendees
- Includes meeting details and join link
- Prevents duplicate reminders

RESCHEDULING:
- Detects reschedule requests
- Updates calendar event
- Notifies all attendees
- Adjusts reminders automatically

The system ensures all meeting communication happens in a single email thread, keeping conversations organized and context-aware."""
        },
        {
            "title": "Pricing Information",
            "category": "Pricing",
            "content": """Pricing Plans:

FREE TIER:
- 100 emails per day
- Basic intent classification
- AI draft generation
- Manual approval required
- Email support
- Perfect for: Individuals and small teams testing the platform

PROFESSIONAL - $29/month:
- 500 emails per day
- Advanced intent classification
- AI draft generation & validation
- Auto-send capability
- Meeting detection & calendar integration
- Follow-up automation
- Priority email support
- Perfect for: Solo professionals and consultants

BUSINESS - $79/month:
- 2,000 emails per day
- All Professional features
- Multiple email accounts
- Team collaboration features
- Custom intents and knowledge base
- Advanced analytics
- API access
- Priority support with SLA
- Perfect for: Small to medium businesses

ENTERPRISE - Custom pricing:
- Unlimited emails
- All Business features
- Custom integrations
- Dedicated account manager
- On-premise deployment option
- Custom AI model training
- 24/7 support
- Perfect for: Large organizations with complex needs

All plans include:
- 14-day free trial
- No credit card required for trial
- Cancel anytime
- SSL encryption
- GDPR compliance"""
        },
        {
            "title": "Getting Started Guide",
            "category": "Documentation",
            "content": """Quick Start Guide:

STEP 1: CREATE ACCOUNT
- Sign up with email and password
- Verify email address
- Complete profile setup

STEP 2: CONNECT EMAIL ACCOUNT
- Go to Email Accounts page
- Click "Connect Gmail" or "Connect Outlook"
- Authorize OAuth access
- Your account will start syncing immediately

STEP 3: CONFIGURE INTENTS
- Navigate to Intents page
- Review default intents (Meeting, Support, etc.)
- Customize intent prompts and keywords
- Set auto-send preferences
- Enable/disable intents as needed

STEP 4: ADD KNOWLEDGE BASE
- Go to Knowledge Base page
- Create entries for your business
- Categories: Company, Product, Support, etc.
- AI uses this for accurate responses

STEP 5: SET UP CALENDAR (OPTIONAL)
- Navigate to Calendar Providers page
- Click "Connect Google Calendar"
- Authorize calendar access
- Meeting requests will auto-create events

STEP 6: CUSTOMIZE PERSONA
- Go to Profile page
- Set your email persona/voice
- Add email signature
- Configure notification preferences

STEP 7: MONITOR & ADJUST
- Use Dashboard to track metrics
- Review Email Processing page for activity
- Check drafts before they're sent (if not auto-send)
- Adjust intents based on performance

TIPS FOR SUCCESS:
- Start with manual approval (auto_send=false)
- Review and improve intent prompts
- Keep knowledge base updated
- Monitor classification accuracy
- Use follow-ups strategically"""
        },
        {
            "title": "Support and Contact",
            "category": "Support",
            "content": """Support Channels:

EMAIL SUPPORT:
- support@emailassistant.ai
- Response time: 24 hours (Free), 4 hours (Professional), 1 hour (Business)
- Include: User ID, error description, screenshots if applicable

DOCUMENTATION:
- Help Center: docs.emailassistant.ai
- API Documentation: api.emailassistant.ai
- Video Tutorials: youtube.com/emailassistant
- Community Forum: community.emailassistant.ai

LIVE CHAT:
- Available: Mon-Fri, 9 AM - 6 PM EST
- Professional and Business plans only
- Average response time: Under 5 minutes

COMMON ISSUES:

1. OAuth Connection Failed:
   - Clear browser cache and cookies
   - Try incognito/private mode
   - Check Google/Microsoft account permissions
   - Ensure pop-ups are not blocked

2. Emails Not Processing:
   - Verify email account is active
   - Check OAuth tokens haven't expired
   - Confirm email account has proper permissions
   - Review backend logs for errors

3. Auto-Send Not Working:
   - Check intent has auto_send=true
   - Verify draft passed validation
   - Confirm email classification matched an intent
   - Review intent priority settings

4. Meeting Detection Issues:
   - Ensure calendar provider is connected
   - Check meeting keywords in email
   - Verify meeting has clear date/time
   - Review calendar permissions

5. Knowledge Base Not Loading:
   - Check user authentication
   - Verify knowledge base entries exist
   - Clear browser cache
   - Try re-login

ESCALATION:
For critical issues, email: urgent@emailassistant.ai
Include "URGENT" in subject line."""
        },
        {
            "title": "Security and Privacy",
            "category": "Security",
            "content": """Security & Privacy Measures:

DATA ENCRYPTION:
- All data encrypted in transit (TLS 1.3)
- Encryption at rest for stored data
- OAuth tokens encrypted in database
- Email content encrypted in storage

AUTHENTICATION:
- JWT-based authentication
- Secure password hashing (bcrypt)
- OAuth 2.0 for email/calendar access
- Session management with expiration

PRIVACY:
- GDPR compliant
- SOC 2 Type II certified
- Regular security audits
- Data retention policies

YOUR DATA:
- Email content: Stored for processing, deleted after 90 days
- Draft responses: Stored until sent, then archived
- OAuth tokens: Stored securely, refreshed automatically
- Analytics: Aggregated, no personal identifiers

YOUR RIGHTS:
- Right to access your data
- Right to delete your data
- Right to export your data
- Right to opt-out of analytics

THIRD-PARTY ACCESS:
- Google/Microsoft: Only authorized scopes
- AI Services: Email content sent for processing
- No data sold to third parties
- No marketing without consent

SECURITY BEST PRACTICES:
- Use strong, unique passwords
- Enable 2FA where available
- Review OAuth permissions regularly
- Revoke access for unused integrations
- Monitor account activity

DATA BREACH PROTOCOL:
- Immediate notification to affected users
- Root cause analysis within 24 hours
- Remediation steps communicated
- Compliance with notification laws

COMPLIANCE:
- GDPR (EU)
- CCPA (California)
- HIPAA (Healthcare) - Enterprise only
- SOC 2 Type II

For security concerns: security@emailassistant.ai
For privacy questions: privacy@emailassistant.ai"""
        }
    ]
    
    for kb_item in kb_data:
        kb = KnowledgeBase(
            user_id=USER_ID,
            title=kb_item["title"],
            category=kb_item["category"],
            content=kb_item["content"]
        )
        
        doc = kb.model_dump()
        await db.knowledge_base.insert_one(doc)
        
        print(f"   ✓ {kb.title} ({kb.category})")
    
    # ========== SUMMARY ==========
    print("\n" + "=" * 60)
    print("✅ SEED DATA CREATED SUCCESSFULLY!")
    print("=" * 60)
    print(f"\n📊 Summary:")
    print(f"   • {len(intents_data)} Intents created")
    print(f"   • {len(kb_data)} Knowledge Base entries created")
    print(f"   • User ID: {USER_ID}")
    
    print(f"\n🎯 Intent Configuration:")
    print(f"   • {sum(1 for i in intents_data if i['auto_send'])} intents with auto-send enabled")
    print(f"   • {sum(1 for i in intents_data if not i['auto_send'])} intents requiring manual review")
    print(f"   • 1 default intent for unmatched emails")
    
    print(f"\n📚 Knowledge Base Categories:")
    categories = set(item["category"] for item in kb_data)
    for cat in sorted(categories):
        count = sum(1 for item in kb_data if item["category"] == cat)
        print(f"   • {cat}: {count} entries")
    
    print(f"\n🚀 Next Steps:")
    print(f"   1. Refresh frontend to see new intents and knowledge base")
    print(f"   2. Connect email account via OAuth if not already done")
    print(f"   3. Connect Google Calendar for meeting features")
    print(f"   4. Send test email to verify complete flow")
    print(f"   5. Monitor Dashboard for processing statistics")
    
    # Close connection
    client.close()

if __name__ == "__main__":
    asyncio.run(create_seed_data())
