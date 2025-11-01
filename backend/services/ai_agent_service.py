import json
from typing import List, Optional, Dict, Tuple
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging
import httpx
from datetime import datetime, timezone

from config import config
from models.email import Email
from models.intent import Intent
from models.knowledge_base import KnowledgeBase

logger = logging.getLogger(__name__)

class AIAgentService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.groq_api_key = config.GROQ_API_KEY
        self.cohere_api_key = config.COHERE_API_KEY
        self.tokens_used = 0
    
    async def classify_intent(self, email: Email, user_id: str) -> Tuple[Optional[str], float]:
        """Classify email intent using keywords and Cohere"""
        try:
            # Get user intents
            intents = await self.db.intents.find({"user_id": user_id, "is_active": True}).sort("priority", -1).to_list(100)
            
            if not intents:
                return None, 0.0
            
            # First try keyword matching
            email_text = f"{email.subject} {email.body}".lower()
            
            for intent_doc in intents:
                intent = Intent(**intent_doc)
                for keyword in intent.keywords:
                    if keyword.lower() in email_text:
                        logger.info(f"Intent '{intent.name}' matched by keyword: {keyword}")
                        return intent.id, 0.9  # High confidence for keyword match
            
            # Fallback to Cohere classification
            # For MVP, we'll use simple keyword matching only to save costs
            # In production, you can add Cohere classification here
            
            return None, 0.0
        except Exception as e:
            logger.error(f"Error classifying intent: {e}")
            return None, 0.0
    
    async def detect_meeting(self, email: Email, thread_context: List[Dict] = None) -> Tuple[bool, float, Optional[Dict]]:
        """Detect if email contains meeting request using Groq with thread context"""
        try:
            current_time = config.get_datetime_string()
            
            # Build thread context string
            thread_str = ""
            if thread_context:
                thread_str = "\n\nPrevious messages in this thread:\n"
                for msg in thread_context:
                    thread_str += f"From: {msg['from']} | {msg['received_at']}\nSubject: {msg['subject']}\nBody: {msg['body'][:200]}...\n\n"
            
            prompt = f"""Current Date & Time: {current_time}
{thread_str}

Analyze this email and determine if it contains a meeting request or invitation.

Email Subject: {email.subject}
Email Body: {email.body}

If a meeting is detected, extract:
1. Meeting date and time (convert to ISO format YYYY-MM-DDTHH:MM:SS)
2. Duration or end time
3. Location (physical or virtual)
4. Meeting title/purpose
5. Attendees

IMPORTANT: Use the thread context to avoid extracting duplicate meeting information if this is a follow-up message about an existing meeting.

Respond in JSON format:
{{
  "is_meeting": true/false,
  "confidence": 0.0-1.0,
  "details": {{
    "title": "...",
    "start_time": "2025-01-15T14:00:00",
    "end_time": "2025-01-15T15:00:00",
    "location": "...",
    "description": "...",
    "attendees": ["email@example.com"]
  }}
}}

If no meeting detected, set is_meeting to false and confidence to 0.0."""
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    'https://api.groq.com/openai/v1/chat/completions',
                    headers={
                        'Authorization': f'Bearer {self.groq_api_key}',
                        'Content-Type': 'application/json'
                    },
                    json={
                        'model': config.GROQ_CALENDAR_MODEL,
                        'messages': [
                            {'role': 'system', 'content': 'You are a meeting detection AI. Always respond with valid JSON.'},
                            {'role': 'user', 'content': prompt}
                        ],
                        'temperature': 0.3,
                        'max_tokens': 500
                    }
                )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                # Track tokens
                usage = result.get('usage', {})
                tokens = usage.get('total_tokens', 0)
                self.tokens_used += tokens
                
                # Parse JSON response
                try:
                    data = json.loads(content)
                    is_meeting = data.get('is_meeting', False)
                    confidence = data.get('confidence', 0.0)
                    details = data.get('details')
                    
                    return is_meeting, confidence, details
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse meeting detection JSON: {content}")
                    return False, 0.0, None
            else:
                logger.error(f"Groq API error: {response.status_code} - {response.text}")
                return False, 0.0, None
        except Exception as e:
            logger.error(f"Error detecting meeting: {e}")
            return False, 0.0, None
    
    async def generate_draft(self, email: Email, user_id: str, intent_id: Optional[str] = None, 
                            thread_context: List[Dict] = None, validation_issues: List[str] = None) -> Tuple[str, int]:
        """Generate email draft using Groq (Draft Agent) with thread context"""
        try:
            current_time = config.get_datetime_string()
            
            # Get context
            context = await self._get_draft_context(user_id, email.email_account_id, intent_id)
            
            # Build thread context
            thread_str = ""
            if thread_context and len(thread_context) > 0:
                thread_str = "\n\nPrevious messages in this conversation:\n" + "="*50 + "\n"
                for i, msg in enumerate(thread_context, 1):
                    thread_str += f"Message {i}:\nFrom: {msg['from']}\nTo: {', '.join(msg['to'])}\nDate: {msg['received_at']}\nSubject: {msg['subject']}\nBody:\n{msg['body']}\n\n"
                    if msg.get('draft_sent'):
                        thread_str += f"Our Response:\n{msg['draft_sent']}\n\n"
                    thread_str += "="*50 + "\n"
            
            # Build validation feedback
            feedback_str = ""
            if validation_issues:
                feedback_str = f"\n\nPrevious draft had these issues (MUST FIX):\n" + "\n".join([f"- {issue}" for issue in validation_issues])
            
            prompt = f"""Current Date & Time: {current_time}

You are an AI email assistant. Generate a professional email response.

{context}
{thread_str}

Incoming Email:
From: {email.from_email}
Subject: {email.subject}
Body: {email.body}
{feedback_str}

Generate a clear, professional response that:
1. Addresses all points from the email
2. Matches the persona and tone
3. Uses information from the knowledge base if relevant
4. Includes the signature
5. Is concise and actionable
6. Contains NO placeholders like [Your Name] or [Date]
7. IMPORTANT: Use thread context to avoid repeating information already discussed
8. Do NOT repeat meeting details or calendar information already sent
9. If validation issues provided, fix them specifically

Respond with ONLY the email body text, no subject line."""
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    'https://api.groq.com/openai/v1/chat/completions',
                    headers={
                        'Authorization': f'Bearer {self.groq_api_key}',
                        'Content-Type': 'application/json'
                    },
                    json={
                        'model': config.GROQ_DRAFT_MODEL,
                        'messages': [
                            {'role': 'system', 'content': 'You are a professional email writing assistant. Write clear, actionable emails with no placeholders.'},
                            {'role': 'user', 'content': prompt}
                        ],
                        'temperature': 0.7,
                        'max_tokens': 800
                    }
                )
            
            if response.status_code == 200:
                result = response.json()
                draft = result['choices'][0]['message']['content'].strip()
                
                # Track tokens
                usage = result.get('usage', {})
                tokens = usage.get('total_tokens', 0)
                self.tokens_used += tokens
                
                return draft, tokens
            else:
                logger.error(f"Groq API error: {response.status_code} - {response.text}")
                return "Error generating draft", 0
        except Exception as e:
            logger.error(f"Error generating draft: {e}")
            return f"Error: {str(e)}", 0
    
    async def validate_draft(self, draft: str, email: Email, user_id: str, intent_id: Optional[str] = None,
                            thread_context: List[Dict] = None) -> Tuple[bool, List[str]]:
        """Validate draft using Groq (Validation Agent) with thread context"""
        try:
            current_time = config.get_datetime_string()
            
            # Get intent prompt if available
            intent_prompt = ""
            if intent_id:
                intent_doc = await self.db.intents.find_one({"id": intent_id})
                if intent_doc:
                    intent = Intent(**intent_doc)
                    intent_prompt = f"Intent: {intent.name}\nIntent Requirements: {intent.prompt}"
            
            # Build thread context for validation
            thread_str = ""
            if thread_context and len(thread_context) > 0:
                thread_str = "\n\nPrevious messages in thread:\n"
                for msg in thread_context:
                    if msg.get('draft_sent'):
                        thread_str += f"We already sent: {msg['draft_sent'][:300]}...\n"
            
            prompt = f"""Current Date & Time: {current_time}

You are a validation AI. Check if this email draft meets quality standards.

Original Email:
Subject: {email.subject}
Body: {email.body}

Generated Draft:
{draft}

{intent_prompt}
{thread_str}

Validation Checklist:
1. No placeholders like [Name], [Date], [Your Company]
2. All points from original email are addressed
3. Professional tone
4. Clear and concise
5. Actionable (if needed)
6. Matches intent requirements (if specified)
7. CRITICAL: NOT repeating information already sent in previous messages
8. NOT sending duplicate meeting details or calendar information

Respond in JSON:
{{
  "valid": true/false,
  "issues": ["list of issues found, empty if valid"]
}}"""
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    'https://api.groq.com/openai/v1/chat/completions',
                    headers={
                        'Authorization': f'Bearer {self.groq_api_key}',
                        'Content-Type': 'application/json'
                    },
                    json={
                        'model': config.GROQ_VALIDATION_MODEL,
                        'messages': [
                            {'role': 'system', 'content': 'You are a validation AI. Always respond with valid JSON.'},
                            {'role': 'user', 'content': prompt}
                        ],
                        'temperature': 0.2,
                        'max_tokens': 300
                    }
                )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                # Track tokens
                usage = result.get('usage', {})
                tokens = usage.get('total_tokens', 0)
                self.tokens_used += tokens
                
                try:
                    data = json.loads(content)
                    valid = data.get('valid', False)
                    issues = data.get('issues', [])
                    return valid, issues
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse validation JSON: {content}")
                    return True, []  # Assume valid if parse fails
            else:
                logger.error(f"Groq API error: {response.status_code} - {response.text}")
                return True, []
        except Exception as e:
            logger.error(f"Error validating draft: {e}")
            return True, []
    
    async def _get_draft_context(self, user_id: str, account_id: str, intent_id: Optional[str] = None) -> str:
        """Get context for draft generation"""
        context_parts = []
        
        # Get account details (persona, signature)
        account_doc = await self.db.email_accounts.find_one({"id": account_id})
        if account_doc:
            if account_doc.get('persona'):
                context_parts.append(f"Persona: {account_doc['persona']}")
            if account_doc.get('signature'):
                context_parts.append(f"Signature: {account_doc['signature']}")
        
        # Get intent
        if intent_id:
            intent_doc = await self.db.intents.find_one({"id": intent_id})
            if intent_doc:
                intent = Intent(**intent_doc)
                context_parts.append(f"Intent: {intent.name}")
                context_parts.append(f"Response Guidelines: {intent.prompt}")
        
        # Get relevant knowledge base (simple: get all active KB)
        kb_docs = await self.db.knowledge_base.find({"user_id": user_id, "is_active": True}).limit(5).to_list(5)
        if kb_docs:
            kb_text = "\n".join([f"- {doc['title']}: {doc['content'][:200]}..." for doc in kb_docs])
            context_parts.append(f"Knowledge Base:\n{kb_text}")
        
        return "\n\n".join(context_parts)
    
    async def check_meeting_details_complete(self, meeting_details: Dict) -> Tuple[bool, List[str]]:
        """Check if meeting details are complete and confirmed"""
        missing_fields = []
        
        # Check required fields
        if not meeting_details.get('start_time'):
            missing_fields.append('start time')
        if not meeting_details.get('end_time'):
            missing_fields.append('end time')
        if not meeting_details.get('title'):
            missing_fields.append('meeting title/purpose')
        
        # Validate date format and timezone
        try:
            if meeting_details.get('start_time'):
                datetime.fromisoformat(meeting_details['start_time'].replace('Z', '+00:00'))
            if meeting_details.get('end_time'):
                datetime.fromisoformat(meeting_details['end_time'].replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            missing_fields.append('valid date/time format')
        
        # Check if timezone is specified or assume UTC
        if not meeting_details.get('timezone'):
            # If no timezone, we'll assume UTC but flag it
            meeting_details['timezone'] = 'UTC'
        
        is_complete = len(missing_fields) == 0
        return is_complete, missing_fields
    
    async def generate_meeting_confirmation_email(self, email: Email, meeting_details: Dict, 
                                                   missing_fields: List[str] = None) -> str:
        """Generate confirmation email for meeting details"""
        try:
            current_time = config.get_datetime_string()
            
            # Get account context
            account_doc = await self.db.email_accounts.find_one({"id": email.email_account_id})
            signature = account_doc.get('signature', '') if account_doc else ''
            
            missing_str = ""
            if missing_fields:
                missing_str = f"\n\nI noticed the following details are unclear or missing:\n" + "\n".join([f"- {field}" for field in missing_fields])
            
            prompt = f"""Current Date & Time: {current_time}

Generate a professional confirmation email for a meeting request.

Original Email:
From: {email.from_email}
Subject: {email.subject}
Body: {email.body}

Detected Meeting Details:
- Title: {meeting_details.get('title', 'Not specified')}
- Date & Time: {meeting_details.get('start_time', 'Not specified')} to {meeting_details.get('end_time', 'Not specified')}
- Timezone: {meeting_details.get('timezone', 'UTC')}
- Location: {meeting_details.get('location', 'Not specified')}
- Description: {meeting_details.get('description', 'Not specified')}
{missing_str}

Write a brief, professional email that:
1. Confirms the meeting details listed above
2. Politely asks for clarification on any missing details
3. Requests the recipient to confirm or correct the details
4. Is warm and professional in tone
5. Includes the signature at the end

Signature to use:
{signature}

Respond with ONLY the email body text."""
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    'https://api.groq.com/openai/v1/chat/completions',
                    headers={
                        'Authorization': f'Bearer {self.groq_api_key}',
                        'Content-Type': 'application/json'
                    },
                    json={
                        'model': config.GROQ_DRAFT_MODEL,
                        'messages': [
                            {'role': 'system', 'content': 'You are a professional email assistant. Write clear, concise confirmation emails.'},
                            {'role': 'user', 'content': prompt}
                        ],
                        'temperature': 0.7,
                        'max_tokens': 500
                    }
                )
            
            if response.status_code == 200:
                result = response.json()
                confirmation_email = result['choices'][0]['message']['content'].strip()
                
                # Track tokens
                usage = result.get('usage', {})
                tokens = usage.get('total_tokens', 0)
                self.tokens_used += tokens
                
                return confirmation_email
            else:
                logger.error(f"Groq API error: {response.status_code} - {response.text}")
                return "Error generating confirmation email"
        except Exception as e:
            logger.error(f"Error generating confirmation email: {e}")
            return f"Error: {str(e)}"
    
    def get_tokens_used(self) -> int:
        """Get total tokens used"""
        return self.tokens_used
