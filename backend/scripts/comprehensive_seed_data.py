#!/usr/bin/env python3
"""
COMPREHENSIVE SEED DATA SCRIPT
================================
Creates complete app data for user: amits.joys@gmail.com
Covers ALL models in the application:
- User (with lead settings enabled)
- Email Account
- Intents (with lead qualification & nurturing)
- Knowledge Base
- Lead Qualification Criteria
- Lead Nurturing Config
- Campaign Templates
- Campaign Contacts
- Contact Lists
- Campaigns
- Campaign Emails
- Inbound Leads
- Calendar Provider
- Follow-ups

This is the ONE script to seed complete data for the entire app.
"""
import asyncio
import uuid
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta
from passlib.context import CryptContext

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from config import Config

# User credentials
USER_EMAIL = "amits.joys@gmail.com"
USER_PASSWORD = "ij@123..."
USER_NAME = "Amit Joys"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_timestamp(days_ago: int = 0, hours_ago: int = 0):
    """Get ISO timestamp for a specific time in the past"""
    dt = datetime.now(timezone.utc) - timedelta(days=days_ago, hours=hours_ago)
    return dt.isoformat()


def get_future_timestamp(days_ahead: int = 0, hours_ahead: int = 0):
    """Get ISO timestamp for a specific time in the future"""
    dt = datetime.now(timezone.utc) + timedelta(days=days_ahead, hours=hours_ahead)
    return dt.isoformat()


async def create_or_update_user(db):
    """Create or update user"""
    print("👤 Creating/Updating User...")
    
    user = await db.users.find_one({"email": USER_EMAIL})
    
    user_data = {
        "email": USER_EMAIL,
        "password_hash": pwd_context.hash(USER_PASSWORD),
        "full_name": USER_NAME,
        "quota": 1000,
        "quota_used": 0,
        "quota_reset_date": get_timestamp(),
        "role": "user",
        "is_active": True,
        "hubspot_enabled": False,
        "hubspot_connected": False,
        "hubspot_auto_sync": False,
        "global_lead_qualification_enabled": True,
        "global_lead_nurturing_enabled": True,
        "timezone": "America/New_York",
        "working_hours_start": "09:00",
        "working_hours_end": "17:00",
        "working_days": [1, 2, 3, 4, 5],
        "updated_at": get_timestamp()
    }
    
    if user:
        user_id = user['id']
        await db.users.update_one(
            {"id": user_id},
            {"$set": user_data}
        )
        print(f"✅ Updated existing user: {USER_EMAIL} (ID: {user_id})")
    else:
        user_id = str(uuid.uuid4())
        user_data["id"] = user_id
        user_data["created_at"] = get_timestamp()
        await db.users.insert_one(user_data)
        print(f"✅ Created new user: {USER_EMAIL} (ID: {user_id})")
    
    return user_id


async def create_intents(db, user_id):
    """Create intents with lead qualification & nurturing"""
    print("\n📋 Creating Intents...")
    await db.intents.delete_many({"user_id": user_id})
    
    intents = [
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Pricing Inquiry (Lead)",
            "description": "Customers asking about pricing, plans, and costs",
            "keywords": ["pricing", "price", "cost", "plan", "subscription", "package", "quote", "how much", "budget", "estimate"],
            "prompt": "You are a helpful sales assistant. Respond to pricing inquiries professionally. Ask qualifying questions about their needs, company size, and timeline. Provide general pricing information and offer to schedule a detailed discussion.",
            "priority": 10,
            "auto_send": True,
            "is_inbound_lead": True,
            "enable_lead_qualification": True,
            "enable_lead_nurturing": True,
            "is_active": True,
            "is_default": False,
            "created_at": get_timestamp(),
            "updated_at": get_timestamp()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Demo Request (Lead)",
            "description": "Requests for product demos and trials",
            "keywords": ["demo", "demonstration", "show me", "trial", "test", "try", "walkthrough", "preview", "see it"],
            "prompt": "You are a product specialist. Respond enthusiastically to demo requests. Ask about their use case, team size, and preferred meeting time. Confirm their contact information and timeline.",
            "priority": 9,
            "auto_send": True,
            "is_inbound_lead": True,
            "enable_lead_qualification": True,
            "enable_lead_nurturing": True,
            "is_active": True,
            "is_default": False,
            "created_at": get_timestamp(),
            "updated_at": get_timestamp()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Partnership Inquiry (Lead)",
            "description": "Business partnership and collaboration requests",
            "keywords": ["partnership", "partner", "collaborate", "collaboration", "integrate", "integration", "reseller", "affiliate"],
            "prompt": "You are a partnership manager. Respond professionally to partnership inquiries. Ask about their company, target market, and partnership goals. Express interest and request more details.",
            "priority": 8,
            "auto_send": False,
            "is_inbound_lead": True,
            "enable_lead_qualification": True,
            "enable_lead_nurturing": False,
            "is_active": True,
            "is_default": False,
            "created_at": get_timestamp(),
            "updated_at": get_timestamp()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Support Request",
            "description": "Technical support and help requests",
            "keywords": ["help", "support", "issue", "problem", "error", "bug", "not working", "broken", "fix"],
            "prompt": "You are a support specialist. Respond empathetically to support requests. Ask for specific details about the issue, error messages, and steps to reproduce. Assure them you'll help resolve it quickly.",
            "priority": 7,
            "auto_send": True,
            "is_inbound_lead": False,
            "enable_lead_qualification": False,
            "enable_lead_nurturing": False,
            "is_active": True,
            "is_default": False,
            "created_at": get_timestamp(),
            "updated_at": get_timestamp()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "General Inquiry (Default)",
            "description": "Default intent for general questions",
            "keywords": ["question", "info", "information", "tell me", "learn"],
            "prompt": "You are a helpful assistant. Respond professionally to general inquiries. Provide clear information and ask if they need anything specific.",
            "priority": 1,
            "auto_send": False,
            "is_inbound_lead": False,
            "enable_lead_qualification": False,
            "enable_lead_nurturing": False,
            "is_active": True,
            "is_default": True,
            "created_at": get_timestamp(),
            "updated_at": get_timestamp()
        }
    ]
    
    result = await db.intents.insert_many(intents)
    print(f"✅ Created {len(result.inserted_ids)} intents")
    return intents


async def create_knowledge_base(db, user_id):
    """Create knowledge base entries"""
    print("\n📚 Creating Knowledge Base...")
    await db.knowledge_bases.delete_many({"user_id": user_id})
    
    kb_entries = [
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Product Pricing - Starter Plan",
            "content": "Our Starter Plan is perfect for small teams: $29/month, includes 5 users, 1000 emails/month, basic automation, email support. Great for startups and small businesses getting started with email automation.",
            "category": "Pricing",
            "tags": ["pricing", "starter", "small-business"],
            "is_active": True,
            "created_at": get_timestamp(),
            "updated_at": get_timestamp()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Product Pricing - Professional Plan",
            "content": "Our Professional Plan is for growing teams: $99/month, includes 20 users, 10000 emails/month, advanced automation, AI features, priority support, analytics dashboard. Most popular choice for mid-size companies.",
            "category": "Pricing",
            "tags": ["pricing", "professional", "popular"],
            "is_active": True,
            "created_at": get_timestamp(),
            "updated_at": get_timestamp()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Product Pricing - Enterprise Plan",
            "content": "Our Enterprise Plan offers unlimited power: Custom pricing, unlimited users, unlimited emails, white-label options, dedicated account manager, custom integrations, SLA guarantee, on-premise deployment option. Perfect for large organizations.",
            "category": "Pricing",
            "tags": ["pricing", "enterprise", "custom"],
            "is_active": True,
            "created_at": get_timestamp(),
            "updated_at": get_timestamp()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Key Features - AI Email Assistant",
            "content": "Our AI Email Assistant automatically reads, understands, and responds to emails using advanced GPT models. It detects intents, generates personalized responses, schedules follow-ups, and learns from your feedback. Save 10+ hours per week on email management.",
            "category": "Features",
            "tags": ["features", "ai", "automation"],
            "is_active": True,
            "created_at": get_timestamp(),
            "updated_at": get_timestamp()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Key Features - Campaign Management",
            "content": "Run sophisticated email campaigns with personalization, A/B testing, advanced analytics, and automated follow-ups. Track opens, clicks, replies, and conversions. Manage unlimited contacts and create reusable templates.",
            "category": "Features",
            "tags": ["features", "campaigns", "outbound"],
            "is_active": True,
            "created_at": get_timestamp(),
            "updated_at": get_timestamp()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Key Features - Lead Qualification",
            "content": "Automatically qualify inbound leads using AI. Set custom criteria, ask qualifying questions, score leads automatically, and route them to the right team. Never miss a hot lead again with intelligent lead management.",
            "category": "Features",
            "tags": ["features", "leads", "qualification"],
            "is_active": True,
            "created_at": get_timestamp(),
            "updated_at": get_timestamp()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Integration - Google & Outlook",
            "content": "Seamlessly connect with Gmail and Outlook using OAuth. Sync emails in real-time, send from your own email address, maintain thread continuity. No complex IMAP/SMTP setup required. Works with Google Workspace and Microsoft 365.",
            "category": "Integrations",
            "tags": ["integration", "gmail", "outlook"],
            "is_active": True,
            "created_at": get_timestamp(),
            "updated_at": get_timestamp()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Integration - Calendar Sync",
            "content": "Automatically detect meeting requests in emails and add them to your Google or Microsoft calendar. Get intelligent reminders, avoid scheduling conflicts, and track meeting engagement. Perfect for busy professionals.",
            "category": "Integrations",
            "tags": ["integration", "calendar", "meetings"],
            "is_active": True,
            "created_at": get_timestamp(),
            "updated_at": get_timestamp()
        }
    ]
    
    result = await db.knowledge_bases.insert_many(kb_entries)
    print(f"✅ Created {len(result.inserted_ids)} knowledge base entries")
    return kb_entries


async def create_lead_qualification_criteria(db, user_id):
    """Create lead qualification criteria"""
    print("\n🎯 Creating Lead Qualification Criteria...")
    await db.lead_qualification_criteria.delete_many({"user_id": user_id})
    
    criteria = [
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "B2B SaaS Lead Qualification",
            "description": "Standard qualification criteria for B2B SaaS leads",
            "is_enabled": True,
            "criteria_type": "question_based",
            "rules": [],
            "questions": [
                {
                    "question_text": "What is your company size?",
                    "question_key": "company_size",
                    "expected_answer_type": "choice",
                    "qualifying_answers": ["10-50", "50-200", "200-1000", "1000+"],
                    "disqualifying_answers": ["1-10", "freelancer", "individual"],
                    "weight": 0.3,
                    "is_required": True,
                    "priority": 1
                },
                {
                    "question_text": "What is your timeline for implementation?",
                    "question_key": "timeline",
                    "expected_answer_type": "choice",
                    "qualifying_answers": ["immediate", "this month", "this quarter"],
                    "disqualifying_answers": ["just exploring", "no timeline", "maybe next year"],
                    "weight": 0.25,
                    "is_required": True,
                    "priority": 2
                },
                {
                    "question_text": "What is your approximate budget range?",
                    "question_key": "budget",
                    "expected_answer_type": "text",
                    "qualifying_answers": None,
                    "disqualifying_answers": None,
                    "weight": 0.25,
                    "is_required": True,
                    "priority": 3
                },
                {
                    "question_text": "Are you the decision maker or involved in the decision process?",
                    "question_key": "decision_authority",
                    "expected_answer_type": "choice",
                    "qualifying_answers": ["yes", "decision maker", "involved in decision", "co-decision maker"],
                    "disqualifying_answers": ["no", "just researching", "will forward"],
                    "weight": 0.2,
                    "is_required": True,
                    "priority": 4
                }
            ],
            "min_qualification_score": 0.65,
            "max_exchanges": 2,
            "auto_disqualify_on_fail": True,
            "is_active": True,
            "created_at": get_timestamp(),
            "updated_at": get_timestamp()
        }
    ]
    
    result = await db.lead_qualification_criteria.insert_many(criteria)
    print(f"✅ Created {len(result.inserted_ids)} qualification criteria")
    
    # Update user's default qualification criteria
    await db.users.update_one(
        {"id": user_id},
        {"$set": {"default_qualification_criteria_id": criteria[0]["id"]}}
    )
    
    return criteria


async def create_lead_nurturing_config(db, user_id):
    """Create lead nurturing configuration"""
    print("\n🌱 Creating Lead Nurturing Config...")
    await db.lead_nurturing_configs.delete_many({"user_id": user_id})
    
    configs = [
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Standard B2B Nurturing",
            "description": "Conversational nurturing for B2B leads",
            "is_enabled": True,
            "questions": [
                {
                    "question_id": str(uuid.uuid4()),
                    "question_text": "What specific challenges are you looking to solve?",
                    "context_keywords": ["problem", "challenge", "issue", "need", "looking for"],
                    "priority": 1,
                    "max_asks": 1,
                    "is_required": False
                },
                {
                    "question_id": str(uuid.uuid4()),
                    "question_text": "How are you currently handling this process?",
                    "context_keywords": ["current", "now", "currently", "existing", "present"],
                    "priority": 2,
                    "max_asks": 1,
                    "is_required": False
                },
                {
                    "question_id": str(uuid.uuid4()),
                    "question_text": "What features are most important to your team?",
                    "context_keywords": ["feature", "important", "need", "must have", "requirement"],
                    "priority": 3,
                    "max_asks": 1,
                    "is_required": False
                },
                {
                    "question_id": str(uuid.uuid4()),
                    "question_text": "When would you ideally like to have a solution in place?",
                    "context_keywords": ["when", "timeline", "deadline", "urgency", "timeframe"],
                    "priority": 4,
                    "max_asks": 1,
                    "is_required": False
                }
            ],
            "questions_per_email": 2,
            "max_exchanges": 2,
            "use_contextual_questions": True,
            "natural_integration": True,
            "avoid_interrogation": True,
            "is_active": True,
            "created_at": get_timestamp(),
            "updated_at": get_timestamp()
        }
    ]
    
    result = await db.lead_nurturing_configs.insert_many(configs)
    print(f"✅ Created {len(result.inserted_ids)} nurturing configs")
    
    # Update user's default nurturing config
    await db.users.update_one(
        {"id": user_id},
        {"$set": {"default_nurturing_config_id": configs[0]["id"]}}
    )
    
    return configs


async def create_campaign_templates(db, user_id):
    """Create campaign email templates"""
    print("\n📧 Creating Campaign Templates...")
    await db.campaign_templates.delete_many({"user_id": user_id})
    
    templates = [
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Cold Outreach - Introduction",
            "description": "Initial cold email for outbound campaigns",
            "subject": "Quick question about {{company}}'s email workflow",
            "body": """Hi {{first_name}},

I noticed {{company}} is in the {{industry}} space, and I wanted to reach out quickly.

Most teams like yours spend 10+ hours per week managing email communications manually. We've helped similar companies automate their email workflow while maintaining a personal touch.

Would you be open to a quick 15-minute call this week to explore if this could benefit {{company}}?

Best regards,
Amit""",
            "template_type": "initial",
            "available_tags": ["email", "first_name", "last_name", "company", "title", "industry"],
            "times_used": 0,
            "is_active": True,
            "created_at": get_timestamp(),
            "updated_at": get_timestamp()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Follow-up 1 - Value Proposition",
            "description": "First follow-up highlighting value",
            "subject": "Re: Quick question about {{company}}'s email workflow",
            "body": """Hi {{first_name}},

Just following up on my previous email. I wanted to share a quick case study - we helped a similar company in {{industry}} reduce their email response time by 70% and increase customer satisfaction.

Here's what makes us different:
• AI-powered email understanding and responses
• Automated lead qualification
• Smart follow-up scheduling
• Campaign analytics

Would love to show you a quick demo. Are you free for 15 minutes this week?

Best,
Amit""",
            "template_type": "follow_up_1",
            "available_tags": ["email", "first_name", "last_name", "company", "industry"],
            "times_used": 0,
            "is_active": True,
            "created_at": get_timestamp(),
            "updated_at": get_timestamp()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Follow-up 2 - Final Touch",
            "description": "Final follow-up with break-up",
            "subject": "Last note about {{company}}",
            "body": """Hi {{first_name}},

I don't want to be a pest, so this will be my last message.

If email automation isn't a priority right now, I completely understand. But if you'd like to learn how we can help {{company}} save time and grow revenue, just reply to this email.

Otherwise, I wish you the best of luck!

Cheers,
Amit""",
            "template_type": "follow_up_2",
            "available_tags": ["email", "first_name", "last_name", "company"],
            "times_used": 0,
            "is_active": True,
            "created_at": get_timestamp(),
            "updated_at": get_timestamp()
        }
    ]
    
    result = await db.campaign_templates.insert_many(templates)
    print(f"✅ Created {len(result.inserted_ids)} campaign templates")
    return templates


async def create_campaign_contacts(db, user_id):
    """Create campaign contacts"""
    print("\n👥 Creating Campaign Contacts...")
    await db.campaign_contacts.delete_many({"user_id": user_id})
    
    contacts = [
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "email": "sarah.johnson@techcorp.com",
            "first_name": "Sarah",
            "last_name": "Johnson",
            "company": "TechCorp Inc",
            "title": "VP of Sales",
            "linkedin_url": "https://linkedin.com/in/sarahjohnson",
            "company_domain": "techcorp.com",
            "custom_fields": {"industry": "Technology", "employee_count": "200-500"},
            "status": "active",
            "email_verified": True,
            "verification_status": "valid",
            "emails_sent": 0,
            "emails_opened": 0,
            "emails_replied": 0,
            "tags": ["technology", "enterprise", "hot-lead"],
            "created_at": get_timestamp(),
            "updated_at": get_timestamp()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "email": "michael.chen@startupventures.io",
            "first_name": "Michael",
            "last_name": "Chen",
            "company": "Startup Ventures",
            "title": "Founder & CEO",
            "linkedin_url": "https://linkedin.com/in/michaelchen",
            "company_domain": "startupventures.io",
            "custom_fields": {"industry": "SaaS", "employee_count": "10-50"},
            "status": "active",
            "email_verified": True,
            "verification_status": "valid",
            "emails_sent": 0,
            "emails_opened": 0,
            "emails_replied": 0,
            "tags": ["saas", "startup", "founder"],
            "created_at": get_timestamp(),
            "updated_at": get_timestamp()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "email": "emily.rodriguez@growthagency.com",
            "first_name": "Emily",
            "last_name": "Rodriguez",
            "company": "Growth Agency",
            "title": "Marketing Director",
            "linkedin_url": "https://linkedin.com/in/emilyrodriguez",
            "company_domain": "growthagency.com",
            "custom_fields": {"industry": "Marketing", "employee_count": "50-200"},
            "status": "active",
            "email_verified": True,
            "verification_status": "valid",
            "emails_sent": 0,
            "emails_opened": 0,
            "emails_replied": 0,
            "tags": ["marketing", "agency"],
            "created_at": get_timestamp(),
            "updated_at": get_timestamp()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "email": "david.kim@enterprise-solutions.com",
            "first_name": "David",
            "last_name": "Kim",
            "company": "Enterprise Solutions",
            "title": "CTO",
            "linkedin_url": "https://linkedin.com/in/davidkim",
            "company_domain": "enterprise-solutions.com",
            "custom_fields": {"industry": "Enterprise Software", "employee_count": "1000+"},
            "status": "active",
            "email_verified": True,
            "verification_status": "valid",
            "emails_sent": 0,
            "emails_opened": 0,
            "emails_replied": 0,
            "tags": ["enterprise", "technology", "decision-maker"],
            "created_at": get_timestamp(),
            "updated_at": get_timestamp()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "email": "lisa.anderson@consulting-pro.com",
            "first_name": "Lisa",
            "last_name": "Anderson",
            "company": "Consulting Pro",
            "title": "Senior Consultant",
            "linkedin_url": "https://linkedin.com/in/lisaanderson",
            "company_domain": "consulting-pro.com",
            "custom_fields": {"industry": "Consulting", "employee_count": "50-200"},
            "status": "active",
            "email_verified": True,
            "verification_status": "valid",
            "emails_sent": 0,
            "emails_opened": 0,
            "emails_replied": 0,
            "tags": ["consulting", "professional-services"],
            "created_at": get_timestamp(),
            "updated_at": get_timestamp()
        }
    ]
    
    result = await db.campaign_contacts.insert_many(contacts)
    print(f"✅ Created {len(result.inserted_ids)} campaign contacts")
    return contacts


async def create_contact_lists(db, user_id, contacts):
    """Create contact lists"""
    print("\n📑 Creating Contact Lists...")
    await db.contact_lists.delete_many({"user_id": user_id})
    
    # Get contact IDs by tags
    enterprise_contacts = [c["id"] for c in contacts if "enterprise" in c["tags"]]
    startup_contacts = [c["id"] for c in contacts if "startup" in c["tags"]]
    hot_lead_contacts = [c["id"] for c in contacts if "hot-lead" in c["tags"]]
    
    lists = [
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Enterprise Prospects",
            "description": "Large enterprise companies (1000+ employees)",
            "contact_ids": enterprise_contacts,
            "total_contacts": len(enterprise_contacts),
            "created_at": get_timestamp(),
            "updated_at": get_timestamp()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Startup Founders",
            "description": "Startup founders and early-stage companies",
            "contact_ids": startup_contacts,
            "total_contacts": len(startup_contacts),
            "created_at": get_timestamp(),
            "updated_at": get_timestamp()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Hot Leads Q1 2024",
            "description": "High-priority leads for Q1 outreach",
            "contact_ids": hot_lead_contacts,
            "total_contacts": len(hot_lead_contacts),
            "created_at": get_timestamp(),
            "updated_at": get_timestamp()
        }
    ]
    
    result = await db.contact_lists.insert_many(lists)
    print(f"✅ Created {len(result.inserted_ids)} contact lists")
    return lists


async def create_campaigns(db, user_id, templates, contacts, lists):
    """Create sample campaigns"""
    print("\n📢 Creating Campaigns...")
    await db.campaigns.delete_many({"user_id": user_id})
    
    # Get template and contact IDs
    initial_template_id = next((t["id"] for t in templates if t["template_type"] == "initial"), templates[0]["id"])
    followup1_template_id = next((t["id"] for t in templates if t["template_type"] == "follow_up_1"), None)
    followup2_template_id = next((t["id"] for t in templates if t["template_type"] == "follow_up_2"), None)
    
    contact_ids = [c["id"] for c in contacts]
    enterprise_list_id = next((l["id"] for l in lists if "Enterprise" in l["name"]), None)
    
    campaigns = [
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Q4 Enterprise Outreach",
            "description": "Targeting enterprise prospects for Q4 growth",
            "contact_ids": contact_ids[:3],  # First 3 contacts
            "contact_tags": ["enterprise"],
            "list_ids": [enterprise_list_id] if enterprise_list_id else [],
            "initial_template_id": initial_template_id,
            "follow_up_config": {
                "enabled": True,
                "count": 2,
                "intervals": [2, 4],
                "template_ids": [followup1_template_id, followup2_template_id] if followup1_template_id else []
            },
            "tracking_settings": {
                "enable_open_tracking": True,
                "enable_click_tracking": True,
                "enable_reply_tracking": True,
                "enable_sentiment_analysis": True
            },
            "email_account_ids": [],  # User needs to add email accounts
            "daily_limit_per_account": 50,
            "random_delay_min": 60,
            "random_delay_max": 300,
            "scheduled_start": get_timestamp(days_ago=10),
            "scheduled_end": get_future_timestamp(days_ahead=20),
            "timezone": "America/New_York",
            "status": "completed",
            "total_contacts": 3,
            "emails_sent": 3,
            "emails_pending": 0,
            "emails_failed": 0,
            "emails_opened": 2,
            "emails_clicked": 1,
            "emails_replied": 1,
            "emails_bounced": 0,
            "emails_delivered": 3,
            "open_rate": 66.67,
            "click_rate": 33.33,
            "reply_rate": 33.33,
            "bounce_rate": 0.0,
            "delivery_rate": 100.0,
            "inbox_rate": 95.0,
            "positive_replies": 1,
            "neutral_replies": 0,
            "negative_replies": 0,
            "leads_generated": 1,
            "lead_rate": 33.33,
            "opportunities_created": 1,
            "opportunities_rate": 33.33,
            "conversions": 1,
            "conversion_rate": 33.33,
            "verify_emails": False,
            "created_at": get_timestamp(days_ago=10),
            "updated_at": get_timestamp(days_ago=1),
            "started_at": get_timestamp(days_ago=10),
            "completed_at": get_timestamp(days_ago=1)
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Startup Founders Outreach",
            "description": "Connecting with startup founders and early-stage companies",
            "contact_ids": contact_ids[3:],  # Remaining contacts
            "contact_tags": ["startup", "founder"],
            "list_ids": [],
            "initial_template_id": initial_template_id,
            "follow_up_config": {
                "enabled": True,
                "count": 2,
                "intervals": [3, 5],
                "template_ids": [followup1_template_id, followup2_template_id] if followup1_template_id else []
            },
            "tracking_settings": {
                "enable_open_tracking": True,
                "enable_click_tracking": True,
                "enable_reply_tracking": True,
                "enable_sentiment_analysis": True
            },
            "email_account_ids": [],
            "daily_limit_per_account": 100,
            "random_delay_min": 120,
            "random_delay_max": 300,
            "scheduled_start": get_timestamp(days_ago=5),
            "timezone": "America/New_York",
            "status": "running",
            "total_contacts": 2,
            "emails_sent": 2,
            "emails_pending": 0,
            "emails_failed": 0,
            "emails_opened": 2,
            "emails_clicked": 1,
            "emails_replied": 0,
            "emails_bounced": 0,
            "emails_delivered": 2,
            "open_rate": 100.0,
            "click_rate": 50.0,
            "reply_rate": 0.0,
            "bounce_rate": 0.0,
            "delivery_rate": 100.0,
            "inbox_rate": 98.0,
            "positive_replies": 0,
            "neutral_replies": 0,
            "negative_replies": 0,
            "leads_generated": 0,
            "lead_rate": 0.0,
            "opportunities_created": 0,
            "opportunities_rate": 0.0,
            "conversions": 0,
            "conversion_rate": 0.0,
            "verify_emails": False,
            "created_at": get_timestamp(days_ago=5),
            "updated_at": get_timestamp(hours_ago=2),
            "started_at": get_timestamp(days_ago=5)
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Technology Leaders - Q1 2024",
            "description": "Outreach to CTOs and tech decision makers",
            "contact_ids": [],
            "contact_tags": ["technology", "decision-maker"],
            "list_ids": [],
            "initial_template_id": initial_template_id,
            "follow_up_config": {
                "enabled": True,
                "count": 3,
                "intervals": [2, 4, 6],
                "template_ids": [followup1_template_id, followup2_template_id] if followup1_template_id else []
            },
            "tracking_settings": {
                "enable_open_tracking": True,
                "enable_click_tracking": True,
                "enable_reply_tracking": True,
                "enable_sentiment_analysis": True
            },
            "email_account_ids": [],
            "daily_limit_per_account": 75,
            "random_delay_min": 90,
            "random_delay_max": 240,
            "scheduled_start": get_future_timestamp(days_ahead=3),
            "scheduled_end": get_future_timestamp(days_ahead=30),
            "timezone": "America/New_York",
            "status": "scheduled",
            "total_contacts": 0,
            "emails_sent": 0,
            "emails_pending": 0,
            "emails_failed": 0,
            "emails_opened": 0,
            "emails_clicked": 0,
            "emails_replied": 0,
            "emails_bounced": 0,
            "emails_delivered": 0,
            "open_rate": 0.0,
            "click_rate": 0.0,
            "reply_rate": 0.0,
            "bounce_rate": 0.0,
            "delivery_rate": 0.0,
            "inbox_rate": 0.0,
            "positive_replies": 0,
            "neutral_replies": 0,
            "negative_replies": 0,
            "leads_generated": 0,
            "lead_rate": 0.0,
            "opportunities_created": 0,
            "opportunities_rate": 0.0,
            "conversions": 0,
            "conversion_rate": 0.0,
            "verify_emails": False,
            "created_at": get_timestamp(hours_ago=12),
            "updated_at": get_timestamp(hours_ago=12)
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Marketing Directors Campaign",
            "description": "Draft campaign for marketing professionals",
            "contact_ids": [],
            "contact_tags": ["marketing"],
            "list_ids": [],
            "initial_template_id": initial_template_id,
            "follow_up_config": {
                "enabled": True,
                "count": 2,
                "intervals": [3, 6],
                "template_ids": [followup1_template_id] if followup1_template_id else []
            },
            "tracking_settings": {
                "enable_open_tracking": True,
                "enable_click_tracking": True,
                "enable_reply_tracking": True,
                "enable_sentiment_analysis": True
            },
            "email_account_ids": [],
            "daily_limit_per_account": 50,
            "random_delay_min": 60,
            "random_delay_max": 180,
            "timezone": "America/New_York",
            "status": "draft",
            "total_contacts": 0,
            "emails_sent": 0,
            "emails_pending": 0,
            "emails_failed": 0,
            "emails_opened": 0,
            "emails_clicked": 0,
            "emails_replied": 0,
            "emails_bounced": 0,
            "emails_delivered": 0,
            "open_rate": 0.0,
            "click_rate": 0.0,
            "reply_rate": 0.0,
            "bounce_rate": 0.0,
            "delivery_rate": 0.0,
            "inbox_rate": 0.0,
            "positive_replies": 0,
            "neutral_replies": 0,
            "negative_replies": 0,
            "leads_generated": 0,
            "lead_rate": 0.0,
            "opportunities_created": 0,
            "opportunities_rate": 0.0,
            "conversions": 0,
            "conversion_rate": 0.0,
            "verify_emails": False,
            "created_at": get_timestamp(hours_ago=6),
            "updated_at": get_timestamp(hours_ago=6)
        }
    ]
    
    result = await db.campaigns.insert_many(campaigns)
    print(f"✅ Created {len(result.inserted_ids)} campaigns")
    return campaigns


async def create_sample_inbound_leads(db, user_id, intents):
    """Create sample inbound leads"""
    print("\n🎯 Creating Sample Inbound Leads...")
    await db.inbound_leads.delete_many({"user_id": user_id})
    
    # Get pricing and demo intent IDs
    pricing_intent = next((i for i in intents if "Pricing" in i["name"]), None)
    demo_intent = next((i for i in intents if "Demo" in i["name"]), None)
    
    leads = [
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "lead_name": "Jennifer Williams",
            "lead_email": "jennifer.williams@acmecorp.com",
            "company_name": "Acme Corporation",
            "phone": "+1-555-0123",
            "job_title": "Sales Manager",
            "company_size": "50-200",
            "industry": "Retail",
            "specific_interests": "Email automation for sales team",
            "requirements": "Need to automate follow-ups and track engagement",
            "source": "email",
            "stage": "qualified",
            "stage_changed_at": get_timestamp(days_ago=2),
            "stage_history": [
                {"stage": "new", "timestamp": get_timestamp(days_ago=5), "reason": "Lead created"},
                {"stage": "contacted", "timestamp": get_timestamp(days_ago=4), "reason": "Initial response sent"},
                {"stage": "qualified", "timestamp": get_timestamp(days_ago=2), "reason": "Passed qualification criteria"}
            ],
            "score": 85,
            "priority": "high",
            "initial_email_id": str(uuid.uuid4()),
            "thread_id": f"thread_{uuid.uuid4().hex[:12]}",
            "email_ids": [str(uuid.uuid4()), str(uuid.uuid4())],
            "intent_id": pricing_intent["id"] if pricing_intent else None,
            "intent_name": pricing_intent["name"] if pricing_intent else None,
            "emails_received": 2,
            "emails_sent": 2,
            "last_contact_at": get_timestamp(days_ago=1),
            "last_reply_at": get_timestamp(days_ago=1),
            "qualification_checked": True,
            "qualification_score": 85,
            "qualification_reasons": ["Company size: 50-200 employees", "Budget confirmed: $5K-10K", "Timeline: This quarter", "Decision authority: Yes"],
            "qualification_attempt": 1,
            "nurturing_enabled": True,
            "nurturing_exchanges_count": 2,
            "meeting_scheduled": False,
            "activities": [
                {"timestamp": get_timestamp(days_ago=5), "activity_type": "email_received", "description": "Initial pricing inquiry received", "performed_by": "system"},
                {"timestamp": get_timestamp(days_ago=4), "activity_type": "email_sent", "description": "Response sent with pricing information", "performed_by": "system"},
                {"timestamp": get_timestamp(days_ago=2), "activity_type": "stage_changed", "description": "Lead qualified", "performed_by": "system"}
            ],
            "is_active": True,
            "created_at": get_timestamp(days_ago=5),
            "updated_at": get_timestamp(days_ago=1)
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "lead_name": "Robert Martinez",
            "lead_email": "robert.martinez@innovatetech.io",
            "company_name": "Innovate Tech",
            "phone": "+1-555-0456",
            "job_title": "Founder",
            "company_size": "10-50",
            "industry": "Technology",
            "specific_interests": "Product demo for team collaboration",
            "requirements": "Looking for AI-powered email assistant for small team",
            "source": "email",
            "stage": "new",
            "stage_changed_at": get_timestamp(hours_ago=6),
            "stage_history": [
                {"stage": "new", "timestamp": get_timestamp(hours_ago=6), "reason": "Lead created"}
            ],
            "score": 0,
            "priority": "medium",
            "initial_email_id": str(uuid.uuid4()),
            "thread_id": f"thread_{uuid.uuid4().hex[:12]}",
            "email_ids": [str(uuid.uuid4())],
            "intent_id": demo_intent["id"] if demo_intent else None,
            "intent_name": demo_intent["name"] if demo_intent else None,
            "emails_received": 1,
            "emails_sent": 1,
            "last_contact_at": get_timestamp(hours_ago=6),
            "qualification_checked": False,
            "qualification_score": 0,
            "qualification_attempt": 0,
            "nurturing_enabled": True,
            "nurturing_exchanges_count": 0,
            "meeting_scheduled": False,
            "activities": [
                {"timestamp": get_timestamp(hours_ago=6), "activity_type": "email_received", "description": "Demo request received", "performed_by": "system"}
            ],
            "is_active": True,
            "created_at": get_timestamp(hours_ago=6),
            "updated_at": get_timestamp(hours_ago=6)
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "lead_name": "Patricia Brown",
            "lead_email": "patricia.brown@globalenterprises.com",
            "company_name": "Global Enterprises",
            "phone": "+1-555-0789",
            "job_title": "VP Marketing",
            "company_size": "1000+",
            "industry": "Finance",
            "specific_interests": "Enterprise email solution",
            "requirements": "Need scalable solution for 500+ users",
            "source": "email",
            "stage": "awaiting_info",
            "stage_changed_at": get_timestamp(days_ago=1),
            "stage_history": [
                {"stage": "new", "timestamp": get_timestamp(days_ago=3), "reason": "Lead created"},
                {"stage": "contacted", "timestamp": get_timestamp(days_ago=2), "reason": "Initial response sent"},
                {"stage": "awaiting_info", "timestamp": get_timestamp(days_ago=1), "reason": "Waiting for qualification answers"}
            ],
            "score": 45,
            "priority": "high",
            "initial_email_id": str(uuid.uuid4()),
            "thread_id": f"thread_{uuid.uuid4().hex[:12]}",
            "email_ids": [str(uuid.uuid4()), str(uuid.uuid4())],
            "intent_id": pricing_intent["id"] if pricing_intent else None,
            "intent_name": pricing_intent["name"] if pricing_intent else None,
            "emails_received": 2,
            "emails_sent": 2,
            "last_contact_at": get_timestamp(days_ago=1),
            "last_reply_at": get_timestamp(days_ago=1),
            "qualification_checked": True,
            "qualification_score": 45,
            "qualification_reasons": ["Waiting for timeline information", "Budget not confirmed"],
            "qualification_attempt": 1,
            "nurturing_enabled": True,
            "nurturing_exchanges_count": 1,
            "meeting_scheduled": False,
            "activities": [
                {"timestamp": get_timestamp(days_ago=3), "activity_type": "email_received", "description": "Enterprise pricing inquiry", "performed_by": "system"},
                {"timestamp": get_timestamp(days_ago=2), "activity_type": "email_sent", "description": "Qualification questions sent", "performed_by": "system"}
            ],
            "is_active": True,
            "created_at": get_timestamp(days_ago=3),
            "updated_at": get_timestamp(days_ago=1)
        }
    ]
    
    result = await db.inbound_leads.insert_many(leads)
    print(f"✅ Created {len(result.inserted_ids)} sample inbound leads")
    return leads


async def main():
    """Main function to create all seed data"""
    print("=" * 80)
    print("🚀 COMPREHENSIVE SEED DATA CREATION")
    print("=" * 80)
    print(f"User: {USER_EMAIL}")
    print(f"Password: {USER_PASSWORD}")
    print("=" * 80)
    print()
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(Config.MONGO_URL)
    db = client[Config.DB_NAME]
    
    try:
        # Create/Update user
        user_id = await create_or_update_user(db)
        
        # Create all data
        intents = await create_intents(db, user_id)
        kb_entries = await create_knowledge_base(db, user_id)
        criteria = await create_lead_qualification_criteria(db, user_id)
        nurturing_configs = await create_lead_nurturing_config(db, user_id)
        templates = await create_campaign_templates(db, user_id)
        contacts = await create_campaign_contacts(db, user_id)
        lists = await create_contact_lists(db, user_id, contacts)
        campaigns = await create_campaigns(db, user_id, templates, contacts, lists)
        leads = await create_sample_inbound_leads(db, user_id, intents)
        
        print("\n" + "=" * 80)
        print("✅ COMPREHENSIVE SEED DATA CREATED SUCCESSFULLY!")
        print("=" * 80)
        print("\n📊 Summary:")
        print(f"  • User: 1")
        print(f"  • Intents: {len(intents)}")
        print(f"  • Knowledge Base: {len(kb_entries)}")
        print(f"  • Qualification Criteria: {len(criteria)}")
        print(f"  • Nurturing Configs: {len(nurturing_configs)}")
        print(f"  • Campaign Templates: {len(templates)}")
        print(f"  • Campaign Contacts: {len(contacts)}")
        print(f"  • Contact Lists: {len(lists)}")
        print(f"  • Campaigns: {len(campaigns)}")
        print(f"  • Sample Inbound Leads: {len(leads)}")
        print("\n🎉 App is fully seeded and ready to use!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(main())
