"""
Create seed data for Intents and Knowledge Base for user amits.joys@gmail.com
"""
import asyncio
import sys
sys.path.append('/app/backend')

from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import uuid

# MongoDB connection
MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "email_assistant_db"

async def create_seed_data():
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Find user by email
    user = await db.users.find_one({"email": "amits.joys@gmail.com"})
    if not user:
        print("❌ User amits.joys@gmail.com not found!")
        return
    
    user_id = user['id']
    print(f"✓ Found user: {user['email']} (ID: {user_id})")
    
    # Delete existing intents and knowledge base for this user
    deleted_intents = await db.intents.delete_many({"user_id": user_id})
    deleted_kb = await db.knowledge_base.delete_many({"user_id": user_id})
    print(f"✓ Deleted {deleted_intents.deleted_count} existing intents")
    print(f"✓ Deleted {deleted_kb.deleted_count} existing knowledge base entries")
    
    # Create timestamp
    now = datetime.now(timezone.utc).isoformat()
    
    # ============================================================================
    # CREATE INTENTS
    # ============================================================================
    
    intents = [
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Meeting Request",
            "description": "Handle meeting and scheduling requests",
            "prompt": """You are responding to a meeting or scheduling request. Be professional and helpful.

Guidelines:
- Acknowledge the meeting request warmly
- If a calendar event was created, mention the meeting details naturally
- Include the Google Meet link and calendar link if provided
- Confirm the date, time, and timezone
- Offer flexibility for rescheduling if needed
- Keep the tone professional but friendly""",
            "keywords": ["meeting", "schedule", "calendar", "appointment", "call", "zoom", "teams", "discuss", "sync", "catch up", "meet"],
            "auto_send": True,
            "priority": 10,
            "is_default": False,
            "is_active": True,
            "created_at": now,
            "updated_at": now
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Meeting Reschedule",
            "description": "Handle requests to reschedule existing meetings",
            "prompt": """You are responding to a request to reschedule a meeting.

Guidelines:
- Acknowledge the reschedule request professionally
- Show understanding and flexibility
- If a new calendar event was created, provide the updated details
- Include the new Google Meet link and calendar link if provided
- Confirm the new date, time, and timezone
- Apologize for any inconvenience if appropriate""",
            "keywords": ["reschedule", "change meeting", "move meeting", "different time", "postpone", "delay"],
            "auto_send": True,
            "priority": 9,
            "is_default": False,
            "is_active": True,
            "created_at": now,
            "updated_at": now
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Support Request",
            "description": "Handle technical support and problem-solving requests",
            "prompt": """You are responding to a support or technical issue request.

Guidelines:
- Show empathy and understanding
- Acknowledge the issue clearly
- Use the knowledge base to provide relevant troubleshooting steps
- Be specific and actionable in your guidance
- Offer to follow up if the issue persists
- Keep the tone supportive and helpful""",
            "keywords": ["issue", "problem", "error", "help", "support", "not working", "bug", "broken", "fix", "troubleshoot"],
            "auto_send": True,
            "priority": 8,
            "is_default": False,
            "is_active": True,
            "created_at": now,
            "updated_at": now
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "General Inquiry",
            "description": "Handle general questions about products, services, or information",
            "prompt": """You are responding to a general inquiry or question.

Guidelines:
- Answer the question directly using information from the knowledge base
- Be clear and concise
- Provide relevant details without overwhelming
- Offer additional resources or information if helpful
- Encourage follow-up questions
- Maintain a friendly, informative tone""",
            "keywords": ["question", "inquiry", "information", "tell me", "how", "what", "when", "where", "why", "explain"],
            "auto_send": True,
            "priority": 5,
            "is_default": False,
            "is_active": True,
            "created_at": now,
            "updated_at": now
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Follow-up Request",
            "description": "Handle follow-up emails and status update requests",
            "prompt": """You are responding to a follow-up or status update request.

Guidelines:
- Review the conversation thread carefully
- Provide a clear status update based on context
- Reference previous communications naturally
- Be transparent about progress or delays
- Set clear expectations for next steps
- Keep the tone professional and proactive""",
            "keywords": ["follow up", "followup", "following up", "checking in", "status", "update", "any progress", "any news"],
            "auto_send": True,
            "priority": 7,
            "is_default": False,
            "is_active": True,
            "created_at": now,
            "updated_at": now
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Introduction",
            "description": "Handle introduction and networking emails",
            "prompt": """You are responding to an introduction or networking email.

Guidelines:
- Respond warmly and professionally
- Acknowledge the introduction graciously
- Use knowledge base to share relevant background about yourself/company
- Express interest in potential collaboration
- Suggest next steps or offer to schedule a conversation
- Keep the tone friendly and open""",
            "keywords": ["introduction", "introduce", "introducing", "connection", "network", "reach out", "connect"],
            "auto_send": True,
            "priority": 6,
            "is_default": False,
            "is_active": True,
            "created_at": now,
            "updated_at": now
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Thank You",
            "description": "Handle thank you and appreciation emails",
            "prompt": """You are responding to a thank you or appreciation email.

Guidelines:
- Acknowledge the thanks graciously
- Be warm and genuine in your response
- Keep it brief and appropriate
- Reinforce the positive relationship
- Offer continued support if relevant
- Maintain a friendly, professional tone""",
            "keywords": ["thank you", "thanks", "appreciate", "grateful", "gratitude"],
            "auto_send": True,
            "priority": 4,
            "is_default": False,
            "is_active": True,
            "created_at": now,
            "updated_at": now
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Default Intent",
            "description": "Handle emails that don't match any specific category",
            "prompt": """You are responding to an email that doesn't match any specific category.

Guidelines:
- Use the knowledge base to craft a helpful, relevant response
- Focus on understanding the sender's intent
- Be professional and courteous
- Provide value based on available information
- If unsure about specific details, acknowledge it professionally
- Offer to get more information or direct them to the right resource
- Keep the tone helpful and approachable""",
            "keywords": [],
            "auto_send": True,
            "priority": 1,
            "is_default": True,
            "is_active": True,
            "created_at": now,
            "updated_at": now
        }
    ]
    
    # Insert intents
    result = await db.intents.insert_many(intents)
    print(f"\n✓ Created {len(result.inserted_ids)} intents:")
    for intent in intents:
        auto_send_label = "✅ Auto-send" if intent['auto_send'] else "❌ Manual"
        default_label = " [DEFAULT]" if intent['is_default'] else ""
        print(f"  - {intent['name']} (Priority: {intent['priority']}, {auto_send_label}){default_label}")
    
    # ============================================================================
    # CREATE KNOWLEDGE BASE
    # ============================================================================
    
    knowledge_base = [
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Company Overview",
            "content": """We are a technology company focused on AI-powered productivity solutions. Our mission is to help businesses automate routine tasks and improve communication efficiency.

Key Information:
- Founded: 2023
- Team Size: 15-20 employees
- Location: Remote-first company with headquarters in San Francisco
- Focus Areas: Email automation, AI assistants, workflow optimization
- Core Values: Innovation, Customer-centricity, Transparency, Continuous Improvement

Our flagship product is an AI email assistant that helps businesses manage their email communications more efficiently through intelligent automation and smart responses.""",
            "category": "Company Information",
            "tags": ["company", "about", "overview"],
            "embedding": None,
            "is_active": True,
            "created_at": now,
            "updated_at": now
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Product Features",
            "content": """Our AI Email Assistant includes the following features:

1. Intelligent Email Classification
   - Automatically categorizes incoming emails by intent
   - Keyword-based matching with customizable rules
   - Priority-based processing

2. Automated Response Generation
   - AI-powered draft creation using GPT models
   - Knowledge base integration for accurate information
   - Customizable response templates per intent
   - Multi-attempt validation for quality assurance

3. Calendar Integration
   - Automatic meeting detection from emails
   - Google Calendar event creation
   - Google Meet link generation
   - Conflict detection and notifications
   - Reminder system (1 hour before events)

4. Follow-up Management
   - Automatic follow-up scheduling
   - Smart cancellation when replies are received
   - Customizable follow-up intervals

5. Thread Management
   - Maintains conversation context
   - All replies sent in the same thread
   - Prevents repetitive information

6. Multi-Account Support
   - OAuth integration with Gmail
   - SMTP support for other email providers
   - Per-account personas and signatures""",
            "category": "Product",
            "tags": ["features", "capabilities", "product"],
            "embedding": None,
            "is_active": True,
            "created_at": now,
            "updated_at": now
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Meeting and Calendar Features",
            "content": """Our system provides comprehensive meeting and calendar management:

Meeting Detection:
- Automatically identifies meeting requests in emails
- Extracts date, time, timezone, location, and attendees
- Handles relative dates ("tomorrow", "next Tuesday")
- Confidence scoring for accuracy

Calendar Event Creation:
- Creates events in Google Calendar automatically
- Generates Google Meet links for virtual meetings
- Sends event details in the email response
- Includes calendar view links
- Timezone-aware scheduling

Event Management:
- Update existing events via API
- Reschedule meetings
- Conflict detection across your calendar
- Event notifications via email

Reminder System:
- Automatic reminders sent 1 hour before events
- Email notifications with meeting details
- Join links included for easy access

All meeting communications happen in the same email thread for easy tracking.""",
            "category": "Meetings",
            "tags": ["meetings", "calendar", "scheduling"],
            "embedding": None,
            "is_active": True,
            "created_at": now,
            "updated_at": now
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Pricing Information",
            "content": """Our pricing is designed to scale with your needs:

Starter Plan - $29/month
- 1 email account
- 500 emails/month
- Basic intent templates
- Email support
- Perfect for: Solo professionals, freelancers

Professional Plan - $79/month
- 3 email accounts
- 2,000 emails/month
- Custom intent creation
- Knowledge base management
- Calendar integration
- Priority email support
- Perfect for: Small teams, growing businesses

Business Plan - $199/month
- 10 email accounts
- 10,000 emails/month
- Advanced automation
- Team collaboration features
- API access
- Dedicated support
- Perfect for: Established businesses, agencies

Enterprise Plan - Custom Pricing
- Unlimited email accounts
- Custom email volume
- Custom AI models
- White-label options
- SLA guarantees
- Dedicated account manager
- Perfect for: Large organizations

All plans include:
- AI-powered responses
- Thread management
- Follow-up automation
- Analytics dashboard

Free 14-day trial available for all plans. No credit card required.""",
            "category": "Pricing",
            "tags": ["pricing", "plans", "cost"],
            "embedding": None,
            "is_active": True,
            "created_at": now,
            "updated_at": now
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Getting Started Guide",
            "content": """Getting started with our AI Email Assistant is easy:

Step 1: Connect Your Email Account
- Click "Email Accounts" in the sidebar
- Choose OAuth (Gmail) or SMTP connection
- Follow the authorization flow
- Your account will sync automatically

Step 2: Set Up Your Persona
- Edit your email account settings
- Add a persona (your communication style)
- Add a signature (appears in all emails)
- Save changes

Step 3: Create Intents
- Navigate to "Intents" page
- Create intents for different email types
- Add keywords for detection
- Write response guidelines
- Enable auto-send for trusted intents

Step 4: Add Knowledge Base
- Go to "Knowledge Base" page
- Add information about your company, products, policies
- Categorize entries for easy reference
- The AI will use this for accurate responses

Step 5: Connect Calendar (Optional)
- Go to "Calendar Providers"
- Connect your Google Calendar
- Enable automatic meeting creation
- Configure reminder preferences

Step 6: Monitor and Refine
- Check the "Emails" dashboard
- Review auto-generated responses
- Adjust intents based on performance
- Update knowledge base as needed

Tips for Success:
- Start with auto-send disabled, review drafts manually
- Enable auto-send for low-risk intents (thank you notes)
- Keep knowledge base updated
- Use specific keywords for better intent matching
- Review and adjust priorities regularly""",
            "category": "Documentation",
            "tags": ["getting started", "setup", "onboarding"],
            "embedding": None,
            "is_active": True,
            "created_at": now,
            "updated_at": now
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Support and Contact",
            "content": """We're here to help you succeed:

Support Channels:
- Email: support@example.com (24-hour response time)
- Priority Support: priority@example.com (Business plan and above, 4-hour response)
- Live Chat: Available 9 AM - 6 PM EST, Monday-Friday
- Help Center: help.example.com (documentation, FAQs, tutorials)

Common Issues:
1. Email Not Syncing
   - Check OAuth token expiration
   - Verify SMTP credentials
   - Check internet connection
   - Restart email worker

2. Poor Response Quality
   - Review and update knowledge base
   - Adjust intent prompts
   - Check keyword matches
   - Verify persona is set

3. Calendar Events Not Creating
   - Verify calendar provider connected
   - Check OAuth permissions
   - Ensure meeting detected with high confidence
   - Review calendar API quotas

4. Follow-ups Not Sending
   - Check follow-up settings in intent
   - Verify email account active
   - Review follow-up schedule
   - Check worker status

Emergency Contact:
For critical issues affecting your business, call our emergency hotline: +1 (555) 123-4567

Business Hours: Monday-Friday, 9 AM - 6 PM EST
We aim to respond to all inquiries within 24 hours.""",
            "category": "Support",
            "tags": ["support", "help", "contact"],
            "embedding": None,
            "is_active": True,
            "created_at": now,
            "updated_at": now
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Security and Privacy",
            "content": """We take your data security and privacy seriously:

Data Security:
- All data encrypted at rest (AES-256)
- All data encrypted in transit (TLS 1.3)
- Regular security audits and penetration testing
- SOC 2 Type II certified
- GDPR and CCPA compliant

Email Security:
- OAuth tokens encrypted in database
- Passwords encrypted with industry-standard algorithms
- No plaintext storage of credentials
- Automatic token refresh
- Secure API communication

Privacy Commitments:
- We never read your emails beyond what's needed for processing
- We never share your data with third parties
- We never use your data for training public AI models
- You can delete your data at any time
- You own all your email data

AI Models:
- We use Groq API for AI processing
- Your emails are processed securely
- No data retention by AI provider
- Models don't learn from your specific emails

Compliance:
- GDPR compliant (EU)
- CCPA compliant (California)
- HIPAA available for healthcare (Enterprise plan)
- Regular compliance audits

Data Retention:
- Email data retained as long as account is active
- Can be deleted on request
- 30-day grace period after account deletion
- Backups retained for 90 days for recovery

For detailed security information, visit: security.example.com
For privacy policy: privacy.example.com""",
            "category": "Security",
            "tags": ["security", "privacy", "compliance"],
            "embedding": None,
            "is_active": True,
            "created_at": now,
            "updated_at": now
        }
    ]
    
    # Insert knowledge base
    result = await db.knowledge_base.insert_many(knowledge_base)
    print(f"\n✓ Created {len(result.inserted_ids)} knowledge base entries:")
    for kb in knowledge_base:
        print(f"  - {kb['title']} ({kb['category']})")
    
    print("\n" + "="*80)
    print("✅ SEED DATA CREATION COMPLETE!")
    print("="*80)
    print(f"\nUser: amits.joys@gmail.com")
    print(f"Intents: {len(intents)} (7 with auto-send enabled, 1 default)")
    print(f"Knowledge Base: {len(knowledge_base)} entries")
    print("\nThe system is now ready to process emails!")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(create_seed_data())
