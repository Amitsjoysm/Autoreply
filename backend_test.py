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

class OAuthTester:
    def __init__(self):
        self.session = requests.Session()
        self.jwt_token = None
        self.user_id = None
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
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
            elif response.status_code == 400:
                # User might already exist, try login
                self.log("User might already exist, will try login")
                return self.test_user_login()
            else:
                self.log(f"❌ Registration failed: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Registration error: {str(e)}", "ERROR")
            return False
    
    def test_user_login(self):
        """Test user login"""
        self.log("Testing user login...")
        
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
            else:
                self.log(f"❌ Login failed: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Login error: {str(e)}", "ERROR")
            return False
    
    def test_google_oauth_url(self):
        """Test getting Google OAuth URL"""
        self.log("Testing Google OAuth URL endpoint...")
        
        if not self.jwt_token:
            self.log("❌ No JWT token available", "ERROR")
            return False
            
        try:
            headers = {
                "Authorization": f"Bearer {self.jwt_token}",
                "Content-Type": "application/json"
            }
            
            response = self.session.get(
                f"{API_BASE}/oauth/google/url?account_type=email",
                headers=headers
            )
            
            self.log(f"OAuth URL response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                oauth_url = data.get("url")
                state = data.get("state")
                
                self.log("✅ OAuth URL endpoint successful")
                self.log(f"OAuth URL: {oauth_url}")
                self.log(f"State: {state}")
                
                # Verify URL contains required components
                if oauth_url and "accounts.google.com" in oauth_url:
                    self.log("✅ OAuth URL contains Google endpoint")
                else:
                    self.log("❌ OAuth URL doesn't contain Google endpoint", "ERROR")
                    return False
                    
                if "redirect_uri" in oauth_url:
                    self.log("✅ OAuth URL contains redirect_uri parameter")
                else:
                    self.log("❌ OAuth URL missing redirect_uri parameter", "ERROR")
                    return False
                    
                if "scope" in oauth_url:
                    self.log("✅ OAuth URL contains scope parameter")
                else:
                    self.log("❌ OAuth URL missing scope parameter", "ERROR")
                    return False
                    
                if state:
                    self.log("✅ State parameter returned")
                    self.oauth_state = state
                    return True
                else:
                    self.log("❌ No state parameter returned", "ERROR")
                    return False
                    
            else:
                self.log(f"❌ OAuth URL failed: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ OAuth URL error: {str(e)}", "ERROR")
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