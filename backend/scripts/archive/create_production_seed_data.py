#!/usr/bin/env python3
"""
Create comprehensive production seed data including:
- Intents
- Knowledge Base
- Campaigns
- Inbound Leads
- Campaign Templates
"""
import asyncio
import uuid
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from config import Config

USER_EMAIL = "amits.joys@gmail.com"


def get_timestamp(days_ago: int = 0, hours_ago: int = 0):
    """Get ISO timestamp for a specific time in the past"""
    dt = datetime.now(timezone.utc) - timedelta(days=days_ago, hours=hours_ago)
    return dt.isoformat()


async def create_production_seed_data():
    """Create comprehensive production seed data"""
    print("🚀 Creating Production Seed Data...")
    print("=" * 70)
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(Config.MONGO_URL)
    db = client[Config.DB_NAME]
    
    # Get user
    user = await db.users.find_one({"email": USER_EMAIL})
    if not user:
        print(f"❌ User {USER_EMAIL} not found!")
        print("Please ensure the user account is created first.")
        client.close()
        return
    
    user_id = user['id']
    print(f"✅ Found user: {USER_EMAIL} (ID: {user_id})\n")
    
    # ========================================
    # 1. CREATE INTENTS
    # ========================================
    print("📋 Creating Intents...")
    await db.intents.delete_many({"user_id": user_id})
    
    intents = [
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Meeting Request",
            "description": "Emails requesting to schedule a meeting or call",
            "keywords": ["meeting", "schedule", "call", "discuss", "meet", "zoom", "teams", "appointment", "demo", "presentation"],
            "prompt": "You are a professional assistant scheduling meetings. Be courteous, confirm availability, and suggest meeting times if not provided. Always include calendar details if a meeting is being scheduled.",
            "priority": 10,
            "auto_send": True,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Meeting Reschedule",
            "description": "Requests to change or reschedule existing meetings",
            "keywords": ["reschedule", "change meeting", "move meeting", "different time", "postpone", "cancel meeting"],
            "prompt": "You are helping to reschedule a meeting. Be understanding and flexible. Acknowledge the need to reschedule and propose alternative times.",
            "priority": 9,
            "auto_send": True,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Support Request",
            "description": "Technical support or help requests",
            "keywords": ["help", "support", "issue", "problem", "error", "bug", "not working", "assistance", "troubleshoot"],
            "prompt": "You are a technical support specialist. Be helpful, patient, and provide clear solutions. Ask for relevant details if needed.",
            "priority": 8,
            "auto_send": True,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Follow-up Request",
            "description": "Requests for follow-up communication",
            "keywords": ["follow up", "follow-up", "check in", "update", "status", "progress", "any news"],
            "prompt": "You are providing a follow-up. Be proactive and informative. Reference previous conversations and provide relevant updates.",
            "priority": 7,
            "auto_send": True,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Introduction",
            "description": "Introduction or networking emails",
            "keywords": ["introduction", "introduce", "connect", "networking", "pleasure", "nice to meet", "reaching out"],
            "prompt": "You are responding to an introduction. Be warm, professional, and express interest in connecting. Mention relevant background if applicable.",
            "priority": 6,
            "auto_send": True,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "General Inquiry",
            "description": "General questions about products, services, or information",
            "keywords": ["question", "inquiry", "wondering", "curious", "information", "details", "learn more", "pricing"],
            "prompt": "You are answering a general inquiry. Be informative, clear, and helpful. Use knowledge base to provide accurate information.",
            "priority": 5,
            "auto_send": True,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Thank You",
            "description": "Gratitude and appreciation emails",
            "keywords": ["thank you", "thanks", "grateful", "appreciate", "appreciated", "gratitude"],
            "prompt": "You are responding to a thank you message. Be gracious and warm. Express that you're happy to help.",
            "priority": 4,
            "auto_send": True,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Default Intent",
            "description": "Catch-all intent for emails that don't match other categories",
            "keywords": [],
            "prompt": "You are a professional assistant. Respond appropriately based on the email content. Be helpful and courteous.",
            "priority": 1,
            "auto_send": True,
            "is_default": True,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    await db.intents.insert_many(intents)
    print(f"  ✅ Created {len(intents)} intents")
    
    # Store intent IDs for later use
    meeting_intent = next(i for i in intents if "Meeting Request" in i['name'])
    general_intent = next(i for i in intents if "General Inquiry" in i['name'])
    support_intent = next(i for i in intents if "Support Request" in i['name'])
    
    # ========================================
    # 2. CREATE KNOWLEDGE BASE
    # ========================================
    print("\n📚 Creating Knowledge Base...")
    await db.knowledge_base.delete_many({"user_id": user_id})
    
    knowledge_base = [
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Company Overview",
            "content": """We are a cutting-edge AI-powered email assistant platform that helps professionals manage their email communication efficiently. Our platform automates email responses, schedules meetings, and ensures no important message goes unanswered.

Key Features:
- AI-powered draft generation
- Automatic email classification
- Meeting scheduling with calendar integration
- Smart follow-up system
- Knowledge base integration for accurate responses
- Multi-account support (Gmail, Outlook, custom SMTP)
- Campaign management for outbound emails

Our mission is to save professionals time and improve communication quality through intelligent automation.""",
            "category": "Company Information",
            "tags": ["company", "overview", "about", "platform"],
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Product Features",
            "content": """Our AI Email Assistant includes the following features:

1. Smart Email Classification
   - Automatic intent detection
   - Priority-based handling
   - Context-aware responses

2. AI Draft Generation
   - Uses your knowledge base
   - Maintains your tone and style
   - Includes relevant information automatically

3. Meeting Scheduling
   - Automatic calendar integration
   - Google Meet link generation
   - Conflict detection
   - Meeting reminders

4. Follow-Up System
   - Time-based follow-ups
   - Automatic follow-up scheduling
   - Reply detection and cancellation

5. Campaign Management
   - Outbound email campaigns
   - Contact list management
   - Template personalization
   - Follow-up sequences

6. Multi-Account Support
   - Gmail OAuth integration
   - Outlook/Microsoft OAuth
   - Custom SMTP/IMAP support""",
            "category": "Product",
            "tags": ["features", "capabilities", "functionality"],
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Meeting and Calendar Features",
            "content": """Our platform provides comprehensive meeting and calendar management:

Meeting Detection:
- Automatically detects meeting requests in emails
- Extracts meeting details (date, time, attendees, agenda)
- High confidence threshold ensures accuracy

Calendar Integration:
- Direct integration with Google Calendar
- Automatic event creation with all details
- Google Meet links generated automatically
- Calendar conflict detection
- Meeting reminders sent 1 hour before

Event Details in Responses:
- Meeting confirmation emails include all details
- Date, time, and timezone clearly stated
- Google Meet joining link provided
- Calendar view link included
- Attendee information listed

Calendar Event Updates:
- Reschedule meetings via email
- Automatic calendar synchronization
- Updated details sent to all attendees""",
            "category": "Meetings",
            "tags": ["meetings", "calendar", "scheduling", "google meet"],
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Pricing Information",
            "content": """Our pricing is designed to be transparent and flexible:

Free Tier:
- 100 emails per month
- 1 email account
- Basic AI responses
- Standard support

Professional ($29/month):
- 1,000 emails per month
- 3 email accounts
- Advanced AI with knowledge base
- Priority support
- Calendar integration
- Meeting scheduling

Enterprise (Custom):
- Unlimited emails
- Unlimited accounts
- Custom AI training
- Dedicated support
- API access
- Custom integrations
- SLA guarantees

All plans include:
- Automatic follow-ups
- Campaign management
- Email templates
- Analytics dashboard

Contact us for volume discounts and custom solutions.""",
            "category": "Pricing",
            "tags": ["pricing", "plans", "cost", "subscription"],
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Support and Contact",
            "content": """We're here to help! Here's how to get support:

Email Support:
- support@emailassistant.ai
- Response time: Within 24 hours
- Include your account email for faster service

Live Chat:
- Available Monday-Friday, 9 AM - 6 PM EST
- Access via platform dashboard
- Instant assistance for urgent issues

Documentation:
- Comprehensive guides at docs.emailassistant.ai
- Video tutorials available
- API documentation for developers

Common Issues:
1. Email not syncing: Check OAuth token validity
2. AI not responding: Verify intent configuration
3. Meeting not creating: Ensure calendar is connected
4. Follow-ups not working: Check account settings

Feature Requests:
- Submit via feedback form
- Community voting on roadmap
- Regular feature updates""",
            "category": "Support",
            "tags": ["support", "help", "contact", "assistance"],
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    await db.knowledge_base.insert_many(knowledge_base)
    print(f"  ✅ Created {len(knowledge_base)} knowledge base entries")
    
    # ========================================
    # 3. CREATE CAMPAIGN TEMPLATES
    # ========================================
    print("\n📝 Creating Campaign Templates...")
    
    templates = [
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Initial Outreach",
            "description": "Initial email template for cold outreach",
            "subject": "Quick question about {{company}}",
            "body": """Hi {{first_name}},

I noticed you're working at {{company}} as {{title}}. I wanted to reach out because I think we could help your team with AI-powered email automation.

Our platform helps professionals like you:
- Automate routine email responses
- Schedule meetings automatically
- Never miss important emails
- Save hours every week

Would you be open to a quick 15-minute call this week to discuss how we can help {{company}}?

Looking forward to hearing from you!""",
            "available_tags": ["email", "first_name", "last_name", "company", "title", "linkedin_url", "company_domain"],
            "template_type": "initial",
            "times_used": 0,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Follow-up 1",
            "description": "First follow-up email",
            "subject": "Re: Quick question about {{company}}",
            "body": """Hi {{first_name}},

I wanted to follow up on my previous email. I know you're probably busy, but I genuinely believe we could add value to {{company}}.

Our AI email assistant has helped companies like yours save an average of 10 hours per week on email management.

Are you available for a brief chat this week?

Best regards!""",
            "available_tags": ["email", "first_name", "last_name", "company", "title"],
            "template_type": "follow_up_1",
            "times_used": 0,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Follow-up 2",
            "description": "Second follow-up email",
            "subject": "Re: Quick question about {{company}}",
            "body": """Hi {{first_name}},

This is my last follow-up. I understand if now isn't the right time, but I wanted to make sure you had the opportunity to learn about how we're helping companies like {{company}}.

If you're interested, just reply to this email and we'll find a time that works.

Thanks for your time!""",
            "available_tags": ["email", "first_name", "last_name", "company"],
            "template_type": "follow_up_2",
            "times_used": 0,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    await db.campaign_templates.insert_many(templates)
    print(f"  ✅ Created {len(templates)} campaign templates")
    
    # ========================================
    # 4. CREATE INBOUND LEADS
    # ========================================
    print("\n👥 Creating Inbound Leads...")
    await db.inbound_leads.delete_many({"user_id": user_id})
    
    leads = [
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "lead_name": "Sarah Johnson",
            "lead_email": "sarah.johnson@techcorp.com",
            "company_name": "TechCorp Solutions",
            "address": "123 Business Park, San Francisco, CA 94105",
            "phone": "+1 (415) 555-0123",
            "job_title": "VP of Engineering",
            "company_size": "200-500 employees",
            "industry": "Technology",
            "specific_interests": "AI-powered email automation for engineering team",
            "requirements": "Need solution for 50+ engineers, must integrate with Slack and Jira",
            "source": "email",
            "stage": "qualified",
            "stage_changed_at": get_timestamp(days_ago=1),
            "stage_history": [
                {
                    "stage": "new",
                    "changed_at": get_timestamp(days_ago=7),
                    "performed_by": "system",
                    "reason": "Lead created from initial email"
                },
                {
                    "stage": "contacted",
                    "changed_at": get_timestamp(days_ago=6),
                    "performed_by": "system",
                    "reason": "Auto-reply sent with product information"
                },
                {
                    "stage": "qualified",
                    "changed_at": get_timestamp(days_ago=1),
                    "performed_by": user_id,
                    "reason": "Budget confirmed, decision-maker identified"
                }
            ],
            "score": 85,
            "priority": "high",
            "initial_email_id": str(uuid.uuid4()),
            "thread_id": f"thread-{uuid.uuid4()}",
            "email_ids": [str(uuid.uuid4()), str(uuid.uuid4())],
            "intent_id": meeting_intent['id'],
            "intent_name": "Meeting Request",
            "emails_received": 3,
            "emails_sent": 3,
            "last_contact_at": get_timestamp(days_ago=1),
            "last_reply_at": get_timestamp(days_ago=1, hours_ago=2),
            "response_time_avg": 1.5,
            "meeting_scheduled": True,
            "meeting_date": get_timestamp(days_ago=-3),
            "calendar_event_id": str(uuid.uuid4()),
            "activities": [
                {
                    "timestamp": get_timestamp(days_ago=7),
                    "activity_type": "email_received",
                    "description": "Initial inquiry email received",
                    "details": {"subject": "Interested in AI Email Assistant"},
                    "performed_by": "system"
                },
                {
                    "timestamp": get_timestamp(days_ago=1),
                    "activity_type": "meeting_scheduled",
                    "description": "Demo meeting scheduled",
                    "details": {"meeting_date": get_timestamp(days_ago=-3)},
                    "performed_by": "system"
                }
            ],
            "is_active": True,
            "notes": "Very engaged prospect. VP of Engineering with decision-making authority.",
            "created_at": get_timestamp(days_ago=7),
            "updated_at": get_timestamp(days_ago=1)
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "lead_name": "Michael Chen",
            "lead_email": "m.chen@startupxyz.io",
            "company_name": "StartupXYZ",
            "phone": "+1 (650) 555-0198",
            "job_title": "Founder & CEO",
            "company_size": "10-50 employees",
            "industry": "SaaS",
            "specific_interests": "Quick setup for small team",
            "requirements": "Need immediate solution, team of 15",
            "source": "email",
            "stage": "new",
            "stage_changed_at": get_timestamp(hours_ago=4),
            "stage_history": [
                {
                    "stage": "new",
                    "changed_at": get_timestamp(hours_ago=4),
                    "performed_by": "system",
                    "reason": "Lead created from initial email"
                }
            ],
            "score": 70,
            "priority": "urgent",
            "initial_email_id": str(uuid.uuid4()),
            "thread_id": f"thread-{uuid.uuid4()}",
            "email_ids": [str(uuid.uuid4())],
            "intent_id": general_intent['id'],
            "intent_name": "General Inquiry",
            "emails_received": 1,
            "emails_sent": 1,
            "last_contact_at": get_timestamp(hours_ago=4),
            "last_reply_at": get_timestamp(hours_ago=3),
            "response_time_avg": 1.0,
            "meeting_scheduled": False,
            "activities": [
                {
                    "timestamp": get_timestamp(hours_ago=4),
                    "activity_type": "email_received",
                    "description": "Urgent inquiry - need solution ASAP",
                    "details": {"subject": "URGENT: Email automation needed"},
                    "performed_by": "system"
                }
            ],
            "is_active": True,
            "notes": "Urgent lead - startup founder, needs quick decision.",
            "created_at": get_timestamp(hours_ago=4),
            "updated_at": get_timestamp(hours_ago=3)
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "lead_name": "Emily Rodriguez",
            "lead_email": "emily.r@marketingpros.com",
            "company_name": "Marketing Pros Agency",
            "phone": "+1 (213) 555-0167",
            "job_title": "Director of Operations",
            "company_size": "50-200 employees",
            "industry": "Marketing & Advertising",
            "specific_interests": "Managing client emails efficiently",
            "requirements": "Need for marketing team of 30",
            "source": "email",
            "stage": "contacted",
            "stage_changed_at": get_timestamp(days_ago=3),
            "stage_history": [
                {
                    "stage": "new",
                    "changed_at": get_timestamp(days_ago=4),
                    "performed_by": "system",
                    "reason": "Lead created"
                },
                {
                    "stage": "contacted",
                    "changed_at": get_timestamp(days_ago=3),
                    "performed_by": "system",
                    "reason": "Auto-reply sent"
                }
            ],
            "score": 65,
            "priority": "medium",
            "initial_email_id": str(uuid.uuid4()),
            "thread_id": f"thread-{uuid.uuid4()}",
            "email_ids": [str(uuid.uuid4()), str(uuid.uuid4())],
            "intent_id": general_intent['id'],
            "intent_name": "General Inquiry",
            "emails_received": 2,
            "emails_sent": 2,
            "last_contact_at": get_timestamp(days_ago=3),
            "last_reply_at": get_timestamp(days_ago=2),
            "response_time_avg": 6.0,
            "meeting_scheduled": False,
            "activities": [
                {
                    "timestamp": get_timestamp(days_ago=4),
                    "activity_type": "email_received",
                    "description": "Initial inquiry about product",
                    "details": {"subject": "Email automation for marketing team"},
                    "performed_by": "system"
                }
            ],
            "is_active": True,
            "notes": "Interested in solution for marketing team.",
            "created_at": get_timestamp(days_ago=4),
            "updated_at": get_timestamp(days_ago=2)
        }
    ]
    
    await db.inbound_leads.insert_many(leads)
    print(f"  ✅ Created {len(leads)} inbound leads")
    
    # ========================================
    # SUMMARY
    # ========================================
    print("\n" + "=" * 70)
    print("✅ PRODUCTION SEED DATA CREATION COMPLETED!")
    print("=" * 70)
    print(f"\n📊 Summary:")
    print(f"   - User: {USER_EMAIL} (ID: {user_id})")
    print(f"   - Intents: {len(intents)} created (auto_send enabled for all)")
    print(f"   - Knowledge Base: {len(knowledge_base)} entries")
    print(f"   - Campaign Templates: {len(templates)} templates")
    print(f"   - Inbound Leads: {len(leads)} leads")
    print(f"\n📋 Intent Categories:")
    for intent in intents:
        print(f"   - {intent['name']} (Priority: {intent['priority']})")
    print(f"\n👥 Inbound Leads by Stage:")
    stage_counts = {}
    for lead in leads:
        stage = lead['stage']
        stage_counts[stage] = stage_counts.get(stage, 0) + 1
    for stage, count in sorted(stage_counts.items()):
        print(f"   - {stage.upper()}: {count} leads")
    
    print("\n🎉 Ready for production testing!")
    print("=" * 70)
    
    client.close()


if __name__ == "__main__":
    asyncio.run(create_production_seed_data())
