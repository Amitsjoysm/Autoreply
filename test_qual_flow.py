"""
Direct Test of Lead Qualification for amits.joys@gmail.com
Uses Test Session API which is verified working
"""
import requests
import json

BASE_URL = "https://agentfix.preview.emergentagent.com/api"

def test_lead_qualification():
    print("=" * 80)
    print("🧪 TESTING LEAD QUALIFICATION FOR amits.joys@gmail.com")
    print("=" * 80)
    
    # Step 1: Login
    print("\n📝 Step 1: Logging in...")
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": "amits.joys@gmail.com",
            "password": "ij@123"
        }
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(login_response.text)
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Logged in successfully")
    
    # Step 2: Send test email using test-session API
    print("\n📧 Step 2: Sending test pricing inquiry email...")
    
    test_email = {
        "from_email": "john.doe@testcompany.com",
        "subject": "Pricing Information Request",
        "body": "Hi, I'm interested in learning about your pricing plans. Can you share more details?",
        "received_at": "2026-01-12T10:00:00Z"
    }
    
    session_response = requests.post(
        f"{BASE_URL}/test-session/send-message",
        headers=headers,
        json=test_email
    )
    
    if session_response.status_code != 200:
        print(f"❌ API Error: {session_response.status_code}")
        print(f"Response: {session_response.text}")
        return
    
    result = session_response.json()
    print("✅ Email processed successfully")
    
    # Analyze the response
    print("\n" + "=" * 80)
    print("📊 LEAD QUALIFICATION ANALYSIS")
    print("=" * 80)
    
    # Check intent classification
    agent_actions = result.get("agent_actions", [])
    intent_action = next((a for a in agent_actions if a["action"] == "intent_classified"), None)
    
    if intent_action:
        print(f"\n✓ Intent Classification:")
        print(f"  Intent: {intent_action['details'].get('intent_name')}")
        print(f"  Confidence: {intent_action['details'].get('confidence', 0):.1%}")
    
    # Check lead processing
    lead_action = next((a for a in agent_actions if a["action"] == "lead_processed"), None)
    
    if lead_action:
        print(f"\n✓ Lead Processing:")
        lead_details = lead_action['details']
        print(f"  Stage: {lead_details.get('stage')}")
        print(f"  Score: {lead_details.get('score')}")
        print(f"  Qualification Attempt: {lead_details.get('qualification_attempt')}")
        
        questions = lead_details.get('questions_to_ask', [])
        print(f"  Questions to ask: {len(questions)}")
        
        if questions:
            print(f"\n  📋 Nurturing Questions Generated:")
            for i, q in enumerate(questions, 1):
                print(f"    {i}. {q.get('question_text')}")
        else:
            print(f"\n  ⚠️  WARNING: No questions generated!")
    else:
        print(f"\n❌ No lead processing occurred!")
        print("This indicates lead qualification is NOT working.")
    
    # Check draft
    draft = result.get("draft")
    if draft:
        print(f"\n✓ Draft Generated:")
        print(f"  Length: {len(draft)} characters")
        print(f"\n  Draft Content:")
        print("  " + "-" * 76)
        draft_lines = draft.split('\n')
        for line in draft_lines[:15]:  # Show first 15 lines
            print(f"  {line}")
        if len(draft_lines) > 15:
            print(f"  ... ({len(draft_lines) - 15} more lines)")
        print("  " + "-" * 76)
        
        # Check if questions are in the draft
        if lead_action and lead_action['details'].get('questions_to_ask'):
            print(f"\n  🔍 Checking if questions are in draft...")
            questions_in_draft = 0
            for q in lead_action['details']['questions_to_ask']:
                q_text = q.get('question_text', '')
                # Check for partial matches (AI might rephrase)
                key_words = q_text.lower().split()[:3]  # First 3 words
                if any(word in draft.lower() for word in key_words if len(word) > 3):
                    questions_in_draft += 1
            
            print(f"  Questions found in draft: {questions_in_draft}/{len(lead_action['details']['questions_to_ask'])}")
            
            if questions_in_draft > 0:
                print(f"  ✅ Questions are integrated in the draft!")
            else:
                print(f"  ⚠️  Questions may not be properly integrated!")
    
    # Check lead info
    lead_info = result.get("lead_info")
    if lead_info:
        print(f"\n✓ Lead Record:")
        print(f"  Stage: {lead_info.get('stage')}")
        print(f"  Score: {lead_info.get('score')}")
        print(f"  Qualification Attempt: {lead_info.get('qualification_attempt')}")
    else:
        print(f"\n⚠️  No lead record created in inbound_leads!")
        print("This is expected for first email - lead is in 'awaiting_info' stage")
    
    # Check follow-ups
    follow_ups = result.get("follow_ups", [])
    pending_followups = [f for f in follow_ups if f.get("status") == "pending"]
    
    print(f"\n✓ Follow-ups:")
    print(f"  Pending: {len(pending_followups)}")
    
    # Summary
    print("\n" + "=" * 80)
    print("📋 SUMMARY")
    print("=" * 80)
    
    has_intent = intent_action is not None
    has_lead_processing = lead_action is not None
    has_questions = lead_action and len(lead_action['details'].get('questions_to_ask', [])) > 0
    has_draft = draft is not None
    
    print(f"\n✓ Intent Classification: {'✅ YES' if has_intent else '❌ NO'}")
    print(f"✓ Lead Processing: {'✅ YES' if has_lead_processing else '❌ NO'}")
    print(f"✓ Questions Generated: {'✅ YES' if has_questions else '❌ NO'}")
    print(f"✓ Draft Generated: {'✅ YES' if has_draft else '❌ NO'}")
    
    if has_questions:
        print(f"\n✅ LEAD QUALIFICATION IS WORKING!")
        print(f"   The system is asking questions before adding to Inbound Leads.")
    else:
        print(f"\n❌ LEAD QUALIFICATION NOT WORKING!")
        print(f"   Questions are NOT being generated.")
        print(f"\n🔍 Possible Issues:")
        print(f"   1. Global lead nurturing/qualification might be disabled")
        print(f"   2. Intent might not have enable_lead_qualification=true")
        print(f"   3. Intent might not have nurturing_config_id set")
        print(f"   4. Nurturing config might not have questions")
    
    print("\n" + "=" * 80)
    
    return result

if __name__ == "__main__":
    test_lead_qualification()
