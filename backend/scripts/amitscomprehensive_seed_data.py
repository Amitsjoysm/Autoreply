#!/usr/bin/env python3
"""
Comprehensive Seed Data Script for amits.joys@gmail.com
Creates complete app data including:
- Intents (with lead qualification & nurturing)
- Knowledge Base
- Campaign Templates
- Campaign Contacts
- Contact Lists
- Campaigns
- Inbound Leads
- Lead Qualification Criteria
- Lead Nurturing Config
"""
import asyncio
import uuid
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

from motor.motor_asyncio import AsyncIOMotorClient
from backend.config import Config

USER_EMAIL = "amits.joys@gmail.com"


def get_timestamp(days_ago: int = 0, hours_ago: int = 0):
    """Get ISO timestamp for a specific time in the past"""
    dt = datetime.now(timezone.utc) - timedelta(days=days_ago, hours=hours_ago)
    return dt.isoformat()


async def create_comprehensive_seed_data():
    """Create comprehensive seed data for complete app"""
    print("🚀 Creating Comprehensive Seed Data for Complete App")
    print("=" * 80)
    
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
    
    # Enable global lead qualification and nurturing for user
    print("🔧 Enabling global lead qualification and nurturing...")
    await db.users.update_one(
        {"id": user_id},
        {
            "$set": {
                "global_lead_qualification_enabled": True,
                "global_lead_nurturing_enabled": True,
                "updated_at": get_timestamp()
            }
        }
    )
    print("✅ Global settings enabled\n")
    
    # ========================================
    # 1. CREATE INTENTS
    # ========================================
    print("📋 Creating Intents (with Lead Qualification & Nurturing)...")
    await db.intents.delete_many({"user_id": user_id})
    
    intents_data = [
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Pricing Inquiry (Lead)",
            "description": "Potential customers asking about pricing and plans",
            "keywords": ["pricing", "price", "cost", "plan", "subscription", "package", "quote", "estimate", "budget", "how much"],
            "prompt": "You are a sales assistant responding to pricing inquiries. Be helpful and informative. Mention our flexible pricing options and ask qualifying questions to understand their needs better. Always include relevant knowledge base information about our pricing tiers.",
            "priority": 10,
            "auto_send": True,
            "is_inbound_lead": True,
            "enable_lead_qualification": True,
            "enable_lead_nurturing": True,
            "is_active": True,
            "created_at": get_timestamp(),
            "updated_at": get_timestamp()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Demo Request (Lead)",
            "description": "Requests for product demonstrations",
            "keywords": ["demo", "demonstration", "show me", "trial", "test", "try", "walkthrough", "preview"],
            "prompt": "You are a sales assistant handling demo requests. Be enthusiastic and helpful. Confirm their interest and ask qualifying questions about their use case and timeline. Offer to schedule a personalized demo.",
            "priority": 10,
            "auto_send": True,
            "is_inbound_lead": True,
            "enable_lead_qualification": True,
            "enable_lead_nurturing": True,
            "is_active": True,
            "created_at": get_timestamp(),
            "updated_at": get_timestamp()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Feature Inquiry (Lead)",
            "description": "Questions about specific features or capabilities",
            "keywords": ["feature", "capability", "function", "does it", "can it", "support", "integration", "api"],
            "prompt": "You are a product specialist answering feature questions. Be detailed and technical when appropriate. Use knowledge base to provide accurate feature information. Ask about their specific use case to provide relevant examples.",
            "priority": 9,
            "auto_send": True,
            "is_inbound_lead": True,
            "enable_lead_qualification": True,
            "enable_lead_nurturing": True,
            "is_active": True,
            "created_at": get_timestamp(),
            "updated_at": get_timestamp()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Meeting Request",
            "description": "Emails requesting to schedule a meeting or call",
            "keywords": ["meeting", "schedule", "call", "discuss", "meet", "zoom", "teams", "appointment"],
            "prompt": "You are a professional assistant scheduling meetings. Be courteous, confirm availability, and suggest meeting times if not provided. Always include calendar details if a meeting is being scheduled.",
            "priority": 8,
            "auto_send": True,
            "is_inbound_lead": False,
            "enable_lead_qualification": False,
            "enable_lead_nurturing": False,
            "is_active": True,
            "created_at": get_timestamp(),
            "updated_at": get_timestamp()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Support Request",
            "description": "Technical support or help requests",
            "keywords": ["help", "support", "issue", "problem", "error", "bug", "not working", "assistance", "troubleshoot"],
            "prompt": "You are a technical support specialist. Be helpful, patient, and provide clear solutions. Use knowledge base to reference documentation and guides. Ask for relevant details if needed.",
            "priority": 7,
            "auto_send": True,
            "is_inbound_lead": False,
            "enable_lead_qualification": False,
            "enable_lead_nurturing": False,
            "is_active": True,
            "created_at": get_timestamp(),
            "updated_at": get_timestamp()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "General Inquiry",
            "description": "General questions about products, services, or company",
            "keywords": ["question", "inquiry", "wondering", "curious", "information", "details", "learn more", "tell me"],
            "prompt": "You are answering a general inquiry. Be informative, clear, and helpful. Use knowledge base to provide accurate information about our company and offerings.",
            "priority": 5,
            "auto_send": True,
            "is_inbound_lead": False,
            "enable_lead_qualification": False,
            "enable_lead_nurturing": False,
            "is_active": True,
            "created_at": get_timestamp(),
            "updated_at": get_timestamp()
        }
    ]
    
    await db.intents.insert_many(intents_data)
    print(f"✅ Created {len(intents_data)} intents\n")
    
    # ========================================
    # 2. CREATE KNOWLEDGE BASE
    # ========================================
    print("📚 Creating Knowledge Base entries...")
    await db.knowledge_base.delete_many({"user_id": user_id})
    
    knowledge_base_data = [
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Company Overview",
            "content": "We are TechFlow Solutions, a leading provider of AI-powered email automation and CRM solutions. Founded in 2023, we help businesses streamline their email communications, manage leads effectively, and automate their sales outreach. Our platform serves over 5,000+ companies worldwide.",
            "category": "Company",
            "tags": ["company", "about", "overview"],
            "is_active": True,
            "created_at": get_timestamp(),
            "updated_at": get_timestamp()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Pricing Plans",
            "content": """Our pricing plans are designed for businesses of all sizes:

**Starter Plan** - $49/month
- Up to 1,000 emails/month
- 2 email accounts
- Basic intent classification
- Email templates
- 24/7 support

**Professional Plan** - $149/month (Most Popular)
- Up to 10,000 emails/month
- 5 email accounts
- Advanced AI features
- Lead qualification & nurturing
- Campaign analytics
- Priority support
- Calendar integration

**Enterprise Plan** - $499/month
- Unlimited emails
- Unlimited email accounts
- Custom AI training
- Advanced lead scoring
- HubSpot integration
- Dedicated account manager
- Custom integrations
- SLA guarantee

All plans include a 14-day free trial. Annual billing gets 20% discount.""",
            "category": "Pricing",
            "tags": ["pricing", "plans", "cost", "subscription"],
            "is_active": True,
            "created_at": get_timestamp(),
            "updated_at": get_timestamp()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Key Features",
            "content": """Our platform includes these powerful features:

**Email Automation:**
- AI-powered intent classification
- Automatic draft generation
- Smart follow-up sequences
- Email scheduling and sending

**Lead Management:**
- Automatic lead detection and qualification
- Lead scoring (0-100 scale)
- Nurturing with contextual questions
- Lead pipeline management
- Stage tracking and history

**Campaign Management:**
- Bulk email campaigns
- Template management with personalization
- A/B testing capabilities
- Advanced analytics and reporting
- Contact list segmentation

**Integrations:**
- Gmail & Microsoft 365 OAuth
- Google Calendar integration
- HubSpot CRM sync
- Slack notifications
- Zapier webhooks

**AI Capabilities:**
- Groq LLM for draft generation
- Meeting detection and extraction
- Sentiment analysis
- Answer extraction from replies
- Natural language date parsing""",
            "category": "Features",
            "tags": ["features", "capabilities", "functionality"],
            "is_active": True,
            "created_at": get_timestamp(),
            "updated_at": get_timestamp()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Integration Capabilities",
            "content": """Our platform seamlessly integrates with popular business tools:

**Email Providers:**
- Gmail (via OAuth 2.0)
- Microsoft 365 (via OAuth 2.0)
- IMAP support for other providers

**Calendar Systems:**
- Google Calendar (full read/write access)
- Microsoft Calendar (coming soon)
- iCal format support

**CRM Integration:**
- HubSpot (native integration)
- Salesforce (via Zapier)
- Pipedrive (via Zapier)

**Communication:**
- Slack webhooks for notifications
- Microsoft Teams (coming soon)

**Automation:**
- Zapier (1000+ app connections)
- Make.com support
- REST API for custom integrations

Our API allows you to build custom integrations with detailed documentation available at api.techflowsolutions.com""",
            "category": "Integrations",
            "tags": ["integration", "api", "connectivity"],
            "is_active": True,
            "created_at": get_timestamp(),
            "updated_at": get_timestamp()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Getting Started Guide",
            "content": """Quick start guide for new users:

**Step 1: Connect Your Email**
- Navigate to Email Accounts page
- Click "Connect with Google" or "Connect with Microsoft"
- Authorize access to your email account
- Your emails will automatically sync

**Step 2: Set Up Intents**
- Go to Intents page
- Create intents for common email types (pricing, demo, support)
- Add keywords and custom prompts
- Enable auto-send for automated responses

**Step 3: Add Knowledge Base**
- Add company information, product details, pricing
- The AI will use this to generate accurate responses
- Keep it updated for best results

**Step 4: Configure Lead Management**
- Enable global lead qualification and nurturing
- Create qualification criteria
- Set up nurturing questions
- Define scoring thresholds

**Step 5: Create Campaign Templates**
- Build email templates with personalization tags
- Use {{first_name}}, {{company}}, etc.
- Test your templates before campaigns

**Step 6: Launch Your First Campaign**
- Upload contacts or create contact lists
- Select template and email account
- Configure follow-up sequence
- Schedule and launch!

Need help? Contact support@techflowsolutions.com or book a demo call.""",
            "category": "Guide",
            "tags": ["getting started", "tutorial", "setup"],
            "is_active": True,
            "created_at": get_timestamp(),
            "updated_at": get_timestamp()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Security & Compliance",
            "content": """We take security and compliance seriously:

**Data Security:**
- End-to-end encryption for all communications
- OAuth 2.0 for secure email access (no password storage)
- AES-256 encryption for stored credentials
- SOC 2 Type II certified
- Regular security audits

**Privacy Compliance:**
- GDPR compliant
- CCPA compliant
- Data processing agreements available
- Data retention policies
- Right to deletion honored within 30 days

**Infrastructure:**
- Hosted on AWS with 99.9% uptime SLA
- Daily backups with 30-day retention
- Disaster recovery plan in place
- Multi-region redundancy

**Access Control:**
- Role-based access control (RBAC)
- Two-factor authentication (2FA) available
- Single sign-on (SSO) for Enterprise
- Audit logs for all activities

Your data is never shared with third parties or used for training AI models.""",
            "category": "Security",
            "tags": ["security", "compliance", "privacy", "gdpr"],
            "is_active": True,
            "created_at": get_timestamp(),
            "updated_at": get_timestamp()
        }
    ]
    
    await db.knowledge_base.insert_many(knowledge_base_data)
    print(f"✅ Created {len(knowledge_base_data)} knowledge base entries\n")
    
    # ========================================
    # 3. CREATE CAMPAIGN TEMPLATES
    # ========================================
    print("📝 Creating Campaign Templates...")
    await db.campaign_templates.delete_many({"user_id": user_id})
    
    template_1_id = str(uuid.uuid4())
    template_2_id = str(uuid.uuid4())
    template_3_id = str(uuid.uuid4())
    
    templates_data = [
        {
            "id": template_1_id,
            "user_id": user_id,
            "name": "Product Introduction",
            "description": "Initial outreach for introducing our product",
            "subject": "Streamline your email workflow with AI - {{first_name}}",
            "body": """Hi {{first_name}},

I hope this email finds you well. I'm reaching out because I noticed {{company}} might benefit from streamlining your email communications.

At TechFlow Solutions, we've helped companies like yours automate email responses, qualify leads automatically, and increase response rates by 3x using AI.

Our platform can help you:
• Automatically classify and respond to incoming emails
• Qualify leads with AI-powered conversations
• Run personalized email campaigns at scale
• Integrate with your existing tools (Gmail, HubSpot, etc.)

Would you be interested in a quick 15-minute demo to see how we can help {{company}}?

Best regards,
{{sender_name}}""",
            "template_type": "initial",
            "available_tags": ["email", "first_name", "last_name", "company", "title", "sender_name"],
            "times_used": 0,
            "is_active": True,
            "created_at": get_timestamp(),
            "updated_at": get_timestamp()
        },
        {
            "id": template_2_id,
            "user_id": user_id,
            "name": "Follow-up #1",
            "description": "First follow-up after initial outreach",
            "subject": "Quick follow-up - {{first_name}}",
            "body": """Hi {{first_name}},

I wanted to follow up on my previous email about TechFlow Solutions.

I understand you're busy, so I'll keep this brief. We've recently helped similar companies in {{industry}} save 20+ hours per week on email management.

Here's a quick case study that might interest you: [Link to case study]

Would next Tuesday or Wednesday work for a brief call?

Thanks,
{{sender_name}}""",
            "template_type": "follow_up_1",
            "available_tags": ["email", "first_name", "last_name", "company", "title", "industry", "sender_name"],
            "times_used": 0,
            "is_active": True,
            "created_at": get_timestamp(),
            "updated_at": get_timestamp()
        },
        {
            "id": template_3_id,
            "user_id": user_id,
            "name": "Follow-up #2 - Last Attempt",
            "description": "Final follow-up email",
            "subject": "Last check-in - {{first_name}}",
            "body": """Hi {{first_name}},

I don't want to clutter your inbox, so this will be my last email.

If you're interested in learning how AI can transform your email workflow at {{company}}, I'm here to help. Otherwise, I'll assume the timing isn't right.

Feel free to reach out anytime at {{sender_email}}.

All the best,
{{sender_name}}

P.S. We're offering a 30-day free trial for new signups this month - no credit card required!""",
            "template_type": "follow_up_2",
            "available_tags": ["email", "first_name", "last_name", "company", "sender_name", "sender_email"],
            "times_used": 0,
            "is_active": True,
            "created_at": get_timestamp(),
            "updated_at": get_timestamp()
        }
    ]
    
    await db.campaign_templates.insert_many(templates_data)
    print(f"✅ Created {len(templates_data)} campaign templates\n")
    
    # ========================================
    # 4. CREATE CAMPAIGN CONTACTS
    # ========================================
    print("👥 Creating Campaign Contacts...")
    await db.campaign_contacts.delete_many({"user_id": user_id})
    
    contacts_data = [
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "email": "john.smith@acmecorp.com",
            "first_name": "John",
            "last_name": "Smith",
            "company": "Acme Corp",
            "title": "VP of Sales",
            "company_domain": "acmecorp.com",
            "custom_fields": {"industry": "Technology", "company_size": "50-200"},
            "tags": ["tech", "enterprise"],
            "status": "active",
            "email_verified": True,
            "verification_status": "valid",
            "emails_sent": 0,
            "emails_opened": 0,
            "emails_replied": 0,
            "created_at": get_timestamp(),
            "updated_at": get_timestamp()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "email": "sarah.johnson@techstart.io",
            "first_name": "Sarah",
            "last_name": "Johnson",
            "company": "TechStart",
            "title": "CEO",
            "linkedin_url": "https://linkedin.com/in/sarahjohnson",
            "company_domain": "techstart.io",
            "custom_fields": {"industry": "SaaS", "company_size": "10-50"},
            "tags": ["startup", "saas"],
            "status": "active",
            "email_verified": True,
            "verification_status": "valid",
            "emails_sent": 0,
            "emails_opened": 0,
            "emails_replied": 0,
            "created_at": get_timestamp(),
            "updated_at": get_timestamp()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "email": "mike.brown@innovate.com",
            "first_name": "Mike",
            "last_name": "Brown",
            "company": "Innovate Inc",
            "title": "Director of Marketing",
            "company_domain": "innovate.com",
            "custom_fields": {"industry": "Marketing", "company_size": "200-500"},
            "tags": ["marketing", "enterprise"],
            "status": "active",
            "email_verified": True,
            "verification_status": "valid",
            "emails_sent": 0,
            "emails_opened": 0,
            "emails_replied": 0,
            "created_at": get_timestamp(),
            "updated_at": get_timestamp()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "email": "emily.davis@growthco.com",
            "first_name": "Emily",
            "last_name": "Davis",
            "company": "Growth Co",
            "title": "Head of Operations",
            "linkedin_url": "https://linkedin.com/in/emilydavis",
            "company_domain": "growthco.com",
            "custom_fields": {"industry": "Consulting", "company_size": "50-200"},
            "tags": ["consulting", "operations"],
            "status": "active",
            "email_verified": True,
            "verification_status": "valid",
            "emails_sent": 0,
            "emails_opened": 0,
            "emails_replied": 0,
            "created_at": get_timestamp(),
            "updated_at": get_timestamp()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "email": "david.wilson@salesforce.io",
            "first_name": "David",
            "last_name": "Wilson",
            "company": "SalesForce Pro",
            "title": "Sales Manager",
            "company_domain": "salesforce.io",
            "custom_fields": {"industry": "Technology", "company_size": "500+"},
            "tags": ["tech", "sales"],
            "status": "active",
            "email_verified": True,
            "verification_status": "valid",
            "emails_sent": 0,
            "emails_opened": 0,
            "emails_replied": 0,
            "created_at": get_timestamp(),
            "updated_at": get_timestamp()
        }
    ]
    
    contact_result = await db.campaign_contacts.insert_many(contacts_data)
    contact_ids = [str(contact['id']) for contact in contacts_data]
    print(f"✅ Created {len(contacts_data)} campaign contacts\n")
    
    # ========================================
    # 5. CREATE CONTACT LISTS
    # ========================================
    print("📋 Creating Contact Lists...")
    await db.contact_lists.delete_many({"user_id": user_id})
    
    list_1_id = str(uuid.uuid4())
    
    contact_lists_data = [
        {
            "id": list_1_id,
            "user_id": user_id,
            "name": "Tech Companies",
            "description": "Technology and SaaS companies",
            "contact_ids": contact_ids[:3],
            "total_contacts": 3,
            "created_at": get_timestamp(),
            "updated_at": get_timestamp()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Enterprise Prospects",
            "description": "Large enterprise companies (200+ employees)",
            "contact_ids": [contact_ids[2], contact_ids[4]],
            "total_contacts": 2,
            "created_at": get_timestamp(),
            "updated_at": get_timestamp()
        }
    ]
    
    await db.contact_lists.insert_many(contact_lists_data)
    print(f"✅ Created {len(contact_lists_data)} contact lists\n")
    
    # ========================================
    # 6. CREATE CAMPAIGNS
    # ========================================
    print("📧 Creating Campaigns...")
    await db.campaigns.delete_many({"user_id": user_id})
    
    campaigns_data = [
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Q1 Product Launch Campaign",
            "description": "Outreach campaign for new product features",
            "contact_ids": contact_ids[:3],
            "contact_tags": [],
            "list_ids": [list_1_id],
            "initial_template_id": template_1_id,
            "follow_up_config": {
                "enabled": True,
                "count": 2,
                "intervals": [3, 7],
                "template_ids": [template_2_id, template_3_id]
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
            "scheduled_start": get_timestamp(days_ago=-7),
            "timezone": "UTC",
            "status": "draft",
            "total_contacts": 3,
            "emails_sent": 0,
            "emails_pending": 3,
            "emails_failed": 0,
            "emails_opened": 0,
            "emails_clicked": 0,
            "emails_replied": 0,
            "emails_bounced": 0,
            "open_rate": 0.0,
            "click_rate": 0.0,
            "reply_rate": 0.0,
            "bounce_rate": 0.0,
            "positive_replies": 0,
            "neutral_replies": 0,
            "negative_replies": 0,
            "leads_generated": 0,
            "lead_rate": 0.0,
            "opportunities_created": 0,
            "opportunities_rate": 0.0,
            "conversions": 0,
            "conversion_rate": 0.0,
            "emails_delivered": 0,
            "delivery_rate": 0.0,
            "inbox_rate": 0.0,
            "verify_emails": False,
            "created_at": get_timestamp(days_ago=7),
            "updated_at": get_timestamp(),
            "started_at": None,
            "completed_at": None
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Enterprise Outreach",
            "description": "Targeted campaign for enterprise decision makers",
            "contact_ids": [contact_ids[2], contact_ids[4]],
            "contact_tags": ["enterprise"],
            "list_ids": [],
            "initial_template_id": template_1_id,
            "follow_up_config": {
                "enabled": True,
                "count": 2,
                "intervals": [4, 8],
                "template_ids": [template_2_id, template_3_id]
            },
            "tracking_settings": {
                "enable_open_tracking": True,
                "enable_click_tracking": True,
                "enable_reply_tracking": True,
                "enable_sentiment_analysis": True
            },
            "email_account_ids": [],
            "daily_limit_per_account": 30,
            "random_delay_min": 120,
            "random_delay_max": 300,
            "scheduled_start": get_timestamp(days_ago=-3),
            "timezone": "UTC",
            "status": "draft",
            "total_contacts": 2,
            "emails_sent": 0,
            "emails_pending": 2,
            "emails_failed": 0,
            "emails_opened": 0,
            "emails_clicked": 0,
            "emails_replied": 0,
            "emails_bounced": 0,
            "open_rate": 0.0,
            "click_rate": 0.0,
            "reply_rate": 0.0,
            "bounce_rate": 0.0,
            "positive_replies": 0,
            "neutral_replies": 0,
            "negative_replies": 0,
            "leads_generated": 0,
            "lead_rate": 0.0,
            "opportunities_created": 0,
            "opportunities_rate": 0.0,
            "conversions": 0,
            "conversion_rate": 0.0,
            "emails_delivered": 0,
            "delivery_rate": 0.0,
            "inbox_rate": 0.0,
            "verify_emails": False,
            "created_at": get_timestamp(days_ago=3),
            "updated_at": get_timestamp(),
            "started_at": None,
            "completed_at": None
        }
    ]
    
    await db.campaigns.insert_many(campaigns_data)
    print(f"✅ Created {len(campaigns_data)} campaigns\n")
    
    # ========================================
    # 7. CREATE LEAD QUALIFICATION CRITERIA
    # ========================================
    print("🎯 Creating Lead Qualification Criteria...")
    await db.lead_qualification_criteria.delete_many({"user_id": user_id})
    
    criteria_id = str(uuid.uuid4())
    
    qualification_criteria = {
        "id": criteria_id,
        "user_id": user_id,
        "name": "Standard Lead Qualification",
        "description": "Default criteria for qualifying inbound leads",
        "criteria_type": "question_based",
        "min_score": 60,
        "max_qualification_attempts": 3,
        "auto_disqualify_after_max_attempts": True,
        "questions": [
            {
                "key": "company_size",
                "text": "What's your company size?",
                "weight": 0.33,
                "required": True
            },
            {
                "key": "budget",
                "text": "What's your monthly budget for this solution?",
                "weight": 0.33,
                "required": True
            },
            {
                "key": "timeline",
                "text": "What's your timeline for implementation?",
                "weight": 0.34,
                "required": True
            }
        ],
        "is_active": True,
        "created_at": get_timestamp(),
        "updated_at": get_timestamp()
    }
    
    await db.lead_qualification_criteria.insert_one(qualification_criteria)
    print(f"✅ Created lead qualification criteria\n")
    
    # ========================================
    # 8. CREATE LEAD NURTURING CONFIG
    # ========================================
    print("🌱 Creating Lead Nurturing Config...")
    await db.lead_nurturing_config.delete_many({"user_id": user_id})
    
    nurturing_config = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "name": "Default Nurturing Strategy",
        "description": "Standard nurturing configuration for inbound leads",
        "max_exchanges": 3,
        "questions_per_email": 2,
        "use_contextual_questions": True,
        "questions": [
            {
                "key": "company_size",
                "text": "What's your company size?",
                "priority": 1,
                "required": True
            },
            {
                "key": "budget",
                "text": "What's your monthly budget for this type of solution?",
                "priority": 2,
                "required": True
            },
            {
                "key": "timeline",
                "text": "What's your timeline for making a decision?",
                "priority": 3,
                "required": True
            },
            {
                "key": "industry",
                "text": "What industry is your company in?",
                "priority": 4,
                "required": False
            }
        ],
        "follow_up_config": {
            "enabled": True,
            "intervals": [2, 4, 6],
            "max_follow_ups": 3
        },
        "is_active": True,
        "created_at": get_timestamp(),
        "updated_at": get_timestamp()
    }
    
    await db.lead_nurturing_config.insert_one(nurturing_config)
    print(f"✅ Created lead nurturing config\n")
    
    # ========================================
    # 9. CREATE INBOUND LEADS
    # ========================================
    print("🎯 Creating Inbound Leads...")
    await db.inbound_leads.delete_many({"user_id": user_id})
    
    # Get a pricing inquiry intent for reference
    pricing_intent = await db.intents.find_one({"user_id": user_id, "name": "Pricing Inquiry (Lead)"})
    demo_intent = await db.intents.find_one({"user_id": user_id, "name": "Demo Request (Lead)"})
    
    leads_data = [
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "lead_name": "Jennifer Martinez",
            "lead_email": "jennifer.martinez@innovatetech.com",
            "company_name": "InnovateTech",
            "job_title": "Marketing Director",
            "company_size": "100-500",
            "industry": "Technology",
            "specific_interests": "Email automation and lead qualification",
            "requirements": "Need to automate email responses and qualify leads efficiently",
            "source": "email",
            "stage": "awaiting_info",
            "stage_changed_at": get_timestamp(days_ago=2),
            "stage_history": [
                {
                    "stage": "new",
                    "timestamp": get_timestamp(days_ago=2),
                    "reason": "Initial lead creation from pricing inquiry"
                },
                {
                    "stage": "awaiting_info",
                    "timestamp": get_timestamp(days_ago=2),
                    "reason": "Sent qualification questions"
                }
            ],
            "score": 45,
            "priority": "high",
            "initial_email_id": str(uuid.uuid4()),
            "thread_id": f"thread_{uuid.uuid4()}",
            "email_ids": [str(uuid.uuid4())],
            "intent_id": pricing_intent['id'] if pricing_intent else None,
            "intent_name": "Pricing Inquiry (Lead)",
            "emails_received": 1,
            "emails_sent": 1,
            "last_contact_at": get_timestamp(days_ago=2),
            "qualification_checked": True,
            "qualification_score": 45,
            "qualification_reasons": ["Answered 1 out of 3 required questions", "company_size: Answered - 100-500"],
            "qualification_criteria_id": criteria_id,
            "qualification_attempt": 1,
            "nurturing_enabled": True,
            "nurturing_exchanges_count": 1,
            "nurturing_questions_asked": [
                {"key": "company_size", "text": "What's your company size?", "answer": "100-500"}
            ],
            "last_questions_asked": [
                {"key": "budget", "text": "What's your monthly budget for this solution?"},
                {"key": "timeline", "text": "What's your timeline for implementation?"}
            ],
            "meeting_scheduled": False,
            "activities": [
                {
                    "timestamp": get_timestamp(days_ago=2),
                    "activity_type": "email_received",
                    "description": "Initial pricing inquiry received",
                    "details": {"subject": "Pricing information request"},
                    "performed_by": "system"
                },
                {
                    "timestamp": get_timestamp(days_ago=2),
                    "activity_type": "stage_changed",
                    "description": "Stage changed from new to awaiting_info",
                    "details": {"old_stage": "new", "new_stage": "awaiting_info"},
                    "performed_by": "system"
                }
            ],
            "is_active": True,
            "created_at": get_timestamp(days_ago=2),
            "updated_at": get_timestamp(days_ago=2)
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "lead_name": "Robert Chen",
            "lead_email": "robert.chen@dataflow.io",
            "company_name": "DataFlow Systems",
            "job_title": "CTO",
            "company_size": "50-100",
            "industry": "SaaS",
            "specific_interests": "AI-powered email automation and campaign management",
            "requirements": "Looking for enterprise-grade solution with API access",
            "source": "email",
            "stage": "qualified",
            "stage_changed_at": get_timestamp(days_ago=1),
            "stage_history": [
                {
                    "stage": "new",
                    "timestamp": get_timestamp(days_ago=3),
                    "reason": "Initial lead creation from demo request"
                },
                {
                    "stage": "awaiting_info",
                    "timestamp": get_timestamp(days_ago=3),
                    "reason": "Sent qualification questions"
                },
                {
                    "stage": "qualified",
                    "timestamp": get_timestamp(days_ago=1),
                    "reason": "All questions answered, score 85/100"
                }
            ],
            "score": 85,
            "priority": "urgent",
            "initial_email_id": str(uuid.uuid4()),
            "thread_id": f"thread_{uuid.uuid4()}",
            "email_ids": [str(uuid.uuid4()), str(uuid.uuid4())],
            "intent_id": demo_intent['id'] if demo_intent else None,
            "intent_name": "Demo Request (Lead)",
            "emails_received": 2,
            "emails_sent": 2,
            "last_contact_at": get_timestamp(days_ago=1),
            "last_reply_at": get_timestamp(days_ago=1),
            "qualification_checked": True,
            "qualification_score": 85,
            "qualification_reasons": [
                "Answered all required questions",
                "company_size: 50-100 employees",
                "budget: $10k-15k/month",
                "timeline: Within 2 weeks"
            ],
            "qualification_criteria_id": criteria_id,
            "qualification_attempt": 1,
            "nurturing_enabled": True,
            "nurturing_exchanges_count": 2,
            "nurturing_questions_asked": [
                {"key": "company_size", "text": "What's your company size?", "answer": "50-100 employees"},
                {"key": "budget", "text": "What's your monthly budget?", "answer": "$10k-15k/month"},
                {"key": "timeline", "text": "What's your timeline?", "answer": "Within 2 weeks"}
            ],
            "meeting_scheduled": False,
            "activities": [
                {
                    "timestamp": get_timestamp(days_ago=3),
                    "activity_type": "email_received",
                    "description": "Demo request received",
                    "details": {"subject": "Request for product demo"},
                    "performed_by": "system"
                },
                {
                    "timestamp": get_timestamp(days_ago=1),
                    "activity_type": "email_received",
                    "description": "Lead replied with qualification answers",
                    "details": {"answered_questions": 3},
                    "performed_by": "system"
                },
                {
                    "timestamp": get_timestamp(days_ago=1),
                    "activity_type": "stage_changed",
                    "description": "Lead qualified with score 85/100",
                    "details": {"old_stage": "awaiting_info", "new_stage": "qualified", "score": 85},
                    "performed_by": "system"
                }
            ],
            "is_active": True,
            "created_at": get_timestamp(days_ago=3),
            "updated_at": get_timestamp(days_ago=1)
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "lead_name": "Lisa Anderson",
            "lead_email": "lisa.anderson@businesspro.com",
            "company_name": "BusinessPro Solutions",
            "job_title": "VP of Sales",
            "company_size": "200-500",
            "industry": "Consulting",
            "specific_interests": "Campaign management and analytics",
            "requirements": "Need to run large-scale email campaigns with detailed analytics",
            "source": "email",
            "stage": "new",
            "stage_changed_at": get_timestamp(hours_ago=6),
            "stage_history": [
                {
                    "stage": "new",
                    "timestamp": get_timestamp(hours_ago=6),
                    "reason": "Initial lead creation from feature inquiry"
                }
            ],
            "score": 0,
            "priority": "medium",
            "initial_email_id": str(uuid.uuid4()),
            "thread_id": f"thread_{uuid.uuid4()}",
            "email_ids": [str(uuid.uuid4())],
            "intent_id": pricing_intent['id'] if pricing_intent else None,
            "intent_name": "Feature Inquiry (Lead)",
            "emails_received": 1,
            "emails_sent": 0,
            "last_contact_at": get_timestamp(hours_ago=6),
            "qualification_checked": False,
            "qualification_score": 0,
            "qualification_reasons": [],
            "qualification_criteria_id": criteria_id,
            "qualification_attempt": 0,
            "nurturing_enabled": True,
            "nurturing_exchanges_count": 0,
            "nurturing_questions_asked": [],
            "last_questions_asked": [],
            "meeting_scheduled": False,
            "activities": [
                {
                    "timestamp": get_timestamp(hours_ago=6),
                    "activity_type": "email_received",
                    "description": "Feature inquiry received",
                    "details": {"subject": "Questions about campaign features"},
                    "performed_by": "system"
                }
            ],
            "is_active": True,
            "created_at": get_timestamp(hours_ago=6),
            "updated_at": get_timestamp(hours_ago=6)
        }
    ]
    
    await db.inbound_leads.insert_many(leads_data)
    print(f"✅ Created {len(leads_data)} inbound leads\n")
    
    # ========================================
    # SUMMARY
    # ========================================
    print("\n" + "=" * 80)
    print("✅ SEED DATA CREATION COMPLETE!")
    print("=" * 80)
    print(f"\n📊 Summary for {USER_EMAIL}:")
    print(f"   • {len(intents_data)} Intents (3 with lead qualification & nurturing)")
    print(f"   • {len(knowledge_base_data)} Knowledge Base entries")
    print(f"   • {len(templates_data)} Campaign Templates")
    print(f"   • {len(contacts_data)} Campaign Contacts")
    print(f"   • {len(contact_lists_data)} Contact Lists")
    print(f"   • {len(campaigns_data)} Campaigns")
    print(f"   • 1 Lead Qualification Criteria")
    print(f"   • 1 Lead Nurturing Config")
    print(f"   • {len(leads_data)} Inbound Leads")
    print(f"\n🎯 Lead Status:")
    print(f"   • 1 lead in 'awaiting_info' stage")
    print(f"   • 1 lead in 'qualified' stage")
    print(f"   • 1 lead in 'new' stage")
    print(f"\n📧 Campaign Status:")
    print(f"   • 2 campaigns in 'draft' status")
    print(f"   • Ready to be scheduled and launched")
    print("\n🔐 Global Settings:")
    print("   • Lead Qualification: ENABLED")
    print("   • Lead Nurturing: ENABLED")
    print("\n💡 Next Steps:")
    print("   1. Connect your email account (Gmail/Microsoft)")
    print("   2. Review and customize intents and knowledge base")
    print("   3. Schedule campaigns to start sending")
    print("   4. Monitor inbound leads in the Leads page")
    print("   5. Review campaign analytics")
    print("\n✨ Your application is now fully populated with seed data!")
    print("=" * 80)
    
    client.close()


if __name__ == "__main__":
    asyncio.run(create_comprehensive_seed_data())
