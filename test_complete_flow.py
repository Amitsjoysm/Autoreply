#!/usr/bin/env python3
"""
Complete Email Automation Flow Test
Tests the entire email processing pipeline through the Test Email API endpoint
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
    "email": "amits.joys@gmail.com",
    "password": "ij@123"
}

class FlowTester:
    def __init__(self):
        self.session = requests.Session()
        self.jwt_token = None
        self.user_id = None
        self.test_results = []
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
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
                self.log(f"✅ Login successful - User ID: {self.user_id}")
                return True
            else:
                self.log(f"❌ Login failed: {response.status_code} - {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Login error: {str(e)}", "ERROR")
            return False
    
    def get_headers(self):
        """Get authorization headers"""
        return {
            "Authorization": f"Bearer {self.jwt_token}",
            "Content-Type": "application/json"
        }
    
    def test_system_status(self):
        """Test system status endpoint"""
        self.log("\n" + "="*60)
        self.log("TESTING SYSTEM STATUS")
        self.log("="*60)
        
        try:
            response = self.session.get(
                f"{API_BASE}/test/system-status",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log("✅ System Status Retrieved")
                self.log(f"System Ready: {data.get('ready')}")
                
                config = data.get('configuration', {})
                self.log("\nConfiguration:")
                self.log(f"  - Intents: {config.get('intents')}")
                self.log(f"  - Knowledge Base: {config.get('knowledge_base')}")
                self.log(f"  - Qualification Criteria: {config.get('qualification_criteria')}")
                self.log(f"  - Nurturing Config: {config.get('nurturing_config')}")
                self.log(f"  - Persona Set: {config.get('persona_set')}")
                self.log(f"  - Global Qualification: {config.get('global_qualification_enabled')}")
                self.log(f"  - Global Nurturing: {config.get('global_nurturing_enabled')}")
                
                warnings = data.get('warnings', [])
                if warnings:
                    self.log("\n⚠️  Warnings:")
                    for warning in warnings:
                        self.log(f"  - {warning}")
                
                return True, data
            else:
                self.log(f"❌ System status failed: {response.status_code} - {response.text}", "ERROR")
                return False, None
                
        except Exception as e:
            self.log(f"❌ System status error: {str(e)}", "ERROR")
            return False, None
    
    def test_scenario_a_lead_qualification(self):
        """Test Scenario A: Lead Qualification Flow"""
        self.log("\n" + "="*60)
        self.log("SCENARIO A: LEAD QUALIFICATION FLOW")
        self.log("="*60)
        
        request_data = {
            "from_email": "john@techcompany.com",
            "subject": "Pricing inquiry",
            "body": "I'm interested in your pricing for a 75-person company. Budget is $10k/month. We're in tech/SaaS.",
            "simulate_reply": False
        }
        
        self.log(f"Testing email from: {request_data['from_email']}")
        self.log(f"Subject: {request_data['subject']}")
        
        try:
            response = self.session.post(
                f"{API_BASE}/test/complete-flow",
                json=request_data,
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log("✅ Scenario A completed successfully")
                
                # Analyze results
                self.analyze_flow_response(data, "Scenario A")
                
                # Verify specific requirements
                self.verify_scenario_a_requirements(data)
                
                return True, data
            else:
                self.log(f"❌ Scenario A failed: {response.status_code} - {response.text}", "ERROR")
                return False, None
                
        except Exception as e:
            self.log(f"❌ Scenario A error: {str(e)}", "ERROR")
            return False, None
    
    def test_scenario_b_lead_reply(self):
        """Test Scenario B: Lead Reply & Qualification"""
        self.log("\n" + "="*60)
        self.log("SCENARIO B: LEAD REPLY & QUALIFICATION")
        self.log("="*60)
        
        request_data = {
            "from_email": "john@techcompany.com",
            "subject": "Re: Pricing inquiry",
            "body": "I'm interested in your pricing for a 75-person company.",
            "simulate_reply": True,
            "reply_body": "Company size: 75 employees. Budget: $10,000/month. Industry: Technology/SaaS. Timeline: 2-3 months."
        }
        
        self.log(f"Testing email from: {request_data['from_email']}")
        self.log(f"Subject: {request_data['subject']}")
        self.log("With simulated reply containing answers")
        
        try:
            response = self.session.post(
                f"{API_BASE}/test/complete-flow",
                json=request_data,
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log("✅ Scenario B completed successfully")
                
                # Analyze results
                self.analyze_flow_response(data, "Scenario B")
                
                # Verify specific requirements
                self.verify_scenario_b_requirements(data)
                
                return True, data
            else:
                self.log(f"❌ Scenario B failed: {response.status_code} - {response.text}", "ERROR")
                return False, None
                
        except Exception as e:
            self.log(f"❌ Scenario B error: {str(e)}", "ERROR")
            return False, None
    
    def test_scenario_c_meeting_request(self):
        """Test Scenario C: Meeting Request"""
        self.log("\n" + "="*60)
        self.log("SCENARIO C: MEETING REQUEST")
        self.log("="*60)
        
        request_data = {
            "from_email": "customer@company.com",
            "subject": "Schedule a call",
            "body": "Can we schedule a call next Tuesday at 2 PM to discuss implementation?",
            "simulate_reply": False
        }
        
        self.log(f"Testing email from: {request_data['from_email']}")
        self.log(f"Subject: {request_data['subject']}")
        
        try:
            response = self.session.post(
                f"{API_BASE}/test/complete-flow",
                json=request_data,
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log("✅ Scenario C completed successfully")
                
                # Analyze results
                self.analyze_flow_response(data, "Scenario C")
                
                # Verify specific requirements
                self.verify_scenario_c_requirements(data)
                
                return True, data
            else:
                self.log(f"❌ Scenario C failed: {response.status_code} - {response.text}", "ERROR")
                return False, None
                
        except Exception as e:
            self.log(f"❌ Scenario C error: {str(e)}", "ERROR")
            return False, None
    
    def analyze_flow_response(self, data, scenario_name):
        """Analyze and display flow response"""
        self.log(f"\n{scenario_name} Results:")
        self.log("-" * 40)
        
        success = data.get('success', False)
        steps = data.get('steps', [])
        summary = data.get('summary', {})
        warnings = data.get('warnings', [])
        errors = data.get('errors', [])
        
        self.log(f"Overall Success: {success}")
        self.log(f"Total Steps: {len(steps)}")
        
        # Display each step
        for step in steps:
            step_num = step.get('step')
            step_name = step.get('name')
            step_status = step.get('status')
            details = step.get('details', {})
            
            status_icon = "✅" if step_status == "success" else "⚠️" if step_status == "skipped" else "ℹ️"
            self.log(f"\n{status_icon} Step {step_num}: {step_name} ({step_status})")
            
            # Display relevant details
            for key, value in details.items():
                if isinstance(value, (list, dict)):
                    self.log(f"  {key}: {json.dumps(value, indent=2)}")
                else:
                    self.log(f"  {key}: {value}")
        
        # Display summary
        self.log("\nSummary:")
        for key, value in summary.items():
            self.log(f"  {key}: {value}")
        
        # Display warnings
        if warnings:
            self.log("\n⚠️  Warnings:")
            for warning in warnings:
                self.log(f"  - {warning}")
        
        # Display errors
        if errors:
            self.log("\n❌ Errors:")
            for error in errors:
                self.log(f"  - {error}")
    
    def verify_scenario_a_requirements(self, data):
        """Verify Scenario A specific requirements"""
        self.log("\n" + "-"*40)
        self.log("VERIFYING SCENARIO A REQUIREMENTS")
        self.log("-"*40)
        
        steps = data.get('steps', [])
        summary = data.get('summary', {})
        
        checks = {
            "Intent Classification": False,
            "Lead Detection": False,
            "Qualification Initiated": False,
            "Questions Generated": False,
            "Draft Includes Questions": False,
            "Draft Generated": False
        }
        
        # Check intent classification
        for step in steps:
            if step.get('name') == 'Intent Classification':
                checks["Intent Classification"] = step.get('status') == 'success'
                details = step.get('details', {})
                checks["Lead Detection"] = details.get('is_lead', False)
        
        # Check lead qualification
        for step in steps:
            if step.get('name') == 'Lead Qualification Processing':
                checks["Qualification Initiated"] = step.get('status') == 'success'
                details = step.get('details', {})
                checks["Questions Generated"] = details.get('questions_to_ask', 0) > 0
        
        # Check draft generation
        for step in steps:
            if step.get('name') == 'Draft Generation':
                checks["Draft Generated"] = step.get('status') == 'success'
                details = step.get('details', {})
                checks["Draft Includes Questions"] = details.get('includes_questions', False)
        
        # Display results
        for check, passed in checks.items():
            icon = "✅" if passed else "❌"
            self.log(f"{icon} {check}: {passed}")
        
        all_passed = all(checks.values())
        if all_passed:
            self.log("\n✅ ALL SCENARIO A REQUIREMENTS MET")
        else:
            self.log("\n❌ SOME SCENARIO A REQUIREMENTS NOT MET")
        
        return all_passed
    
    def verify_scenario_b_requirements(self, data):
        """Verify Scenario B specific requirements"""
        self.log("\n" + "-"*40)
        self.log("VERIFYING SCENARIO B REQUIREMENTS")
        self.log("-"*40)
        
        steps = data.get('steps', [])
        
        checks = {
            "Reply Received": False,
            "Lead Re-qualification": False,
            "Score Calculated": False,
            "Qualification Decision": False,
            "Follow-ups Would Cancel": False
        }
        
        # Check reply
        for step in steps:
            if step.get('name') == 'Reply Received':
                checks["Reply Received"] = step.get('status') == 'success'
                details = step.get('details', {})
                checks["Follow-ups Would Cancel"] = details.get('would_cancel_followups', False)
        
        # Check re-qualification
        for step in steps:
            if step.get('name') == 'Lead Re-qualification':
                checks["Lead Re-qualification"] = step.get('status') == 'success'
                details = step.get('details', {})
                checks["Score Calculated"] = 'score' in details
                checks["Qualification Decision"] = 'decision' in details
                
                # Log the decision
                if 'decision' in details:
                    self.log(f"\nQualification Decision: {details['decision']}")
                if 'score' in details:
                    self.log(f"Lead Score: {details['score']}/100")
        
        # Display results
        for check, passed in checks.items():
            icon = "✅" if passed else "❌"
            self.log(f"{icon} {check}: {passed}")
        
        all_passed = all(checks.values())
        if all_passed:
            self.log("\n✅ ALL SCENARIO B REQUIREMENTS MET")
        else:
            self.log("\n❌ SOME SCENARIO B REQUIREMENTS NOT MET")
        
        return all_passed
    
    def verify_scenario_c_requirements(self, data):
        """Verify Scenario C specific requirements"""
        self.log("\n" + "-"*40)
        self.log("VERIFYING SCENARIO C REQUIREMENTS")
        self.log("-"*40)
        
        steps = data.get('steps', [])
        
        checks = {
            "Meeting Detected": False,
            "Confidence Score": False,
            "Calendar Event Would Create": False,
            "Meeting Details Extracted": False
        }
        
        # Check meeting detection
        for step in steps:
            if step.get('name') == 'Meeting Detection':
                details = step.get('details', {})
                checks["Meeting Detected"] = details.get('detected', False)
                checks["Confidence Score"] = 'confidence' in details
                checks["Calendar Event Would Create"] = details.get('would_create_calendar_event', False)
                checks["Meeting Details Extracted"] = 'title' in details or 'start_time' in details
                
                # Log meeting details
                if details.get('detected'):
                    self.log(f"\nMeeting Details:")
                    self.log(f"  Confidence: {details.get('confidence', 'N/A')}%")
                    self.log(f"  Title: {details.get('title', 'N/A')}")
                    self.log(f"  Start Time: {details.get('start_time', 'N/A')}")
        
        # Display results
        for check, passed in checks.items():
            icon = "✅" if passed else "❌"
            self.log(f"{icon} {check}: {passed}")
        
        all_passed = all(checks.values())
        if all_passed:
            self.log("\n✅ ALL SCENARIO C REQUIREMENTS MET")
        else:
            self.log("\n❌ SOME SCENARIO C REQUIREMENTS NOT MET")
        
        return all_passed
    
    def run_all_tests(self):
        """Run all test scenarios"""
        self.log("="*60)
        self.log("COMPLETE EMAIL AUTOMATION FLOW TEST")
        self.log("="*60)
        
        # Login
        if not self.login():
            self.log("❌ Cannot proceed without login", "ERROR")
            return False
        
        # Test system status
        status_ok, status_data = self.test_system_status()
        
        # Run all scenarios
        scenario_a_ok, scenario_a_data = self.test_scenario_a_lead_qualification()
        scenario_b_ok, scenario_b_data = self.test_scenario_b_lead_reply()
        scenario_c_ok, scenario_c_data = self.test_scenario_c_meeting_request()
        
        # Final summary
        self.log("\n" + "="*60)
        self.log("FINAL TEST SUMMARY")
        self.log("="*60)
        
        results = {
            "System Status": status_ok,
            "Scenario A (Lead Qualification)": scenario_a_ok,
            "Scenario B (Lead Reply)": scenario_b_ok,
            "Scenario C (Meeting Request)": scenario_c_ok
        }
        
        for test_name, passed in results.items():
            icon = "✅" if passed else "❌"
            self.log(f"{icon} {test_name}: {'PASSED' if passed else 'FAILED'}")
        
        all_passed = all(results.values())
        
        if all_passed:
            self.log("\n🎉 ALL TESTS PASSED!")
            return True
        else:
            failed_count = sum(1 for v in results.values() if not v)
            self.log(f"\n❌ {failed_count} TEST(S) FAILED")
            return False

if __name__ == "__main__":
    tester = FlowTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
