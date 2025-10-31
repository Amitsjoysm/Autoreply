#!/usr/bin/env python3
"""
Email Polling and Auto-Reply Testing Script
Tests email polling improvements, auto-reply functionality, and calendar setup
"""

import requests
import json
import sys
from datetime import datetime
import pymongo
import redis

# Configuration - Use the correct backend URL from review request
BACKEND_URL = "https://8c808a32-7d7f-4bdf-be1a-fa305bf15637.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test data - Use realistic test data
TEST_USER = {
    "email": "emailassistant.test@gmail.com",
    "password": "SecurePass2024!",
    "name": "Email Assistant Tester"
}

class EmailPollingTester:
    def __init__(self):
        self.session = requests.Session()
        self.jwt_token = None
        self.user_id = None
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def test_user_login(self):
        """Test user login to get JWT token"""
        self.log("Testing user login to get JWT token...")
        
        try:
            login_data = {
                "email": TEST_USER["email"],
                "password": TEST_USER["password"]
            }
            
            response = self.session.post(
                f"{API_BASE}/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            self.log(f"Login response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.jwt_token = data.get("access_token")
                self.user_id = data.get("user", {}).get("id")
                self.log("✅ User login successful")
                self.log(f"JWT Token: {self.jwt_token[:50]}...")
                self.log(f"User ID: {self.user_id}")
                return True
            elif response.status_code == 400 or response.status_code == 401:
                # Try registration first
                self.log("User doesn't exist, trying registration...")
                return self.test_user_registration()
            else:
                self.log(f"❌ Login failed: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Login error: {str(e)}", "ERROR")
            return False
    
    def test_user_registration(self):
        """Test user registration"""
        self.log("Testing user registration...")
        
        try:
            response = self.session.post(
                f"{API_BASE}/auth/register",
                json=TEST_USER,
                headers={"Content-Type": "application/json"}
            )
            
            self.log(f"Registration response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.jwt_token = data.get("access_token")
                self.user_id = data.get("user", {}).get("id")
                self.log("✅ User registration successful")
                self.log(f"JWT Token: {self.jwt_token[:50]}...")
                self.log(f"User ID: {self.user_id}")
                return True
            else:
                self.log(f"❌ Registration failed: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Registration error: {str(e)}", "ERROR")
            return False
    
    def test_email_accounts(self):
        """Test checking email accounts"""
        self.log("Testing email accounts endpoint...")
        
        if not self.jwt_token:
            self.log("❌ No JWT token available", "ERROR")
            return False
            
        try:
            headers = {
                "Authorization": f"Bearer {self.jwt_token}",
                "Content-Type": "application/json"
            }
            
            response = self.session.get(
                f"{API_BASE}/email-accounts",
                headers=headers
            )
            
            self.log(f"Email accounts response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.log("✅ Email accounts endpoint successful")
                self.log(f"Found {len(data)} email accounts")
                
                for i, account in enumerate(data):
                    self.log(f"Account {i+1}:")
                    self.log(f"  - ID: {account.get('id')}")
                    self.log(f"  - Email: {account.get('email')}")
                    self.log(f"  - Type: {account.get('account_type')}")
                    self.log(f"  - Active: {account.get('is_active')}")
                    self.log(f"  - Created: {account.get('created_at')}")
                    self.log(f"  - Last Sync: {account.get('last_sync')}")
                    
                    # Store first account for later tests
                    if i == 0:
                        self.email_account = account
                
                return True
            else:
                self.log(f"❌ Email accounts failed: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Email accounts error: {str(e)}", "ERROR")
            return False
    
    def test_processed_emails(self):
        """Test checking processed emails"""
        self.log("Testing processed emails endpoint...")
        
        if not self.jwt_token:
            self.log("❌ No JWT token available", "ERROR")
            return False
            
        try:
            headers = {
                "Authorization": f"Bearer {self.jwt_token}",
                "Content-Type": "application/json"
            }
            
            response = self.session.get(
                f"{API_BASE}/emails?limit=20",
                headers=headers
            )
            
            self.log(f"Emails response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.log("✅ Emails endpoint successful")
                self.log(f"Found {len(data)} emails in database")
                
                # Check if we have the email account creation time
                account_created_at = None
                if hasattr(self, 'email_account') and self.email_account:
                    account_created_at = self.email_account.get('created_at')
                    self.log(f"Email account created at: {account_created_at}")
                
                recent_emails = 0
                for i, email in enumerate(data[:5]):  # Show first 5 emails
                    self.log(f"Email {i+1}:")
                    self.log(f"  - ID: {email.get('id')}")
                    self.log(f"  - From: {email.get('from_email')}")
                    self.log(f"  - Subject: {email.get('subject', '')[:50]}...")
                    self.log(f"  - Received: {email.get('received_at')}")
                    self.log(f"  - Status: {email.get('status')}")
                    self.log(f"  - Draft Generated: {email.get('draft_generated')}")
                    self.log(f"  - Replied: {email.get('replied')}")
                    
                    # Check if email is after account creation
                    if account_created_at and email.get('received_at'):
                        if email.get('received_at') > account_created_at:
                            recent_emails += 1
                
                if account_created_at:
                    self.log(f"✅ Found {recent_emails} emails after account creation")
                else:
                    self.log("⚠️  Cannot verify email timing - no account creation time")
                
                return True
            else:
                self.log(f"❌ Emails failed: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Emails error: {str(e)}", "ERROR")
            return False
    
    def test_oauth_state_storage(self):
        """Test OAuth state storage in MongoDB"""
        self.log("Testing OAuth state storage in MongoDB...")
        
        if not hasattr(self, 'oauth_state'):
            self.log("❌ No OAuth state to verify", "ERROR")
            return False
            
        try:
            # Connect to MongoDB
            client = pymongo.MongoClient("mongodb://localhost:27017")
            db = client["email_assistant_db"]
            
            # Find the state document
            state_doc = db.oauth_states.find_one({"state": self.oauth_state})
            
            if state_doc:
                self.log("✅ OAuth state found in MongoDB")
                self.log(f"State document: {json.dumps(state_doc, default=str, indent=2)}")
                
                # Verify required fields
                required_fields = ["state", "user_id", "provider", "account_type", "created_at"]
                for field in required_fields:
                    if field in state_doc:
                        self.log(f"✅ Field '{field}' present: {state_doc[field]}")
                    else:
                        self.log(f"❌ Field '{field}' missing", "ERROR")
                        return False
                        
                # Verify values
                if state_doc.get("provider") == "google":
                    self.log("✅ Provider is 'google'")
                else:
                    self.log(f"❌ Provider is '{state_doc.get('provider')}', expected 'google'", "ERROR")
                    return False
                    
                if state_doc.get("account_type") == "email":
                    self.log("✅ Account type is 'email'")
                else:
                    self.log(f"❌ Account type is '{state_doc.get('account_type')}', expected 'email'", "ERROR")
                    return False
                    
                if state_doc.get("user_id") == self.user_id:
                    self.log("✅ User ID matches")
                else:
                    self.log(f"❌ User ID mismatch: {state_doc.get('user_id')} vs {self.user_id}", "ERROR")
                    return False
                    
                return True
            else:
                self.log("❌ OAuth state not found in MongoDB", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ MongoDB connection error: {str(e)}", "ERROR")
            return False
        finally:
            try:
                client.close()
            except:
                pass
    
    def test_services_status(self):
        """Test backend services status"""
        self.log("Testing services status...")
        
        # Test backend health
        try:
            response = self.session.get(f"{API_BASE}/health")
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ Backend health check: {data}")
            else:
                self.log(f"❌ Backend health check failed: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Backend health check error: {str(e)}", "ERROR")
            return False
        
        # Test MongoDB connection
        try:
            client = pymongo.MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=5000)
            client.server_info()
            self.log("✅ MongoDB is accessible")
            client.close()
        except Exception as e:
            self.log(f"❌ MongoDB connection error: {str(e)}", "ERROR")
            return False
        
        # Test Redis connection
        try:
            r = redis.Redis(host='localhost', port=6379, db=0, socket_timeout=5)
            r.ping()
            self.log("✅ Redis is running")
        except Exception as e:
            self.log(f"❌ Redis connection error: {str(e)}", "ERROR")
            return False
            
        return True
    
    def run_all_tests(self):
        """Run all OAuth tests"""
        self.log("=" * 60)
        self.log("Starting OAuth Integration Tests")
        self.log("=" * 60)
        
        tests = [
            ("User Registration/Login", self.test_user_registration),
            ("Google OAuth URL", self.test_google_oauth_url),
            ("OAuth State Storage", self.test_oauth_state_storage),
            ("Services Status", self.test_services_status)
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            self.log(f"\n--- {test_name} ---")
            try:
                results[test_name] = test_func()
            except Exception as e:
                self.log(f"❌ {test_name} failed with exception: {str(e)}", "ERROR")
                results[test_name] = False
        
        # Summary
        self.log("\n" + "=" * 60)
        self.log("TEST RESULTS SUMMARY")
        self.log("=" * 60)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"{test_name}: {status}")
            if result:
                passed += 1
        
        self.log(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            self.log("🎉 All tests passed!")
            return True
        else:
            self.log("⚠️  Some tests failed")
            return False

if __name__ == "__main__":
    tester = OAuthTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)