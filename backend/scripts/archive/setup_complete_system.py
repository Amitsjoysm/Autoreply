"""
Complete System Setup
Creates all necessary data for testing the full flow
"""
import asyncio
import sys
import uuid
from datetime import datetime, timezone

sys.path.insert(0, '/app/backend')

from motor.motor_asyncio import AsyncIOMotorClient
from config import config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def setup_complete_system():
    """Setup complete system with all required data"""
    
    client = AsyncIOMotorClient(config.MONGO_URL)
    db = client[config.DB_NAME]
    
    logger.info("=" * 80)
    logger.info("COMPLETE SYSTEM SETUP")
    logger.info("=" * 80)
    
    # Get user
    user = await db.users.find_one({})
    if not user:
        logger.error("No user found!")
        return False
    
    user_id = user['id']
    logger.info(f"✓ User: {user['email']}")
    
    # 1. Enable global settings
    logger.info("\n--- Enabling Global Settings ---")
    await db.users.update_one(
        {"id": user_id},
        {"$set": {
            "global_lead_qualification_enabled": True,
            "global_lead_nurturing_enabled": True,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    logger.info("✓ Global qualification enabled")
    logger.info("✓ Global nurturing enabled")
    
    # 2. Create Intents
    logger.info("\n--- Creating Intents ---")
    
    intents_data = [
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Demo Request (Lead)",
            "description": "Customer wants a demo of the product",
            "prompt": "Provide helpful information about our demo process. Ask qualifying questions about their needs.",
            "keywords": ["demo", "trial", "test", "preview", "show me"],
            "auto_send": True,
            "priority": 10,
            "is_default": False,
            "is_inbound_lead": True,
            "enable_lead_qualification": True,
            "enable_lead_nurturing": True,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Pricing Inquiry (Lead)",
            "description": "Customer asking about pricing",
            "prompt": "Provide pricing information and ask about their company size and needs.",
            "keywords": ["pricing", "price", "cost", "budget", "how much"],
            "auto_send": True,
            "priority": 9,
            "is_default": False,
            "is_inbound_lead": True,
            "enable_lead_qualification": True,
            "enable_lead_nurturing": True,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Meeting Request",
            "description": "Customer wants to schedule a meeting",
            "prompt": "Help schedule a meeting and create calendar event.",
            "keywords": ["meeting", "schedule", "call", "zoom", "meet"],
            "auto_send": True,
            "priority": 10,
            "is_default": False,
            "is_inbound_lead": False,
            "enable_lead_qualification": False,
            "enable_lead_nurturing": False,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Support Request",
            "description": "Customer needs help",
            "prompt": "Provide helpful support using knowledge base.",
            "keywords": ["help", "issue", "problem", "error", "broken", "not working"],
            "auto_send": True,
            "priority": 8,
            "is_default": False,
            "is_inbound_lead": False,
            "enable_lead_qualification": False,
            "enable_lead_nurturing": False,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "General Inquiry",
            "description": "General questions",
            "prompt": "Provide helpful information using knowledge base and persona.",
            "keywords": ["question", "info", "information", "tell me"],
            "auto_send": True,
            "priority": 5,
            "is_default": False,
            "is_inbound_lead": False,
            "enable_lead_qualification": False,
            "enable_lead_nurturing": False,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": "Default Response",
            "description": "Default for unmatched emails",
            "prompt": "Provide a polite, helpful response using available context and knowledge base.",
            "keywords": [],
            "auto_send": True,
            "priority": 1,
            "is_default": True,
            "is_inbound_lead": False,
            "enable_lead_qualification": False,
            "enable_lead_nurturing": False,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    # Delete existing intents for clean start
    await db.intents.delete_many({"user_id": user_id})
    
    # Insert new intents
    if intents_data:
        await db.intents.insert_many(intents_data)
        logger.info(f"✓ Created {len(intents_data)} intents")
        logger.info(f"  - Lead intents with qualification: 2")
        logger.info(f"  - Other intents: 4")
    
    # 3. Create Knowledge Base
    logger.info("\n--- Creating Knowledge Base ---")
    
    kb_data = [
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Company Overview",
            "content": "We are an AI-powered email assistant platform that helps businesses automate their email communication, manage leads, and schedule meetings efficiently.",
            "category": "Company Information",
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Product Features",
            "content": "Key features: AI-powered email responses, Lead qualification and nurturing, Calendar integration with meeting scheduling, Follow-up automation, Intent-based email classification, Knowledge base integration.",
            "category": "Product",
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Pricing Plans",
            "content": "Starter Plan: $99/month (up to 1000 emails), Professional Plan: $299/month (up to 5000 emails, includes lead qualification), Enterprise Plan: Custom pricing (unlimited emails, dedicated support, custom integrations).",
            "category": "Pricing",
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": "Lead Qualification Process",
            "content": "Our system automatically qualifies leads by asking smart questions, analyzing responses, and scoring leads 0-100. Leads scoring 60+ are qualified, <40 are disqualified, 40-60 need more information (max 3 attempts).",
            "category": "Product",
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    # Delete existing KB for clean start
    await db.knowledge_base.delete_many({"user_id": user_id})
    
    # Insert new KB
    if kb_data:
        await db.knowledge_base.insert_many(kb_data)
        logger.info(f"✓ Created {len(kb_data)} knowledge base entries")
    
    # 4. Create Qualification Criteria
    logger.info("\n--- Creating Qualification Criteria ---")
    
    criteria_id = str(uuid.uuid4())
    criteria = {
        "id": criteria_id,
        "user_id": user_id,
        "name": "Enterprise Lead Qualification",
        "description": "Qualify leads for enterprise sales",
        "is_enabled": True,
        "criteria_type": "score_based",
        "rules": [
            {
                "field": "company_size",
                "operator": "greater_than",
                "value": 50,
                "weight": 1.0
            },
            {
                "field": "industry",
                "operator": "in_list",
                "value": ["technology", "saas", "software", "tech"],
                "weight": 0.8
            }
        ],
        "questions": [
            {
                "question_id": str(uuid.uuid4()),
                "question_text": "What's your company size?",
                "question_key": "company_size",
                "context_keywords": ["company", "team", "employees", "size"],
                "expected_answer_type": "number",
                "qualifying_answers": None,
                "disqualifying_answers": ["less than 10", "just me", "solo"],
                "weight": 1.0,
                "is_required": True,
                "priority": 1,
                "max_asks": 2
            },
            {
                "question_id": str(uuid.uuid4()),
                "question_text": "What's your monthly budget for this solution?",
                "question_key": "budget",
                "context_keywords": ["budget", "spend", "invest", "cost"],
                "expected_answer_type": "text",
                "qualifying_answers": None,
                "disqualifying_answers": ["no budget", "free", "$0"],
                "weight": 1.0,
                "is_required": True,
                "priority": 2,
                "max_asks": 2
            },
            {
                "question_id": str(uuid.uuid4()),
                "question_text": "What industry are you in?",
                "question_key": "industry",
                "context_keywords": ["industry", "sector", "business", "company"],
                "expected_answer_type": "text",
                "qualifying_answers": ["tech", "technology", "saas", "software"],
                "disqualifying_answers": None,
                "weight": 0.8,
                "is_required": False,
                "priority": 3,
                "max_asks": 1
            }
        ],
        "min_qualification_score": 60,
        "max_exchanges": 3,
        "auto_disqualify_on_fail": True,
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Delete existing criteria
    await db.lead_qualification_criteria.delete_many({"user_id": user_id})
    
    # Insert new criteria
    await db.lead_qualification_criteria.insert_one(criteria)
    logger.info(f"✓ Created qualification criteria")
    logger.info(f"  - Rules: {len(criteria['rules'])}")
    logger.info(f"  - Questions: {len(criteria['questions'])}")
    logger.info(f"  - Min Score: {criteria['min_qualification_score']}")
    
    # 5. Create Nurturing Config
    logger.info("\n--- Creating Nurturing Config ---")
    
    nurturing_id = str(uuid.uuid4())
    nurturing_config = {
        "id": nurturing_id,
        "user_id": user_id,
        "name": "Standard Lead Nurturing",
        "description": "Default nurturing strategy for all leads",
        "is_enabled": True,
        "questions": [
            {
                "question_id": str(uuid.uuid4()),
                "question_text": "What's your company size?",
                "context_keywords": ["company", "team", "employees"],
                "priority": 1,
                "max_asks": 2,
                "is_required": True
            },
            {
                "question_id": str(uuid.uuid4()),
                "question_text": "What's your monthly budget for this solution?",
                "context_keywords": ["budget", "pricing", "cost"],
                "priority": 2,
                "max_asks": 2,
                "is_required": True
            },
            {
                "question_id": str(uuid.uuid4()),
                "question_text": "What industry are you in?",
                "context_keywords": ["industry", "sector", "business"],
                "priority": 3,
                "max_asks": 1,
                "is_required": False
            },
            {
                "question_id": str(uuid.uuid4()),
                "question_text": "When are you looking to implement a solution?",
                "context_keywords": ["when", "timeline", "timeframe"],
                "priority": 4,
                "max_asks": 1,
                "is_required": False
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
    
    # Delete existing config
    await db.lead_nurturing_config.delete_many({"user_id": user_id})
    
    # Insert new config
    await db.lead_nurturing_config.insert_one(nurturing_config)
    logger.info(f"✓ Created nurturing configuration")
    logger.info(f"  - Questions: {len(nurturing_config['questions'])}")
    logger.info(f"  - Per Email: {nurturing_config['questions_per_email']}")
    logger.info(f"  - Max Exchanges: {nurturing_config['max_exchanges']}")
    
    # 6. Link default configs to user
    logger.info("\n--- Linking Default Configs ---")
    
    await db.users.update_one(
        {"id": user_id},
        {"$set": {
            "default_qualification_criteria_id": criteria_id,
            "default_nurturing_config_id": nurturing_id,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    logger.info(f"✓ Linked default qualification criteria")
    logger.info(f"✓ Linked default nurturing config")
    
    # 7. Update user persona
    logger.info("\n--- Setting User Persona ---")
    
    persona = """I am a helpful AI assistant for an email automation platform. 
I help businesses automate their email communication, qualify leads, and schedule meetings.
I'm professional yet friendly, and I always use the knowledge base to provide accurate information.
When asking qualification questions, I integrate them naturally into the conversation."""
    
    await db.users.update_one(
        {"id": user_id},
        {"$set": {
            "persona": persona,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    logger.info(f"✓ Set user persona")
    
    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("SETUP COMPLETE")
    logger.info("=" * 80)
    logger.info("✓ Global settings enabled")
    logger.info(f"✓ {len(intents_data)} intents created (2 lead intents with qualification)")
    logger.info(f"✓ {len(kb_data)} knowledge base entries")
    logger.info(f"✓ 1 qualification criteria with {len(criteria['questions'])} questions")
    logger.info(f"✓ 1 nurturing config with {len(nurturing_config['questions'])} questions")
    logger.info("✓ Default configs linked")
    logger.info("✓ User persona set")
    logger.info("\n🎉 SYSTEM IS NOW READY FOR TESTING!")
    
    client.close()
    return True

if __name__ == "__main__":
    success = asyncio.run(setup_complete_system())
    sys.exit(0 if success else 1)
