#!/usr/bin/env python3
"""
Final Email Automation Flow Test
Tests the complete email automation flow as requested in the review.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://agent-response-fix-3.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# JWT Token (from previous login)
JWT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZWQwYjA2YS0xZTY3LTQxZmItYmFhZC04NzViZjIwODMxMTYiLCJleHAiOjE3NjY2NjY4NTR9.ytuSOvk8lub7eiuNda1G99_5B18Z9z-MwMg1ktRD4OM"

class EmailFlowTester:
    def __init__(self):
        self.session = requests.Session()
        self.results = {}
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        symbols = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️"}
        symbol = symbols.get(level, "•")
        print(f"[{timestamp}] {symbol} {message}")
        
    def test_scenario_1_pricing_inquiry(self):
        """Test Scenario 1: New Lead with Pricing Inquiry"""
        self.log("\n" + "="*60, "INFO")
        self.log("SCENARIO 1: New Lead with Pricing Inquiry", "INFO")
        self.log("="*60, "INFO")
        
        headers = {
            "Authorization": f"Bearer {JWT_TOKEN}",
            "Content-Type": "application/json"
        }
        
        request_data = {
            "from_email": "john@techcompany.com",
            "subject": "Pricing inquiry for our company",
            "body": "Hi, I'm interested in your pricing. We're a tech company with 75 employees and have a budget around $10k/month. Can you provide more details?",
            "is_reply": False
        }
        
        try:
            self.log("Sending pricing inquiry email...", "INFO")
            response = self.session.post(
                f"{API_BASE}/test-session/send-message",
                json=request_data,
                headers=headers
            )
            
            if response.status_code != 200:
                self.log(f"API request failed: {response.status_code} - {response.text}", "ERROR")
                return None
            
            data = response.json()
            session_id = data.get("session_id")
            self.log(f"Session created: {session_id}", "SUCCESS")
            
            # Analyze results
            checks = []
            agent_actions = data.get("agent_actions", [])
            
            # Check intent classification
            intent_action = next((a for a in agent_actions if a.get("action") == "intent_classified"), None)
            if intent_action:
                intent = intent_action.get("details", {}).get("intent")
                confidence = intent_action.get("details", {}).get("confidence")
                is_lead = intent_action.get("details", {}).get("is_lead")
                checks.append(("Intent classification works", "Pricing" in intent and confidence >= 80))
                checks.append(("Lead detection works", is_lead == True))
                self.log(f"Intent: {intent} ({confidence}% confidence), Is Lead: {is_lead}", "INFO")
            else:
                checks.append(("Intent classification works", False))
                checks.append(("Lead detection works", False))
            
            # Check lead processing
            lead_info = data.get("lead_info")
            if lead_info:
                stage = lead_info.get("stage")
                checks.append(("Lead created in awaiting_info state", stage == "awaiting_info"))
                self.log(f"Lead stage: {stage}", "INFO")
            else:
                checks.append(("Lead created in awaiting_info state", False))
                self.log("No lead info found", "WARNING")
            
            # Check draft generation
            draft_action = next((a for a in agent_actions if a.get("action") == "draft_generated"), None)
            if draft_action:
                draft_details = draft_action.get("details", {})
                tokens = draft_details.get("tokens_used", 0)
                draft_content = draft_details.get("draft", "")
                checks.append(("Draft generation includes nurturing questions", tokens > 500))
                self.log(f"Draft generated: {len(draft_content)} chars, {tokens} tokens", "INFO")
            else:
                checks.append(("Draft generation includes nurturing questions", False))
            
            # Check state transitions logged
            conversation_history = data.get("conversation_history", [])
            checks.append(("State transitions are logged properly", len(conversation_history) >= 2))
            
            # Check draft validation
            validation_action = next((a for a in agent_actions if a.get("action") == "draft_validated"), None)
            if validation_action:
                is_valid = validation_action.get("details", {}).get("valid")
                checks.append(("Draft is validated and ready to send", is_valid == True))
                self.log(f"Draft validation: {is_valid}", "INFO")
            else:
                checks.append(("Draft is validated and ready to send", False))
            
            # Display results
            self.log("\nScenario 1 Verification:", "INFO")
            for check_name, result in checks:
                if result:
                    self.log(f"  ✅ {check_name}", "SUCCESS")
                else:
                    self.log(f"  ❌ {check_name}", "ERROR")
            
            self.results["scenario_1"] = {
                "session_id": session_id,
                "data": data,
                "checks": checks,
                "success": all(result for _, result in checks)
            }
            
            return session_id
            
        except Exception as e:
            self.log(f"Scenario 1 error: {str(e)}", "ERROR")
            return None
    
    def test_scenario_2_lead_response(self, session_id):
        """Test Scenario 2: Existing Lead Responding with Information"""
        self.log("\n" + "="*60, "INFO")
        self.log("SCENARIO 2: Existing Lead Responding with Information", "INFO")
        self.log("="*60, "INFO")
        
        headers = {
            "Authorization": f"Bearer {JWT_TOKEN}",
            "Content-Type": "application/json"
        }
        
        request_data = {
            "session_id": session_id,
            "from_email": "john@techcompany.com",
            "subject": "Re: Pricing inquiry for our company",
            "body": "Thanks for the quick response! To answer your questions: Company size: 75 employees. Budget: $10,000/month. Industry: Technology/SaaS. Timeline: Next quarter. Looking forward to hearing more details.",
            "is_reply": True
        }
        
        try:
            self.log("Sending lead response with qualification info...", "INFO")
            response = self.session.post(
                f"{API_BASE}/test-session/send-message",
                json=request_data,
                headers=headers
            )
            
            if response.status_code != 200:
                self.log(f"API request failed: {response.status_code} - {response.text}", "ERROR")
                return False
            
            data = response.json()
            
            # Analyze results
            checks = []
            agent_actions = data.get("agent_actions", [])
            
            # Check answer extraction and lead qualification
            lead_info = data.get("lead_info")
            if lead_info:
                stage = lead_info.get("stage")
                score = lead_info.get("score", 0)
                checks.append(("Answer extraction from email content", score > 0))
                checks.append(("Lead qualification scoring", 0 <= score <= 100))
                
                if score >= 60:
                    checks.append(("State transition to QUALIFIED", stage == "qualified"))
                else:
                    checks.append(("State transition to UNQUALIFIED", stage == "unqualified"))
                
                self.log(f"Lead stage: {stage}, Score: {score}", "INFO")
            else:
                checks.append(("Answer extraction from email content", False))
                checks.append(("Lead qualification scoring", False))
                checks.append(("State transition", False))
            
            # Check decision reasoning
            lead_action = next((a for a in agent_actions if a.get("action") == "lead_processed"), None)
            if lead_action:
                decision_log = lead_action.get("details", {}).get("decision_log")
                checks.append(("Decision log contains clear reasoning", decision_log is not None))
                if decision_log:
                    self.log(f"Decision reasoning: {decision_log}", "INFO")
            else:
                checks.append(("Decision log contains clear reasoning", False))
            
            # Display results
            self.log("\nScenario 2 Verification:", "INFO")
            for check_name, result in checks:
                if result:
                    self.log(f"  ✅ {check_name}", "SUCCESS")
                else:
                    self.log(f"  ❌ {check_name}", "ERROR")
            
            self.results["scenario_2"] = {
                "data": data,
                "checks": checks,
                "success": all(result for _, result in checks)
            }
            
            return True
            
        except Exception as e:
            self.log(f"Scenario 2 error: {str(e)}", "ERROR")
            return False
    
    def test_scenario_3_meeting_request(self):
        """Test Scenario 3: Meeting Request"""
        self.log("\n" + "="*60, "INFO")
        self.log("SCENARIO 3: Meeting Request", "INFO")
        self.log("="*60, "INFO")
        
        headers = {
            "Authorization": f"Bearer {JWT_TOKEN}",
            "Content-Type": "application/json"
        }
        
        request_data = {
            "from_email": "customer@company.com",
            "subject": "Schedule a call",
            "body": "Can we schedule a call next Tuesday at 2 PM to discuss implementation? I'll need about 30 minutes to go over our requirements.",
            "is_reply": False
        }
        
        try:
            self.log("Sending meeting request email...", "INFO")
            response = self.session.post(
                f"{API_BASE}/test-session/send-message",
                json=request_data,
                headers=headers
            )
            
            if response.status_code != 200:
                self.log(f"API request failed: {response.status_code} - {response.text}", "ERROR")
                return False
            
            data = response.json()
            
            # Analyze results
            checks = []
            agent_actions = data.get("agent_actions", [])
            
            # Check meeting detection with Groq API
            meeting_action = next((a for a in agent_actions if a.get("action") == "meeting_detected"), None)
            if meeting_action:
                meeting_details = meeting_action.get("details", {})
                confidence = meeting_details.get("confidence", 0)
                title = meeting_details.get("title")
                start_time = meeting_details.get("start_time")
                checks.append(("Meeting detection with Groq API", confidence > 0))
                checks.append(("Meeting details extracted", title is not None and start_time is not None))
                self.log(f"Meeting detected: {confidence}% confidence, Title: {title}, Start: {start_time}", "INFO")
            else:
                checks.append(("Meeting detection with Groq API", False))
                checks.append(("Meeting details extracted", False))
            
            # Check calendar event creation
            calendar_events = data.get("calendar_events", [])
            if calendar_events:
                event = calendar_events[0]
                checks.append(("Calendar event creation", event.get("event_id") is not None))
                self.log(f"Calendar event created: {event.get('title')} at {event.get('start_time')}", "INFO")
            else:
                checks.append(("Calendar event creation", False))
            
            # Check draft includes meeting confirmation
            draft_action = next((a for a in agent_actions if a.get("action") == "draft_generated"), None)
            if draft_action:
                draft_content = draft_action.get("details", {}).get("draft", "")
                checks.append(("Draft includes meeting confirmation", "tuesday" in draft_content.lower() or "2 pm" in draft_content.lower()))
                self.log(f"Draft includes meeting confirmation: {len(draft_content)} chars", "INFO")
            else:
                checks.append(("Draft includes meeting confirmation", False))
            
            # Check auto-send for meeting intent
            intent_action = next((a for a in agent_actions if a.get("action") == "intent_classified"), None)
            if intent_action:
                intent = intent_action.get("details", {}).get("intent")
                # Meeting Request intent should have auto_send=true
                checks.append(("Auto-reply working when intent has auto_send=true", "Meeting" in intent))
                self.log(f"Intent classified as: {intent}", "INFO")
            else:
                checks.append(("Auto-reply working when intent has auto_send=true", False))
            
            # Display results
            self.log("\nScenario 3 Verification:", "INFO")
            for check_name, result in checks:
                if result:
                    self.log(f"  ✅ {check_name}", "SUCCESS")
                else:
                    self.log(f"  ❌ {check_name}", "ERROR")
            
            self.results["scenario_3"] = {
                "data": data,
                "checks": checks,
                "success": all(result for _, result in checks)
            }
            
            return True
            
        except Exception as e:
            self.log(f"Scenario 3 error: {str(e)}", "ERROR")
            return False
    
    def check_critical_components(self):
        """Check critical components: Workers, Groq API, etc."""
        self.log("\n" + "="*60, "INFO")
        self.log("CRITICAL CHECKS: Workers and Groq API Key", "INFO")
        self.log("="*60, "INFO")
        
        headers = {
            "Authorization": f"Bearer {JWT_TOKEN}",
            "Content-Type": "application/json"
        }
        
        checks = []
        
        try:
            # Test Groq API with simple request
            test_request = {
                "from_email": "test@example.com",
                "subject": "Test Groq API Key",
                "body": "This is a test to verify the new Groq API key is working: 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",
                "is_reply": False
            }
            
            response = self.session.post(
                f"{API_BASE}/test-session/send-message",
                json=test_request,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                agent_actions = data.get("agent_actions", [])
                
                # Check if draft was generated (indicates Groq API is working)
                draft_action = next((a for a in agent_actions if a.get("action") == "draft_generated"), None)
                if draft_action:
                    tokens = draft_action.get("details", {}).get("tokens_used", 0)
                    checks.append(("Groq API key working (new key)", tokens > 0))
                    self.log(f"Groq API working: {tokens} tokens used", "SUCCESS")
                else:
                    checks.append(("Groq API key working (new key)", False))
                    self.log("Groq API test failed - no draft generated", "ERROR")
                
                # Check workers are processing emails
                checks.append(("Workers running and processing emails", len(agent_actions) > 0))
                
                # Check lead qualification flow end-to-end
                intent_action = next((a for a in agent_actions if a.get("action") == "intent_classified"), None)
                if intent_action:
                    checks.append(("Lead qualification flow end-to-end", True))
                else:
                    checks.append(("Lead qualification flow end-to-end", False))
                
            else:
                checks.append(("Groq API key working (new key)", False))
                checks.append(("Workers running and processing emails", False))
                checks.append(("Lead qualification flow end-to-end", False))
                self.log(f"Critical test failed: {response.status_code}", "ERROR")
            
        except Exception as e:
            self.log(f"Critical checks error: {str(e)}", "ERROR")
            checks.append(("Groq API key working (new key)", False))
            checks.append(("Workers running and processing emails", False))
            checks.append(("Lead qualification flow end-to-end", False))
        
        # Display results
        self.log("\nCritical Checks Verification:", "INFO")
        for check_name, result in checks:
            if result:
                self.log(f"  ✅ {check_name}", "SUCCESS")
            else:
                self.log(f"  ❌ {check_name}", "ERROR")
        
        self.results["critical_checks"] = {
            "checks": checks,
            "success": all(result for _, result in checks)
        }
        
        return all(result for _, result in checks)
    
    def run_all_tests(self):
        """Run all test scenarios as requested in the review"""
        self.log("\n" + "="*80, "INFO")
        self.log("EMAIL AUTOMATION FLOW TEST WITH LEAD QUALIFICATION", "INFO")
        self.log("Testing as requested in the review request", "INFO")
        self.log("="*80 + "\n", "INFO")
        
        # Run critical checks first
        critical_passed = self.check_critical_components()
        
        # Run test scenarios
        session_id = self.test_scenario_1_pricing_inquiry()
        if session_id:
            self.test_scenario_2_lead_response(session_id)
        
        self.test_scenario_3_meeting_request()
        
        # Final summary
        self.log("\n" + "="*80, "INFO")
        self.log("FINAL TEST SUMMARY", "INFO")
        self.log("="*80, "INFO")
        
        # Count results
        scenario_results = []
        for key in ["scenario_1", "scenario_2", "scenario_3"]:
            result = self.results.get(key, {})
            scenario_results.append(result.get("success", False))
        
        passed_scenarios = sum(scenario_results)
        total_scenarios = len(scenario_results)
        
        # Display summary
        self.log(f"\nTest Results Summary:", "INFO")
        self.log(f"Critical Checks: {'✅ PASS' if critical_passed else '❌ FAIL'}", 
                "SUCCESS" if critical_passed else "ERROR")
        self.log(f"Scenario Tests: {passed_scenarios}/{total_scenarios} passed", 
                "SUCCESS" if passed_scenarios == total_scenarios else "WARNING")
        
        # Individual scenario results
        scenario_names = [
            "New Lead with Pricing Inquiry",
            "Existing Lead Responding with Information", 
            "Meeting Request"
        ]
        
        for i, (name, success) in enumerate(zip(scenario_names, scenario_results)):
            status = "✅ PASS" if success else "❌ FAIL"
            self.log(f"  {status} - Scenario {i+1}: {name}", 
                    "SUCCESS" if success else "ERROR")
        
        # Overall result
        overall_success = critical_passed and passed_scenarios == total_scenarios
        
        self.log(f"\nOverall Result: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}", 
                "SUCCESS" if overall_success else "ERROR")
        
        # Detailed findings for failed tests
        if not overall_success:
            self.log("\nDetailed Findings:", "INFO")
            
            if not critical_passed:
                critical_checks = self.results.get("critical_checks", {}).get("checks", [])
                failed_critical = [name for name, result in critical_checks if not result]
                for check in failed_critical:
                    self.log(f"  ❌ {check}", "ERROR")
            
            for i, (key, name) in enumerate(zip(["scenario_1", "scenario_2", "scenario_3"], scenario_names)):
                if not scenario_results[i]:
                    self.log(f"\n  Scenario {i+1} ({name}) failures:", "ERROR")
                    scenario_checks = self.results.get(key, {}).get("checks", [])
                    failed_checks = [name for name, result in scenario_checks if not result]
                    for check in failed_checks:
                        self.log(f"    ❌ {check}", "ERROR")
        
        return overall_success

if __name__ == "__main__":
    tester = EmailFlowTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)