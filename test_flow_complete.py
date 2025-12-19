#!/usr/bin/env python3
"""
Test complete auto-reply flow with lead qualification
"""
import asyncio
import sys
sys.path.insert(0, 'backend')
from motor.motor_asyncio import AsyncIOMotorClient
import httpx

API_BASE = "http://localhost:8001/api"

async def test_complete_flow():
    """Test the complete auto-reply and lead qualification flow"""
    
    print("=" * 70)
    print("TESTING COMPLETE AUTO-REPLY WITH LEAD QUALIFICATION FLOW")
    print("=" * 70)
    
    # Step 1: Login
    print("\n📝 Step 1: Logging in as test user...")
    async with httpx.AsyncClient() as client:
        login_response = await client.post(
            f"{API_BASE}/auth/login",
            json={"email": "test@example.com", "password": "test123"}
        )
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.text}")
            return
        
        token = login_response.json()["access_token"]
        print(f"✅ Logged in successfully")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Step 2: Check system status
        print("\n📊 Step 2: Checking system status...")
        status_response = await client.get(
            f"{API_BASE}/test-flow/system-status",
            headers=headers
        )
        
        if status_response.status_code == 200:
            status = status_response.json()
            print(f"✅ System Status:")
            print(f"   - Intents: {status['intents_count']}")
            print(f"   - Knowledge Base: {status['kb_count']}")
            print(f"   - Qualification Criteria: {status['qualification_criteria_count']}")
            print(f"   - Nurturing Config: {status['nurturing_config_count']}")
            print(f"   - Global Qualification Enabled: {status['global_qualification_enabled']}")
            print(f"   - Global Nurturing Enabled: {status['global_nurturing_enabled']}")
        
        # Step 3: Test with lead qualification intent
        print("\n📧 Step 3: Testing auto-reply with lead qualification...")
        print("   Scenario: Pricing inquiry from potential lead")
        
        test_response = await client.post(
            f"{API_BASE}/test-flow/complete-flow",
            headers=headers,
            json={
                "scenario": "a",  # Lead qualification scenario
                "from_email": "john@techcompany.com",
                "subject": "Pricing Information",
                "body": "Hi, I'm interested in your product. Can you share pricing details?"
            }
        )
        
        if test_response.status_code == 200:
            result = test_response.json()
            print(f"\n✅ Test completed successfully!")
            print(f"\n📋 Results:")
            print(f"   - Intent: {result['intent_classification']['intent_name']} ({result['intent_classification']['confidence']}% confidence)")
            print(f"   - Is Lead: {result['intent_classification']['is_lead']}")
            
            if result.get('lead_processing'):
                lead = result['lead_processing']
                print(f"\n👤 Lead Processing:")
                print(f"   - Lead Created: {lead['lead_created']}")
                print(f"   - Lead Stage: {lead['stage']}")
                print(f"   - Lead Score: {lead['score']}")
                print(f"   - Questions to Ask: {lead['questions_count']}")
                if lead.get('questions'):
                    print(f"   - Questions:")
                    for q in lead['questions']:
                        print(f"      • {q}")
            else:
                print(f"\n⚠️  Lead processing: {result.get('lead_info', 'Not processed')}")
            
            if result.get('draft_generation'):
                draft = result['draft_generation']
                print(f"\n✉️  Draft Generated:")
                print(f"   - Token Count: {draft['tokens']}")
                print(f"   - Has Questions: {draft.get('has_nurturing_questions', False)}")
                print(f"\n   Draft Preview:")
                print(f"   {'-' * 60}")
                preview = draft['draft_content'][:400] + "..." if len(draft['draft_content']) > 400 else draft['draft_content']
                print(f"   {preview}")
                print(f"   {'-' * 60}")
            
            if result.get('follow_ups'):
                print(f"\n📅 Follow-ups: {len(result['follow_ups'])} scheduled")
        else:
            print(f"❌ Test failed: {test_response.text}")
        
        # Step 4: Check lead records
        print("\n\n📊 Step 4: Checking lead records in database...")
        mongo_client = AsyncIOMotorClient('mongodb://localhost:27017')
        db = mongo_client['ai_email_assistant']
        
        user = await db.users.find_one({'email': 'test@example.com'})
        leads = await db.inbound_leads.find({'user_id': user['id']}).to_list(length=10)
        
        print(f"   Total leads: {len(leads)}")
        for lead in leads:
            print(f"\n   Lead: {lead.get('email')}")
            print(f"   - Stage: {lead.get('stage')}")
            print(f"   - Score: {lead.get('qualification_score', 0)}")
            print(f"   - Attempt: {lead.get('qualification_attempt', 0)}")
        
        mongo_client.close()
        
    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(test_complete_flow())
