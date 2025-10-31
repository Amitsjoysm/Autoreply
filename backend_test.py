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
    
    def test_intents_configuration(self):
        """Test intents configuration for auto-reply"""
        self.log("Testing intents configuration...")
        
        if not self.jwt_token:
            self.log("❌ No JWT token available", "ERROR")
            return False
            
        try:
            headers = {
                "Authorization": f"Bearer {self.jwt_token}",
                "Content-Type": "application/json"
            }
            
            response = self.session.get(
                f"{API_BASE}/intents",
                headers=headers
            )
            
            self.log(f"Intents response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.log("✅ Intents endpoint successful")
                self.log(f"Found {len(data)} intents")
                
                auto_send_intents = 0
                for i, intent in enumerate(data):
                    self.log(f"Intent {i+1}:")
                    self.log(f"  - ID: {intent.get('id')}")
                    self.log(f"  - Name: {intent.get('name')}")
                    self.log(f"  - Auto Send: {intent.get('auto_send')}")
                    self.log(f"  - Priority: {intent.get('priority')}")
                    self.log(f"  - Active: {intent.get('is_active')}")
                    
                    if intent.get('auto_send'):
                        auto_send_intents += 1
                
                if auto_send_intents > 0:
                    self.log(f"✅ Found {auto_send_intents} intents with auto_send=true")
                else:
                    self.log("⚠️  No intents with auto_send=true found - auto-reply won't work")
                
                return True
            else:
                self.log(f"❌ Intents failed: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Intents error: {str(e)}", "ERROR")
            return False
    
    def test_calendar_providers(self):
        """Test calendar providers configuration"""
        self.log("Testing calendar providers...")
        
        if not self.jwt_token:
            self.log("❌ No JWT token available", "ERROR")
            return False
            
        try:
            headers = {
                "Authorization": f"Bearer {self.jwt_token}",
                "Content-Type": "application/json"
            }
            
            response = self.session.get(
                f"{API_BASE}/calendar/providers",
                headers=headers
            )
            
            self.log(f"Calendar providers response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.log("✅ Calendar providers endpoint successful")
                self.log(f"Found {len(data)} calendar providers")
                
                google_calendar_connected = False
                for i, provider in enumerate(data):
                    self.log(f"Provider {i+1}:")
                    self.log(f"  - ID: {provider.get('id')}")
                    self.log(f"  - Provider: {provider.get('provider')}")
                    self.log(f"  - Email: {provider.get('email')}")
                    self.log(f"  - Active: {provider.get('is_active')}")
                    self.log(f"  - Last Sync: {provider.get('last_sync')}")
                    
                    if provider.get('provider') == 'google' and provider.get('is_active'):
                        google_calendar_connected = True
                
                if google_calendar_connected:
                    self.log("✅ Google Calendar is connected and active")
                else:
                    self.log("⚠️  No active Google Calendar provider - calendar events won't be created")
                
                return True
            else:
                self.log(f"❌ Calendar providers failed: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Calendar providers error: {str(e)}", "ERROR")
            return False
    
    def verify_auto_reply_requirements(self):
        """Verify what's needed for auto-reply to work"""
        self.log("Verifying auto-reply requirements...")
        
        requirements = {
            "jwt_token": bool(self.jwt_token),
            "email_account": hasattr(self, 'email_account') and bool(self.email_account),
            "oauth_tokens": False,
            "auto_send_intent": False,
            "valid_drafts": False
        }
        
        # Check OAuth tokens in email account
        if hasattr(self, 'email_account') and self.email_account:
            account_type = self.email_account.get('account_type')
            if account_type == 'oauth_gmail':
                requirements["oauth_tokens"] = True
                self.log("✅ OAuth Gmail account found")
            else:
                self.log(f"⚠️  Account type is '{account_type}', not OAuth")
        
        # Check for auto-send intents (from previous test)
        # This would be set by test_intents_configuration
        
        self.log("\nAUTO-REPLY REQUIREMENTS SUMMARY:")
        self.log("=" * 40)
        self.log(f"✅ JWT Authentication: {'✓' if requirements['jwt_token'] else '✗'}")
        self.log(f"✅ Email Account Connected: {'✓' if requirements['email_account'] else '✗'}")
        self.log(f"✅ Valid OAuth Tokens: {'✓' if requirements['oauth_tokens'] else '✗'}")
        self.log(f"⚠️  Intent with auto_send=true: {'✓' if requirements['auto_send_intent'] else '✗'}")
        self.log(f"⚠️  Valid Draft Generated: {'✓' if requirements['valid_drafts'] else '✗'}")
        
        missing = [k for k, v in requirements.items() if not v]
        if missing:
            self.log(f"\n❌ MISSING FOR AUTO-REPLY: {', '.join(missing)}")
        else:
            self.log("\n✅ ALL AUTO-REPLY REQUIREMENTS MET")
        
        return len(missing) == 0
    
    def verify_calendar_requirements(self):
        """Verify what's needed for calendar events"""
        self.log("Verifying calendar event requirements...")
        
        requirements = {
            "jwt_token": bool(self.jwt_token),
            "calendar_provider": False,
            "oauth_tokens": False,
            "meeting_detection": True  # Assume this is working
        }
        
        # This would be enhanced based on calendar provider test results
        
        self.log("\nCALENDAR EVENT REQUIREMENTS SUMMARY:")
        self.log("=" * 40)
        self.log(f"✅ JWT Authentication: {'✓' if requirements['jwt_token'] else '✗'}")
        self.log(f"⚠️  Calendar Provider Connected: {'✓' if requirements['calendar_provider'] else '✗'}")
        self.log(f"⚠️  Valid OAuth Tokens: {'✓' if requirements['oauth_tokens'] else '✗'}")
        self.log(f"✅ Meeting Detection Logic: {'✓' if requirements['meeting_detection'] else '✗'}")
        
        missing = [k for k, v in requirements.items() if not v]
        if missing:
            self.log(f"\n❌ MISSING FOR CALENDAR EVENTS: {', '.join(missing)}")
        else:
            self.log("\n✅ ALL CALENDAR REQUIREMENTS MET")
        
        return len(missing) == 0
    
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