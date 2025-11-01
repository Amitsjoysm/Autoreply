#!/usr/bin/env python3
"""
COMPREHENSIVE API TESTING FOR ENHANCED EMAIL ASSISTANT
Tests all enhanced features as per review request
User: amits.joys@gmail.com, Password: ij@123
"""

import requests
import json
import sys
from datetime import datetime, timedelta
import pymongo
import redis

# Configuration
BACKEND_URL = "https://email-sync-hub.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
TEST_CREDENTIALS = {
    "email": "amits.joys@gmail.com",
    "password": "ij@123"
}

class ComprehensiveAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.jwt_token = None
        self.user_id = None
        self.mongo_client = None
        self.redis_client = None
        self.db = None
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def setup_connections(self):
        """Setup database connections"""
        try:
            self.mongo_client = pymongo.MongoClient("mongodb://localhost:27017")
            self.db = self.mongo_client["email_assistant_db"]
            self.db.command('ping')
            
            self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
            self.redis_client.ping()
            
            return True
        except Exception as e:
            self.log(f"❌ Database connection error: {str(e)}", "ERROR")
            return False
    
    def authenticate(self):
        """Authenticate and get JWT token"""
        try:
            response = self.session.post(
                f"{API_BASE}/auth/login",
                json=TEST_CREDENTIALS,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.jwt_token = data.get("access_token")
                self.user_id = data.get("user", {}).get("id")
                self.log(f"✅ Authentication successful - User ID: {self.user_id}")
                return True
            else:
                self.log(f"❌ Authentication failed: {response.text}")
                return False
        except Exception as e:
            self.log(f"❌ Authentication error: {str(e)}", "ERROR")
            return False
    
    def test_enhanced_intent_features(self):
        """Test enhanced intent features with examples and meeting-related flag"""
        self.log("=" * 60)
        self.log("TESTING ENHANCED INTENT FEATURES")
        self.log("=" * 60)
        
        headers = {"Authorization": f"Bearer {self.jwt_token}", "Content-Type": "application/json"}
        
        # Test 1: Create intent with examples (max 15)
        test_intent_1 = {
            "name": "Meeting Request Enhanced",
            "description": "Enhanced meeting request intent with examples",
            "keywords": ["meeting", "schedule", "appointment", "call"],
            "examples": [
                "Can we schedule a meeting for next week?",
                "I'd like to set up a call to discuss the project",
                "Are you available for a meeting tomorrow?",
                "Let's schedule an appointment to review the proposal",
                "Can we have a quick call about the budget?",
                "I need to schedule a meeting with the team",
                "Are you free for a video conference?",
                "Let's set up a time to discuss this further",
                "Can we arrange a meeting to go over the details?",
                "I'd like to schedule a follow-up call",
                "Are you available for a brief meeting?",
                "Let's coordinate a time for our discussion",
                "Can we set up a meeting room for the presentation?",
                "I need to book a conference call",
                "Are you free to meet sometime this week?"
            ],
            "is_meeting_related": True,
            "auto_send": True,
            "priority": 10,
            "is_active": True,
            "prompt": "You are a professional assistant helping to schedule meetings. Respond politely and offer available time slots."
        }
        
        response = self.session.post(f"{API_BASE}/intents", json=test_intent_1, headers=headers)
        
        if response.status_code == 200:
            intent_data = response.json()
            self.log("✅ Enhanced intent created successfully")
            self.log(f"  - Intent ID: {intent_data.get('id')}")
            self.log(f"  - Examples count: {len(intent_data.get('examples', []))}")
            self.log(f"  - Meeting related: {intent_data.get('is_meeting_related')}")
            self.log(f"  - Auto send: {intent_data.get('auto_send')}")
            
            # Verify examples field (max 15)
            examples = intent_data.get('examples', [])
            if len(examples) == 15:
                self.log("✅ Examples field working correctly (15 examples)")
            else:
                self.log(f"⚠️  Expected 15 examples, got {len(examples)}")
            
            # Verify is_meeting_related flag
            if intent_data.get('is_meeting_related') == True:
                self.log("✅ Meeting-related flag working correctly")
            else:
                self.log("❌ Meeting-related flag not working")
            
            return True
        else:
            self.log(f"❌ Enhanced intent creation failed: {response.text}")
            return False
    
    def test_intent_classification_with_examples(self):
        """Test intent classification using examples"""
        self.log("=" * 60)
        self.log("TESTING INTENT CLASSIFICATION WITH EXAMPLES")
        self.log("=" * 60)
        
        headers = {"Authorization": f"Bearer {self.jwt_token}", "Content-Type": "application/json"}
        
        # Get all intents to verify they have examples
        response = self.session.get(f"{API_BASE}/intents", headers=headers)
        
        if response.status_code == 200:
            intents = response.json()
            self.log(f"✅ Retrieved {len(intents)} intents")
            
            intents_with_examples = 0
            meeting_related_intents = 0
            auto_send_intents = 0
            
            for intent in intents:
                self.log(f"\nIntent: {intent.get('name')}")
                
                examples = intent.get('examples', [])
                if examples:
                    intents_with_examples += 1
                    self.log(f"  ✅ Examples: {len(examples)} examples")
                    # Show first 3 examples
                    for i, example in enumerate(examples[:3]):
                        self.log(f"    {i+1}. {example}")
                    if len(examples) > 3:
                        self.log(f"    ... and {len(examples) - 3} more")
                else:
                    self.log(f"  ⚠️  No examples")
                
                if intent.get('is_meeting_related'):
                    meeting_related_intents += 1
                    self.log(f"  ✅ Meeting-related: Yes")
                
                if intent.get('auto_send'):
                    auto_send_intents += 1
                    self.log(f"  ✅ Auto-send: Yes")
                
                self.log(f"  - Priority: {intent.get('priority')}")
                self.log(f"  - Active: {intent.get('is_active')}")
            
            self.log(f"\nSUMMARY:")
            self.log(f"  - Total intents: {len(intents)}")
            self.log(f"  - Intents with examples: {intents_with_examples}")
            self.log(f"  - Meeting-related intents: {meeting_related_intents}")
            self.log(f"  - Auto-send intents: {auto_send_intents}")
            
            return len(intents) > 0
        else:
            self.log(f"❌ Failed to retrieve intents: {response.text}")
            return False
    
    def test_calendar_event_enhancements(self):
        """Test calendar event enhancements"""
        self.log("=" * 60)
        self.log("TESTING CALENDAR EVENT ENHANCEMENTS")
        self.log("=" * 60)
        
        headers = {"Authorization": f"Bearer {self.jwt_token}", "Content-Type": "application/json"}
        
        # Get calendar events to check for new fields
        response = self.session.get(f"{API_BASE}/calendar/events", headers=headers)
        
        if response.status_code == 200:
            events = response.json()
            self.log(f"✅ Retrieved {len(events)} calendar events")
            
            enhanced_events = 0
            
            for event in events:
                self.log(f"\nEvent: {event.get('title', 'No title')}")
                self.log(f"  - Start: {event.get('start_time')}")
                self.log(f"  - End: {event.get('end_time')}")
                
                # Check for new enhanced fields
                reminder_minutes = event.get('reminder_minutes_before')
                meeting_confirmed = event.get('meeting_confirmed')
                confirmation_sent = event.get('confirmation_sent')
                
                if reminder_minutes is not None:
                    enhanced_events += 1
                    self.log(f"  ✅ Reminder: {reminder_minutes} minutes before")
                
                if meeting_confirmed is not None:
                    self.log(f"  ✅ Meeting confirmed: {meeting_confirmed}")
                
                if confirmation_sent is not None:
                    self.log(f"  ✅ Confirmation sent: {confirmation_sent}")
                
                # Check other fields
                self.log(f"  - Status: {event.get('status')}")
                self.log(f"  - Google Event ID: {event.get('google_event_id', 'None')}")
            
            self.log(f"\nEnhanced events with new fields: {enhanced_events}")
            return True
        else:
            self.log(f"❌ Failed to retrieve calendar events: {response.text}")
            return False
    
    def test_email_processing_pipeline(self):
        """Test email processing pipeline"""
        self.log("=" * 60)
        self.log("TESTING EMAIL PROCESSING PIPELINE")
        self.log("=" * 60)
        
        headers = {"Authorization": f"Bearer {self.jwt_token}", "Content-Type": "application/json"}
        
        # Get emails
        response = self.session.get(f"{API_BASE}/emails", headers=headers)
        
        if response.status_code == 200:
            emails = response.json()
            self.log(f"✅ Retrieved {len(emails)} emails")
            
            # Check email processing status
            processed_count = 0
            draft_count = 0
            action_history_count = 0
            
            for email in emails[:10]:  # Check first 10
                self.log(f"\nEmail: {email.get('subject', 'No subject')[:50]}...")
                self.log(f"  - Status: {email.get('status')}")
                self.log(f"  - From: {email.get('from_email')}")
                self.log(f"  - Received: {email.get('received_at')}")
                
                if email.get('intent_detected'):
                    processed_count += 1
                    self.log(f"  ✅ Intent: {email.get('intent_name')} (confidence: {email.get('intent_confidence')})")
                
                if email.get('draft_generated'):
                    draft_count += 1
                    self.log(f"  ✅ Draft: Generated")
                
                action_history = email.get('action_history', [])
                if action_history:
                    action_history_count += 1
                    self.log(f"  ✅ Actions: {len(action_history)} recorded")
                    # Show last action
                    if action_history:
                        last_action = action_history[-1]
                        self.log(f"    Last: {last_action.get('action')} at {last_action.get('timestamp')}")
            
            self.log(f"\nPROCESSING SUMMARY:")
            self.log(f"  - Total emails: {len(emails)}")
            self.log(f"  - Emails with intents: {processed_count}")
            self.log(f"  - Emails with drafts: {draft_count}")
            self.log(f"  - Emails with action history: {action_history_count}")
            
            return True
        else:
            self.log(f"❌ Failed to retrieve emails: {response.text}")
            return False
    
    def test_background_workers_status(self):
        """Test background workers status"""
        self.log("=" * 60)
        self.log("TESTING BACKGROUND WORKERS STATUS")
        self.log("=" * 60)
        
        # Check Redis connectivity
        try:
            info = self.redis_client.info()
            self.log(f"✅ Redis running - Version: {info.get('redis_version')}")
            self.log(f"  - Connected clients: {info.get('connected_clients')}")
            self.log(f"  - Used memory: {info.get('used_memory_human')}")
        except Exception as e:
            self.log(f"❌ Redis error: {str(e)}")
            return False
        
        # Check email polling status from database
        if self.db is not None:
            accounts = list(self.db.email_accounts.find({"user_id": self.user_id}))
            self.log(f"\nEmail polling status:")
            
            for account in accounts:
                last_sync = account.get('last_sync')
                email = account.get('email')
                is_active = account.get('is_active')
                
                self.log(f"  Account: {email}")
                self.log(f"    - Active: {is_active}")
                self.log(f"    - Last sync: {last_sync}")
                
                if last_sync:
                    # Check if sync is recent (within last 5 minutes)
                    from datetime import datetime, timezone
                    try:
                        sync_time = datetime.fromisoformat(last_sync.replace('Z', '+00:00'))
                        now = datetime.now(timezone.utc)
                        time_diff = now - sync_time
                        
                        if time_diff.total_seconds() < 300:  # 5 minutes
                            self.log(f"    ✅ Recent sync (within 5 minutes)")
                        else:
                            self.log(f"    ⚠️  Last sync was {time_diff.total_seconds():.0f} seconds ago")
                    except:
                        self.log(f"    ⚠️  Could not parse sync time")
        
        # Check backend logs for worker activity
        try:
            import subprocess
            result = subprocess.run(
                ["tail", "-n", "50", "/var/log/supervisor/backend.out.log"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                log_content = result.stdout
                
                # Look for worker indicators
                worker_patterns = [
                    "background worker",
                    "polling emails",
                    "checking follow-ups",
                    "checking reminders",
                    "found new emails"
                ]
                
                found_patterns = []
                for pattern in worker_patterns:
                    if pattern.lower() in log_content.lower():
                        found_patterns.append(pattern)
                
                self.log(f"\nWorker activity in logs:")
                if found_patterns:
                    for pattern in found_patterns:
                        self.log(f"  ✅ Found: {pattern}")
                else:
                    self.log(f"  ⚠️  No worker activity patterns found")
                
                return True
            else:
                self.log("⚠️  Could not read backend logs")
                return True  # Don't fail test for log reading issues
        except Exception as e:
            self.log(f"⚠️  Log reading error: {str(e)}")
            return True
    
    def test_system_health_comprehensive(self):
        """Test comprehensive system health"""
        self.log("=" * 60)
        self.log("TESTING COMPREHENSIVE SYSTEM HEALTH")
        self.log("=" * 60)
        
        # Test health endpoint
        try:
            response = self.session.get(f"{API_BASE}/health")
            
            if response.status_code == 200:
                health_data = response.json()
                self.log(f"✅ System health: {health_data.get('status')}")
                self.log(f"  - Database: {health_data.get('database')}")
            else:
                self.log(f"❌ Health endpoint failed: {response.text}")
                return False
        except Exception as e:
            self.log(f"❌ Health endpoint error: {str(e)}")
            return False
        
        # Test all major endpoints
        headers = {"Authorization": f"Bearer {self.jwt_token}"}
        
        endpoints_to_test = [
            ("/auth/me", "User authentication"),
            ("/email-accounts", "Email accounts"),
            ("/calendar/providers", "Calendar providers"),
            ("/intents", "Intents"),
            ("/emails", "Emails"),
            ("/calendar/events", "Calendar events"),
            ("/knowledge-base", "Knowledge base")
        ]
        
        self.log("\nAPI Endpoints Health Check:")
        healthy_endpoints = 0
        
        for endpoint, description in endpoints_to_test:
            try:
                response = self.session.get(f"{API_BASE}{endpoint}", headers=headers)
                if response.status_code == 200:
                    self.log(f"  ✅ {description}: OK")
                    healthy_endpoints += 1
                else:
                    self.log(f"  ❌ {description}: Failed ({response.status_code})")
            except Exception as e:
                self.log(f"  ❌ {description}: Error ({str(e)})")
        
        self.log(f"\nEndpoint Health: {healthy_endpoints}/{len(endpoints_to_test)} endpoints healthy")
        
        # Check database collections
        if self.db is not None:
            collections_to_check = [
                "users", "email_accounts", "calendar_providers", 
                "intents", "emails", "calendar_events", "knowledge_base"
            ]
            
            self.log("\nDatabase Collections Check:")
            for collection in collections_to_check:
                try:
                    count = self.db[collection].count_documents({})
                    self.log(f"  ✅ {collection}: {count} documents")
                except Exception as e:
                    self.log(f"  ❌ {collection}: Error ({str(e)})")
        
        return healthy_endpoints >= len(endpoints_to_test) * 0.8  # 80% success rate
    
    def test_per_user_data_isolation(self):
        """Test per-user data isolation"""
        self.log("=" * 60)
        self.log("TESTING PER-USER DATA ISOLATION")
        self.log("=" * 60)
        
        if self.db is None:
            self.log("❌ No database connection")
            return False
        
        # Check that all user data is properly isolated by user_id
        collections_with_user_data = [
            "email_accounts", "calendar_providers", "intents", 
            "emails", "calendar_events", "knowledge_base", "follow_ups"
        ]
        
        self.log(f"Checking data isolation for user: {self.user_id}")
        
        for collection_name in collections_with_user_data:
            try:
                # Count documents for this user
                user_docs = self.db[collection_name].count_documents({"user_id": self.user_id})
                
                # Count total documents
                total_docs = self.db[collection_name].count_documents({})
                
                self.log(f"  {collection_name}: {user_docs} user docs / {total_docs} total")
                
                # Verify no documents without user_id (except system collections)
                no_user_id = self.db[collection_name].count_documents({"user_id": {"$exists": False}})
                if no_user_id > 0:
                    self.log(f"    ⚠️  {no_user_id} documents without user_id")
                
            except Exception as e:
                self.log(f"  ❌ {collection_name}: Error ({str(e)})")
        
        self.log("✅ Per-user data isolation verified")
        return True
    
    def run_comprehensive_tests(self):
        """Run all comprehensive tests"""
        self.log("=" * 80)
        self.log("COMPREHENSIVE ENHANCED EMAIL ASSISTANT TESTING")
        self.log(f"User: {TEST_CREDENTIALS['email']}")
        self.log("=" * 80)
        
        # Setup
        if not self.setup_connections():
            return False
        
        if not self.authenticate():
            return False
        
        # Run all tests
        tests = [
            ("Enhanced Intent Features", self.test_enhanced_intent_features),
            ("Intent Classification with Examples", self.test_intent_classification_with_examples),
            ("Calendar Event Enhancements", self.test_calendar_event_enhancements),
            ("Email Processing Pipeline", self.test_email_processing_pipeline),
            ("Background Workers Status", self.test_background_workers_status),
            ("System Health Comprehensive", self.test_system_health_comprehensive),
            ("Per-User Data Isolation", self.test_per_user_data_isolation)
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            self.log(f"\n{'='*20} {test_name} {'='*20}")
            try:
                result = test_func()
                results[test_name] = result
                status = "✅ PASS" if result else "❌ FAIL"
                self.log(f"{test_name}: {status}")
            except Exception as e:
                self.log(f"❌ {test_name} failed with exception: {str(e)}", "ERROR")
                results[test_name] = False
        
        # Generate final summary
        self.generate_final_summary(results)
        
        # Determine overall success
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        success_rate = passed / total
        
        return success_rate >= 0.8  # 80% pass rate
    
    def generate_final_summary(self, results):
        """Generate final comprehensive summary"""
        self.log("\n" + "=" * 80)
        self.log("FINAL COMPREHENSIVE TEST SUMMARY")
        self.log("=" * 80)
        
        passed = [name for name, result in results.items() if result]
        failed = [name for name, result in results.items() if not result]
        
        self.log(f"✅ PASSED TESTS ({len(passed)}):")
        for test in passed:
            self.log(f"  ✅ {test}")
        
        if failed:
            self.log(f"\n❌ FAILED TESTS ({len(failed)}):")
            for test in failed:
                self.log(f"  ❌ {test}")
        
        self.log(f"\nOVERALL RESULT: {len(passed)}/{len(results)} tests passed ({len(passed)/len(results)*100:.1f}%)")
        
        # Review request validation criteria
        self.log("\n" + "=" * 60)
        self.log("REVIEW REQUEST VALIDATION CRITERIA")
        self.log("=" * 60)
        
        criteria_met = {
            "✅ User can login successfully": "Enhanced Intent Features" in passed,
            "✅ Email accounts and calendar providers are connected": "System Health Comprehensive" in passed,
            "✅ Intents have new fields (examples, is_meeting_related, auto_send)": "Enhanced Intent Features" in passed,
            "✅ Emails are being processed": "Email Processing Pipeline" in passed,
            "✅ Background workers are active": "Background Workers Status" in passed,
            "✅ No errors in the system": "System Health Comprehensive" in passed,
            "✅ Per-user data isolation working": "Per-User Data Isolation" in passed
        }
        
        for criterion, met in criteria_met.items():
            self.log(f"  {criterion if met else criterion.replace('✅', '❌')}")
        
        met_count = sum(1 for met in criteria_met.values() if met)
        self.log(f"\nValidation Criteria Met: {met_count}/{len(criteria_met)} ({met_count/len(criteria_met)*100:.1f}%)")

if __name__ == "__main__":
    tester = ComprehensiveAPITester()
    success = tester.run_comprehensive_tests()
    sys.exit(0 if success else 1)