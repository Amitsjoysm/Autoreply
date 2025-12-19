#!/usr/bin/env python3
"""
Comprehensive Seed Data Script
Populates entire application with realistic demo data for testing and demonstration
"""
import asyncio
import sys
sys.path.insert(0, 'backend')

from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone, timedelta
from passlib.context import CryptContext
import uuid
import random

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# Demo data
DEMO_EMAIL = "demo@example.com"
DEMO_PASSWORD = "demo123"

async def create_comprehensive_seed_data():
    """Create complete seed data across all collections"""
    
    print("=" * 80)
    print("COMPREHENSIVE SEED DATA CREATION")
    print("=" * 80)
    
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['email_assistant_db']
    
    try:
        # ============================================================
        # 1. CREATE DEMO USER
        # ============================================================
        print("\n📝 Step 1: Creating Demo User...")
        
        # Delete existing demo user
        await db.users.delete_one({"email": DEMO_EMAIL})
        
        demo_user_id = str(uuid.uuid4())
        demo_user = {
            "id": demo_user_id,
            "email": DEMO_EMAIL,
            "password_hash": pwd_context.hash(DEMO_PASSWORD),
            "full_name": "Demo User",
            "quota": 1000,
            "quota_used": 45,
            "quota_reset_date": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
            "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "role": "user",
            "is_active": True,
            "hubspot_enabled": True,
            "hubspot_connected": False,
            "hubspot_portal_id": None,
            "hubspot_auto_sync": False,
            "global_lead_qualification_enabled": True,
            "global_lead_nurturing_enabled": True,
            "default_qualification_criteria_id": None,  # Will set later
            "default_nurturing_config_id": None  # Will set later
        }
        
        await db.users.insert_one(demo_user)
        print(f"✅ Created demo user: {DEMO_EMAIL}")
        print(f"   Password: {DEMO_PASSWORD}")
        print(f"   User ID: {demo_user_id}")
        
        # ============================================================
        # 2. CREATE QUALIFICATION CRITERIA
        # ============================================================
        print("\n📊 Step 2: Creating Lead Qualification Criteria...")
        
        await db.lead_qualification_criteria.delete_many({"user_id": demo_user_id})
        
        criteria_id = str(uuid.uuid4())
        qualification_criteria = {
            "id": criteria_id,
            "user_id": demo_user_id,
            "name": "B2B SaaS Lead Qualification",
            "description": "Standard qualification for B2B SaaS leads",
            "is_enabled": True,
            "criteria_type": "question_based",
            "rules": [],
            "questions": [
                {
                    "question_text": "What is your company size?",
                    "question_key": "company_size",
                    "expected_answer_type": "choice",
                    "qualifying_answers": ["51-200", "201-500", "501+", "enterprise"],
                    "disqualifying_answers": ["1-10", "self-employed"],
                    "weight": 0.25,
                    "is_required": True,
                    "priority": 1
                },
                {
                    "question_text": "What is your monthly budget for this solution?",
                    "question_key": "budget",
                    "expected_answer_type": "text",
                    "weight": 0.30,
                    "is_required": True,
                    "priority": 2
                },
                {
                    "question_text": "What industry are you in?",
                    "question_key": "industry",
                    "expected_answer_type": "text",
                    "weight": 0.20,
                    "is_required": True,
                    "priority": 3
                },
                {
                    "question_text": "What is your role in the company?",
                    "question_key": "job_title",
                    "expected_answer_type": "text",
                    "weight": 0.25,
                    "is_required": False,
                    "priority": 4
                }
            ],
            "min_qualification_score": 0.6,
            "max_exchanges": 3,
            "auto_disqualify_on_fail": True,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.lead_qualification_criteria.insert_one(qualification_criteria)
        print(f"✅ Created qualification criteria: {criteria_id}")
        
        # ============================================================
        # 3. CREATE NURTURING CONFIGURATION
        # ============================================================
        print("\n💬 Step 3: Creating Lead Nurturing Configuration...")
        
        await db.lead_nurturing_config.delete_many({"user_id": demo_user_id})
        
        nurturing_id = str(uuid.uuid4())
        nurturing_config = {
            "id": nurturing_id,
            "user_id": demo_user_id,
            "name": "Standard B2B Nurturing",
            "description": "Contextual questions for B2B leads",
            "is_enabled": True,
            "questions": [
                {
                    "question_id": str(uuid.uuid4()),
                    "question_text": "What specific features are you most interested in?",
                    "context_keywords": ["feature", "functionality", "capability", "tool"],
                    "priority": 1,
                    "max_asks": 1,
                    "is_required": False
                },
                {
                    "question_id": str(uuid.uuid4()),
                    "question_text": "What is your company size?",
                    "context_keywords": ["company", "team", "employees", "organization"],
                    "priority": 2,
                    "max_asks": 1,
                    "is_required": True
                },
                {
                    "question_id": str(uuid.uuid4()),
                    "question_text": "What is your budget range for this solution?",
                    "context_keywords": ["budget", "price", "cost", "pricing"],
                    "priority": 3,
                    "max_asks": 1,
                    "is_required": True
                },
                {
                    "question_id": str(uuid.uuid4()),
                    "question_text": "When are you looking to implement this?",
                    "context_keywords": ["timeline", "when", "start", "implement"],
                    "priority": 4,
                    "max_asks": 1,
                    "is_required": False
                },
                {
                    "question_id": str(uuid.uuid4()),
                    "question_text": "What industry is your company in?",
                    "context_keywords": ["industry", "sector", "business"],
                    "priority": 5,
                    "max_asks": 1,
                    "is_required": True
                }
            ],
            "questions_per_email": 2,
            "max_exchanges": 3,
            "use_contextual_questions": True,
            "natural_integration": True,
            "avoid_interrogation": True,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.lead_nurturing_config.insert_one(nurturing_config)
        print(f"✅ Created nurturing config: {nurturing_id}")
        
        # Link configs to user
        await db.users.update_one(
            {"id": demo_user_id},
            {"$set": {
                "default_qualification_criteria_id": criteria_id,
                "default_nurturing_config_id": nurturing_id
            }}
        )
        print(f"✅ Linked configs to demo user")
        
        # ============================================================
        # 4. CREATE INTENTS
        # ============================================================
        print("\n🎯 Step 4: Creating Intents...")
        
        await db.intents.delete_many({"user_id": demo_user_id})
        
        intents = [
            {
                "id": str(uuid.uuid4()),
                "user_id": demo_user_id,
                "name": "Pricing Inquiry (Lead)",
                "description": "Pricing questions from potential customers",
                "keywords": ["pricing", "price", "cost", "how much", "quote", "fee", "payment", "plan", "subscription"],
                "prompt": "Respond to pricing inquiry professionally. Reference pricing from knowledge base. Be helpful and transparent about costs. This is a potential lead so be engaging.",
                "priority": 10,
                "auto_send": True,
                "is_inbound_lead": True,
                "enable_lead_qualification": True,
                "enable_lead_nurturing": True,
                "is_default": False,
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": demo_user_id,
                "name": "Demo Request (Lead)",
                "description": "Product demo and trial requests",
                "keywords": ["demo", "trial", "test", "try", "demonstration", "preview", "show me", "see it"],
                "prompt": "Respond enthusiastically to demo request. Offer to schedule a demo session. Explain what they'll see. This is a high-quality lead.",
                "priority": 9,
                "auto_send": True,
                "is_inbound_lead": True,
                "enable_lead_qualification": True,
                "enable_lead_nurturing": True,
                "is_default": False,
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": demo_user_id,
                "name": "Meeting Request",
                "description": "Schedule meeting or call",
                "keywords": ["meeting", "schedule", "call", "meet", "discussion", "chat", "zoom", "video call"],
                "prompt": "Respond professionally to meeting request. Be accommodating with timing. If time is confirmed (high confidence), mention calendar event will be created.",
                "priority": 8,
                "auto_send": True,
                "is_inbound_lead": False,
                "enable_lead_qualification": False,
                "enable_lead_nurturing": False,
                "is_default": False,
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": demo_user_id,
                "name": "Support Request",
                "description": "Customer support and help",
                "keywords": ["help", "support", "issue", "problem", "error", "bug", "not working", "broken"],
                "prompt": "Respond helpfully to support request. Be empathetic. Reference support documentation from knowledge base. Provide clear next steps.",
                "priority": 7,
                "auto_send": True,
                "is_inbound_lead": False,
                "enable_lead_qualification": False,
                "enable_lead_nurturing": False,
                "is_default": False,
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": demo_user_id,
                "name": "Partnership Inquiry (Lead)",
                "description": "Business partnership requests",
                "keywords": ["partnership", "partner", "collaborate", "integration", "reseller", "affiliate"],
                "prompt": "Respond professionally to partnership inquiry. Express interest in collaboration. This is a potential business opportunity.",
                "priority": 6,
                "auto_send": True,
                "is_inbound_lead": True,
                "enable_lead_qualification": True,
                "enable_lead_nurturing": False,
                "is_default": False,
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": demo_user_id,
                "name": "General Inquiry",
                "description": "General questions and information requests",
                "keywords": ["question", "inquiry", "information", "curious", "wondering"],
                "prompt": "Respond helpfully to general inquiry. Reference knowledge base. Be friendly and informative.",
                "priority": 3,
                "auto_send": True,
                "is_inbound_lead": False,
                "enable_lead_qualification": False,
                "enable_lead_nurturing": False,
                "is_default": False,
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": demo_user_id,
                "name": "Default Intent",
                "description": "Fallback for unmatched emails",
                "keywords": [],
                "prompt": "Respond politely to email. Acknowledge receipt and ask how you can help. Be professional and friendly.",
                "priority": 1,
                "auto_send": False,
                "is_inbound_lead": False,
                "enable_lead_qualification": False,
                "enable_lead_nurturing": False,
                "is_default": True,
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        ]
        
        await db.intents.insert_many(intents)
        print(f"✅ Created {len(intents)} intents")
        
        # ============================================================
        # 5. CREATE KNOWLEDGE BASE
        # ============================================================
        print("\n📚 Step 5: Creating Knowledge Base...")
        
        await db.knowledge_base.delete_many({"user_id": demo_user_id})
        
        kb_entries = [
            {
                "id": str(uuid.uuid4()),
                "user_id": demo_user_id,
                "title": "Product Overview",
                "content": """Our AI Email Assistant is a comprehensive email automation platform that helps businesses:
- Automatically process and respond to incoming emails
- Classify emails by intent and generate intelligent responses
- Manage inbound leads through the sales pipeline
- Schedule meetings with integrated calendar
- Run email campaigns with advanced analytics
- Provide automated follow-ups

The platform uses state-of-the-art AI (Groq LLM) for natural language understanding and generation.""",
                "category": "product",
                "keywords": ["product", "overview", "features", "what is", "about"],
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": demo_user_id,
                "title": "Pricing Plans",
                "content": """Our pricing is designed to scale with your business:

**Starter Plan - $99/month**
- Up to 1,000 emails/month
- 2 email accounts
- Basic AI responses
- Email classification
- 7-day free trial

**Professional Plan - $299/month**
- Up to 5,000 emails/month
- 5 email accounts
- Advanced AI with custom training
- Lead qualification & nurturing
- Campaign management
- Calendar integration
- Priority support

**Enterprise Plan - $799/month**
- Unlimited emails
- Unlimited email accounts
- White-label options
- Dedicated account manager
- Custom integrations
- SLA guarantee
- Advanced analytics

All plans include free setup and training. Annual billing gets 20% discount.""",
                "category": "pricing",
                "keywords": ["pricing", "price", "cost", "plan", "subscription", "fee", "how much"],
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": demo_user_id,
                "title": "Getting Started Guide",
                "content": """Getting started is easy:

1. **Connect Your Email** - Link your Gmail or Outlook account via OAuth
2. **Set Up Intents** - Define how AI should classify and respond to different email types
3. **Add Knowledge Base** - Upload your company information, pricing, and FAQs
4. **Configure Lead Management** - Set up qualification criteria and nurturing questions
5. **Test & Launch** - Use test mode to verify responses, then enable auto-send

Most customers are fully set up within 30 minutes. We offer free onboarding calls for all new users.""",
                "category": "getting_started",
                "keywords": ["getting started", "setup", "how to", "onboard", "begin", "start"],
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": demo_user_id,
                "title": "Support & Contact",
                "content": """We're here to help!

**Support Channels:**
- Email: support@emailassistant.ai (Response within 24 hours)
- Live Chat: Available Mon-Fri 9 AM - 5 PM EST
- Help Center: docs.emailassistant.ai
- Video Tutorials: youtube.com/emailassistant

**Enterprise Support:**
- Dedicated Slack channel
- Priority phone support
- 99.9% uptime SLA
- Response within 1 hour

**Community:**
- Join our Discord community
- Monthly webinars and best practices
- Feature request portal""",
                "category": "support",
                "keywords": ["support", "help", "contact", "reach", "assistance"],
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": demo_user_id,
                "title": "AI Capabilities",
                "content": """Our AI Email Assistant uses Groq's latest LLM technology:

**What Our AI Can Do:**
- Understand email context and intent with 90%+ accuracy
- Generate human-like responses tailored to each situation
- Extract meeting details (date, time, participants)
- Qualify leads by analyzing responses
- Maintain conversation context across threads
- Personalize responses based on sender information
- Detect sentiment and urgency

**Powered by Groq:**
- Ultra-fast response times (< 2 seconds)
- Cost-effective at scale
- Supports multiple languages
- Continuously learning and improving

**Privacy & Security:**
- Your data is never used to train models
- End-to-end encryption
- GDPR and SOC 2 compliant
- Full audit trails""",
                "category": "ai_features",
                "keywords": ["ai", "artificial intelligence", "how does it work", "technology", "llm"],
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
        ]
        
        await db.knowledge_base.insert_many(kb_entries)
        print(f"✅ Created {len(kb_entries)} knowledge base entries")
        
        # ============================================================
        # 6. CREATE SAMPLE INBOUND LEADS
        # ============================================================
        print("\n👥 Step 6: Creating Sample Inbound Leads...")
        
        await db.inbound_leads.delete_many({"user_id": demo_user_id})
        
        leads = [
            {
                "id": str(uuid.uuid4()),
                "user_id": demo_user_id,
                "email": "sarah.johnson@techcorp.com",
                "full_name": "Sarah Johnson",
                "company": "TechCorp Solutions",
                "job_title": "VP of Operations",
                "phone": "+1-555-0101",
                "stage": "qualified",
                "priority": "high",
                "source": "email",
                "tags": ["enterprise", "saas"],
                "qualification_score": 85,
                "qualification_checked": True,
                "qualification_reasons": [
                    "✓ company_size: 200+ employees",
                    "✓ budget: $500/month",
                    "✓ industry: Technology/SaaS"
                ],
                "nurturing_exchanges_count": 2,
                "last_questions_asked": ["company_size", "budget"],
                "qualification_attempt": 2,
                "notes": "Very interested in Enterprise plan. Mentioned integration needs.",
                "meeting_scheduled": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=5)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": demo_user_id,
                "email": "michael.chen@startupventures.io",
                "full_name": "Michael Chen",
                "company": "Startup Ventures",
                "job_title": "Founder & CEO",
                "stage": "awaiting_info",
                "priority": "medium",
                "source": "email",
                "tags": ["startup"],
                "qualification_score": 45,
                "qualification_checked": False,
                "qualification_attempt": 1,
                "nurturing_exchanges_count": 1,
                "last_questions_asked": ["company_size", "budget"],
                "notes": "Early stage startup. Requested demo.",
                "meeting_scheduled": False,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=3)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(hours=12)).isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": demo_user_id,
                "email": "emily.rodriguez@marketingpro.com",
                "full_name": "Emily Rodriguez",
                "company": "Marketing Pro Agency",
                "job_title": "Marketing Director",
                "stage": "new",
                "priority": "medium",
                "source": "email",
                "tags": ["agency", "marketing"],
                "qualification_score": 0,
                "qualification_checked": False,
                "qualification_attempt": 0,
                "nurturing_exchanges_count": 0,
                "notes": "Just sent initial inquiry about features.",
                "meeting_scheduled": False,
                "created_at": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": demo_user_id,
                "email": "david.kim@globalenterprise.com",
                "full_name": "David Kim",
                "company": "Global Enterprise Inc",
                "job_title": "CTO",
                "phone": "+1-555-0199",
                "stage": "qualified",
                "priority": "urgent",
                "source": "email",
                "tags": ["enterprise", "urgent"],
                "qualification_score": 95,
                "qualification_checked": True,
                "qualification_reasons": [
                    "✓ company_size: Enterprise (1000+ employees)",
                    "✓ budget: $2000/month",
                    "✓ industry: Financial Services",
                    "✓ job_title: C-level executive"
                ],
                "nurturing_exchanges_count": 1,
                "qualification_attempt": 1,
                "notes": "Enterprise deal. Needs custom integration. Meeting scheduled for next week.",
                "meeting_scheduled": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=7)).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": demo_user_id,
                "email": "lisa.anderson@consulting.co",
                "full_name": "Lisa Anderson",
                "company": "Anderson Consulting",
                "job_title": "Managing Partner",
                "phone": "+1-555-0155",
                "stage": "unqualified",
                "priority": "low",
                "source": "email",
                "tags": ["small_business"],
                "qualification_score": 25,
                "qualification_checked": True,
                "qualification_reasons": [
                    "✗ company_size: 5 employees (too small)",
                    "✗ budget: $50/month (below minimum)"
                ],
                "nurturing_exchanges_count": 2,
                "qualification_attempt": 2,
                "notes": "Company too small for our solution. Recommended alternative tools.",
                "meeting_scheduled": False,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=10)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=8)).isoformat()
            }
        ]
        
        await db.inbound_leads.insert_many(leads)
        print(f"✅ Created {len(leads)} sample inbound leads")
        
        # ============================================================
        # 7. CREATE CAMPAIGN TEMPLATES
        # ============================================================
        print("\n📧 Step 7: Creating Campaign Templates...")
        
        await db.campaign_templates.delete_many({"user_id": demo_user_id})
        
        templates = [
            {
                "id": str(uuid.uuid4()),
                "user_id": demo_user_id,
                "name": "Product Launch - Initial",
                "description": "Initial email for product launch campaign",
                "subject": "Introducing {{product_name}} - Transform Your {{industry}}",
                "body": """Hi {{first_name}},

I wanted to personally reach out to introduce {{product_name}} - we're revolutionizing how {{industry}} companies handle their email communication.

**What makes us different:**
- AI-powered responses that save 10+ hours per week
- 90%+ accuracy in email classification
- Seamless integration with your existing tools

We're offering early access to {{company}} with a special 30% discount for the first 3 months.

Would you be interested in a quick 15-minute demo to see how {{product_name}} can help your team?

Best regards,
{{sender_name}}""",
                "category": "outreach",
                "variables": ["product_name", "industry", "first_name", "company", "sender_name"],
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": demo_user_id,
                "name": "Product Launch - Follow-up 1",
                "description": "First follow-up for product launch",
                "subject": "Quick question about {{company}}'s email workflow",
                "body": """Hi {{first_name}},

I sent you an email a few days ago about {{product_name}}. I understand you're probably busy, so I wanted to follow up quickly.

I've helped companies like {{competitor_example}} reduce their email response time by 75% while improving customer satisfaction.

**Quick wins we can deliver:**
✓ Automated responses to common inquiries
✓ Smart email classification  
✓ Lead qualification on autopilot

Are you free for a 10-minute call this week to explore if this could help {{company}}?

Best,
{{sender_name}}""",
                "category": "follow_up",
                "variables": ["first_name", "product_name", "company", "competitor_example", "sender_name"],
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": demo_user_id,
                "name": "Customer Success Story",
                "description": "Share customer success story",
                "subject": "How {{customer_name}} Saved 15 Hours/Week with {{product_name}}",
                "body": """Hi {{first_name}},

I thought you'd find this interesting - {{customer_name}}, a company similar to {{company}}, recently shared their results with {{product_name}}:

📊 **Their Results:**
- 15 hours saved per week per team member
- 92% of emails handled automatically
- 40% increase in lead response rate
- ROI achieved in just 6 weeks

They started with the same concerns you might have about AI handling customer communication. But after seeing the quality and control they maintain, they're now expanding to 3 more teams.

Would you like to see a quick demo showing exactly how they use it?

Best regards,
{{sender_name}}

P.S. I can share the full case study if you're interested!""",
                "category": "nurture",
                "variables": ["first_name", "customer_name", "company", "product_name", "sender_name"],
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
        ]
        
        await db.campaign_templates.insert_many(templates)
        print(f"✅ Created {len(templates)} campaign templates")
        
        # ============================================================
        # 8. CREATE CONTACT LISTS
        # ============================================================
        print("\n📋 Step 8: Creating Contact Lists...")
        
        await db.contact_lists.delete_many({"user_id": demo_user_id})
        
        lists = [
            {
                "id": str(uuid.uuid4()),
                "user_id": demo_user_id,
                "name": "Enterprise Prospects",
                "description": "Large companies interested in enterprise plan",
                "tags": ["enterprise", "high-value"],
                "contact_count": 0,
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": demo_user_id,
                "name": "SaaS Startups",
                "description": "Early stage SaaS companies",
                "tags": ["startup", "saas"],
                "contact_count": 0,
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
        ]
        
        await db.contact_lists.insert_many(lists)
        print(f"✅ Created {len(lists)} contact lists")
        
        # ============================================================
        # 9. CREATE CAMPAIGN CONTACTS
        # ============================================================
        print("\n👤 Step 9: Creating Campaign Contacts...")
        
        await db.campaign_contacts.delete_many({"user_id": demo_user_id})
        
        contacts = [
            {
                "id": str(uuid.uuid4()),
                "user_id": demo_user_id,
                "email": "john.smith@acmecorp.com",
                "first_name": "John",
                "last_name": "Smith",
                "company": "Acme Corp",
                "job_title": "Sales Director",
                "phone": "+1-555-1001",
                "industry": "Technology",
                "company_size": "51-200",
                "tags": ["prospect", "saas"],
                "list_ids": [lists[1]["id"]],
                "status": "active",
                "email_verified": True,
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": demo_user_id,
                "email": "jane.doe@innovate.io",
                "first_name": "Jane",
                "last_name": "Doe",
                "company": "Innovate Inc",
                "job_title": "CEO",
                "industry": "SaaS",
                "company_size": "11-50",
                "tags": ["startup", "founder"],
                "list_ids": [lists[1]["id"]],
                "status": "active",
                "email_verified": True,
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": demo_user_id,
                "email": "robert.brown@enterprise.com",
                "first_name": "Robert",
                "last_name": "Brown",
                "company": "Enterprise Solutions Ltd",
                "job_title": "CTO",
                "phone": "+1-555-2001",
                "industry": "Enterprise Software",
                "company_size": "501+",
                "tags": ["enterprise", "decision-maker"],
                "list_ids": [lists[0]["id"]],
                "status": "active",
                "email_verified": True,
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
        ]
        
        await db.campaign_contacts.insert_many(contacts)
        print(f"✅ Created {len(contacts)} campaign contacts")
        
        # Update list counts
        for contact_list in lists:
            count = len([c for c in contacts if contact_list["id"] in c.get("list_ids", [])])
            await db.contact_lists.update_one(
                {"id": contact_list["id"]},
                {"$set": {"contact_count": count}}
            )
        
        # ============================================================
        # 10. CREATE SAMPLE CAMPAIGNS
        # ============================================================
        print("\n📢 Step 10: Creating Sample Campaigns...")
        
        await db.campaigns.delete_many({"user_id": demo_user_id})
        
        campaigns = [
            {
                "id": str(uuid.uuid4()),
                "user_id": demo_user_id,
                "name": "Q4 Product Launch",
                "description": "Product launch campaign for Q4 2025",
                "contact_ids": [c["id"] for c in contacts],
                "contact_tags": ["prospect", "saas"],
                "list_ids": [lists[1]["id"]],
                "initial_template_id": templates[0]["id"],
                "follow_up_config": {
                    "enabled": True,
                    "count": 2,
                    "intervals": [3, 7],
                    "template_ids": [templates[1]["id"], templates[2]["id"]]
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
                "scheduled_start": None,
                "scheduled_end": None,
                "timezone": "UTC",
                "status": "completed",
                "total_contacts": 3,
                "emails_sent": 3,
                "emails_pending": 0,
                "emails_failed": 0,
                "emails_delivered": 3,
                "emails_opened": 2,
                "emails_clicked": 1,
                "emails_replied": 2,
                "emails_bounced": 0,
                "open_rate": 66.67,
                "click_rate": 33.33,
                "reply_rate": 66.67,
                "bounce_rate": 0.0,
                "delivery_rate": 100.0,
                "inbox_rate": 66.67,
                "positive_replies": 1,
                "neutral_replies": 1,
                "negative_replies": 0,
                "leads_generated": 2,
                "lead_rate": 100.0,
                "opportunities_created": 1,
                "opportunities_rate": 50.0,
                "conversions": 1,
                "conversion_rate": 50.0,
                "verify_emails": False,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=15)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(),
                "started_at": (datetime.now(timezone.utc) - timedelta(days=15)).isoformat(),
                "completed_at": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": demo_user_id,
                "name": "Enterprise Outreach",
                "description": "Targeted outreach to enterprise prospects",
                "contact_ids": [contacts[2]["id"]],
                "contact_tags": ["enterprise"],
                "list_ids": [lists[0]["id"]],
                "initial_template_id": templates[0]["id"],
                "follow_up_config": {
                    "enabled": True,
                    "count": 1,
                    "intervals": [5],
                    "template_ids": [templates[1]["id"]]
                },
                "tracking_settings": {
                    "enable_open_tracking": True,
                    "enable_click_tracking": True,
                    "enable_reply_tracking": True,
                    "enable_sentiment_analysis": True
                },
                "email_account_ids": [],
                "daily_limit_per_account": 50,
                "random_delay_min": 180,
                "random_delay_max": 600,
                "scheduled_start": None,
                "scheduled_end": None,
                "timezone": "UTC",
                "status": "running",
                "total_contacts": 1,
                "emails_sent": 1,
                "emails_pending": 0,
                "emails_failed": 0,
                "emails_delivered": 1,
                "emails_opened": 1,
                "emails_clicked": 0,
                "emails_replied": 0,
                "emails_bounced": 0,
                "open_rate": 100.0,
                "click_rate": 0.0,
                "reply_rate": 0.0,
                "bounce_rate": 0.0,
                "delivery_rate": 100.0,
                "inbox_rate": 100.0,
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
                "created_at": (datetime.now(timezone.utc) - timedelta(days=3)).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "started_at": (datetime.now(timezone.utc) - timedelta(days=3)).isoformat(),
                "completed_at": None
            }
        ]
        
        await db.campaigns.insert_many(campaigns)
        print(f"✅ Created {len(campaigns)} sample campaigns")
        
        # ============================================================
        # 11. CREATE FOLLOW-UPS
        # ============================================================
        print("\n📅 Step 11: Creating Sample Follow-ups...")
        
        await db.follow_ups.delete_many({"user_id": demo_user_id})
        
        follow_ups = [
            {
                "id": str(uuid.uuid4()),
                "user_id": demo_user_id,
                "email_id": str(uuid.uuid4()),
                "thread_id": f"thread-{uuid.uuid4()}",
                "to_email": "prospect@example.com",
                "subject": "Re: Pricing Information",
                "body": "Following up on your pricing inquiry...",
                "scheduled_at": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat(),
                "status": "pending",
                "type": "standard",
                "days_from_initial": 2,
                "attempt_number": 1,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
        ]
        
        await db.follow_ups.insert_many(follow_ups)
        print(f"✅ Created {len(follow_ups)} sample follow-ups")
        
        # ============================================================
        # SUMMARY
        # ============================================================
        print("\n" + "=" * 80)
        print("✅ SEED DATA CREATION COMPLETE")
        print("=" * 80)
        print(f"\n📊 Summary:")
        print(f"   - Demo User: {DEMO_EMAIL} / {DEMO_PASSWORD}")
        print(f"   - User ID: {demo_user_id}")
        print(f"   - Intents: {len(intents)}")
        print(f"   - Knowledge Base: {len(kb_entries)}")
        print(f"   - Inbound Leads: {len(leads)}")
        print(f"   - Campaign Templates: {len(templates)}")
        print(f"   - Campaign Contacts: {len(contacts)}")
        print(f"   - Contact Lists: {len(lists)}")
        print(f"   - Campaigns: {len(campaigns)}")
        print(f"   - Follow-ups: {len(follow_ups)}")
        print(f"   - Lead Qualification: ENABLED")
        print(f"   - Lead Nurturing: ENABLED")
        print(f"\n🎯 You can now login at the frontend with:")
        print(f"   Email: {DEMO_EMAIL}")
        print(f"   Password: {DEMO_PASSWORD}")
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error creating seed data: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(create_comprehensive_seed_data())
