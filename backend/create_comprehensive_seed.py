#!/usr/bin/env python3
"""
Comprehensive seed data creator for AI Email Assistant
Creates realistic intents and knowledge base entries for testing
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import uuid
from dotenv import load_dotenv

load_dotenv()

async def create_seed_data():
    client = AsyncIOMotorClient(os.getenv('MONGO_URL'))
    db_name = os.getenv('DB_NAME', 'email_assistant_db')
    db = client[db_name]
    
    print("=" * 60)
    print("Creating Comprehensive Seed Data")
    print("=" * 60)
    
    # Get user
    user = await db.users.find_one({'email': 'amits.joys@gmail.com'})
    
    if not user:
        print("✗ User not found. Please register first.")
        client.close()
        return
    
    user_id = user['id']
    print(f"\n✓ User found: {user['email']} (ID: {user_id})")
    
    # Clear existing data
    print("\nClearing existing intents and knowledge base...")
    await db.intents.delete_many({'user_id': user_id})
    await db.knowledge_base.delete_many({'user_id': user_id})
    print("✓ Cleared existing data")
    
    # Create Intents
    print("\nCreating Intents...")
    intents = [
        {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'name': 'Meeting Request',
            'description': 'Handle incoming meeting requests and schedule meetings',
            'prompt': 'You are scheduling a meeting. Check calendar availability, propose times, and confirm details. Be professional and accommodating.',
            'keywords': ['meeting', 'schedule', 'call', 'zoom', 'teams', 'appointment', 'discuss', 'chat', 'video call'],
            'auto_send': True,
            'priority': 100,
            'is_default': False,
            'is_active': True,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        },
        {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'name': 'Job Application',
            'description': 'Respond to job applications and recruitment emails',
            'prompt': 'You are responding to a job-related email. Be professional, express interest if appropriate, and provide relevant information about your experience. Maintain a formal tone.',
            'keywords': ['job', 'position', 'hiring', 'interview', 'application', 'resume', 'cv', 'career', 'opportunity', 'recruitment'],
            'auto_send': False,
            'priority': 90,
            'is_default': False,
            'is_active': True,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        },
        {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'name': 'Customer Support',
            'description': 'Handle customer inquiries and support requests',
            'prompt': 'You are providing customer support. Be helpful, empathetic, and solution-oriented. Address the customer\'s concerns clearly and offer assistance.',
            'keywords': ['help', 'support', 'issue', 'problem', 'question', 'inquiry', 'assist', 'trouble', 'error', 'bug'],
            'auto_send': True,
            'priority': 80,
            'is_default': False,
            'is_active': True,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        },
        {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'name': 'Partnership Inquiry',
            'description': 'Respond to partnership and collaboration proposals',
            'prompt': 'You are responding to a partnership inquiry. Be professional and open to collaboration. Express interest in learning more and suggest next steps.',
            'keywords': ['partnership', 'collaborate', 'collaboration', 'business', 'proposal', 'joint', 'alliance', 'cooperation'],
            'auto_send': False,
            'priority': 70,
            'is_default': False,
            'is_active': True,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        },
        {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'name': 'General Inquiry',
            'description': 'Handle general questions and information requests',
            'prompt': 'You are responding to a general inquiry. Be helpful, provide relevant information, and maintain a friendly yet professional tone.',
            'keywords': ['information', 'details', 'inquiry', 'question', 'wondering', 'curious', 'clarification'],
            'auto_send': True,
            'priority': 60,
            'is_default': False,
            'is_active': True,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        },
        {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'name': 'Default Response',
            'description': 'Default intent for emails that don\'t match any specific category',
            'prompt': 'You are responding to an email that doesn\'t fit a specific category. Use the knowledge base and persona to craft an appropriate, helpful response. Be professional and courteous. Stay strictly within the bounds of the provided knowledge base - do not make assumptions or provide information not in the knowledge base.',
            'keywords': [],
            'auto_send': True,
            'priority': 0,
            'is_default': True,
            'is_active': True,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
    ]
    
    result = await db.intents.insert_many(intents)
    print(f"✓ Created {len(result.inserted_ids)} intents:")
    for intent in intents:
        default_tag = " (DEFAULT)" if intent['is_default'] else ""
        auto_tag = " [AUTO-SEND]" if intent['auto_send'] else ""
        print(f"  - {intent['name']}{default_tag}{auto_tag} (Priority: {intent['priority']})")
    
    # Create Knowledge Base
    print("\nCreating Knowledge Base...")
    knowledge_base = [
        {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'title': 'Company Overview',
            'content': 'TechVision Solutions is a leading AI and software development company founded in 2020. We specialize in building intelligent automation solutions for businesses. Our core services include AI integration, custom software development, and cloud infrastructure management. We have successfully delivered 50+ projects across industries including healthcare, finance, and e-commerce.',
            'category': 'Company Info',
            'tags': ['company', 'about', 'overview', 'services'],
            'is_active': True,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        },
        {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'title': 'Services and Pricing',
            'content': 'We offer three main service tiers: Starter ($5,000-$15,000) for MVPs and prototypes, Growth ($15,000-$50,000) for full-featured applications, and Enterprise ($50,000+) for complex, scalable solutions. All projects include free maintenance for the first 3 months. We provide AI integration, web/mobile app development, cloud deployment, and technical consulting.',
            'category': 'Services',
            'tags': ['pricing', 'services', 'packages', 'cost'],
            'is_active': True,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        },
        {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'title': 'Meeting Availability',
            'content': 'I am generally available for meetings on Mondays, Wednesdays, and Fridays between 10 AM and 4 PM EST. For urgent matters, I can accommodate meetings on Tuesdays and Thursdays as well. Please provide at least 24 hours notice for meeting requests. I prefer Zoom or Google Meet for virtual meetings.',
            'category': 'Scheduling',
            'tags': ['meetings', 'availability', 'schedule', 'calendar'],
            'is_active': True,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        },
        {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'title': 'Technical Expertise',
            'content': 'Our technical stack includes: Frontend (React, Vue.js, Next.js), Backend (Python/FastAPI, Node.js), AI/ML (OpenAI GPT, LangChain, TensorFlow), Databases (PostgreSQL, MongoDB, Redis), Cloud (AWS, Google Cloud, Azure), and DevOps (Docker, Kubernetes, CI/CD). We follow SOLID principles and best practices for all development.',
            'category': 'Technical',
            'tags': ['technology', 'stack', 'expertise', 'skills'],
            'is_active': True,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        },
        {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'title': 'Project Timeline',
            'content': 'Typical project timelines: MVP development takes 2-4 weeks, full applications take 6-12 weeks, and enterprise solutions take 3-6 months. We follow an agile development process with bi-weekly sprints and regular client demos. We deliver milestone-based updates and maintain transparent communication throughout the project lifecycle.',
            'category': 'Process',
            'tags': ['timeline', 'duration', 'process', 'agile'],
            'is_active': True,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        },
        {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'title': 'Contact and Support',
            'content': 'For inquiries, contact us at contact@techvisionsolutions.com or call +1 (555) 123-4567. Our support team is available Monday-Friday, 9 AM - 6 PM EST. Emergency support is available 24/7 for enterprise clients. We typically respond to emails within 4 business hours.',
            'category': 'Contact',
            'tags': ['contact', 'support', 'communication', 'phone', 'email'],
            'is_active': True,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        },
        {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'title': 'Client Success Stories',
            'content': 'Recent projects include: HealthTrack AI (healthcare automation platform serving 10,000+ users), FinanceFlow (automated accounting system for SMBs), and ShopSmart (AI-powered e-commerce recommendation engine). Our clients report an average of 40% efficiency improvement and 99.9% system uptime.',
            'category': 'Case Studies',
            'tags': ['projects', 'clients', 'portfolio', 'success'],
            'is_active': True,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        },
        {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'title': 'Partnership Opportunities',
            'content': 'We are open to strategic partnerships with agencies, consultants, and technology providers. Partnership benefits include: 20% referral commission, co-branding opportunities, priority support, and joint marketing initiatives. We have existing partnerships with 15+ agencies across North America and Europe.',
            'category': 'Partnerships',
            'tags': ['partnership', 'collaboration', 'referral', 'alliance'],
            'is_active': True,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
    ]
    
    result = await db.knowledge_base.insert_many(knowledge_base)
    print(f"✓ Created {len(result.inserted_ids)} knowledge base entries:")
    for kb in knowledge_base:
        print(f"  - {kb['title']} ({kb['category']})")
    
    # Update user with persona
    print("\nUpdating user persona...")
    await db.users.update_one(
        {'id': user_id},
        {'$set': {
            'persona': 'I am Amit, the founder and lead developer at TechVision Solutions. I am passionate about AI and building innovative solutions that help businesses automate and scale. I value clear communication, quality code, and delivering exceptional results. My communication style is professional yet friendly, and I always strive to understand client needs before proposing solutions.'
        }}
    )
    print("✓ Updated user persona")
    
    print("\n" + "=" * 60)
    print("✓ Seed data creation complete!")
    print("=" * 60)
    print(f"\nSummary:")
    print(f"  - {len(intents)} intents created (including 1 default)")
    print(f"  - {len(knowledge_base)} knowledge base entries created")
    print(f"  - User persona updated")
    print(f"\nDefault Intent: 'Default Response' will handle unmatched emails")
    print(f"Auto-send enabled for: Meeting Request, Customer Support, General Inquiry, Default Response")
    print("\n✓ Ready for testing!")
    
    client.close()

if __name__ == '__main__':
    asyncio.run(create_seed_data())
