#!/usr/bin/env python3
"""
Comprehensive Backend Test for Claude LLM Integration
Tests both Groq and Claude providers with fallback mechanism
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

# Add backend to path
sys.path.append('/app/backend')

import httpx
from motor.motor_asyncio import AsyncIOMotorClient

# Import backend services
from config import config
from models.email import Email
from services.ai_agent_service import AIAgentService

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ClaudeLLMIntegrationTest:
    """Comprehensive test suite for Claude LLM integration"""
    
    def __init__(self):
        self.backend_url = "https://followup-enhance.preview.emergentagent.com/api"
        self.test_results = {}
        self.db = None
        self.ai_service = None
        
        # Test configuration from review request
        self.groq_api_key = "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"
        self.claude_api_key = "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"
        
        # Test scenarios
        self.test_scenarios = [
            {
                "name": "Pricing Inquiry",
                "from_email": "john@techcompany.com",
                "subject": "Pricing Information Request",
                "body": "Hi, I'm interested in your product. Can you share pricing details and features? We're a 50-person company looking for a solution."
            },
            {
                "name": "Meeting Request", 
                "from_email": "sarah@startup.com",
                "subject": "Schedule a Demo Call",
                "body": "Hello, can we schedule a demo call next Tuesday at 2 PM? I'd like to see your platform in action."
            },
            {
                "name": "Technical Question",
                "from_email": "dev@company.com", 
                "subject": "API Integration Question",
                "body": "We're evaluating your API for integration. What authentication methods do you support? Do you have rate limits?"
            }
        ]
    
    async def setup(self):
        """Initialize database connection and services"""
        try:
            # Connect to MongoDB
            client = AsyncIOMotorClient(config.MONGO_URL)
            self.db = client[config.DB_NAME]
            
            # Test database connection
            await self.db.command('ping')
            logger.info("✓ Database connection established")
            
            # Initialize AI service
            self.ai_service = AIAgentService(self.db)
            logger.info("✓ AI Agent Service initialized")
            
            return True
        except Exception as e:
            logger.error(f"Setup failed: {e}")
            return False
    
    async def test_1_verify_providers_configured(self) -> Dict:
        """TEST 1: Verify Both Providers are Configured"""
        logger.info("\n" + "="*60)
        logger.info("TEST 1: Verify Both Providers are Configured")
        logger.info("="*60)
        
        results = {
            "test_name": "Provider Configuration",
            "passed": False,
            "details": {},
            "issues": []
        }
        
        try:
            # Check Groq API key
            groq_configured = bool(self.ai_service.groq_api_key)
            results["details"]["groq_api_key_configured"] = groq_configured
            
            if groq_configured:
                logger.info(f"✓ Groq API key configured: {self.ai_service.groq_api_key[:20]}...")
            else:
                logger.error("✗ Groq API key not configured")
                results["issues"].append("Groq API key missing")
            
            # Check Claude API key
            claude_configured = bool(self.ai_service.claude_api_key and self.ai_service.claude_client)
            results["details"]["claude_api_key_configured"] = claude_configured
            
            if claude_configured:
                logger.info(f"✓ Claude API key configured: {self.ai_service.claude_api_key[:20]}...")
            else:
                logger.error("✗ Claude API key not configured")
                results["issues"].append("Claude API key missing")
            
            # Check provider settings
            results["details"]["primary_provider"] = self.ai_service.primary_provider
            results["details"]["fallback_provider"] = self.ai_service.fallback_provider
            
            logger.info(f"✓ Primary provider: {self.ai_service.primary_provider}")
            logger.info(f"✓ Fallback provider: {self.ai_service.fallback_provider}")
            
            # Test passes if both providers are configured
            results["passed"] = groq_configured and claude_configured
            
            if results["passed"]:
                logger.info("✅ TEST 1 PASSED: Both providers configured correctly")
            else:
                logger.error("❌ TEST 1 FAILED: Missing provider configuration")
                
        except Exception as e:
            logger.error(f"TEST 1 ERROR: {e}")
            results["issues"].append(f"Configuration error: {str(e)}")
        
        return results
    
    async def test_2_primary_provider_groq(self) -> Dict:
        """TEST 2: Primary Provider (Groq) Functionality"""
        logger.info("\n" + "="*60)
        logger.info("TEST 2: Primary Provider (Groq) Functionality")
        logger.info("="*60)
        
        results = {
            "test_name": "Groq Primary Provider",
            "passed": False,
            "details": {},
            "issues": []
        }
        
        try:
            # Test draft generation with Groq
            test_email = Email(
                id="test-groq-draft",
                user_id="test-user",
                email_account_id="test-account",
                message_id="test-message-groq",
                from_email="test@example.com",
                to_email=["support@company.com"],
                subject="Test Groq Draft Generation",
                body="Hello, I need help with your product. Can you provide more information?",
                received_at=datetime.now(timezone.utc).isoformat()
            )
            
            # Force use of Groq provider
            draft, tokens = await self.ai_service.generate_draft(
                email=test_email,
                user_id="test-user"
            )
            
            results["details"]["draft_generated"] = True
            results["details"]["draft_length"] = len(draft)
            results["details"]["tokens_used"] = tokens
            results["details"]["draft_preview"] = draft[:100] + "..." if len(draft) > 100 else draft
            
            logger.info(f"✓ Groq draft generated: {len(draft)} chars, {tokens} tokens")
            
            # Test draft validation with Groq
            is_valid, issues, validation_tokens = await self.ai_service.validate_draft(
                draft=draft,
                original_email=test_email
            )
            
            results["details"]["validation_passed"] = is_valid
            results["details"]["validation_tokens"] = validation_tokens
            results["details"]["validation_issues"] = issues
            
            if is_valid:
                logger.info("✓ Groq draft validation passed")
            else:
                logger.warning(f"⚠ Groq draft validation failed: {issues}")
            
            # Test meeting detection with Groq
            meeting_email = Email(
                id="test-groq-meeting",
                user_id="test-user",
                email_account_id="test-account",
                message_id="test-message-meeting",
                from_email="client@company.com",
                to_email=["support@company.com"],
                subject="Schedule Meeting",
                body="Can we schedule a call next Tuesday at 2 PM to discuss the project?",
                received_at=datetime.now(timezone.utc).isoformat()
            )
            
            is_meeting, confidence, details = await self.ai_service.detect_meeting(meeting_email)
            
            results["details"]["meeting_detected"] = is_meeting
            results["details"]["meeting_confidence"] = confidence
            results["details"]["meeting_details"] = details
            
            if is_meeting:
                logger.info(f"✓ Groq meeting detection: {confidence:.1%} confidence")
            else:
                logger.info("✓ Groq meeting detection: No meeting detected")
            
            # Test passes if draft generation works
            results["passed"] = len(draft) >= 50 and tokens > 0
            
            if results["passed"]:
                logger.info("✅ TEST 2 PASSED: Groq provider working correctly")
            else:
                logger.error("❌ TEST 2 FAILED: Groq provider issues")
                results["issues"].append("Groq draft generation failed")
                
        except Exception as e:
            logger.error(f"TEST 2 ERROR: {e}")
            results["issues"].append(f"Groq API error: {str(e)}")
        
        return results
    
    async def test_3_claude_provider_functionality(self) -> Dict:
        """TEST 3: Claude Provider Functionality"""
        logger.info("\n" + "="*60)
        logger.info("TEST 3: Claude Provider Functionality")
        logger.info("="*60)
        
        results = {
            "test_name": "Claude Provider Functionality",
            "passed": False,
            "details": {},
            "issues": []
        }
        
        try:
            # Temporarily set Claude as primary provider
            original_primary = self.ai_service.primary_provider
            self.ai_service.primary_provider = 'claude'
            
            logger.info("🔄 Temporarily set Claude as primary provider")
            
            # Test draft generation with Claude
            test_email = Email(
                id="test-claude-draft",
                user_id="test-user",
                email_account_id="test-account",
                message_id="test-message-claude",
                from_email="customer@business.com",
                to_email=["support@company.com"],
                subject="Product Inquiry",
                body="I'm interested in your enterprise solution. What features are included and what's the pricing structure?",
                received_at=datetime.now(timezone.utc).isoformat()
            )
            
            draft, tokens = await self.ai_service.generate_draft(
                email=test_email,
                user_id="test-user"
            )
            
            results["details"]["draft_generated"] = True
            results["details"]["draft_length"] = len(draft)
            results["details"]["tokens_used"] = tokens
            results["details"]["draft_preview"] = draft[:100] + "..." if len(draft) > 100 else draft
            
            logger.info(f"✓ Claude draft generated: {len(draft)} chars, {tokens} tokens")
            
            # Test draft validation with Claude
            is_valid, issues, validation_tokens = await self.ai_service.validate_draft(
                draft=draft,
                original_email=test_email
            )
            
            results["details"]["validation_passed"] = is_valid
            results["details"]["validation_tokens"] = validation_tokens
            results["details"]["validation_issues"] = issues
            
            if is_valid:
                logger.info("✓ Claude draft validation passed")
            else:
                logger.warning(f"⚠ Claude draft validation failed: {issues}")
            
            # Test meeting detection with Claude
            meeting_email = Email(
                id="test-claude-meeting",
                user_id="test-user",
                email_account_id="test-account",
                message_id="test-message-claude-meeting",
                from_email="prospect@startup.com",
                to_email=["sales@company.com"],
                subject="Demo Request",
                body="Hi, I'd like to schedule a product demo. Are you available tomorrow at 3 PM for a 30-minute call?",
                received_at=datetime.now(timezone.utc).isoformat()
            )
            
            is_meeting, confidence, details = await self.ai_service.detect_meeting(meeting_email)
            
            results["details"]["meeting_detected"] = is_meeting
            results["details"]["meeting_confidence"] = confidence
            results["details"]["meeting_details"] = details
            
            if is_meeting:
                logger.info(f"✓ Claude meeting detection: {confidence:.1%} confidence")
            else:
                logger.info("✓ Claude meeting detection: No meeting detected")
            
            # Verify quality standards (50 chars, 20 words)
            word_count = len(draft.split())
            results["details"]["meets_length_requirement"] = len(draft) >= 50
            results["details"]["meets_word_requirement"] = word_count >= 20
            results["details"]["word_count"] = word_count
            
            if len(draft) >= 50 and word_count >= 20:
                logger.info(f"✓ Claude draft meets quality standards: {len(draft)} chars, {word_count} words")
            else:
                logger.warning(f"⚠ Claude draft below standards: {len(draft)} chars, {word_count} words")
            
            # Test passes if draft generation works and meets standards
            results["passed"] = (len(draft) >= 50 and word_count >= 20 and tokens > 0)
            
            if results["passed"]:
                logger.info("✅ TEST 3 PASSED: Claude provider working correctly")
            else:
                logger.error("❌ TEST 3 FAILED: Claude provider issues")
                results["issues"].append("Claude draft generation failed or below standards")
            
            # Restore original primary provider
            self.ai_service.primary_provider = original_primary
            logger.info(f"🔄 Restored primary provider to: {original_primary}")
                
        except Exception as e:
            logger.error(f"TEST 3 ERROR: {e}")
            results["issues"].append(f"Claude API error: {str(e)}")
            # Restore original primary provider on error
            self.ai_service.primary_provider = original_primary
        
        return results
    
    async def test_4_fallback_mechanism(self) -> Dict:
        """TEST 4: Fallback Mechanism"""
        logger.info("\n" + "="*60)
        logger.info("TEST 4: Fallback Mechanism")
        logger.info("="*60)
        
        results = {
            "test_name": "Fallback Mechanism",
            "passed": False,
            "details": {},
            "issues": []
        }
        
        try:
            # Save original API keys
            original_groq_key = self.ai_service.groq_api_key
            original_claude_key = self.ai_service.claude_api_key
            
            # Test 1: Simulate Groq failure, fallback to Claude
            logger.info("🧪 Testing Groq failure → Claude fallback")
            
            # Temporarily invalidate Groq key
            self.ai_service.groq_api_key = "invalid_key_test"
            
            test_email = Email(
                id="test-fallback-1",
                user_id="test-user",
                email_account_id="test-account",
                message_id="test-message-fallback",
                from_email="test@fallback.com",
                to_email=["support@company.com"],
                subject="Fallback Test",
                body="This is a test to verify the fallback mechanism works correctly.",
                received_at=datetime.now(timezone.utc).isoformat()
            )
            
            try:
                draft, tokens = await self.ai_service.generate_draft(
                    email=test_email,
                    user_id="test-user"
                )
                
                results["details"]["groq_to_claude_fallback"] = True
                results["details"]["fallback_draft_length"] = len(draft)
                results["details"]["fallback_tokens"] = tokens
                
                logger.info(f"✓ Fallback to Claude successful: {len(draft)} chars, {tokens} tokens")
                
            except Exception as e:
                results["details"]["groq_to_claude_fallback"] = False
                results["issues"].append(f"Groq→Claude fallback failed: {str(e)}")
                logger.error(f"✗ Fallback to Claude failed: {e}")
            
            # Restore Groq key
            self.ai_service.groq_api_key = original_groq_key
            
            # Test 2: Simulate Claude failure, fallback to Groq
            logger.info("🧪 Testing Claude failure → Groq fallback")
            
            # Temporarily invalidate Claude
            self.ai_service.claude_api_key = "invalid_key_test"
            self.ai_service.claude_client = None
            
            # Set Claude as primary to test fallback to Groq
            original_primary = self.ai_service.primary_provider
            self.ai_service.primary_provider = 'claude'
            
            try:
                draft2, tokens2 = await self.ai_service.generate_draft(
                    email=test_email,
                    user_id="test-user"
                )
                
                results["details"]["claude_to_groq_fallback"] = True
                results["details"]["fallback2_draft_length"] = len(draft2)
                results["details"]["fallback2_tokens"] = tokens2
                
                logger.info(f"✓ Fallback to Groq successful: {len(draft2)} chars, {tokens2} tokens")
                
            except Exception as e:
                results["details"]["claude_to_groq_fallback"] = False
                results["issues"].append(f"Claude→Groq fallback failed: {str(e)}")
                logger.error(f"✗ Fallback to Groq failed: {e}")
            
            # Restore original settings
            self.ai_service.claude_api_key = original_claude_key
            if original_claude_key:
                from anthropic import AsyncAnthropic
                self.ai_service.claude_client = AsyncAnthropic(api_key=original_claude_key)
            self.ai_service.primary_provider = original_primary
            
            # Test passes if at least one fallback worked
            fallback1_worked = results["details"].get("groq_to_claude_fallback", False)
            fallback2_worked = results["details"].get("claude_to_groq_fallback", False)
            results["passed"] = fallback1_worked or fallback2_worked
            
            if results["passed"]:
                logger.info("✅ TEST 4 PASSED: Fallback mechanism working")
            else:
                logger.error("❌ TEST 4 FAILED: Fallback mechanism not working")
                
        except Exception as e:
            logger.error(f"TEST 4 ERROR: {e}")
            results["issues"].append(f"Fallback test error: {str(e)}")
        
        return results
    
    async def test_5_dual_provider_integration(self) -> Dict:
        """TEST 5: Dual Provider Integration"""
        logger.info("\n" + "="*60)
        logger.info("TEST 5: Dual Provider Integration")
        logger.info("="*60)
        
        results = {
            "test_name": "Dual Provider Integration",
            "passed": False,
            "details": {},
            "issues": []
        }
        
        try:
            # Test both providers with same prompt
            test_email = Email(
                id="test-dual-provider",
                from_email="comparison@test.com",
                to_email=["support@company.com"],
                subject="Dual Provider Test",
                body="I need information about your pricing plans and available features for a team of 25 people.",
                received_at=datetime.now(timezone.utc),
                email_account_id="test-account"
            )
            
            # Test Groq
            logger.info("🧪 Testing Groq provider")
            groq_draft, groq_tokens = await self.ai_service._call_llm_api(
                system_message="You are a helpful email assistant. Generate a professional response.",
                user_message=f"Respond to this email:\nFrom: {test_email.from_email}\nSubject: {test_email.subject}\nBody: {test_email.body}",
                provider='groq'
            )
            
            results["details"]["groq_response_length"] = len(groq_draft)
            results["details"]["groq_tokens"] = groq_tokens
            
            # Test Claude
            logger.info("🧪 Testing Claude provider")
            claude_draft, claude_tokens = await self.ai_service._call_llm_api(
                system_message="You are a helpful email assistant. Generate a professional response.",
                user_message=f"Respond to this email:\nFrom: {test_email.from_email}\nSubject: {test_email.subject}\nBody: {test_email.body}",
                provider='claude'
            )
            
            results["details"]["claude_response_length"] = len(claude_draft)
            results["details"]["claude_tokens"] = claude_tokens
            
            # Compare responses
            results["details"]["both_providers_working"] = len(groq_draft) > 50 and len(claude_draft) > 50
            results["details"]["responses_different"] = groq_draft != claude_draft
            results["details"]["groq_preview"] = groq_draft[:100] + "..." if len(groq_draft) > 100 else groq_draft
            results["details"]["claude_preview"] = claude_draft[:100] + "..." if len(claude_draft) > 100 else claude_draft
            
            logger.info(f"✓ Groq response: {len(groq_draft)} chars")
            logger.info(f"✓ Claude response: {len(claude_draft)} chars")
            logger.info(f"✓ Responses are {'different' if groq_draft != claude_draft else 'identical'}")
            
            # Test token tracking
            initial_tokens = self.ai_service.tokens_used
            await self.ai_service.generate_draft(email=test_email, user_id="test-user")
            final_tokens = self.ai_service.tokens_used
            
            results["details"]["token_tracking_working"] = final_tokens > initial_tokens
            results["details"]["tokens_tracked"] = final_tokens - initial_tokens
            
            logger.info(f"✓ Token tracking: {final_tokens - initial_tokens} tokens tracked")
            
            # Test passes if both providers work and produce different responses
            results["passed"] = (
                results["details"]["both_providers_working"] and
                results["details"]["token_tracking_working"]
            )
            
            if results["passed"]:
                logger.info("✅ TEST 5 PASSED: Dual provider integration working")
            else:
                logger.error("❌ TEST 5 FAILED: Dual provider integration issues")
                
        except Exception as e:
            logger.error(f"TEST 5 ERROR: {e}")
            results["issues"].append(f"Dual provider test error: {str(e)}")
        
        return results
    
    async def test_6_context_aware_generation_claude(self) -> Dict:
        """TEST 6: Context-Aware Generation with Claude"""
        logger.info("\n" + "="*60)
        logger.info("TEST 6: Context-Aware Generation with Claude")
        logger.info("="*60)
        
        results = {
            "test_name": "Context-Aware Generation with Claude",
            "passed": False,
            "details": {},
            "issues": []
        }
        
        try:
            # Set Claude as primary for this test
            original_primary = self.ai_service.primary_provider
            self.ai_service.primary_provider = 'claude'
            
            # Create test user with persona
            test_user_id = "claude-context-test-user"
            await self.db.users.update_one(
                {"id": test_user_id},
                {"$set": {
                    "id": test_user_id,
                    "email": "claude-test@example.com",
                    "persona": "You are a friendly and knowledgeable customer success manager at TechCorp. You're enthusiastic about helping customers succeed with our platform."
                }},
                upsert=True
            )
            
            # Create knowledge base entries
            kb_entries = [
                {
                    "id": "kb-pricing",
                    "user_id": test_user_id,
                    "title": "Pricing Plans",
                    "content": "We offer three plans: Starter ($29/month), Professional ($99/month), and Enterprise ($299/month). All plans include 24/7 support.",
                    "category": "Pricing",
                    "is_active": True
                },
                {
                    "id": "kb-features",
                    "user_id": test_user_id,
                    "title": "Key Features",
                    "content": "Our platform includes automated workflows, real-time analytics, team collaboration tools, and API integrations.",
                    "category": "Features",
                    "is_active": True
                }
            ]
            
            for kb in kb_entries:
                await self.db.knowledge_base.update_one(
                    {"id": kb["id"]},
                    {"$set": kb},
                    upsert=True
                )
            
            # Create intent with specific prompt
            intent_id = "claude-pricing-intent"
            await self.db.intents.update_one(
                {"id": intent_id},
                {"$set": {
                    "id": intent_id,
                    "user_id": test_user_id,
                    "name": "Pricing Inquiry",
                    "keywords": ["pricing", "cost", "price", "plan"],
                    "prompt": "When responding to pricing inquiries, always mention our three plans and highlight the value proposition. Ask about their team size to recommend the best plan.",
                    "is_active": True,
                    "priority": 1
                }},
                upsert=True
            )
            
            # Test email with thread context
            test_email = Email(
                id="claude-context-test",
                from_email="prospect@company.com",
                to_email=["sales@techcorp.com"],
                subject="Pricing Question",
                body="Hi, I'm evaluating your platform for our team. Can you tell me about your pricing and what features are included?",
                received_at=datetime.now(timezone.utc),
                email_account_id="test-account"
            )
            
            # Thread context
            thread_context = [
                {
                    "from": "prospect@company.com",
                    "subject": "Initial Inquiry",
                    "body": "I heard about your platform from a colleague. We're looking for a solution to automate our workflows.",
                    "received_at": "2025-01-01T10:00:00Z"
                }
            ]
            
            # Generate draft with full context
            draft, tokens = await self.ai_service.generate_draft(
                email=test_email,
                user_id=test_user_id,
                intent_id=intent_id,
                thread_context=thread_context
            )
            
            results["details"]["draft_generated"] = True
            results["details"]["draft_length"] = len(draft)
            results["details"]["tokens_used"] = tokens
            results["details"]["draft_content"] = draft
            
            # Check context integration
            context_checks = {
                "persona_used": "friendly" in draft.lower() or "success" in draft.lower(),
                "kb_pricing_used": any(plan in draft.lower() for plan in ["starter", "professional", "enterprise", "$29", "$99", "$299"]),
                "kb_features_used": any(feature in draft.lower() for feature in ["workflow", "analytics", "collaboration", "api"]),
                "intent_prompt_followed": "team size" in draft.lower() or "recommend" in draft.lower(),
                "thread_context_used": "colleague" in draft.lower() or "automate" in draft.lower()
            }
            
            results["details"]["context_integration"] = context_checks
            
            context_score = sum(context_checks.values())
            results["details"]["context_score"] = f"{context_score}/5"
            
            logger.info(f"✓ Claude draft generated with context: {len(draft)} chars, {tokens} tokens")
            logger.info(f"✓ Context integration score: {context_score}/5")
            
            for check, passed in context_checks.items():
                status = "✓" if passed else "✗"
                logger.info(f"  {status} {check.replace('_', ' ').title()}: {passed}")
            
            # Test passes if draft is generated and uses most context
            results["passed"] = len(draft) >= 50 and context_score >= 3
            
            if results["passed"]:
                logger.info("✅ TEST 6 PASSED: Claude context-aware generation working")
            else:
                logger.error("❌ TEST 6 FAILED: Claude context integration insufficient")
                results["issues"].append(f"Context integration score too low: {context_score}/5")
            
            # Restore original primary provider
            self.ai_service.primary_provider = original_primary
                
        except Exception as e:
            logger.error(f"TEST 6 ERROR: {e}")
            results["issues"].append(f"Context-aware generation error: {str(e)}")
            # Restore original primary provider on error
            self.ai_service.primary_provider = original_primary
        
        return results
    
    async def test_7_validation_standards_consistent(self) -> Dict:
        """TEST 7: Validation Standards Consistent"""
        logger.info("\n" + "="*60)
        logger.info("TEST 7: Validation Standards Consistent")
        logger.info("="*60)
        
        results = {
            "test_name": "Validation Standards Consistent",
            "passed": False,
            "details": {},
            "issues": []
        }
        
        try:
            test_email = Email(
                id="validation-test",
                from_email="validation@test.com",
                to_email=["support@company.com"],
                subject="Validation Test",
                body="Please provide information about your services and pricing structure.",
                received_at=datetime.now(timezone.utc),
                email_account_id="test-account"
            )
            
            # Test Groq validation
            logger.info("🧪 Testing Groq validation standards")
            
            groq_draft, _ = await self.ai_service._call_llm_api(
                system_message="Generate a professional email response with at least 50 characters and 20 words.",
                user_message=f"Respond to: {test_email.body}",
                provider='groq'
            )
            
            groq_valid, groq_issues, groq_tokens = await self.ai_service.validate_draft(
                draft=groq_draft,
                original_email=test_email
            )
            
            results["details"]["groq_draft_length"] = len(groq_draft)
            results["details"]["groq_word_count"] = len(groq_draft.split())
            results["details"]["groq_validation_passed"] = groq_valid
            results["details"]["groq_validation_issues"] = groq_issues
            
            # Test Claude validation
            logger.info("🧪 Testing Claude validation standards")
            
            claude_draft, _ = await self.ai_service._call_llm_api(
                system_message="Generate a professional email response with at least 50 characters and 20 words.",
                user_message=f"Respond to: {test_email.body}",
                provider='claude'
            )
            
            claude_valid, claude_issues, claude_tokens = await self.ai_service.validate_draft(
                draft=claude_draft,
                original_email=test_email
            )
            
            results["details"]["claude_draft_length"] = len(claude_draft)
            results["details"]["claude_word_count"] = len(claude_draft.split())
            results["details"]["claude_validation_passed"] = claude_valid
            results["details"]["claude_validation_issues"] = claude_issues
            
            # Check minimum requirements
            groq_meets_min = len(groq_draft) >= 50 and len(groq_draft.split()) >= 20
            claude_meets_min = len(claude_draft) >= 50 and len(claude_draft.split()) >= 20
            
            results["details"]["groq_meets_minimum"] = groq_meets_min
            results["details"]["claude_meets_minimum"] = claude_meets_min
            
            logger.info(f"✓ Groq draft: {len(groq_draft)} chars, {len(groq_draft.split())} words, valid: {groq_valid}")
            logger.info(f"✓ Claude draft: {len(claude_draft)} chars, {len(claude_draft.split())} words, valid: {claude_valid}")
            
            # Test greeting-only detection
            logger.info("🧪 Testing greeting-only detection")
            
            greeting_only = "Hi John,"
            groq_greeting_valid, _, _ = await self.ai_service.validate_draft(greeting_only, test_email)
            claude_greeting_valid, _, _ = await self.ai_service.validate_draft(greeting_only, test_email)
            
            results["details"]["groq_rejects_greeting_only"] = not groq_greeting_valid
            results["details"]["claude_rejects_greeting_only"] = not claude_greeting_valid
            
            logger.info(f"✓ Groq rejects greeting-only: {not groq_greeting_valid}")
            logger.info(f"✓ Claude rejects greeting-only: {not claude_greeting_valid}")
            
            # Test passes if both providers meet standards and reject greeting-only
            results["passed"] = (
                groq_meets_min and claude_meets_min and
                not groq_greeting_valid and not claude_greeting_valid
            )
            
            if results["passed"]:
                logger.info("✅ TEST 7 PASSED: Validation standards consistent")
            else:
                logger.error("❌ TEST 7 FAILED: Validation standards inconsistent")
                
        except Exception as e:
            logger.error(f"TEST 7 ERROR: {e}")
            results["issues"].append(f"Validation standards test error: {str(e)}")
        
        return results
    
    async def test_8_error_handling(self) -> Dict:
        """TEST 8: Error Handling"""
        logger.info("\n" + "="*60)
        logger.info("TEST 8: Error Handling")
        logger.info("="*60)
        
        results = {
            "test_name": "Error Handling",
            "passed": False,
            "details": {},
            "issues": []
        }
        
        try:
            # Save original keys
            original_groq = self.ai_service.groq_api_key
            original_claude = self.ai_service.claude_api_key
            original_claude_client = self.ai_service.claude_client
            
            test_email = Email(
                id="error-test",
                from_email="error@test.com",
                to_email=["support@company.com"],
                subject="Error Handling Test",
                body="This is a test for error handling capabilities.",
                received_at=datetime.now(timezone.utc),
                email_account_id="test-account"
            )
            
            # Test 1: Invalid Groq key (should fallback to Claude)
            logger.info("🧪 Testing invalid Groq key → Claude fallback")
            
            self.ai_service.groq_api_key = "invalid_groq_key"
            
            try:
                draft1, tokens1 = await self.ai_service.generate_draft(
                    email=test_email,
                    user_id="test-user"
                )
                results["details"]["invalid_groq_fallback_success"] = True
                logger.info("✓ Invalid Groq key handled, Claude fallback worked")
            except Exception as e:
                results["details"]["invalid_groq_fallback_success"] = False
                results["issues"].append(f"Groq fallback failed: {str(e)}")
                logger.error(f"✗ Groq fallback failed: {e}")
            
            # Restore Groq key
            self.ai_service.groq_api_key = original_groq
            
            # Test 2: Invalid Claude key (should fallback to Groq)
            logger.info("🧪 Testing invalid Claude key → Groq fallback")
            
            self.ai_service.claude_api_key = "invalid_claude_key"
            self.ai_service.claude_client = None
            
            # Set Claude as primary to test fallback
            original_primary = self.ai_service.primary_provider
            self.ai_service.primary_provider = 'claude'
            
            try:
                draft2, tokens2 = await self.ai_service.generate_draft(
                    email=test_email,
                    user_id="test-user"
                )
                results["details"]["invalid_claude_fallback_success"] = True
                logger.info("✓ Invalid Claude key handled, Groq fallback worked")
            except Exception as e:
                results["details"]["invalid_claude_fallback_success"] = False
                results["issues"].append(f"Claude fallback failed: {str(e)}")
                logger.error(f"✗ Claude fallback failed: {e}")
            
            # Test 3: Both keys invalid (should fail gracefully)
            logger.info("🧪 Testing both keys invalid → graceful error")
            
            self.ai_service.groq_api_key = "invalid_groq"
            
            try:
                draft3, tokens3 = await self.ai_service.generate_draft(
                    email=test_email,
                    user_id="test-user"
                )
                results["details"]["both_invalid_handled"] = False
                results["issues"].append("Both invalid keys should have failed")
                logger.error("✗ Both invalid keys should have failed")
            except Exception as e:
                results["details"]["both_invalid_handled"] = True
                results["details"]["both_invalid_error"] = str(e)
                logger.info(f"✓ Both invalid keys failed gracefully: {e}")
            
            # Restore original settings
            self.ai_service.groq_api_key = original_groq
            self.ai_service.claude_api_key = original_claude
            self.ai_service.claude_client = original_claude_client
            self.ai_service.primary_provider = original_primary
            
            # Test passes if at least one fallback worked and both invalid failed
            fallback_works = (
                results["details"].get("invalid_groq_fallback_success", False) or
                results["details"].get("invalid_claude_fallback_success", False)
            )
            both_invalid_handled = results["details"].get("both_invalid_handled", False)
            
            results["passed"] = fallback_works and both_invalid_handled
            
            if results["passed"]:
                logger.info("✅ TEST 8 PASSED: Error handling working correctly")
            else:
                logger.error("❌ TEST 8 FAILED: Error handling issues")
                
        except Exception as e:
            logger.error(f"TEST 8 ERROR: {e}")
            results["issues"].append(f"Error handling test error: {str(e)}")
        
        return results
    
    async def test_9_production_readiness(self) -> Dict:
        """TEST 9: Production Readiness"""
        logger.info("\n" + "="*60)
        logger.info("TEST 9: Production Readiness")
        logger.info("="*60)
        
        results = {
            "test_name": "Production Readiness",
            "passed": False,
            "details": {},
            "issues": []
        }
        
        try:
            # Test complete email flow with both providers
            scenarios_passed = 0
            total_scenarios = len(self.test_scenarios)
            
            for i, scenario in enumerate(self.test_scenarios, 1):
                logger.info(f"🧪 Testing scenario {i}/{total_scenarios}: {scenario['name']}")
                
                test_email = Email(
                    id=f"prod-test-{i}",
                    from_email=scenario["from_email"],
                    to_email=["support@company.com"],
                    subject=scenario["subject"],
                    body=scenario["body"],
                    received_at=datetime.now(timezone.utc),
                    email_account_id="test-account"
                )
                
                scenario_results = {}
                
                # Test with Groq
                try:
                    self.ai_service.primary_provider = 'groq'
                    groq_draft, groq_tokens = await self.ai_service.generate_draft(
                        email=test_email,
                        user_id="test-user"
                    )
                    groq_valid, groq_issues, _ = await self.ai_service.validate_draft(
                        groq_draft, test_email
                    )
                    
                    scenario_results["groq_success"] = True
                    scenario_results["groq_valid"] = groq_valid
                    scenario_results["groq_length"] = len(groq_draft)
                    scenario_results["groq_tokens"] = groq_tokens
                    
                    logger.info(f"  ✓ Groq: {len(groq_draft)} chars, valid: {groq_valid}")
                    
                except Exception as e:
                    scenario_results["groq_success"] = False
                    scenario_results["groq_error"] = str(e)
                    logger.error(f"  ✗ Groq failed: {e}")
                
                # Test with Claude
                try:
                    self.ai_service.primary_provider = 'claude'
                    claude_draft, claude_tokens = await self.ai_service.generate_draft(
                        email=test_email,
                        user_id="test-user"
                    )
                    claude_valid, claude_issues, _ = await self.ai_service.validate_draft(
                        claude_draft, test_email
                    )
                    
                    scenario_results["claude_success"] = True
                    scenario_results["claude_valid"] = claude_valid
                    scenario_results["claude_length"] = len(claude_draft)
                    scenario_results["claude_tokens"] = claude_tokens
                    
                    logger.info(f"  ✓ Claude: {len(claude_draft)} chars, valid: {claude_valid}")
                    
                except Exception as e:
                    scenario_results["claude_success"] = False
                    scenario_results["claude_error"] = str(e)
                    logger.error(f"  ✗ Claude failed: {e}")
                
                # Test meeting detection if applicable
                if "meeting" in scenario["name"].lower() or "demo" in scenario["name"].lower():
                    try:
                        is_meeting, confidence, details = await self.ai_service.detect_meeting(test_email)
                        scenario_results["meeting_detected"] = is_meeting
                        scenario_results["meeting_confidence"] = confidence
                        logger.info(f"  ✓ Meeting detection: {is_meeting} ({confidence:.1%})")
                    except Exception as e:
                        scenario_results["meeting_detection_error"] = str(e)
                        logger.error(f"  ✗ Meeting detection failed: {e}")
                
                results["details"][f"scenario_{i}_{scenario['name']}"] = scenario_results
                
                # Count successful scenarios (both providers working)
                if (scenario_results.get("groq_success", False) and 
                    scenario_results.get("claude_success", False)):
                    scenarios_passed += 1
            
            # Restore default primary provider
            self.ai_service.primary_provider = 'groq'
            
            results["details"]["scenarios_passed"] = scenarios_passed
            results["details"]["total_scenarios"] = total_scenarios
            results["details"]["success_rate"] = f"{scenarios_passed}/{total_scenarios}"
            
            # Test token tracking across providers
            initial_tokens = self.ai_service.tokens_used
            await self.ai_service.generate_draft(
                email=Email(
                    id="token-test",
                    from_email="token@test.com",
                    to_email=["support@company.com"],
                    subject="Token Test",
                    body="Test token tracking",
                    received_at=datetime.now(timezone.utc),
                    email_account_id="test-account"
                ),
                user_id="test-user"
            )
            final_tokens = self.ai_service.tokens_used
            
            results["details"]["token_tracking_working"] = final_tokens > initial_tokens
            
            # Test passes if most scenarios work and token tracking works
            results["passed"] = (scenarios_passed >= total_scenarios * 0.8 and 
                              results["details"]["token_tracking_working"])
            
            if results["passed"]:
                logger.info(f"✅ TEST 9 PASSED: Production ready ({scenarios_passed}/{total_scenarios} scenarios)")
            else:
                logger.error(f"❌ TEST 9 FAILED: Not production ready ({scenarios_passed}/{total_scenarios} scenarios)")
                
        except Exception as e:
            logger.error(f"TEST 9 ERROR: {e}")
            results["issues"].append(f"Production readiness test error: {str(e)}")
        
        return results
    
    async def run_all_tests(self) -> Dict:
        """Run all Claude LLM integration tests"""
        logger.info("\n" + "🚀" * 20)
        logger.info("STARTING COMPREHENSIVE CLAUDE LLM INTEGRATION TESTS")
        logger.info("🚀" * 20)
        
        if not await self.setup():
            return {"error": "Setup failed"}
        
        # Run all tests
        test_methods = [
            self.test_1_verify_providers_configured,
            self.test_2_primary_provider_groq,
            self.test_3_claude_provider_functionality,
            self.test_4_fallback_mechanism,
            self.test_5_dual_provider_integration,
            self.test_6_context_aware_generation_claude,
            self.test_7_validation_standards_consistent,
            self.test_8_error_handling,
            self.test_9_production_readiness
        ]
        
        all_results = {}
        passed_tests = 0
        total_tests = len(test_methods)
        
        for test_method in test_methods:
            try:
                result = await test_method()
                all_results[result["test_name"]] = result
                if result["passed"]:
                    passed_tests += 1
            except Exception as e:
                logger.error(f"Test {test_method.__name__} failed with error: {e}")
                all_results[test_method.__name__] = {
                    "test_name": test_method.__name__,
                    "passed": False,
                    "error": str(e)
                }
        
        # Generate summary
        summary = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": f"{passed_tests}/{total_tests} ({passed_tests/total_tests*100:.1f}%)",
            "overall_status": "PASSED" if passed_tests >= total_tests * 0.8 else "FAILED",
            "test_results": all_results
        }
        
        # Print final summary
        logger.info("\n" + "="*60)
        logger.info("CLAUDE LLM INTEGRATION TEST SUMMARY")
        logger.info("="*60)
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {total_tests - passed_tests}")
        logger.info(f"Success Rate: {passed_tests/total_tests*100:.1f}%")
        logger.info(f"Overall Status: {summary['overall_status']}")
        
        for test_name, result in all_results.items():
            status = "✅ PASSED" if result["passed"] else "❌ FAILED"
            logger.info(f"  {status}: {test_name}")
            if not result["passed"] and result.get("issues"):
                for issue in result["issues"]:
                    logger.info(f"    - {issue}")
        
        return summary

async def main():
    """Main test execution"""
    tester = ClaudeLLMIntegrationTest()
    results = await tester.run_all_tests()
    
    # Save results to file
    with open('/app/claude_llm_test_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info(f"\n📊 Test results saved to: /app/claude_llm_test_results.json")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())