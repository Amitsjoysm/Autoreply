"""
Test Lead Qualification Flow with Test Session API
"""
import asyncio
import httpx
import json
from datetime import datetime

BASE_URL = "https://agentfix.preview.emergentagent.com"
TEST_EMAIL = "amits.joys@gmail.com"
TEST_PASSWORD = "ij@123"

async def login():
    """Login and get access token"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        if response.status_code == 200:
            data = response.json()
            return data.get('access_token')
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return None

async def send_test_message(token, session_id, from_email, subject, body, is_reply=False):
    """Send a test message via test session API"""
    async with httpx.AsyncClient(timeout=60.0) as client:
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "from_email": from_email,
            "to_email": TEST_EMAIL,
            "subject": subject,
            "body": body,
            "is_reply": is_reply
        }
        
        if session_id:
            payload["session_id"] = session_id
        
        response = await client.post(
            f"{BASE_URL}/api/test-session/send-message",
            json=payload,
            headers=headers
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None

def print_section(title):
    """Print a section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def print_lead_info(lead_info):
    """Print lead information"""
    if not lead_info:
        print("❌ Lead Info: None (ISSUE DETECTED)")
        return
    
    print(f"✅ Lead Info:")
    print(f"   - Lead ID: {lead_info.get('lead_id')}")
    print(f"   - Stage: {lead_info.get('stage')}")
    print(f"   - Score: {lead_info.get('score')}")
    print(f"   - Attempt: {lead_info.get('attempt')}")
    print(f"   - Nurturing Exchanges: {lead_info.get('nurturing_exchanges')}")
    print(f"   - Questions Asked: {lead_info.get('questions_asked')}")
    print(f"   - Qualification Checked: {lead_info.get('qualification_checked')}")

def print_agent_actions(actions):
    """Print agent actions"""
    if not actions:
        print("No agent actions recorded")
        return
    
    print(f"\n📋 Agent Actions ({len(actions)}):")
    for i, action in enumerate(actions, 1):
        print(f"\n   Action {i}: {action.get('action')}")
        details = action.get('details', {})
        for key, value in details.items():
            if key not in ['draft', 'questions_to_ask']:  # Skip long text
                print(f"      - {key}: {value}")

async def test_lead_qualification():
    """Test complete lead qualification flow"""
    print_section("LEAD QUALIFICATION FLOW TEST")
    
    # Login
    print("\n🔑 Logging in...")
    token = await login()
    if not token:
        print("❌ Login failed - cannot continue")
        return
    print("✅ Logged in successfully")
    
    # Test 1: Initial inquiry (should trigger lead detection)
    print_section("Step 1: Initial Pricing Inquiry")
    
    result1 = await send_test_message(
        token=token,
        session_id=None,
        from_email="john.smith@techcorp.com",
        subject="Interested in your product",
        body="Hi, I'm interested in your product. Can you tell me more about pricing and features? We're looking for a solution to automate our email responses."
    )
    
    if not result1:
        print("❌ Step 1 failed")
        return
    
    session_id = result1.get('session_id')
    print(f"✅ Session ID: {session_id}")
    print(f"✅ Messages: {len(result1.get('conversation_history', []))}")
    print(f"✅ Follow-ups Created: {len([f for f in result1.get('follow_ups', []) if f.get('status') == 'pending'])}")
    
    print_lead_info(result1.get('lead_info'))
    print_agent_actions(result1.get('agent_actions'))
    
    # Check draft for nurturing questions
    last_message = result1.get('conversation_history', [])[-1]
    draft = last_message.get('body', '')
    print(f"\n📧 Draft Preview (first 300 chars):")
    print(f"   {draft[:300]}...")
    
    # Test 2: Reply with qualification answers
    print_section("Step 2: Reply with Qualification Answers")
    
    result2 = await send_test_message(
        token=token,
        session_id=session_id,
        from_email="john.smith@techcorp.com",
        subject="Re: Interested in your product",
        body="""Thanks for the quick response! Here are the details:

Our company has about 75 employees, and we're in the Technology sector. 
Our monthly budget for this solution is around $10,000. 
We're looking to implement this within the next 2 months.

Can we schedule a call to discuss further?""",
        is_reply=True
    )
    
    if not result2:
        print("❌ Step 2 failed")
        return
    
    print(f"✅ Messages: {len(result2.get('conversation_history', []))}")
    print(f"✅ Follow-ups Cancelled: {len([f for f in result2.get('follow_ups', []) if f.get('status') == 'cancelled'])}")
    print(f"✅ Active Follow-ups: {len([f for f in result2.get('follow_ups', []) if f.get('status') == 'pending'])}")
    
    print_lead_info(result2.get('lead_info'))
    print_agent_actions(result2.get('agent_actions'))
    
    # Final Summary
    print_section("FINAL TEST SUMMARY")
    
    lead_info = result2.get('lead_info')
    
    if not lead_info:
        print("❌ FAILED: lead_info is None")
        print("\n🔍 Troubleshooting:")
        print("   1. Check if global_lead_nurturing_enabled is True")
        print("   2. Check if global_lead_qualification_enabled is True")
        print("   3. Check if intent has enable_lead_nurturing=True")
        print("   4. Check if intent has enable_lead_qualification=True")
        print("   5. Check backend logs for errors")
    elif lead_info.get('stage') == 'qualified' and lead_info.get('score', 0) >= 60:
        print("✅ SUCCESS: Lead properly qualified!")
        print(f"   - Stage: {lead_info.get('stage')}")
        print(f"   - Score: {lead_info.get('score')}")
        print(f"   - Attempt: {lead_info.get('attempt')}")
    elif lead_info.get('stage') == 'awaiting_info':
        print("⚠️  PARTIAL: Lead created but still awaiting info")
        print(f"   - Stage: {lead_info.get('stage')}")
        print(f"   - Score: {lead_info.get('score')}")
        print("   - Possible issue: Answer extraction not working")
    else:
        print("⚠️  UNEXPECTED RESULT")
        print(f"   - Stage: {lead_info.get('stage')}")
        print(f"   - Score: {lead_info.get('score')}")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    asyncio.run(test_lead_qualification())
