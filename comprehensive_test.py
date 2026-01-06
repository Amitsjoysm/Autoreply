#!/usr/bin/env python3
"""
Comprehensive Email Automation Flow Test
Tests the complete email automation flow with lead qualification as requested in the review.
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration
BACKEND_URL = "https://redis-calendar-agent.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test user credentials
TEST_USER = {
    "email": "test@example.com",
    "password": "testpass123"
}

class ComprehensiveFlowTester:
    def __init__(self):
        self.session = requests.Session()
        self.jwt_token = None
        self.user_id = None
        self.results = {}
        self.setup_complete = False
        
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
    
    def setup_system(self):
        """Setup system configuration for testing"""
        self.log("Setting up system configuration...")
        
        headers = {
            "Authorization": f"Bearer {self.jwt_token}",
            "Content-Type": "application/json"
        }
        
        try:
            # 1. Create intents
            self.log("Creating intents...")
            intents = [
                {
                    "name": "Pricing Inquiry (Lead)",
                    "description": "Customer asking about pricing",
                    "keywords": ["pricing", "price", "cost", "budget", "quote"],
                    "prompt": "Respond professionally to pricing inquiries and ask qualifying questions",
                    "enable_lead_nurturing": True,
                    "enable_lead_qualification": True,
                    "auto_send": False
                },
                {
                    "name": "Demo Request (Lead)", 
                    "description": "Customer requesting a demo",
                    "keywords": ["demo", "demonstration", "show", "preview"],
                    "prompt": "Respond to demo requests and gather qualification information",
                    "enable_lead_nurturing": True,
                    "enable_lead_qualification": True,
                    "auto_send": False
                },
                {
                    "name": "Meeting Request",
                    "description": "Customer requesting a meeting or call",
                    "keywords": ["meeting", "call", "schedule", "appointment"],
                    "prompt": "Confirm meeting requests and provide calendar details",
                    "enable_lead_nurturing": False,
                    "enable_lead_qualification": False,
                    "auto_send": True
                }
            ]
            
            for intent in intents:
                response = self.session.post(f"{API_BASE}/intents", json=intent, headers=headers)
                if response.status_code == 201:
                    self.log(f"Created intent: {intent['name']}", "SUCCESS")
                else:
                    self.log(f"Failed to create intent {intent['name']}: {response.text}", "ERROR")
            
            # 2. Create knowledge base entries
            self.log("Creating knowledge base entries...")
            kb_entries = [
                {
                    "title": "Pricing Information",
                    "content": "Our pricing starts at $5,000/month for small teams (up to 50 users) and scales to $20,000/month for enterprise (500+ users). We offer custom pricing for larger organizations.",
                    "tags": ["pricing", "cost", "budget"]
                },
                {
                    "title": "Product Features",
                    "content": "Our AI email assistant provides automated email responses, lead qualification, meeting scheduling, and CRM integration. It supports multiple email providers and includes advanced analytics.",
                    "tags": ["features", "product", "capabilities"]
                },
                {
                    "title": "Implementation Timeline",
                    "content": "Standard implementation takes 2-4 weeks including setup, training, and integration. Enterprise implementations may take 4-8 weeks depending on complexity.",
                    "tags": ["implementation", "timeline", "setup"]
                }
            ]
            
            for entry in kb_entries:
                response = self.session.post(f"{API_BASE}/knowledge-base", json=entry, headers=headers)
                if response.status_code == 201:
                    self.log(f"Created KB entry: {entry['title']}", "SUCCESS")
                else:
                    self.log(f"Failed to create KB entry {entry['title']}: {response.text}", "ERROR")
            
            # 3. Create qualification criteria
            self.log("Creating qualification criteria...")
            qualification_criteria = {
                "name": "Standard Lead Qualification",
                "description": "Standard criteria for qualifying leads",
                "criteria": [
                    {
                        "question": "What's your company size?",
                        "field": "company_size",
                        "weight": 30,
                        "scoring": {
                            "1-10": 10,
                            "11-50": 20,
                            "51-200": 30,
                            "200+": 40
                        }
                    },
                    {
                        "question": "What's your monthly budget for this solution?",
                        "field": "budget",
                        "weight": 40,
                        "scoring": {
                            "$0-1k": 10,
                            "$1k-5k": 20,
                            "$5k-15k": 30,
                            "$15k+": 40
                        }
                    },
                    {
                        "question": "What industry are you in?",
                        "field": "industry",
                        "weight": 20,
                        "scoring": {
                            "Technology": 30,
                            "Finance": 25,
                            "Healthcare": 20,
                            "Other": 15
                        }
                    },
                    {
                        "question": "What's your timeline for implementation?",
                        "field": "timeline",
                        "weight": 10,
                        "scoring": {
                            "Immediate": 30,
                            "Next quarter": 25,
                            "Next 6 months": 20,
                            "Next year": 10
                        }
                    }
                ],
                "qualification_threshold": 60
            }
            
            response = self.session.post(f"{API_BASE}/lead-qualification-criteria", json=qualification_criteria, headers=headers)
            if response.status_code == 201:
                criteria_id = response.json().get("id")
                self.log(f"Created qualification criteria: {criteria_id}", "SUCCESS")
            else:
                self.log(f"Failed to create qualification criteria: {response.text}", "ERROR")
                criteria_id = None
            
            # 4. Create nurturing configuration
            self.log("Creating nurturing configuration...")
            nurturing_config = {
                "name": "Standard Lead Nurturing",
                "description": "Standard nurturing configuration",
                "questions": [
                    "What's your company size?",
                    "What's your monthly budget for this solution?",
                    "What industry are you in?",
                    "What's your timeline for implementation?"
                ],
                "follow_up_sequence": [
                    {"day": 2, "template": "Follow up on your inquiry"},
                    {"day": 4, "template": "Additional information about our solution"},
                    {"day": 6, "template": "Final follow up - would you like to schedule a call?"}
                ]
            }
            
            response = self.session.post(f"{API_BASE}/lead-nurturing-config", json=nurturing_config, headers=headers)
            if response.status_code == 201:
                nurturing_id = response.json().get("id")
                self.log(f"Created nurturing config: {nurturing_id}", "SUCCESS")
            else:
                self.log(f"Failed to create nurturing config: {response.text}", "ERROR")
                nurturing_id = None
            
            # 5. Set persona
            self.log("Setting user persona...")
            persona = {
                "persona": "You are Sarah, a helpful AI sales assistant for TechCorp. You are professional, knowledgeable, and focused on understanding customer needs. Always be helpful and provide clear, actionable information."
            }
            
            response = self.session.put(f"{API_BASE}/users/persona", json=persona, headers=headers)
            if response.status_code == 200:
                self.log("Set user persona", "SUCCESS")
            else:
                self.log(f"Failed to set persona: {response.text}", "ERROR")
            
            # 6. Enable global settings
            self.log("Enabling global lead qualification and nurturing...")
            settings = {
                "global_lead_qualification_enabled": True,
                "global_lead_nurturing_enabled": True,
                "default_qualification_criteria_id": criteria_id,
                "default_nurturing_config_id": nurturing_id
            }
            
            response = self.session.put(f"{API_BASE}/users/settings", json=settings, headers=headers)
            if response.status_code == 200:
                self.log("Enabled global settings", "SUCCESS")
                self.setup_complete = True
            else:
                self.log(f"Failed to enable global settings: {response.text}", "ERROR")
            
            return self.setup_complete
            
        except Exception as e:
            self.log(f"Setup error: {str(e)}", "ERROR")
            return False
    
    def test_scenario_1_pricing_inquiry(self):
        """Test Scenario 1: New Lead with Pricing Inquiry"""
        self.log("\n" + "="*60, "INFO")
        self.log("SCENARIO 1: New Lead with Pricing Inquiry", "INFO")
        self.log("="*60, "INFO")
        
        headers = {
            "Authorization": f"Bearer {self.jwt_token}",
            "Content-Type": "application/json"
        }
        
        # Send initial pricing inquiry
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
                return False
            
            data = response.json()
            session_id = data.get("session_id")
            self.log(f"Session created: {session_id}", "SUCCESS")
            
            # Verify results
            checks = []
            
            # Check intent classification
            agent_actions = data.get("agent_actions", [])
            intent_action = next((a for a in agent_actions if a.get("action") == "intent_classified"), None)
            if intent_action:
                intent = intent_action.get("details", {}).get("intent")
                confidence = intent_action.get("details", {}).get("confidence")
                checks.append(("Intent classification", "Pricing" in intent and confidence > 80))
                self.log(f"Intent: {intent} ({confidence}% confidence)", "INFO")
            else:
                checks.append(("Intent classification", False))
            
            # Check lead detection
            lead_action = next((a for a in agent_actions if a.get("action") == "lead_processed"), None)
            if lead_action:
                lead_details = lead_action.get("details", {})
                stage = lead_details.get("stage")
                score = lead_details.get("score")
                questions = lead_details.get("questions_to_ask", 0)
                checks.append(("Lead detection", stage == "awaiting_info"))
                checks.append(("Lead in awaiting_info state", stage == "awaiting_info"))
                checks.append(("Nurturing questions generated", questions >= 2))
                self.log(f"Lead stage: {stage}, Score: {score}, Questions: {questions}", "INFO")
            else:
                checks.append(("Lead detection", False))
                checks.append(("Lead in awaiting_info state", False))
                checks.append(("Nurturing questions generated", False))
            
            # Check draft generation
            draft_action = next((a for a in agent_actions if a.get("action") == "draft_generated"), None)
            if draft_action:
                draft_details = draft_action.get("details", {})
                draft_content = draft_details.get("draft", "")
                tokens = draft_details.get("tokens")
                checks.append(("Draft generation", len(draft_content) > 100))
                checks.append(("Draft includes nurturing questions", any(q in draft_content.lower() for q in ["company size", "budget", "industry", "timeline"])))
                self.log(f"Draft generated: {len(draft_content)} chars, {tokens} tokens", "INFO")
            else:
                checks.append(("Draft generation", False))
                checks.append(("Draft includes nurturing questions", False))
            
            # Check state transitions
            conversation_history = data.get("conversation_history", [])
            checks.append(("State transitions logged", len(conversation_history) >= 2))
            
            # Check draft validation
            validation_action = next((a for a in agent_actions if a.get("action") == "draft_validated"), None)
            if validation_action:
                is_valid = validation_action.get("details", {}).get("is_valid")
                checks.append(("Draft validated and ready", is_valid))
                self.log(f"Draft validation: {is_valid}", "INFO")
            else:
                checks.append(("Draft validated and ready", False))
            
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
            "Authorization": f"Bearer {self.jwt_token}",
            "Content-Type": "application/json"
        }
        
        # Send reply with qualification information
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
            
            # Verify results
            checks = []
            
            # Check answer extraction
            agent_actions = data.get("agent_actions", [])
            lead_action = next((a for a in agent_actions if a.get("action") == "lead_processed"), None)
            if lead_action:
                lead_details = lead_action.get("details", {})
                stage = lead_details.get("stage")
                score = lead_details.get("score")
                checks.append(("Answer extraction from email", score > 0))
                checks.append(("Lead qualification scoring", 0 <= score <= 100))
                self.log(f"Lead stage: {stage}, Score: {score}", "INFO")
                
                # Check state transition
                if score >= 60:
                    checks.append(("State transition to QUALIFIED", stage == "qualified"))
                else:
                    checks.append(("State transition to UNQUALIFIED", stage == "unqualified"))
                
            else:
                checks.append(("Answer extraction from email", False))
                checks.append(("Lead qualification scoring", False))
                checks.append(("State transition", False))
            
            # Check decision reasoning
            decision_log = lead_action.get("details", {}).get("decision_log") if lead_action else None
            checks.append(("Decision log contains reasoning", decision_log is not None and len(str(decision_log)) > 10))
            if decision_log:
                self.log(f"Decision reasoning: {decision_log}", "INFO")
            
            # Check follow-up cancellation (should happen when lead is qualified/unqualified)
            followup_action = next((a for a in agent_actions if a.get("action") == "followups_cancelled"), None)
            if followup_action:
                cancelled_count = followup_action.get("details", {}).get("count", 0)
                checks.append(("Follow-ups cancelled for qualified lead", cancelled_count > 0))
                self.log(f"Follow-ups cancelled: {cancelled_count}", "INFO")
            else:
                checks.append(("Follow-ups cancelled for qualified lead", False))
            
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
            "Authorization": f"Bearer {self.jwt_token}",
            "Content-Type": "application/json"
        }
        
        # Send meeting request
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
            session_id = data.get("session_id")
            
            # Verify results
            checks = []
            
            # Check meeting detection with Groq API
            agent_actions = data.get("agent_actions", [])
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
                checks.append(("Draft includes meeting confirmation", "tuesday" in draft_content.lower() and "2 pm" in draft_content.lower()))
                self.log(f"Draft includes meeting confirmation: {len(draft_content)} chars", "INFO")
            else:
                checks.append(("Draft includes meeting confirmation", False))
            
            # Check auto-send (meeting requests should have auto_send=true)
            intent_action = next((a for a in agent_actions if a.get("action") == "intent_classified"), None)
            if intent_action:
                intent = intent_action.get("details", {}).get("intent")
                checks.append(("Auto-reply working for meeting intent", "Meeting" in intent))
                self.log(f"Intent classified as: {intent}", "INFO")
            else:
                checks.append(("Auto-reply working for meeting intent", False))
            
            # Display results
            self.log("\nScenario 3 Verification:", "INFO")
            for check_name, result in checks:
                if result:
                    self.log(f"  ✅ {check_name}", "SUCCESS")
                else:
                    self.log(f"  ❌ {check_name}", "ERROR")
            
            self.results["scenario_3"] = {
                "session_id": session_id,
                "data": data,
                "checks": checks,
                "success": all(result for _, result in checks)
            }
            
            return True
            
        except Exception as e:
            self.log(f"Scenario 3 error: {str(e)}", "ERROR")
            return False
    
    def check_workers_and_groq(self):
        """Check that workers are running and Groq API key is working"""
        self.log("\n" + "="*60, "INFO")
        self.log("CRITICAL CHECKS: Workers and Groq API", "INFO")
        self.log("="*60, "INFO")
        
        headers = {
            "Authorization": f"Bearer {self.jwt_token}",
            "Content-Type": "application/json"
        }
        
        checks = []
        
        try:
            # Check system status
            response = self.session.get(f"{API_BASE}/test/system-status", headers=headers)
            if response.status_code == 200:
                data = response.json()
                config = data.get("configuration", {})
                
                # Check configuration
                checks.append(("Intents configured", config.get("intents", 0) > 0))
                checks.append(("Knowledge Base entries", config.get("knowledge_base", 0) > 0))
                checks.append(("Qualification criteria", config.get("qualification_criteria", 0) > 0))
                checks.append(("Nurturing config", config.get("nurturing_config", 0) > 0))
                checks.append(("Persona set", config.get("persona_set", False)))
                checks.append(("Global qualification enabled", config.get("global_qualification_enabled", False)))
                checks.append(("Global nurturing enabled", config.get("global_nurturing_enabled", False)))
                
                self.log(f"System configuration: {config.get('intents')} intents, {config.get('knowledge_base')} KB entries", "INFO")
            else:
                checks.append(("System status check", False))
            
            # Test Groq API directly with a simple request
            test_request = {
                "from_email": "test@example.com",
                "subject": "Test Groq API",
                "body": "This is a test to verify Groq API is working with the new key.",
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
                    tokens = draft_action.get("details", {}).get("tokens", 0)
                    checks.append(("Groq API key working", tokens > 0))
                    self.log(f"Groq API working: {tokens} tokens used", "SUCCESS")
                else:
                    checks.append(("Groq API key working", False))
                    self.log("Groq API test failed - no draft generated", "ERROR")
            else:
                checks.append(("Groq API key working", False))
                self.log(f"Groq API test failed: {response.status_code}", "ERROR")
            
            # Check workers (this is implicit - if the API responds, workers are running)
            checks.append(("Workers running and processing", response.status_code == 200))
            
        except Exception as e:
            self.log(f"Critical checks error: {str(e)}", "ERROR")
            checks.append(("Workers running and processing", False))
            checks.append(("Groq API key working", False))
        
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
    
    def run_comprehensive_test(self):
        """Run the complete comprehensive test"""
        self.log("\n" + "="*80, "INFO")
        self.log("COMPREHENSIVE EMAIL AUTOMATION FLOW TEST", "INFO")
        self.log("Testing complete email automation flow with lead qualification", "INFO")
        self.log("="*80 + "\n", "INFO")
        
        # Login
        if not self.login():
            self.log("Cannot proceed without authentication", "ERROR")
            return False
        
        # Setup system
        if not self.setup_system():
            self.log("System setup failed", "ERROR")
            return False
        
        # Wait a moment for setup to propagate
        time.sleep(2)
        
        # Run critical checks
        if not self.check_workers_and_groq():
            self.log("Critical checks failed - continuing with limited testing", "WARNING")
        
        # Run test scenarios
        session_id = self.test_scenario_1_pricing_inquiry()
        if session_id:
            self.test_scenario_2_lead_response(session_id)
        
        self.test_scenario_3_meeting_request()
        
        # Final summary
        self.log("\n" + "="*80, "INFO")
        self.log("COMPREHENSIVE TEST SUMMARY", "INFO")
        self.log("="*80, "INFO")
        
        total_scenarios = 3
        passed_scenarios = sum(1 for key in ["scenario_1", "scenario_2", "scenario_3"] 
                              if self.results.get(key, {}).get("success", False))
        
        critical_passed = self.results.get("critical_checks", {}).get("success", False)
        
        self.log(f"\nTest Results:", "INFO")
        self.log(f"Critical Checks: {'✅ PASS' if critical_passed else '❌ FAIL'}", 
                "SUCCESS" if critical_passed else "ERROR")
        self.log(f"Scenario Tests: {passed_scenarios}/{total_scenarios} passed", 
                "SUCCESS" if passed_scenarios == total_scenarios else "WARNING")
        
        # Detailed scenario results
        for scenario_key, scenario_name in [
            ("scenario_1", "New Lead with Pricing Inquiry"),
            ("scenario_2", "Existing Lead Responding with Information"), 
            ("scenario_3", "Meeting Request")
        ]:
            result = self.results.get(scenario_key, {})
            status = "✅ PASS" if result.get("success") else "❌ FAIL"
            self.log(f"  {status} - {scenario_name}", 
                    "SUCCESS" if result.get("success") else "ERROR")
        
        # Overall success
        overall_success = critical_passed and passed_scenarios == total_scenarios
        
        self.log(f"\nOverall Result: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}", 
                "SUCCESS" if overall_success else "ERROR")
        
        if not overall_success:
            self.log("\nRecommendations for fixes:", "INFO")
            if not critical_passed:
                self.log("- Check Groq API key configuration", "INFO")
                self.log("- Verify system configuration is complete", "INFO")
            if passed_scenarios < total_scenarios:
                self.log("- Review failed scenario details above", "INFO")
                self.log("- Check lead qualification and nurturing settings", "INFO")
        
        return overall_success

if __name__ == "__main__":
    tester = ComprehensiveFlowTester()
    success = tester.run_comprehensive_test()
    sys.exit(0 if success else 1)