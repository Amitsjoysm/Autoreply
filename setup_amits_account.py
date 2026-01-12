"""
Complete setup for amits.joys@gmail.com
1. Create comprehensive seed data
2. Enable global lead qualification and nurturing
3. Link intents to qualification criteria and nurturing config
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

from backend.config import config
from backend.models.intent import Intent
from backend.models.knowledge_base import KnowledgeBase
from backend.models.lead_qualification_criteria import (
    LeadQualificationCriteria,
    QualificationQuestion
)
from backend.models.lead_nurturing_config import (
    LeadNurturingConfig,
    NurturingQuestion
)
from backend.models.inbound_lead import InboundLead
from backend.models.user import User
import uuid

async def setup_complete():
    """Complete setup for amits.joys@gmail.com"""
    
    print("=" * 70)
    print("🚀 COMPLETE SETUP FOR amits.joys@gmail.com")
    print("=" * 70)
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(config.MONGO_URL)
    db = client[config.DB_NAME]
    
    # ============================================================================
    # STEP 1: FIND OR CREATE USER
    # ============================================================================
    print("\n📋 Step 1: Finding user...")
    user = await db.users.find_one({"email": "amits.joys@gmail.com"})
    
    if not user:
        print("❌ User not found! Creating user...")
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        new_user = User(
            email="amits.joys@gmail.com",
            hashed_password=pwd_context.hash("ij@123"),
            full_name="Amit Joys",
            role="user",
            global_lead_qualification_enabled=True,
            global_lead_nurturing_enabled=True
        )
        await db.users.insert_one(new_user.model_dump())
        user = await db.users.find_one({"email": "amits.joys@gmail.com"})
        print(f"✓ Created user: {user['email']}")
    else:
        print(f"✓ Found user: {user['email']} (ID: {user['id']})")
    
    user_id = user['id']
    
    # ============================================================================
    # STEP 2: ENABLE GLOBAL SETTINGS
    # ============================================================================
    print("\n⚙️  Step 2: Enabling global lead qualification and nurturing...")
    
    await db.users.update_one(
        {"id": user_id},
        {"$set": {
            "global_lead_qualification_enabled": True,
            "global_lead_nurturing_enabled": True,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    print("  ✓ Global lead qualification: ENABLED")
    print("  ✓ Global lead nurturing: ENABLED")
    
    # ============================================================================
    # STEP 3: CLEAN UP EXISTING DATA
    # ============================================================================
    print("\n🧹 Step 3: Cleaning up existing data...")
    
    deleted_intents = await db.intents.delete_many({"user_id": user_id})
    deleted_kb = await db.knowledge_base.delete_many({"user_id": user_id})
    deleted_qual = await db.lead_qualification_criteria.delete_many({"user_id": user_id})
    deleted_nurt = await db.lead_nurturing_configs.delete_many({"user_id": user_id})
    deleted_leads = await db.inbound_leads.delete_many({"user_id": user_id})
    
    print(f"  ✓ Deleted {deleted_intents.deleted_count} intents")
    print(f"  ✓ Deleted {deleted_kb.deleted_count} knowledge base entries")
    print(f"  ✓ Deleted {deleted_qual.deleted_count} qualification criteria")
    print(f"  ✓ Deleted {deleted_nurt.deleted_count} nurturing configs")
    print(f"  ✓ Deleted {deleted_leads.deleted_count} leads")
    
    # ============================================================================
    # STEP 4: CREATE LEAD QUALIFICATION CRITERIA
    # ============================================================================
    print("\n🎯 Step 4: Creating Lead Qualification Criteria...")
    
    qual_questions = [
        QualificationQuestion(
            question_text="What is the size of your company?",
            question_key="company_size",
            expected_answer_type="choice",
            qualifying_answers=["50-200", "200+", "medium", "large", "enterprise"],
            disqualifying_answers=["1-10", "solo", "individual", "freelancer"],
            weight=0.35,
            is_required=True,
            priority=1
        ),
        QualificationQuestion(
            question_text="What is your budget range for this solution?",
            question_key="budget",
            expected_answer_type="text",
            qualifying_answers=["$1000+", "$5000+", "$10000+"],
            disqualifying_answers=["$0", "free", "no budget"],
            weight=0.35,
            is_required=True,
            priority=2
        ),
        QualificationQuestion(
            question_text="When are you looking to implement this solution?",
            question_key="timeline",
            expected_answer_type="choice",
            qualifying_answers=["immediately", "this month", "within 3 months", "soon", "Q1", "Q2"],
            disqualifying_answers=["just researching", "maybe next year", "no timeline", "no rush"],
            weight=0.30,
            is_required=True,
            priority=3
        )
    ]
    
    qual_criteria = LeadQualificationCriteria(
        user_id=user_id,
        name="Standard B2B Qualification",
        description="Default qualification criteria for B2B inbound leads with company size, budget, and timeline",
        is_enabled=True,
        criteria_type="question_based",
        questions=[q.model_dump() for q in qual_questions],
        min_qualification_score=60,
        max_exchanges=3,
        auto_disqualify_on_fail=True
    )
    
    result = await db.lead_qualification_criteria.insert_one(qual_criteria.model_dump())
    qual_criteria_id = qual_criteria.id
    print(f"  ✓ Created qualification criteria: {qual_criteria.name}")
    print(f"    - ID: {qual_criteria_id}")
    print(f"    - Questions: {len(qual_questions)}")
    print(f"    - Min score: {qual_criteria.min_qualification_score}")
    print(f"    - Max exchanges: {qual_criteria.max_exchanges}")
    
    # ============================================================================
    # STEP 5: CREATE LEAD NURTURING CONFIGURATION
    # ============================================================================
    print("\n🌱 Step 5: Creating Lead Nurturing Configuration...")
    
    nurturing_questions = [
        NurturingQuestion(
            question_text="What is the size of your company?",
            question_key="company_size",
            context_keywords=["company", "team", "size", "employees"],
            priority=1,
            max_asks=1,
            is_required=True
        ),
        NurturingQuestion(
            question_text="What is your budget range for this solution?",
            question_key="budget",
            context_keywords=["budget", "price", "cost", "investment"],
            priority=2,
            max_asks=1,
            is_required=True
        ),
        NurturingQuestion(
            question_text="When are you looking to implement this solution?",
            question_key="timeline",
            context_keywords=["timeline", "when", "implement", "start"],
            priority=3,
            max_asks=1,
            is_required=True
        ),
        NurturingQuestion(
            question_text="What specific challenges are you looking to solve?",
            question_key="challenges",
            context_keywords=["problem", "challenge", "issue", "pain"],
            priority=4,
            max_asks=1,
            is_required=False
        )
    ]
    
    nurturing_config = LeadNurturingConfig(
        user_id=user_id,
        name="Standard B2B Nurturing",
        description="Default nurturing for B2B leads - asks qualification questions naturally",
        is_enabled=True,
        questions=[q.model_dump() for q in nurturing_questions],
        questions_per_email=2,
        max_exchanges=3,
        use_contextual_questions=True,
        natural_integration=True,
        avoid_interrogation=True
    )
    
    result = await db.lead_nurturing_configs.insert_one(nurturing_config.model_dump())
    nurturing_config_id = nurturing_config.id
    print(f"  ✓ Created nurturing config: {nurturing_config.name}")
    print(f"    - ID: {nurturing_config_id}")
    print(f"    - Questions: {len(nurturing_questions)}")
    print(f"    - Questions per email: {nurturing_config.questions_per_email}")
    print(f"    - Max exchanges: {nurturing_config.max_exchanges}")
    
    # ============================================================================
    # STEP 6: CREATE INTENTS (LINKED TO QUAL/NURT)
    # ============================================================================
    print("\n📋 Step 6: Creating Intents (with lead qualification enabled)...")
    
    intents_data = [
        {
            "name": "Product Inquiry (Lead)",
            "description": "Customer inquiring about products or services - LEAD",
            "keywords": ["product", "service", "offering", "solution", "what do you", "tell me about", "interested in"],
            "priority": 9,
            "auto_send": True,
            "is_inbound_lead": True,
            "enable_lead_qualification": True,
            "enable_lead_nurturing": True,
            "is_default": False,
            "prompt": """You are a professional sales assistant. Respond warmly to product inquiries. 
Provide relevant information from the knowledge base. Ask qualifying questions naturally as part of the conversation to understand their needs better."""
        },
        {
            "name": "Pricing Request (Lead)",
            "description": "Customer asking about pricing - LEAD",
            "keywords": ["price", "cost", "pricing", "quote", "budget", "how much", "rates", "fees"],
            "priority": 10,
            "auto_send": True,
            "is_inbound_lead": True,
            "enable_lead_qualification": True,
            "enable_lead_nurturing": True,
            "is_default": False,
            "prompt": """You are a professional sales assistant. Provide pricing information if available in knowledge base. 
Ask qualifying questions naturally to understand their specific needs and budget. Be helpful and consultative."""
        },
        {
            "name": "Demo Request (Lead)",
            "description": "Customer requesting a demo or trial - LEAD",
            "keywords": ["demo", "trial", "try", "test", "preview", "see it in action"],
            "priority": 10,
            "auto_send": True,
            "is_inbound_lead": True,
            "enable_lead_qualification": True,
            "enable_lead_nurturing": True,
            "is_default": False,
            "prompt": """You are a professional sales assistant. Acknowledge their demo request enthusiastically. 
Ask qualifying questions naturally to prepare the best demo for their needs."""
        },
        {
            "name": "Meeting Request (Non-Lead)",
            "description": "Customer requesting a meeting",
            "keywords": ["meeting", "schedule", "call", "zoom", "meet", "catch up", "discuss", "talk"],
            "priority": 8,
            "auto_send": True,
            "is_inbound_lead": False,
            "enable_lead_qualification": False,
            "enable_lead_nurturing": False,
            "is_default": False,
            "prompt": """Acknowledge the meeting request professionally. Confirm or ask about proposed time. 
Mention that calendar invite will follow. Be warm and helpful."""
        },
        {
            "name": "General Inquiry (Lead)",
            "description": "General questions about the business",
            "keywords": ["hello", "hi", "question", "inquiry", "wondering", "information", "help"],
            "priority": 5,
            "auto_send": True,
            "is_inbound_lead": True,
            "enable_lead_qualification": True,
            "enable_lead_nurturing": True,
            "is_default": True,
            "prompt": """You are a professional assistant. Respond professionally and warmly. 
Provide relevant information and ask how you can help further. Naturally ask qualifying questions."""
        }
    ]
    
    created_intents = []
    for intent_data in intents_data:
        intent = Intent(
            user_id=user_id,
            qualification_criteria_id=qual_criteria_id if intent_data.get("enable_lead_qualification") else None,
            nurturing_config_id=nurturing_config_id if intent_data.get("enable_lead_nurturing") else None,
            **intent_data
        )
        await db.intents.insert_one(intent.model_dump())
        created_intents.append(intent)
        lead_flag = "🎯 LEAD" if intent.is_inbound_lead else "📧 NON-LEAD"
        qual_flag = "✓ Qual" if intent.enable_lead_qualification else "✗ Qual"
        nurt_flag = "✓ Nurt" if intent.enable_lead_nurturing else "✗ Nurt"
        print(f"  ✓ Created: {intent.name} [{lead_flag}] [{qual_flag}] [{nurt_flag}]")
    
    # ============================================================================
    # STEP 7: CREATE KNOWLEDGE BASE
    # ============================================================================
    print("\n📚 Step 7: Creating Knowledge Base...")
    
    kb_data = [
        {
            "title": "Company Overview",
            "content": """We are a leading AI-powered CRM and email automation company. 
We help businesses automate their email workflows, qualify leads automatically, and manage customer relationships efficiently using advanced AI technology.
Our platform understands email context and responds intelligently, saving hours of manual work.""",
            "category": "General"
        },
        {
            "title": "Product Features",
            "content": """
Key Features:
- AI-powered email classification and intelligent response generation
- Automated lead qualification with smart scoring (0-100 scale)
- Lead nurturing with contextual questions integrated naturally
- Calendar integration for seamless meeting scheduling
- Email campaign management with follow-up automation
- CRM with visual lead pipeline tracking
- Real-time analytics and actionable insights
- HubSpot integration for existing CRM workflows
            """,
            "category": "Products"
        },
        {
            "title": "Pricing Plans",
            "content": """
Starter Plan: $99/month
- Up to 2,000 emails per month
- Up to 200 leads
- Basic AI features
- Email support

Professional Plan: $299/month
- Up to 10,000 emails per month
- Up to 1,000 leads
- Advanced AI features
- Priority email support
- Calendar integration

Enterprise Plan: Custom pricing
- Unlimited emails and leads
- Custom AI training
- Dedicated account manager
- Phone support
- SLA guarantee

All plans include 14-day free trial with full feature access.
            """,
            "category": "Pricing"
        },
        {
            "title": "Integration Capabilities",
            "content": """
We integrate seamlessly with:
- Google Workspace (Gmail, Google Calendar)
- Microsoft 365 (Outlook, Microsoft Calendar)
- HubSpot CRM (bidirectional sync)
- AI Models: Groq AI for fast processing
- OAuth 2.0 for secure authentication
- Webhook support for custom integrations
            """,
            "category": "Technical"
        },
        {
            "title": "Lead Qualification Process",
            "content": """
Our AI automatically qualifies leads by:
1. Detecting inbound lead emails based on intent
2. Asking 2 natural qualifying questions per email
3. Extracting answers using AI
4. Scoring leads on 0-100 scale based on answers
5. Qualifying leads with score >= 60
6. Maximum 3 email exchanges for qualification
7. Moving qualified leads to your CRM pipeline

This saves hours of manual qualification work.
            """,
            "category": "Features"
        }
    ]
    
    for kb_item in kb_data:
        kb = KnowledgeBase(user_id=user_id, **kb_item)
        await db.knowledge_base.insert_one(kb.model_dump())
        print(f"  ✓ Created: {kb.title}")
    
    # ============================================================================
    # STEP 8: UPDATE USER PERSONA
    # ============================================================================
    print("\n👤 Step 8: Setting User Persona...")
    
    persona = """I am a professional business development assistant representing our AI-powered CRM company. 
I communicate clearly, professionally, and warmly. I always address recipients by their name when known. 
I provide helpful, accurate information based on our knowledge base. 
I ask relevant qualifying questions naturally as part of the conversation to understand prospects' needs better.
My goal is to be helpful and consultative, not pushy."""
    
    await db.users.update_one(
        {"id": user_id},
        {"$set": {
            "persona": persona,
            "email_signature": "\n\nBest regards,\nAI Assistant\nAI-Powered CRM Solutions\nhttps://example.com"
        }}
    )
    print("  ✓ Updated user persona and email signature")
    
    # ============================================================================
    # STEP 9: VERIFICATION
    # ============================================================================
    print("\n✅ Step 9: Verifying setup...")
    
    user_check = await db.users.find_one({"id": user_id})
    intents_count = await db.intents.count_documents({"user_id": user_id})
    kb_count = await db.knowledge_base.count_documents({"user_id": user_id})
    qual_count = await db.lead_qualification_criteria.count_documents({"user_id": user_id})
    nurt_count = await db.lead_nurturing_configs.count_documents({"user_id": user_id})
    
    lead_intents = await db.intents.count_documents({
        "user_id": user_id,
        "is_inbound_lead": True,
        "enable_lead_qualification": True
    })
    
    print(f"  ✓ Global Lead Qualification: {user_check.get('global_lead_qualification_enabled', False)}")
    print(f"  ✓ Global Lead Nurturing: {user_check.get('global_lead_nurturing_enabled', False)}")
    print(f"  ✓ Intents created: {intents_count}")
    print(f"  ✓ Lead intents with qualification: {lead_intents}")
    print(f"  ✓ Knowledge base entries: {kb_count}")
    print(f"  ✓ Qualification criteria: {qual_count}")
    print(f"  ✓ Nurturing configs: {nurt_count}")
    
    # ============================================================================
    # FINAL SUMMARY
    # ============================================================================
    print("\n" + "=" * 70)
    print("✅ SETUP COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    print("\n📊 Configuration Summary:")
    print(f"  User: amits.joys@gmail.com (ID: {user_id})")
    print(f"  Global Lead Qualification: ENABLED ✓")
    print(f"  Global Lead Nurturing: ENABLED ✓")
    print(f"  Intents: {intents_count} ({lead_intents} with lead qualification)")
    print(f"  Knowledge Base: {kb_count} entries")
    print(f"  Qualification Criteria: 1 with {len(qual_questions)} questions")
    print(f"  Nurturing Config: 1 with {len(nurturing_questions)} questions")
    
    print("\n🎯 How Lead Qualification Works:")
    print("  1. Email arrives matching a lead intent (Product/Pricing/Demo/General)")
    print("  2. AI detects it's an inbound lead")
    print("  3. System creates lead in 'awaiting_info' stage")
    print("  4. AI generates 2 qualifying questions naturally in reply")
    print("  5. When prospect replies, AI extracts answers")
    print("  6. Lead is scored (0-100) based on answers")
    print("  7. Score >= 60: Lead is QUALIFIED and added to Inbound Leads")
    print("  8. Score < 40: Lead is DISQUALIFIED")
    print("  9. Score 40-59: Ask more questions (up to 3 exchanges)")
    
    print("\n🧪 Test the System:")
    print("  1. Log in as amits.joys@gmail.com")
    print("  2. Add an email account")
    print("  3. Send a test email with keywords like 'pricing' or 'product inquiry'")
    print("  4. Check that AI asks qualification questions in draft")
    print("  5. Reply with answers to see lead scoring in action")
    
    print("\n🎉 System is ready for testing!")
    
    await client.close()

if __name__ == "__main__":
    asyncio.run(setup_complete())
