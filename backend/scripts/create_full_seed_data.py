#!/usr/bin/env python3
"""
Create comprehensive seed data for the entire application
Including: Users, Intents, Knowledge Base, and Inbound Leads
"""
import asyncio
import uuid
from datetime import datetime, timezone, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext

# MongoDB connection
MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "email_assistant_db"

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_full_seed_data():
    """Create comprehensive seed data for all collections"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("🚀 Creating comprehensive seed data...")
    print("=" * 60)
    
    # ============ CREATE DEMO USER ============
    print("\n📋 Step 1: Creating demo user...")
    
    demo_email = "demo@example.com"
    demo_password = "demo123"
    
    # Check if user exists
    existing_user = await db.users.find_one({"email": demo_email})
    if existing_user:
        user_id = existing_user['id']
        print(f"✅ User already exists: {demo_email} (ID: {user_id})")
    else:
        user_id = str(uuid.uuid4())
        user_data = {
            "id": user_id,
            "email": demo_email,
            "full_name": "Demo User",
            "hashed_password": pwd_context.hash(demo_password),
            "is_active": True,
            "email_verified": True,
            "persona": "You are a professional AI email assistant helping with business communications.",
            "signature": "Best regards,\nDemo User\nAI Email Assistant",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        await db.users.insert_one(user_data)
        print(f"✅ Created user: {demo_email} (ID: {user_id})")
        print(f"   Password: {demo_password}")
    
    # ============ CREATE INTENTS ============
    print("\n📋 Step 2: Creating intents...")
    
    # Clear existing intents for this user
    await db.intents.delete_many({"user_id": user_id})
    
    intents = [
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Meeting Request",
            "description": "Emails requesting to schedule a meeting or call",
            "keywords": ["meeting", "schedule", "call", "discuss", "meet", "zoom", "teams", "appointment", "catch up"],
            "prompt": "You are a professional assistant scheduling meetings. Be courteous, confirm availability, and suggest meeting times if not provided. Always include calendar details if a meeting is being scheduled.",
            "priority": 10,
            "auto_send": True,
            "is_active": True,
            "is_default": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Support Request",
            "description": "Technical support or help requests",
            "keywords": ["help", "support", "issue", "problem", "error", "bug", "not working", "assistance", "trouble"],
            "prompt": "You are a technical support specialist. Be helpful, patient, and provide clear solutions. Ask for relevant details if needed.",
            "priority": 8,
            "auto_send": True,
            "is_active": True,
            "is_default": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "General Inquiry",
            "description": "General questions and information requests",
            "keywords": ["question", "inquiry", "information", "about", "pricing", "details", "wondering"],
            "prompt": "You are providing helpful information. Be clear, concise, and professional. Use the knowledge base to provide accurate information.",
            "priority": 5,
            "auto_send": True,
            "is_active": True,
            "is_default": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Partnership Inquiry",
            "description": "Partnership, collaboration, or business opportunity emails",
            "keywords": ["partnership", "collaborate", "business opportunity", "work together", "joint venture", "alliance"],
            "prompt": "You are exploring partnership opportunities. Be professional and interested. Express openness to discussion and request more details about their proposal.",
            "priority": 7,
            "auto_send": True,
            "is_active": True,
            "is_default": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Default Intent",
            "description": "Default response for unmatched emails",
            "keywords": [],
            "prompt": "You are responding to an email that doesn't match specific categories. Be professional, acknowledge their message, and use the knowledge base to provide relevant information. Ask clarifying questions if needed.",
            "priority": 1,
            "auto_send": True,
            "is_active": True,
            "is_default": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    await db.intents.insert_many(intents)
    print(f"✅ Created {len(intents)} intents")
    
    # ============ CREATE KNOWLEDGE BASE ============
    print("\n📋 Step 3: Creating knowledge base entries...")
    
    # Clear existing KB for this user
    await db.knowledge_base.delete_many({"user_id": user_id})
    
    kb_entries = [
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Company Overview",
            "content": "We are a leading AI-powered email assistant platform that helps businesses automate and optimize their email communications. Our solution uses advanced AI to understand intent, generate contextual responses, and manage follow-ups automatically.",
            "category": "Company Information",
            "tags": ["company", "about", "overview"],
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Product Features",
            "content": "Our platform offers: 1) AI-powered intent classification, 2) Automated email drafting with knowledge base integration, 3) Smart follow-up management, 4) Calendar integration for meeting scheduling, 5) Lead tracking and scoring, 6) Multi-account support, 7) Customizable AI personas and signatures.",
            "category": "Product",
            "tags": ["features", "capabilities", "product"],
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Pricing Plans",
            "content": "We offer three pricing tiers: Starter ($49/month) - 1,000 emails, 1 account, basic features. Professional ($149/month) - 5,000 emails, 3 accounts, advanced AI, priority support. Enterprise (Custom) - Unlimited emails, unlimited accounts, dedicated support, custom integrations.",
            "category": "Pricing",
            "tags": ["pricing", "plans", "cost"],
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Getting Started",
            "content": "To get started: 1) Sign up for an account, 2) Connect your email account via OAuth, 3) Customize your AI persona and signature, 4) Set up intents and keywords, 5) Add knowledge base entries, 6) Configure auto-send settings. Our system will start processing emails automatically within 60 seconds.",
            "category": "Documentation",
            "tags": ["getting started", "setup", "onboarding"],
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Support and Contact",
            "content": "For support: Email us at support@example.com, Live chat available 9AM-5PM EST, Response time: 24 hours for standard, 4 hours for priority. For urgent issues, mark your email as URGENT. Visit our help center at help.example.com for FAQs and guides.",
            "category": "Support",
            "tags": ["support", "contact", "help"],
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    await db.knowledge_base.insert_many(kb_entries)
    print(f"✅ Created {len(kb_entries)} knowledge base entries")
    
    # ============ CREATE INBOUND LEADS ============
    print("\n📋 Step 4: Creating sample inbound leads...")
    
    # Clear existing leads for this user
    await db.inbound_leads.delete_many({"user_id": user_id})
    
    # Create sample leads with realistic data
    leads_data = [
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "lead_name": "Sarah Johnson",
            "lead_email": "sarah.johnson@techcorp.com",
            "company_name": "TechCorp Solutions",
            "job_title": "VP of Sales",
            "phone": "+1-555-0123",
            "industry": "Technology",
            "company_size": "100-500",
            "specific_interests": "Email automation for sales team",
            "requirements": "Looking for solution to handle 500+ inbound leads per month",
            "stage": "qualified",
            "score": 75,
            "priority": "high",
            "initial_email_id": str(uuid.uuid4()),
            "thread_id": f"thread-{uuid.uuid4()}",
            "email_ids": [],
            "intent_name": "Partnership Inquiry",
            "emails_received": 3,
            "emails_sent": 2,
            "last_contact_at": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(),
            "last_reply_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
            "meeting_scheduled": True,
            "meeting_date": (datetime.now(timezone.utc) + timedelta(days=5)).isoformat(),
            "activities": [
                {
                    "timestamp": (datetime.now(timezone.utc) - timedelta(days=7)).isoformat(),
                    "activity_type": "email_received",
                    "description": "Initial inquiry received",
                    "details": {},
                    "performed_by": "system"
                },
                {
                    "timestamp": (datetime.now(timezone.utc) - timedelta(days=5)).isoformat(),
                    "activity_type": "stage_changed",
                    "description": "Stage changed from new to contacted",
                    "details": {"from_stage": "new", "to_stage": "contacted"},
                    "performed_by": "system"
                },
                {
                    "timestamp": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(),
                    "activity_type": "stage_changed",
                    "description": "Stage changed from contacted to qualified",
                    "details": {"from_stage": "contacted", "to_stage": "qualified"},
                    "performed_by": "system"
                },
                {
                    "timestamp": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                    "activity_type": "meeting_scheduled",
                    "description": "Meeting scheduled for next week",
                    "details": {"meeting_date": (datetime.now(timezone.utc) + timedelta(days=5)).isoformat()},
                    "performed_by": "system"
                }
            ],
            "stage_history": [
                {
                    "stage": "new",
                    "timestamp": (datetime.now(timezone.utc) - timedelta(days=7)).isoformat(),
                    "reason": "Initial lead creation",
                    "performed_by": "system"
                },
                {
                    "stage": "contacted",
                    "timestamp": (datetime.now(timezone.utc) - timedelta(days=5)).isoformat(),
                    "reason": "Auto-reply sent",
                    "performed_by": "system"
                },
                {
                    "stage": "qualified",
                    "timestamp": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(),
                    "reason": "High engagement and clear requirements",
                    "performed_by": "system"
                }
            ],
            "is_active": True,
            "created_at": (datetime.now(timezone.utc) - timedelta(days=7)).isoformat(),
            "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "lead_name": "Michael Chen",
            "lead_email": "m.chen@startupventures.io",
            "company_name": "Startup Ventures",
            "job_title": "Founder & CEO",
            "phone": "+1-555-0456",
            "industry": "Finance",
            "company_size": "10-50",
            "specific_interests": "AI email assistant for investor relations",
            "requirements": "Need to manage 100+ investor emails weekly",
            "stage": "contacted",
            "score": 60,
            "priority": "medium",
            "initial_email_id": str(uuid.uuid4()),
            "thread_id": f"thread-{uuid.uuid4()}",
            "email_ids": [],
            "intent_name": "General Inquiry",
            "emails_received": 2,
            "emails_sent": 1,
            "last_contact_at": (datetime.now(timezone.utc) - timedelta(days=3)).isoformat(),
            "last_reply_at": None,
            "meeting_scheduled": False,
            "activities": [
                {
                    "timestamp": (datetime.now(timezone.utc) - timedelta(days=5)).isoformat(),
                    "activity_type": "email_received",
                    "description": "Pricing inquiry received",
                    "details": {},
                    "performed_by": "system"
                },
                {
                    "timestamp": (datetime.now(timezone.utc) - timedelta(days=3)).isoformat(),
                    "activity_type": "email_sent",
                    "description": "Auto-reply with pricing information sent",
                    "details": {},
                    "performed_by": "system"
                },
                {
                    "timestamp": (datetime.now(timezone.utc) - timedelta(days=3)).isoformat(),
                    "activity_type": "stage_changed",
                    "description": "Stage changed from new to contacted",
                    "details": {"from_stage": "new", "to_stage": "contacted"},
                    "performed_by": "system"
                }
            ],
            "stage_history": [
                {
                    "stage": "new",
                    "timestamp": (datetime.now(timezone.utc) - timedelta(days=5)).isoformat(),
                    "reason": "Initial lead creation",
                    "performed_by": "system"
                },
                {
                    "stage": "contacted",
                    "timestamp": (datetime.now(timezone.utc) - timedelta(days=3)).isoformat(),
                    "reason": "Auto-reply sent",
                    "performed_by": "system"
                }
            ],
            "is_active": True,
            "created_at": (datetime.now(timezone.utc) - timedelta(days=5)).isoformat(),
            "updated_at": (datetime.now(timezone.utc) - timedelta(days=3)).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "lead_name": "Emily Rodriguez",
            "lead_email": "emily.r@marketingpro.com",
            "company_name": "Marketing Pro Agency",
            "job_title": "Marketing Director",
            "phone": "+1-555-0789",
            "industry": "Marketing",
            "company_size": "50-100",
            "specific_interests": "Email automation for client communications",
            "requirements": "Handle 200+ client emails daily across multiple accounts",
            "stage": "new",
            "score": 45,
            "priority": "medium",
            "initial_email_id": str(uuid.uuid4()),
            "thread_id": f"thread-{uuid.uuid4()}",
            "email_ids": [],
            "intent_name": "General Inquiry",
            "emails_received": 1,
            "emails_sent": 0,
            "last_contact_at": (datetime.now(timezone.utc) - timedelta(hours=12)).isoformat(),
            "last_reply_at": None,
            "meeting_scheduled": False,
            "activities": [
                {
                    "timestamp": (datetime.now(timezone.utc) - timedelta(hours=12)).isoformat(),
                    "activity_type": "email_received",
                    "description": "Initial inquiry about features",
                    "details": {},
                    "performed_by": "system"
                }
            ],
            "stage_history": [
                {
                    "stage": "new",
                    "timestamp": (datetime.now(timezone.utc) - timedelta(hours=12)).isoformat(),
                    "reason": "Initial lead creation",
                    "performed_by": "system"
                }
            ],
            "is_active": True,
            "created_at": (datetime.now(timezone.utc) - timedelta(hours=12)).isoformat(),
            "updated_at": (datetime.now(timezone.utc) - timedelta(hours=12)).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "lead_name": "David Kim",
            "lead_email": "david.kim@globalenterprise.com",
            "company_name": "Global Enterprise Inc",
            "job_title": "IT Manager",
            "phone": "+1-555-0321",
            "industry": "Enterprise Software",
            "company_size": "500+",
            "specific_interests": "Enterprise email automation solution",
            "requirements": "Need enterprise-grade security and compliance features",
            "stage": "qualified",
            "score": 85,
            "priority": "urgent",
            "initial_email_id": str(uuid.uuid4()),
            "thread_id": f"thread-{uuid.uuid4()}",
            "email_ids": [],
            "intent_name": "Partnership Inquiry",
            "emails_received": 5,
            "emails_sent": 4,
            "last_contact_at": datetime.now(timezone.utc).isoformat(),
            "last_reply_at": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
            "meeting_scheduled": True,
            "meeting_date": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat(),
            "activities": [
                {
                    "timestamp": (datetime.now(timezone.utc) - timedelta(days=10)).isoformat(),
                    "activity_type": "email_received",
                    "description": "Enterprise inquiry received",
                    "details": {},
                    "performed_by": "system"
                },
                {
                    "timestamp": (datetime.now(timezone.utc) - timedelta(days=8)).isoformat(),
                    "activity_type": "stage_changed",
                    "description": "Stage changed from new to contacted",
                    "details": {"from_stage": "new", "to_stage": "contacted"},
                    "performed_by": "system"
                },
                {
                    "timestamp": (datetime.now(timezone.utc) - timedelta(days=4)).isoformat(),
                    "activity_type": "stage_changed",
                    "description": "Stage changed from contacted to qualified",
                    "details": {"from_stage": "contacted", "to_stage": "qualified"},
                    "performed_by": "system"
                },
                {
                    "timestamp": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(),
                    "activity_type": "meeting_scheduled",
                    "description": "Demo meeting scheduled",
                    "details": {"meeting_date": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()},
                    "performed_by": "system"
                }
            ],
            "stage_history": [
                {
                    "stage": "new",
                    "timestamp": (datetime.now(timezone.utc) - timedelta(days=10)).isoformat(),
                    "reason": "Initial lead creation",
                    "performed_by": "system"
                },
                {
                    "stage": "contacted",
                    "timestamp": (datetime.now(timezone.utc) - timedelta(days=8)).isoformat(),
                    "reason": "Auto-reply sent",
                    "performed_by": "system"
                },
                {
                    "stage": "qualified",
                    "timestamp": (datetime.now(timezone.utc) - timedelta(days=4)).isoformat(),
                    "reason": "Enterprise requirements confirmed, high budget",
                    "performed_by": "system"
                }
            ],
            "notes": "High-value enterprise lead. Requires custom pricing and security review.",
            "is_active": True,
            "created_at": (datetime.now(timezone.utc) - timedelta(days=10)).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "lead_name": "Lisa Anderson",
            "lead_email": "lisa.a@consultingfirm.com",
            "company_name": "Anderson Consulting",
            "job_title": "Senior Consultant",
            "phone": "+1-555-0654",
            "industry": "Consulting",
            "company_size": "10-50",
            "specific_interests": "Email management for consulting projects",
            "requirements": "Need to manage client communications across 5-10 active projects",
            "stage": "converted",
            "score": 95,
            "priority": "high",
            "initial_email_id": str(uuid.uuid4()),
            "thread_id": f"thread-{uuid.uuid4()}",
            "email_ids": [],
            "intent_name": "Partnership Inquiry",
            "emails_received": 8,
            "emails_sent": 7,
            "last_contact_at": (datetime.now(timezone.utc) - timedelta(days=15)).isoformat(),
            "last_reply_at": (datetime.now(timezone.utc) - timedelta(days=15)).isoformat(),
            "meeting_scheduled": False,
            "conversion_date": (datetime.now(timezone.utc) - timedelta(days=15)).isoformat(),
            "activities": [
                {
                    "timestamp": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                    "activity_type": "email_received",
                    "description": "Initial inquiry received",
                    "details": {},
                    "performed_by": "system"
                },
                {
                    "timestamp": (datetime.now(timezone.utc) - timedelta(days=15)).isoformat(),
                    "activity_type": "stage_changed",
                    "description": "Stage changed from qualified to converted",
                    "details": {"from_stage": "qualified", "to_stage": "converted"},
                    "performed_by": "user"
                }
            ],
            "stage_history": [
                {
                    "stage": "new",
                    "timestamp": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                    "reason": "Initial lead creation",
                    "performed_by": "system"
                },
                {
                    "stage": "contacted",
                    "timestamp": (datetime.now(timezone.utc) - timedelta(days=28)).isoformat(),
                    "reason": "Auto-reply sent",
                    "performed_by": "system"
                },
                {
                    "stage": "qualified",
                    "timestamp": (datetime.now(timezone.utc) - timedelta(days=20)).isoformat(),
                    "reason": "Strong engagement and clear needs",
                    "performed_by": "system"
                },
                {
                    "stage": "converted",
                    "timestamp": (datetime.now(timezone.utc) - timedelta(days=15)).isoformat(),
                    "reason": "Signed up for Professional plan",
                    "performed_by": "user"
                }
            ],
            "notes": "Successful conversion! Professional plan subscriber.",
            "is_active": True,
            "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
            "updated_at": (datetime.now(timezone.utc) - timedelta(days=15)).isoformat()
        }
    ]
    
    await db.inbound_leads.insert_many(leads_data)
    print(f"✅ Created {len(leads_data)} sample inbound leads")
    
    # ============ SUMMARY ============
    print("\n" + "=" * 60)
    print("🎉 SEED DATA CREATION COMPLETE!")
    print("=" * 60)
    print(f"\n✅ Demo User Created:")
    print(f"   Email: {demo_email}")
    print(f"   Password: {demo_password}")
    print(f"   User ID: {user_id}")
    print(f"\n✅ Data Summary:")
    print(f"   - {len(intents)} Intents")
    print(f"   - {len(kb_entries)} Knowledge Base Entries")
    print(f"   - {len(leads_data)} Inbound Leads")
    print(f"\n✅ Lead Distribution:")
    stage_counts = {}
    for lead in leads_data:
        stage = lead['stage']
        stage_counts[stage] = stage_counts.get(stage, 0) + 1
    for stage, count in sorted(stage_counts.items()):
        print(f"   - {stage}: {count}")
    
    print(f"\n🚀 You can now log in and test the application!")
    print("=" * 60)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(create_full_seed_data())
