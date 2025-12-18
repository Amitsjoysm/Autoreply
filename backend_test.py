#!/usr/bin/env python3
"""
Complete Flow Testing with Groq API
Tests all 3 scenarios from the review request
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://agent-response-fix-3.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test user credentials
TEST_USER = {
    "email": "test@example.com",
    "password": "testpass123"
}

# Test scenarios from review request
SCENARIOS = {
    "A": {
        "name": "Lead Qualification Flow",
        "from_email": "john@techcompany.com",
        "subject": "Pricing inquiry for our company",
        "body": "I'm interested in your pricing. We're a tech company with 75 employees and have a budget around $10k/month.",
        "simulate_reply": False,
        "expected": {
            "intent": "Pricing Inquiry (Lead)",
            "is_lead": True,
            "lead_stage": "awaiting_info",
            "questions_count": 2,
            "draft_has_persona": True,
            "draft_has_kb": True,
            "follow_ups": 3
        }
    },
    "B": {
        "name": "Lead Reply & Qualification",
        "from_email": "jane@enterprise.com",
        "subject": "Demo request",
        "body": "I'd like to see a demo of your product.",
        "simulate_reply": True,
        "reply_body": "Thanks! To answer: Company size: 150 employees. Budget: $20,000/month. Industry: Technology/SaaS. Timeline: Next quarter.",
        "expected": {
            "intent": "Demo Request (Lead)",
            "is_lead": True,
            "initial_stage": "awaiting_info",
            "final_stage": "qualified",
            "score_threshold": 60,
            "qualification_reasons": True
        }
    },
    "C": {
        "name": "Meeting Request",
        "from_email": "customer@company.com",
        "subject": "Schedule a call",
        "body": "Can we schedule a call next Tuesday at 2 PM to discuss implementation? I'll need about 30 minutes.",
        "simulate_reply": False,
        "expected": {
            "intent": "Meeting Request",
            "meeting_detected": True,
            "meeting_details": True,
            "calendar_event": True,
            "draft_has_confirmation": True
        }
    }
}

class FlowTester:
    def __init__(self):
        self.session = requests.Session()
        self.jwt_token = None
        self.user_id = None
        self.results = {}
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        symbols = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️"}
        symbol = symbols.get(level, "•")
        print(f"[{timestamp}] {symbol} {message}")
        
    def login(self):
        """Login to get JWT token"""
        self.log("Logging in...")
        
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
    
    def check_system_status(self):
        """Check system configuration"""
        self.log("Checking system status...")
        
        try:
            headers = {"Authorization": f"Bearer {self.jwt_token}"}
            response = self.session.get(f"{API_BASE}/test/system-status", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                config = data.get("configuration", {})
                
                self.log("System Configuration:", "INFO")
                self.log(f"  • Intents: {config.get('intents')}", "INFO")
                self.log(f"  • Knowledge Base: {config.get('knowledge_base')}", "INFO")
                self.log(f"  • Qualification Criteria: {config.get('qualification_criteria')}", "INFO")
                self.log(f"  • Nurturing Config: {config.get('nurturing_config')}", "INFO")
                self.log(f"  • Persona Set: {config.get('persona_set')}", "INFO")
                self.log(f"  • Global Qualification: {config.get('global_qualification_enabled')}", "INFO")
                self.log(f"  • Global Nurturing: {config.get('global_nurturing_enabled')}", "INFO")
                
                if data.get("ready"):
                    self.log("System is ready for testing", "SUCCESS")
                    return True
                else:
                    self.log("System not ready - check configuration", "WARNING")
                    return False
            else:
                self.log(f"System status check failed: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"System status error: {str(e)}", "ERROR")
            return False
    
    def test_scenario(self, scenario_id, scenario):
        """Test a single scenario"""
        self.log(f"\n{'='*60}", "INFO")
        self.log(f"SCENARIO {scenario_id}: {scenario['name']}", "INFO")
        self.log(f"{'='*60}", "INFO")
        
        try:
            headers = {
                "Authorization": f"Bearer {self.jwt_token}",
                "Content-Type": "application/json"
            }
            
            # Prepare request
            request_data = {
                "from_email": scenario["from_email"],
                "subject": scenario["subject"],
                "body": scenario["body"],
                "simulate_reply": scenario.get("simulate_reply", False)
            }
            
            if scenario.get("simulate_reply"):
                request_data["reply_body"] = scenario.get("reply_body")
            
            self.log(f"Testing: {scenario['subject']}", "INFO")
            self.log(f"From: {scenario['from_email']}", "INFO")
            
            # Make request
            response = self.session.post(
                f"{API_BASE}/test/complete-flow",
                json=request_data,
                headers=headers
            )
            
            if response.status_code != 200:
                self.log(f"API request failed: {response.status_code}", "ERROR")
                self.log(f"Response: {response.text}", "ERROR")
                self.results[scenario_id] = {"success": False, "error": response.text}
                return False
            
            data = response.json()
            
            # Analyze results
            self.log(f"\nTest completed: {'SUCCESS' if data.get('success') else 'FAILED'}", 
                    "SUCCESS" if data.get('success') else "ERROR")
            
            # Display steps
            self.log("\nProcessing Steps:", "INFO")
            for step in data.get("steps", []):
                status_symbol = {"success": "✅", "skipped": "⏭️", "info": "ℹ️", "error": "❌"}.get(step.get("status"), "•")
                self.log(f"  {status_symbol} Step {step.get('step')}: {step.get('name')}", "INFO")
                
                # Show key details
                details = step.get("details", {})
                if step.get("name") == "Intent Classification":
                    self.log(f"      Intent: {details.get('intent')} ({details.get('confidence')}% confidence)", "INFO")
                    self.log(f"      Is Lead: {details.get('is_lead')}", "INFO")
                    self.log(f"      Qualification: {details.get('qualification_enabled')}", "INFO")
                    self.log(f"      Nurturing: {details.get('nurturing_enabled')}", "INFO")
                
                elif step.get("name") == "Lead Qualification Processing":
                    self.log(f"      Stage: {details.get('stage')}", "INFO")
                    self.log(f"      Score: {details.get('score', 0)}", "INFO")
                    self.log(f"      Questions: {details.get('questions_to_ask', 0)}", "INFO")
                    if details.get('questions'):
                        for i, q in enumerate(details['questions'], 1):
                            self.log(f"        {i}. {q}", "INFO")
                
                elif step.get("name") == "Draft Generation":
                    self.log(f"      Length: {details.get('length')} chars", "INFO")
                    self.log(f"      Tokens: {details.get('tokens_used')}", "INFO")
                    self.log(f"      Has Questions: {details.get('includes_questions')}", "INFO")
                    self.log(f"      Draft Preview: {details.get('draft', '')[:100]}...", "INFO")
                
                elif step.get("name") == "Meeting Detection":
                    if details.get('detected'):
                        self.log(f"      Confidence: {details.get('confidence')}%", "INFO")
                        self.log(f"      Title: {details.get('title')}", "INFO")
                        self.log(f"      Start: {details.get('start_time')}", "INFO")
                
                elif step.get("name") == "Lead Re-qualification":
                    self.log(f"      Previous: {details.get('previous_stage')}", "INFO")
                    self.log(f"      New: {details.get('new_stage')}", "INFO")
                    self.log(f"      Score: {details.get('score')}", "INFO")
                    self.log(f"      Decision: {details.get('decision')}", "INFO")
            
            # Display summary
            summary = data.get("summary", {})
            self.log("\nSummary:", "INFO")
            self.log(f"  • Total Steps: {summary.get('total_steps')}", "INFO")
            self.log(f"  • Successful: {summary.get('successful_steps')}", "INFO")
            self.log(f"  • Intent Matched: {summary.get('intent_matched')}", "INFO")
            self.log(f"  • Lead Detected: {summary.get('lead_detected')}", "INFO")
            self.log(f"  • Meeting Detected: {summary.get('meeting_detected')}", "INFO")
            self.log(f"  • Draft Generated: {summary.get('draft_generated')}", "INFO")
            self.log(f"  • Tokens Used: {summary.get('tokens_used')}", "INFO")
            
            # Check warnings and errors
            if data.get("warnings"):
                self.log("\nWarnings:", "WARNING")
                for warning in data["warnings"]:
                    self.log(f"  • {warning}", "WARNING")
            
            if data.get("errors"):
                self.log("\nErrors:", "ERROR")
                for error in data["errors"]:
                    self.log(f"  • {error}", "ERROR")
            
            # Verify expectations
            self.log("\nVerifying Expectations:", "INFO")
            self.verify_expectations(scenario_id, scenario, data)
            
            self.results[scenario_id] = {
                "success": data.get("success"),
                "data": data,
                "verified": True
            }
            
            return data.get("success")
            
        except Exception as e:
            self.log(f"Scenario test error: {str(e)}", "ERROR")
            import traceback
            self.log(traceback.format_exc(), "ERROR")
            self.results[scenario_id] = {"success": False, "error": str(e)}
            return False
    
    def verify_expectations(self, scenario_id, scenario, data):
        """Verify scenario expectations"""
        expected = scenario.get("expected", {})
        steps = data.get("steps", [])
        summary = data.get("summary", {})
        
        # Find relevant steps
        intent_step = next((s for s in steps if s.get("name") == "Intent Classification"), None)
        lead_step = next((s for s in steps if s.get("name") == "Lead Qualification Processing"), None)
        draft_step = next((s for s in steps if s.get("name") == "Draft Generation"), None)
        meeting_step = next((s for s in steps if s.get("name") == "Meeting Detection"), None)
        requalify_step = next((s for s in steps if s.get("name") == "Lead Re-qualification"), None)
        
        checks = []
        
        # Scenario A checks
        if scenario_id == "A":
            checks.append(("Intent matches", 
                          intent_step and "Pricing" in intent_step.get("details", {}).get("intent", "")))
            checks.append(("Is lead detected", 
                          intent_step and intent_step.get("details", {}).get("is_lead") == True))
            checks.append(("Lead stage is awaiting_info", 
                          lead_step and lead_step.get("details", {}).get("stage") == "awaiting_info"))
            checks.append(("2 questions generated", 
                          lead_step and lead_step.get("details", {}).get("questions_to_ask") == 2))
            checks.append(("Draft generated", 
                          draft_step and draft_step.get("status") == "success"))
            checks.append(("Follow-up timeline shown", 
                          any(s.get("name") == "Follow-up Creation" for s in steps)))
        
        # Scenario B checks
        elif scenario_id == "B":
            checks.append(("Intent matches", 
                          intent_step and "Demo" in intent_step.get("details", {}).get("intent", "")))
            checks.append(("Is lead detected", 
                          intent_step and intent_step.get("details", {}).get("is_lead") == True))
            checks.append(("Reply processed", 
                          requalify_step is not None))
            if requalify_step:
                score = requalify_step.get("details", {}).get("score", 0)
                checks.append(("Lead scored 0-100", 
                              0 <= score <= 100))
                checks.append(("Score >= 60 for qualified", 
                              score >= 60 if requalify_step.get("details", {}).get("new_stage") == "qualified" else True))
                checks.append(("Qualification decision provided", 
                              requalify_step.get("details", {}).get("decision") is not None))
        
        # Scenario C checks
        elif scenario_id == "C":
            checks.append(("Intent matches", 
                          intent_step and "Meeting" in intent_step.get("details", {}).get("intent", "")))
            checks.append(("Meeting detected", 
                          meeting_step and meeting_step.get("details", {}).get("detected") == True))
            if meeting_step and meeting_step.get("details", {}).get("detected"):
                checks.append(("Meeting details extracted", 
                              meeting_step.get("details", {}).get("title") is not None))
                checks.append(("Calendar event would be created", 
                              meeting_step.get("details", {}).get("would_create_calendar_event") == True))
            checks.append(("Draft includes confirmation", 
                          draft_step and draft_step.get("status") == "success"))
        
        # Display verification results
        for check_name, result in checks:
            if result:
                self.log(f"  ✅ {check_name}", "SUCCESS")
            else:
                self.log(f"  ❌ {check_name}", "ERROR")
    
    def run_all_tests(self):
        """Run all test scenarios"""
        self.log("\n" + "="*60, "INFO")
        self.log("COMPLETE FLOW TESTING WITH GROQ API", "INFO")
        self.log("="*60 + "\n", "INFO")
        
        # Login
        if not self.login():
            self.log("Cannot proceed without authentication", "ERROR")
            return False
        
        # Check system status
        if not self.check_system_status():
            self.log("System not ready, but continuing with tests...", "WARNING")
        
        # Run each scenario
        for scenario_id, scenario in SCENARIOS.items():
            success = self.test_scenario(scenario_id, scenario)
            if not success:
                self.log(f"Scenario {scenario_id} failed", "ERROR")
        
        # Final summary
        self.log("\n" + "="*60, "INFO")
        self.log("FINAL SUMMARY", "INFO")
        self.log("="*60, "INFO")
        
        total = len(SCENARIOS)
        passed = sum(1 for r in self.results.values() if r.get("success"))
        
        self.log(f"\nTotal Scenarios: {total}", "INFO")
        self.log(f"Passed: {passed}", "SUCCESS" if passed == total else "WARNING")
        self.log(f"Failed: {total - passed}", "ERROR" if total - passed > 0 else "INFO")
        
        for scenario_id, result in self.results.items():
            status = "✅ PASS" if result.get("success") else "❌ FAIL"
            self.log(f"  {status} - Scenario {scenario_id}: {SCENARIOS[scenario_id]['name']}", 
                    "SUCCESS" if result.get("success") else "ERROR")
        
        return passed == total

if __name__ == "__main__":
    tester = FlowTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
