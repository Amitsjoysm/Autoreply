#!/usr/bin/env python3
"""
Test Session API Testing - Complete Email Automation Flow
Tests the enhanced lead qualification service with Parlant.io architecture
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
BACKEND_URL = "http://localhost:8001"
API_BASE = f"{BACKEND_URL}/api"

# Test user from review request
TEST_USER = {
    "email": "test@example.com",
    "password": "test123"
}

USER_ID = "88f2e56b-add4-401a-b46e-919343f1c64f"

class TestSessionTester:
    def __init__(self):
        self.session = requests.Session()
        self.jwt_token = None
        self.user_id = None
        self.session_id = None
        self.results = {}
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        symbols = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️", "DEBUG": "🔍"}
        symbol = symbols.get(level, "•")
        print(f"[{timestamp}] {symbol} {message}")
    
    def login(self):
        """Login to get JWT token"""
        self.log("Logging in as test@example.com...")
        
        try:
            response = self.session.post(
                f"{API_BASE}/auth/login",
                json=TEST_USER,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.jwt_token = data.get("access_token")
                self.user_id = data.get("user", {}).get("id")
                self.log(f"Login successful - User ID: {self.user_id}", "SUCCESS")
                return True
            else:
                self.log(f"Login failed: {response.status_code} - {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Login error: {str(e)}", "ERROR")
            return False
    
    def check_user_settings(self):
        """Check user settings for lead qualification and nurturing"""
        self.log("Checking user settings...")
        
        try:
            headers = {"Authorization": f"Bearer {self.jwt_token}"}
            response = self.session.get(f"{API_BASE}/auth/me", headers=headers)
            
            if response.status_code == 200:
                user = response.json()
                
                global_qual = user.get("global_lead_qualification_enabled", False)
                global_nurt = user.get("global_lead_nurturing_enabled", False)
                
                self.log(f"  • Global Lead Qualification: {global_qual}", "INFO")
                self.log(f"  • Global Lead Nurturing: {global_nurt}", "INFO")
                
                if not global_qual or not global_nurt:
                    self.log("WARNING: Lead processing not fully enabled", "WARNING")
                    return False
                
                self.log("User settings configured correctly", "SUCCESS")
                return True
            else:
                self.log(f"Failed to get user settings: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Settings check error: {str(e)}", "ERROR")
            return False
    
    def send_message(self, from_email: str, subject: str, body: str, is_reply: bool = False) -> Optional[Dict]:
        """Send a message in test session"""
        
        try:
            headers = {
                "Authorization": f"Bearer {self.jwt_token}",
                "Content-Type": "application/json"
            }
            
            request_data = {
                "from_email": from_email,
                "subject": subject,
                "body": body,
                "is_reply": is_reply
            }
            
            # Include session_id if continuing conversation
            if self.session_id:
                request_data["session_id"] = self.session_id
            
            self.log(f"Sending message: {subject[:50]}...", "INFO")
            
            response = self.session.post(
                f"{API_BASE}/test-session/send-message",
                json=request_data,
                headers=headers
            )
            
            if response.status_code != 200:
                self.log(f"API request failed: {response.status_code}", "ERROR")
                self.log(f"Response: {response.text}", "ERROR")
                return None
            
            data = response.json()
            
            # Store session_id for next message
            if not self.session_id:
                self.session_id = data.get("session_id")
                self.log(f"Session created: {self.session_id}", "SUCCESS")
            
            return data
            
        except Exception as e:
            self.log(f"Send message error: {str(e)}", "ERROR")
            import traceback
            self.log(traceback.format_exc(), "DEBUG")
            return None
    
    def verify_scenario_1(self, response: Dict) -> bool:
        """
        Verify Scenario 1: Auto-Reply with Lead Qualification
        
        Expected:
        - Intent: "Pricing Inquiry (Lead)"
        - is_lead: true
        - Lead stage: "awaiting_info"
        - Lead has qualification_attempt: 1
        - Draft includes nurturing questions
        - Auto-reply generated
        """
        self.log("\n" + "="*60, "INFO")
        self.log("SCENARIO 1: Auto-Reply with Lead Qualification", "INFO")
        self.log("="*60, "INFO")
        
        checks = []
        
        # Check agent actions
        actions = response.get("agent_actions", [])
        
        # 1. Intent classification
        intent_action = next((a for a in actions if a['action'] == 'intent_classified'), None)
        if intent_action:
            intent_name = intent_action['details'].get('intent', '')
            is_lead = intent_action['details'].get('is_lead', False)
            
            checks.append(("Intent contains 'Pricing'", "Pricing" in intent_name))
            checks.append(("is_lead = true", is_lead == True))
            
            self.log(f"  Intent: {intent_name}", "INFO")
            self.log(f"  Is Lead: {is_lead}", "INFO")
        else:
            checks.append(("Intent classified", False))
        
        # 2. Lead processing
        lead_action = next((a for a in actions if a['action'] == 'lead_processed'), None)
        if lead_action:
            lead_details = lead_action['details']
            stage = lead_details.get('stage', '')
            attempt = lead_details.get('attempt', 0)
            questions = lead_details.get('questions_to_ask', 0)
            
            checks.append(("Lead stage = 'awaiting_info'", stage == 'awaiting_info'))
            checks.append(("Qualification attempt = 1", attempt == 1))
            checks.append(("Questions generated (>0)", questions > 0))
            
            self.log(f"  Lead Stage: {stage}", "INFO")
            self.log(f"  Attempt: {attempt}", "INFO")
            self.log(f"  Questions: {questions}", "INFO")
        else:
            checks.append(("Lead processed", False))
        
        # 3. Lead info
        lead_info = response.get("lead_info")
        if lead_info:
            checks.append(("Lead record created", True))
            self.log(f"  Lead ID: {lead_info.get('lead_id')}", "INFO")
            self.log(f"  Score: {lead_info.get('score', 0)}", "INFO")
        else:
            checks.append(("Lead record created", False))
            self.log("  ❌ CRITICAL: Lead info is None - lead processing not working", "ERROR")
        
        # 4. Draft generation
        draft_action = next((a for a in actions if a['action'] == 'draft_generated'), None)
        if draft_action:
            draft = draft_action['details'].get('draft', '')
            tokens = draft_action['details'].get('tokens_used', 0)
            includes_questions = draft_action['details'].get('includes_questions', False)
            
            checks.append(("Draft generated", len(draft) > 0))
            checks.append(("Draft includes questions", includes_questions))
            checks.append(("Tokens used > 0", tokens > 0))
            
            self.log(f"  Draft length: {len(draft)} chars", "INFO")
            self.log(f"  Tokens: {tokens}", "INFO")
            self.log(f"  Includes questions: {includes_questions}", "INFO")
        else:
            checks.append(("Draft generated", False))
        
        # 5. Follow-ups
        follow_ups = response.get("follow_ups", [])
        pending_followups = [f for f in follow_ups if f.get('status') == 'pending']
        
        checks.append(("Follow-ups created", len(pending_followups) > 0))
        self.log(f"  Follow-ups: {len(pending_followups)} pending", "INFO")
        
        # Display results
        self.log("\nVerification Results:", "INFO")
        passed = 0
        for check_name, result in checks:
            if result:
                self.log(f"  ✅ {check_name}", "SUCCESS")
                passed += 1
            else:
                self.log(f"  ❌ {check_name}", "ERROR")
        
        self.log(f"\nPassed: {passed}/{len(checks)}", "SUCCESS" if passed == len(checks) else "WARNING")
        
        return passed == len(checks)
    
    def verify_scenario_2(self, response: Dict) -> bool:
        """
        Verify Scenario 2: Lead Reply with Qualification
        
        Expected:
        - Existing lead found
        - Answers extracted
        - Lead score calculated (should be > 60)
        - Lead stage updated to "qualified"
        - Lead record in inbound_leads
        """
        self.log("\n" + "="*60, "INFO")
        self.log("SCENARIO 2: Lead Reply with Qualification", "INFO")
        self.log("="*60, "INFO")
        
        checks = []
        
        # Check lead info
        lead_info = response.get("lead_info")
        if lead_info:
            stage = lead_info.get('stage', '')
            score = lead_info.get('score', 0)
            attempt = lead_info.get('attempt', 0)
            
            checks.append(("Lead found", True))
            checks.append(("Lead stage = 'qualified'", stage == 'qualified'))
            checks.append(("Lead score >= 60", score >= 60))
            checks.append(("Attempt incremented", attempt >= 1))
            
            self.log(f"  Lead Stage: {stage}", "INFO")
            self.log(f"  Score: {score}", "INFO")
            self.log(f"  Attempt: {attempt}", "INFO")
            
            if stage != 'qualified':
                self.log(f"  ⚠️  Expected 'qualified' but got '{stage}'", "WARNING")
            
            if score < 60:
                self.log(f"  ⚠️  Expected score >= 60 but got {score}", "WARNING")
                self.log(f"  This indicates answer extraction may not be working", "WARNING")
        else:
            checks.append(("Lead found", False))
            self.log("  ❌ CRITICAL: Lead info is None", "ERROR")
        
        # Check agent actions
        actions = response.get("agent_actions", [])
        lead_action = next((a for a in actions if a['action'] == 'lead_processed'), None)
        
        if lead_action:
            checks.append(("Lead processing occurred", True))
        else:
            checks.append(("Lead processing occurred", False))
        
        # Check follow-ups cancelled
        cancelled_action = next((a for a in actions if a['action'] == 'followups_cancelled'), None)
        if cancelled_action:
            count = cancelled_action['details'].get('count', 0)
            checks.append(("Old follow-ups cancelled", count > 0))
            self.log(f"  Cancelled follow-ups: {count}", "INFO")
        else:
            checks.append(("Old follow-ups cancelled", False))
        
        # Display results
        self.log("\nVerification Results:", "INFO")
        passed = 0
        for check_name, result in checks:
            if result:
                self.log(f"  ✅ {check_name}", "SUCCESS")
                passed += 1
            else:
                self.log(f"  ❌ {check_name}", "ERROR")
        
        self.log(f"\nPassed: {passed}/{len(checks)}", "SUCCESS" if passed == len(checks) else "WARNING")
        
        return passed == len(checks)
    
    def verify_scenario_3(self, response: Dict) -> bool:
        """
        Verify Scenario 3: Meeting Request (Non-Lead)
        
        Expected:
        - Intent classified correctly (not a lead)
        - Meeting detected
        - Calendar event created (if confidence >= 0.8)
        - No lead processing
        """
        self.log("\n" + "="*60, "INFO")
        self.log("SCENARIO 3: Meeting Request (Non-Lead)", "INFO")
        self.log("="*60, "INFO")
        
        checks = []
        
        # Check agent actions
        actions = response.get("agent_actions", [])
        
        # 1. Intent classification
        intent_action = next((a for a in actions if a['action'] == 'intent_classified'), None)
        if intent_action:
            intent_name = intent_action['details'].get('intent', '')
            is_lead = intent_action['details'].get('is_lead', False)
            
            checks.append(("Intent contains 'Meeting'", "Meeting" in intent_name))
            checks.append(("is_lead = false", is_lead == False))
            
            self.log(f"  Intent: {intent_name}", "INFO")
            self.log(f"  Is Lead: {is_lead}", "INFO")
        else:
            checks.append(("Intent classified", False))
        
        # 2. Meeting detection
        meeting_action = next((a for a in actions if a['action'] == 'meeting_detected'), None)
        if meeting_action:
            detected = meeting_action['details'].get('detected', False)
            confidence = meeting_action['details'].get('confidence', 0)
            
            checks.append(("Meeting detected", detected))
            checks.append(("Confidence > 0", confidence > 0))
            
            self.log(f"  Meeting Detected: {detected}", "INFO")
            self.log(f"  Confidence: {confidence}%", "INFO")
        else:
            checks.append(("Meeting detected", False))
        
        # 3. Calendar event
        calendar_events = response.get("calendar_events", [])
        if len(calendar_events) > 0:
            event = calendar_events[0]
            checks.append(("Calendar event created", True))
            self.log(f"  Event ID: {event.get('event_id')}", "INFO")
            self.log(f"  Title: {event.get('title')}", "INFO")
            self.log(f"  Start: {event.get('start_time')}", "INFO")
        else:
            checks.append(("Calendar event created", False))
            self.log("  No calendar event created (confidence may be < 0.5)", "WARNING")
        
        # 4. No lead processing
        lead_info = response.get("lead_info")
        checks.append(("No lead processing", lead_info is None))
        
        if lead_info:
            self.log(f"  ⚠️  Lead processing occurred when it shouldn't", "WARNING")
        
        # Display results
        self.log("\nVerification Results:", "INFO")
        passed = 0
        for check_name, result in checks:
            if result:
                self.log(f"  ✅ {check_name}", "SUCCESS")
                passed += 1
            else:
                self.log(f"  ❌ {check_name}", "ERROR")
        
        self.log(f"\nPassed: {passed}/{len(checks)}", "SUCCESS" if passed == len(checks) else "WARNING")
        
        return passed == len(checks)
    
    def cleanup_session(self):
        """Delete test session"""
        if not self.session_id:
            return
        
        self.log(f"\nCleaning up session {self.session_id}...", "INFO")
        
        try:
            headers = {"Authorization": f"Bearer {self.jwt_token}"}
            response = self.session.delete(
                f"{API_BASE}/test-session/session/{self.session_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                self.log("Session deleted successfully", "SUCCESS")
            else:
                self.log(f"Failed to delete session: {response.status_code}", "WARNING")
                
        except Exception as e:
            self.log(f"Cleanup error: {str(e)}", "WARNING")
    
    def run_all_tests(self):
        """Run all test scenarios"""
        self.log("\n" + "="*60, "INFO")
        self.log("TEST SESSION API - COMPLETE EMAIL AUTOMATION FLOW", "INFO")
        self.log("="*60 + "\n", "INFO")
        
        # Login
        if not self.login():
            self.log("Cannot proceed without authentication", "ERROR")
            return False
        
        # Check settings
        if not self.check_user_settings():
            self.log("User settings not configured correctly", "WARNING")
        
        # Scenario 1: Auto-Reply with Lead Qualification
        self.log("\n" + "="*60, "INFO")
        self.log("Starting Scenario 1: Pricing Inquiry (Lead)", "INFO")
        self.log("="*60, "INFO")
        
        response1 = self.send_message(
            from_email="john@techcompany.com",
            subject="Pricing Information",
            body="Hi, I'm interested in your product. Can you share pricing details?"
        )
        
        if response1:
            scenario1_passed = self.verify_scenario_1(response1)
            self.results['scenario_1'] = scenario1_passed
        else:
            self.log("Scenario 1 failed - no response", "ERROR")
            self.results['scenario_1'] = False
        
        # Scenario 2: Lead Reply with Qualification
        self.log("\n" + "="*60, "INFO")
        self.log("Starting Scenario 2: Lead Reply with Answers", "INFO")
        self.log("="*60, "INFO")
        
        response2 = self.send_message(
            from_email="john@techcompany.com",
            subject="Re: Pricing Information",
            body="Our company has 75 employees, budget is $10k/month, and we're in Technology industry",
            is_reply=True
        )
        
        if response2:
            scenario2_passed = self.verify_scenario_2(response2)
            self.results['scenario_2'] = scenario2_passed
        else:
            self.log("Scenario 2 failed - no response", "ERROR")
            self.results['scenario_2'] = False
        
        # Scenario 3: Meeting Request (Non-Lead)
        # Start new session for this
        self.session_id = None
        
        self.log("\n" + "="*60, "INFO")
        self.log("Starting Scenario 3: Meeting Request", "INFO")
        self.log("="*60, "INFO")
        
        response3 = self.send_message(
            from_email="customer@company.com",
            subject="Schedule a Call",
            body="Can we schedule a call next Tuesday at 2 PM?"
        )
        
        if response3:
            scenario3_passed = self.verify_scenario_3(response3)
            self.results['scenario_3'] = scenario3_passed
        else:
            self.log("Scenario 3 failed - no response", "ERROR")
            self.results['scenario_3'] = False
        
        # Cleanup
        self.cleanup_session()
        
        # Final summary
        self.log("\n" + "="*60, "INFO")
        self.log("FINAL SUMMARY", "INFO")
        self.log("="*60, "INFO")
        
        total = len(self.results)
        passed = sum(1 for r in self.results.values() if r)
        
        self.log(f"\nTotal Scenarios: {total}", "INFO")
        self.log(f"Passed: {passed}", "SUCCESS" if passed == total else "WARNING")
        self.log(f"Failed: {total - passed}", "ERROR" if total - passed > 0 else "INFO")
        
        for scenario, result in self.results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"  {status} - {scenario}", "SUCCESS" if result else "ERROR")
        
        return passed == total

if __name__ == "__main__":
    tester = TestSessionTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
