"""
Create comprehensive seed data for amits.joys@gmail.com
Includes: Intents, Knowledge Base, Lead Qualification Criteria, Lead Nurturing Config,
Campaigns, and Sample Leads
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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
import uuid

async def create_seed_data():
    """Create comprehensive seed data for amits.joys@gmail.com"""
    
    print("🚀 Starting comprehensive seed data creation...")
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(config.MONGO_URL)
    db = client[config.DB_NAME]
    
    # Find user
    user = await db.users.find_one({"email": "amits.joys@gmail.com"})
    if not user:
        print("❌ User amits.joys@gmail.com not found!")
        print("Creating user...")
        # Create user if not exists
        from backend.models.user import User
        new_user = User(
            email="amits.joys@gmail.com",
            hashed_password="$2b$12$8UgC6.xYZ9vFKqW8mP0Z0eMq7nHqh9NqUZ0H0kC9z0P0Y0qK0W0Zu",  # ij@123
            full_name="Amit Joys",
            role="user"
        )
        await db.users.insert_one(new_user.model_dump())
        user = await db.users.find_one({"email": "amits.joys@gmail.com"})
        print(f"✓ Created user: {user['email']}")
    
    user_id = user['id']
    print(f"✓ Found user: {user['email']} (ID: {user_id})")
    
    # Delete existing seed data
    deleted_intents = await db.intents.delete_many({"user_id": user_id})
    deleted_kb = await db.knowledge_base.delete_many({"user_id": user_id})
    deleted_qual = await db.lead_qualification_criteria.delete_many({"user_id": user_id})
    deleted_nurt = await db.lead_nurturing_configs.delete_many({"user_id": user_id})
    deleted_leads = await db.inbound_leads.delete_many({"user_id": user_id})
    
    print(f"✓ Cleaned up existing data:")
    print(f"  - {deleted_intents.deleted_count} intents")
    print(f"  - {deleted_kb.deleted_count} knowledge base entries")
    print(f"  - {deleted_qual.deleted_count} qualification criteria")
    print(f"  - {deleted_nurt.deleted_count} nurturing configs")
    print(f"  - {deleted_leads.deleted_count} leads")
    
    # ============================================================================
    # 1. CREATE INTENTS
    # ============================================================================
    print("\n📋 Creating Intents...")
    
    intents_data = [
        {
            "name": "Product Inquiry",
            "description": "Customer inquiring about products or services",
            "keywords": ["product", "service", "offering", "solution", "what do you", "tell me about"],
            "priority": 8,
            "auto_send": True,
            "is_lead": True,
            "is_default": False,
            "ai_prompt": """Respond professionally to product inquiries. Provide relevant information from knowledge base. Ask qualifying questions naturally."""
        },
        {
            "name": "Pricing Request",
            "description": "Customer asking about pricing",
            "keywords": ["price", "cost", "pricing", "quote", "budget", "how much"],
            "priority": 9,
            "auto_send": True,
            "is_lead": True,
            "is_default": False,
            "ai_prompt": """Provide pricing information if available in knowledge base. Otherwise, schedule a call to discuss pricing in detail."""
        },
        {
            "name": "Meeting Request",
            "description": "Customer requesting a meeting",
            "keywords": ["meeting", "schedule", "call", "zoom", "meet", "catch up", "discuss"],
            "priority": 10,
            "auto_send": True,
            "is_lead": False,
            "is_default": False,
            "ai_prompt": """Acknowledge the meeting request. Confirm or ask about proposed time. Mention that calendar invite will follow."""
        },
        {
            "name": "General Inquiry",
            "description": "General questions",
            "keywords": ["hello", "hi", "question", "inquiry", "wondering"],
            "priority": 5,
            "auto_send": True,
            "is_lead": True,
            "is_default": True,
            "ai_prompt": """Respond professionally and warmly. Provide relevant information and ask how you can help further."""
        }
    ]
    
    for intent_data in intents_data:
        intent = Intent(user_id=user_id, **intent_data)
        await db.intents.insert_one(intent.model_dump())
        print(f"  ✓ Created intent: {intent.name}")
    
    # ============================================================================
    # 2. CREATE KNOWLEDGE BASE
    # ============================================================================
    print("\n📚 Creating Knowledge Base...")
    
    kb_data = [
        {
            "title": "Company Overview",
            "content": """We are a leading AI-powered CRM and email automation company. 
            We help businesses automate their email workflows, qualify leads, and manage customer relationships efficiently.
            Our platform uses advanced AI to understand context and respond appropriately.""",
            "category": "General"
        },
        {
            "title": "Product Features",
            "content": """
            Key Features:
            - AI-powered email classification and response
            - Automated lead qualification and nurturing
            - Calendar integration for meeting scheduling
            - Email campaign management
            - CRM with lead pipeline tracking
            - Real-time analytics and insights
            """,
            "category": "Products"
        },
        {
            "title": "Pricing Plans",
            "content": """
            Starter Plan: $49/month - Up to 1000 emails, 100 leads
            Professional Plan: $149/month - Up to 5000 emails, 500 leads
            Enterprise Plan: Custom pricing - Unlimited emails and leads
            All plans include 14-day free trial.
            """,
            "category": "Pricing"
        },
        {
            "title": "Integration Capabilities",
            "content": """
            We integrate with:
            - Google Workspace (Gmail, Calendar)
            - Microsoft 365 (Outlook, Calendar)
            - HubSpot CRM
            - Popular calendar systems
            - AI models (Groq, OpenAI compatible)
            """,
            "category": "Technical"
        }
    ]
    
    for kb_item in kb_data:
        kb = KnowledgeBase(user_id=user_id, **kb_item)
        await db.knowledge_base.insert_one(kb.model_dump())
        print(f"  ✓ Created KB: {kb.title}")
    
    # ============================================================================
    # 3. CREATE LEAD QUALIFICATION CRITERIA
    # ============================================================================
    print("\n🎯 Creating Lead Qualification Criteria...")
    
    qual_questions = [
        QualificationQuestion(
            question_text="What is the size of your company?",
            question_key="company_size",
            expected_answer_type="choice",
            qualifying_answers=["50-200", "200+", "medium", "large", "enterprise"],
            disqualifying_answers=["1-10", "solo", "individual"],
            weight=0.3,
            is_required=True,
            priority=1
        ),
        QualificationQuestion(
            question_text="What is your budget range for this solution?",
            question_key="budget",
            expected_answer_type="text",
            weight=0.4,
            is_required=True,
            priority=2
        ),
        QualificationQuestion(
            question_text="When are you looking to implement this solution?",
            question_key="timeline",
            expected_answer_type="choice",
            qualifying_answers=["immediately", "this month", "within 3 months", "soon"],
            disqualifying_answers=["just researching", "maybe next year", "no timeline"],
            weight=0.3,
            is_required=False,
            priority=3
        )
    ]
    
    qual_criteria = LeadQualificationCriteria(
        user_id=user_id,
        name="Standard Qualification",
        description="Default qualification criteria for inbound leads",
        is_enabled=True,
        criteria_type="score_based",
        questions=[q.model_dump() for q in qual_questions],
        min_qualification_score=0.6,
        max_exchanges=3,
        auto_disqualify_on_fail=False
    )
    
    await db.lead_qualification_criteria.insert_one(qual_criteria.model_dump())
    print(f"  ✓ Created qualification criteria: {qual_criteria.name}")
    
    # ============================================================================
    # 4. CREATE LEAD NURTURING CONFIGURATION
    # ============================================================================
    print("\n🌱 Creating Lead Nurturing Configuration...")
    
    nurturing_questions = [
        NurturingQuestion(
            question_text="What specific challenges are you looking to solve?",
            context_keywords=["problem", "challenge", "issue", "pain"],
            priority=1,
            max_asks=1,
            is_required=False
        ),
        NurturingQuestion(
            question_text="Have you used similar solutions before? If so, what worked or didn't work?",
            context_keywords=["experience", "previous", "used", "tried"],
            priority=2,
            max_asks=1,
            is_required=False
        ),
        NurturingQuestion(
            question_text="Who else is involved in the decision-making process?",
            context_keywords=["team", "decision", "stakeholders", "approval"],
            priority=3,
            max_asks=1,
            is_required=False
        )
    ]
    
    nurturing_config = LeadNurturingConfig(
        user_id=user_id,
        name="Standard Nurturing",
        description="Default nurturing configuration for leads",
        is_enabled=True,
        questions=[q.model_dump() for q in nurturing_questions],
        questions_per_email=2,
        max_exchanges=2,
        use_contextual_questions=True,
        natural_integration=True,
        avoid_interrogation=True
    )
    
    await db.lead_nurturing_configs.insert_one(nurturing_config.model_dump())
    print(f"  ✓ Created nurturing config: {nurturing_config.name}")
    
    # ============================================================================
    # 5. CREATE SAMPLE LEADS
    # ============================================================================
    print("\n👥 Creating Sample Leads...")
    
    # First, create a dummy email for lead reference
    dummy_email_id = str(uuid.uuid4())
    
    leads_data = [
        {
            "lead_name": "John Smith",
            "lead_email": "john.smith@techcorp.com",
            "company_name": "TechCorp Inc",
            "job_title": "VP of Engineering",
            "company_size": "200-500",
            "industry": "Technology",
            "specific_interests": "Email automation for sales team",
            "stage": "new",
            "score": 75,
            "priority": "high",
            "initial_email_id": dummy_email_id,
            "emails_received": 2,
            "emails_sent": 1
        },
        {
            "lead_name": "Sarah Johnson",
            "lead_email": "sarah.j@startup.io",
            "company_name": "Startup.io",
            "job_title": "Founder",
            "company_size": "10-50",
            "industry": "SaaS",
            "specific_interests": "CRM and lead management",
            "stage": "contacted",
            "score": 60,
            "priority": "medium",
            "initial_email_id": dummy_email_id,
            "emails_received": 1,
            "emails_sent": 1
        },
        {
            "lead_name": "Michael Chen",
            "lead_email": "m.chen@bigcompany.com",
            "company_name": "BigCompany Corp",
            "job_title": "Sales Director",
            "company_size": "1000+",
            "industry": "Enterprise Software",
            "specific_interests": "Email campaign management",
            "stage": "qualified",
            "score": 85,
            "priority": "high",
            "initial_email_id": dummy_email_id,
            "qualification_checked": True,
            "qualification_score": 85,
            "emails_received": 3,
            "emails_sent": 2
        }
    ]
    
    for lead_data in leads_data:
        lead = InboundLead(user_id=user_id, **lead_data)
        await db.inbound_leads.insert_one(lead.model_dump())
        print(f"  ✓ Created lead: {lead.lead_name} - {lead.company_name}")
    
    # ============================================================================
    # UPDATE USER PERSONA
    # ============================================================================
    print("\n👤 Updating User Persona...")
    
    persona = """I am a professional business assistant representing our AI-powered CRM company. 
    I communicate clearly, professionally, and warmly. I always address recipients by their name when known. 
    I provide helpful, accurate information based on our knowledge base and ask relevant questions to understand their needs better."""
    
    await db.users.update_one(
        {"id": user_id},
        {"$set": {
            "persona": persona,
            "email_signature": "\n\nBest regards,\nAI Assistant\nAI-Powered CRM Solutions"
        }}
    )
    print("  ✓ Updated user persona and signature")
    
    print("\n" + "="*60)
    print("✅ Seed data creation completed successfully!")
    print("="*60)
    print(f"\n📊 Summary:")
    print(f"  - Created {len(intents_data)} intents")
    print(f"  - Created {len(kb_data)} knowledge base entries")
    print(f"  - Created 1 qualification criteria with {len(qual_questions)} questions")
    print(f"  - Created 1 nurturing configuration with {len(nurturing_questions)} questions")
    print(f"  - Created {len(leads_data)} sample leads")
    print(f"\n🎉 User amits.joys@gmail.com is ready to use the system!")

if __name__ == "__main__":
    asyncio.run(create_seed_data())
