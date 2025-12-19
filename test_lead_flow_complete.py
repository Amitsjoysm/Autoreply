"""
Complete Lead Qualification Flow Test
Tests the full flow from initial email to lead qualification
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from motor.motor_asyncio import AsyncIOMotorClient
import httpx
import json

BACKEND_URL = "http://localhost:8001"

async def test_complete_flow():
    """Test complete lead qualification flow"""
    
    print("=" * 80)
    print("COMPLETE LEAD QUALIFICATION FLOW TEST")
    print("=" * 80)
    
    # Step 1: Login
    print("\n1️⃣  Logging in...")
    async with httpx.AsyncClient() as client:
        login_response = await client.post(
            f"{BACKEND_URL}/api/auth/login",
            json={
                "email": "amits.joys@gmail.com",
                "password": "Test@123"
            }
        )
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.text}")
            return
        
        token = login_response.json()['access_token']
        headers = {"Authorization": f"Bearer {token}"}
        print(f"✅ Logged in successfully")
        
        # Step 2: Check configuration
        print("\n2️⃣  Checking configuration...")
        
        # Connect to MongoDB directly
        mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        mongo_client = AsyncIOMotorClient(mongo_url)
        db = mongo_client['email_assistant_db']
        
        user = await db.users.find_one({"email": "amits.joys@gmail.com"})
        if not user:
            print("❌ User not found")
            return
        
        print(f"   User ID: {user['id']}")
        print(f"   Global Lead Nurturing: {user.get('global_lead_nurturing_enabled', False)}")
        print(f"   Global Lead Qualification: {user.get('global_lead_qualification_enabled', False)}")
        print(f"   Nurturing Config ID: {user.get('default_nurturing_config_id', 'Not set')}")
        print(f"   Qualification Criteria ID: {user.get('default_qualification_criteria_id', 'Not set')}")
        
        # Check intents
        intents = await db.intents.find({"user_id": user['id'], "is_lead": True}).to_list(length=10)
        print(f"\n   Lead Intents: {len(intents)}")
        for intent in intents:
            print(f"     - {intent['name']}: nurturing={intent.get('enable_lead_nurturing', False)}, qualification={intent.get('enable_lead_qualification', False)}")
        
        # Step 3: Send initial pricing inquiry (lead detection)
        print("\n3️⃣  Sending initial pricing inquiry...")
        
        initial_response = await client.post(
            f"{BACKEND_URL}/api/test-session/send-message",
            headers=headers,
            json={
                "from_email": "john@techcompany.com",
                "subject": "Pricing Inquiry",
                "body": "Hi, I'm interested in your email automation solution. Could you share your pricing details?",
                "is_reply": False
            }
        )
        
        if initial_response.status_code != 200:
            print(f"❌ Initial request failed: {initial_response.text}")
            return
        
        initial_data = initial_response.json()
        session_id = initial_data['session_id']
        
        print(f"✅ Session created: {session_id}")
        print(f"   Conversation History: {len(initial_data['conversation_history'])} messages")
        print(f"   Follow-ups Created: {len(initial_data['follow_ups'])}")
        
        # Check lead_info
        if initial_data['lead_info']:
            lead_info = initial_data['lead_info']
            print(f"\n   ✅ LEAD INFO PRESENT:")
            print(f"      Lead ID: {lead_info.get('lead_id')}")
            print(f"      Stage: {lead_info.get('stage')}")
            print(f"      Score: {lead_info.get('score')}")
            print(f"      Attempt: {lead_info.get('attempt')}")
            print(f"      Questions Asked: {lead_info.get('questions_asked', 0)}")
        else:
            print(f"\n   ❌ LEAD INFO IS NULL")
            print(f"      This is the main issue - lead processing not working")
            
            # Debug: Check agent actions
            print(f"\n   Debug - Agent Actions:")
            for action in initial_data.get('agent_actions', []):
                print(f"      - {action['action']}: {json.dumps(action['details'], indent=10)}")
        
        # Check draft content
        draft_action = next((a for a in initial_data['agent_actions'] if a['action'] == 'draft_generated'), None)
        if draft_action:
            draft = draft_action['details']['draft']
            print(f"\n   Draft Preview (first 300 chars):")
            print(f"   {draft[:300]}...")
        
        # Step 4: Send reply with qualification answers
        print("\n4️⃣  Sending reply with qualification answers...")
        
        reply_response = await client.post(
            f"{BACKEND_URL}/api/test-session/send-message",
            headers=headers,
            json={
                "session_id": session_id,
                "from_email": "john@techcompany.com",
                "subject": "Re: Pricing Inquiry",
                "body": "Thanks for your response! We're a technology company with 75 employees. Our monthly budget for this solution is around $10,000. We're in the software industry.",
                "is_reply": True
            }
        )
        
        if reply_response.status_code != 200:
            print(f"❌ Reply request failed: {reply_response.text}")
            return
        
        reply_data = reply_response.json()
        
        print(f"✅ Reply processed")
        print(f"   Conversation History: {len(reply_data['conversation_history'])} messages")
        
        # Check updated lead_info
        if reply_data['lead_info']:
            lead_info = reply_data['lead_info']
            print(f"\n   ✅ UPDATED LEAD INFO:")
            print(f"      Lead ID: {lead_info.get('lead_id')}")
            print(f"      Stage: {lead_info.get('stage')}")
            print(f"      Score: {lead_info.get('score')}")
            print(f"      Attempt: {lead_info.get('attempt')}")
            
            # Check if score improved
            if lead_info.get('score', 0) >= 60:
                print(f"      ✅ LEAD QUALIFIED (score >= 60)")
            else:
                print(f"      ⚠️  Lead still not qualified (score < 60)")
        else:
            print(f"\n   ❌ LEAD INFO STILL NULL after reply")
        
        # Step 5: Verify lead in database
        print("\n5️⃣  Verifying lead in database...")
        
        leads = await db.inbound_leads.find({"user_id": user['id']}).to_list(length=10)
        print(f"   Total leads in DB: {len(leads)}")
        
        for lead in leads:
            print(f"\n   Lead: {lead['lead_email']}")
            print(f"      ID: {lead['id']}")
            print(f"      Stage: {lead.get('stage', 'N/A')}")
            print(f"      Score: {lead.get('qualification_score', 0)}")
            print(f"      Attempt: {lead.get('qualification_attempt', 0)}")
            print(f"      Created: {lead.get('created_at', 'N/A')[:19]}")
        
        print("\n" + "=" * 80)
        print("TEST COMPLETE")
        print("=" * 80)
        
        mongo_client.close()

if __name__ == "__main__":
    asyncio.run(test_complete_flow())
