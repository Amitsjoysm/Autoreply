"""
AI Agent Service - Production-Ready Implementation
Handles all AI operations: intent classification, meeting detection, draft generation, and validation
Uses Groq API for all AI operations
"""
import json
import logging
from typing import List, Optional, Dict, Tuple
from datetime import datetime, timezone
import httpx
from motor.motor_asyncio import AsyncIOMotorDatabase

from config import config
from models.email import Email
from models.intent import Intent
from models.knowledge_base import KnowledgeBase
from services.date_parser_service import DateParserService
from services.signature_handler import SignatureHandler

logger = logging.getLogger(__name__)


class AIAgentService:
    """
    Service for all AI operations in the email assistant
    - Intent classification using keyword matching
    - Meeting detection using Groq LLM
    - Draft generation using Groq LLM with context
    - Draft validation using Groq LLM
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.groq_api_key = config.GROQ_API_KEY
        self.tokens_used = 0
        self.date_parser = DateParserService()
        
        if not self.groq_api_key:
            logger.error("GROQ_API_KEY not configured! AI features will not work.")
    
    # ============================================================================
    # INTENT CLASSIFICATION
    # ============================================================================
    
    async def classify_intent(self, email: Email, user_id: str) -> Tuple[Optional[str], float, Optional[Dict]]:
        """
        Classify email intent using improved keyword matching
        
        IMPROVED ALGORITHM:
        - Counts keyword matches for each intent
        - Selects intent with most keyword matches
        - Uses priority as tiebreaker
        - Better accuracy for overlapping keywords
        
        Returns:
            Tuple of (intent_id, confidence, intent_dict)
            - intent_id: The matched intent ID or None
            - confidence: 0.0-1.0 (0.9 for keyword match, 0.5 for default)
            - intent_dict: Full intent document or None
        """
        try:
            # Get all active intents for user, sorted by priority
            intents = await self.db.intents.find({
                "user_id": user_id,
                "is_active": True
            }).sort("priority", -1).to_list(100)
            
            if not intents:
                logger.warning(f"No intents found for user {user_id}")
                return None, 0.0, None
            
            # Prepare email text for matching
            email_text = f"{email.subject} {email.body}".lower()
            
            # Count keyword matches for each intent
            intent_scores = []
            
            for intent_doc in intents:
                # Skip default intent in keyword matching
                if intent_doc.get('is_default', False):
                    continue
                
                # Convert datetime fields to ISO strings for Pydantic compatibility
                self._convert_datetime_fields(intent_doc)
                
                intent = Intent(**intent_doc)
                
                # Count matching keywords
                matched_keywords = []
                for keyword in intent.keywords:
                    if keyword.lower() in email_text:
                        matched_keywords.append(keyword)
                
                if matched_keywords:
                    intent_scores.append({
                        'intent_doc': intent_doc,
                        'match_count': len(matched_keywords),
                        'priority': intent.priority,
                        'name': intent.name,
                        'matched_keywords': matched_keywords
                    })
            
            # If we have matches, select the best one
            if intent_scores:
                # Sort by: 1) match_count (desc), 2) priority (desc)
                intent_scores.sort(key=lambda x: (x['match_count'], x['priority']), reverse=True)
                
                best_match = intent_scores[0]
                logger.info(f"✓ Intent '{best_match['name']}' matched with {best_match['match_count']} keywords: {', '.join(best_match['matched_keywords'][:3])}")
                
                # If there's a tie in match count, log it for debugging
                if len(intent_scores) > 1 and intent_scores[1]['match_count'] == best_match['match_count']:
                    logger.info(f"  → Tiebreaker: Priority {best_match['priority']} > {intent_scores[1]['priority']} ({intent_scores[1]['name']})")
                
                return best_match['intent_doc']['id'], 0.9, best_match['intent_doc']
            
            # No keyword match - check for default intent
            default_intent = next(
                (i for i in intents if i.get('is_default', False)),
                None
            )
            
            if default_intent:
                self._convert_datetime_fields(default_intent)
                logger.info("Using default intent for unmatched email")
                return default_intent['id'], 0.5, default_intent
            
            logger.warning(f"No matching intent found for email: {email.subject}")
            return None, 0.0, None
            
        except Exception as e:
            logger.error(f"Error classifying intent: {e}", exc_info=True)
            return None, 0.0, None
    
    # ============================================================================
    # TIME REFERENCE DETECTION
    # ============================================================================
    
    async def detect_time_reference(self, email: Email) -> List[Dict]:
        """
        Detect time-based follow-up requests in email
        
        Returns:
            List of time references with target dates and context
            [
                {
                    'matched_text': 'next quarter',
                    'target_date': datetime,
                    'context': 'surrounding text',
                    'original_email_body': full email body for reference
                }
            ]
        """
        try:
            # Combine subject and body for analysis
            full_text = f"{email.subject}\n\n{email.body}"
            
            # Parse time references
            time_refs = self.date_parser.parse_time_references(full_text)
            
            if not time_refs:
                return []
            
            results = []
            for matched_text, target_date, context in time_refs:
                results.append({
                    'matched_text': matched_text,
                    'target_date': target_date,
                    'context': context,
                    'original_email_body': email.body[:500]  # First 500 chars for context
                })
            
            logger.info(f"Found {len(results)} time references in email {email.id}")
            return results
            
        except Exception as e:
            logger.error(f"Error detecting time reference: {e}")
            return []
    
    # ============================================================================
    # SIMPLE REPLY DETECTION
    # ============================================================================
    
    def is_simple_acknowledgment(self, email: Email) -> bool:
        """
        Detect if email is a simple acknowledgment that doesn't need follow-up
        
        Examples:
        - "Thanks", "Thank you", "Thanks!"
        - "Got it", "Received", "Noted"
        - "OK", "Okay", "Sure"
        - "Appreciate it", "Much appreciated"
        
        Returns:
            True if this is a simple acknowledgment (no follow-up needed)
        """
        # Combine subject and body
        full_text = f"{email.subject}\n{email.body}".lower().strip()
        
        # Remove common email signatures and footers
        lines = [line.strip() for line in full_text.split('\n') if line.strip()]
        
        # If email is very short (1-3 lines), check for simple acknowledgments
        if len(lines) <= 3:
            content = ' '.join(lines)
            
            # Simple acknowledgment patterns
            simple_patterns = [
                r'\b(thanks?|thank you|thx|ty)\b',
                r'\b(got it|received|noted|understood)\b',
                r'\b(ok|okay|sure|alright)\b',
                r'\b(appreciate it|appreciated|much appreciated)\b',
                r'\b(will do|sounds good|perfect)\b',
                r'\b(no problem|no worries)\b',
                r'^\s*👍\s*$',  # Just a thumbs up emoji
            ]
            
            import re
            for pattern in simple_patterns:
                if re.search(pattern, content):
                    # Make sure there's no time reference or request
                    request_patterns = [
                        r'\b(when|where|how|what|why|can you|could you|would you|please)\b',
                        r'\b(need|want|require|request|asking|question)\b',
                        r'\b(follow up|get back|touch base|reach out)\b',
                    ]
                    
                    has_request = any(re.search(p, content) for p in request_patterns)
                    
                    if not has_request and len(content) < 100:
                        logger.info(f"Email {email.id} detected as simple acknowledgment")
                        return True
        
        return False
    
    # ============================================================================
    # MEETING DETECTION
    # ============================================================================
    
    async def detect_meeting(
        self, 
        email: Email, 
        thread_context: List[Dict] = None
    ) -> Tuple[bool, float, Optional[Dict]]:
        """
        Detect if email contains meeting request using Groq LLM
        
        Returns:
            Tuple of (is_meeting, confidence, details)
            - is_meeting: True if meeting detected
            - confidence: 0.0-1.0 (0.8+ for explicit, 0.6-0.8 for implied)
            - details: Dict with meeting details (title, start_time, end_time, location, etc.)
        """
        try:
            current_time = config.get_datetime_string()
            current_year = datetime.now(timezone.utc).year
            
            # Build prompt with thread context
            prompt = self._build_meeting_detection_prompt(
                email, 
                thread_context, 
                current_time, 
                current_year
            )
            
            # Call Groq API
            result = await self._call_groq_api(
                system_message="You are a meeting detection AI. Analyze emails and extract meeting details. Always respond with valid JSON.",
                user_message=prompt,
                temperature=0.3,
                max_tokens=500
            )
            
            # Parse response
            data = self._parse_json_response(result)
            
            is_meeting = data.get('is_meeting', False)
            confidence = data.get('confidence', 0.0)
            details = data.get('details')
            
            if is_meeting:
                logger.info(f"✓ Meeting detected with confidence {confidence}: {details.get('title', 'Untitled')}")
            
            return is_meeting, confidence, details
            
        except Exception as e:
            logger.error(f"Error detecting meeting: {e}", exc_info=True)
            return False, 0.0, None
    
    def _build_meeting_detection_prompt(
        self, 
        email: Email, 
        thread_context: List[Dict],
        current_time: str,
        current_year: int
    ) -> str:
        """Build meeting detection prompt with thread context"""
        
        # Thread context
        thread_str = ""
        if thread_context:
            thread_str = "\n\nPrevious messages in this thread:\n"
            for msg in thread_context:
                thread_str += f"From: {msg['from']} | {msg['received_at']}\n"
                thread_str += f"Subject: {msg['subject']}\n"
                thread_str += f"Body: {msg['body'][:200]}...\n\n"
        
        return f"""Current Date & Time: {current_time} (UTC)
{thread_str}

Analyze this email and determine if it contains a meeting request, invitation, or scheduling discussion.

Email Subject: {email.subject}
Email Body: {email.body}

MEETING DETECTION RULES:
1. Look for explicit meeting requests or invitations
2. Look for date/time mentions with context of scheduling
3. Check for meeting-related keywords: meeting, call, zoom, teams, schedule, discuss, sync, catch up
4. Ignore casual mentions like "let's meet sometime" without specific details
5. Use thread context to avoid duplicates - if meeting already discussed, confidence should be lower

If a meeting is detected, extract:
1. Meeting date and time:
   - Convert to ISO format: YYYY-MM-DDTHH:MM:SS
   - If timezone mentioned, convert to UTC
   - If no year mentioned, assume {current_year}
   - If only date mentioned, assume 10:00 AM UTC
   - Handle relative dates: "tomorrow", "next Tuesday", etc.

2. Duration/end time:
   - If duration mentioned, calculate end time
   - Default to 1 hour if not specified
   - Format: YYYY-MM-DDTHH:MM:SS

3. Location: physical address, virtual link, or 'TBD'

4. Meeting title: extract or infer from context

5. Attendees: email addresses mentioned

Respond in JSON format:
{{
  "is_meeting": true/false,
  "confidence": 0.0-1.0,
  "details": {{
    "title": "Meeting title",
    "start_time": "2025-01-15T14:00:00",
    "end_time": "2025-01-15T15:00:00",
    "location": "Location or 'Virtual' or 'TBD'",
    "description": "Brief description",
    "attendees": ["email@example.com"],
    "timezone": "UTC"
  }}
}}

If no clear meeting detected, set is_meeting to false and confidence to 0.0."""
    
    # ============================================================================
    # DRAFT GENERATION
    # ============================================================================
    
    async def generate_draft(
        self,
        email: Email,
        user_id: str,
        intent_id: Optional[str] = None,
        thread_context: List[Dict] = None,
        validation_issues: List[str] = None,
        calendar_event = None,
        follow_up_context: Optional[Dict] = None
    ) -> Tuple[str, int]:
        """
        Generate email draft using Groq LLM with full context
        
        Args:
            follow_up_context: Optional dict with:
                - is_automated_followup: bool
                - base_date: str (target date user mentioned)
                - matched_text: str (original time reference)
                - original_context: str (context from original email)
        
        Returns:
            Tuple of (draft_text, tokens_used)
        """
        try:
            current_time = config.get_datetime_string()
            
            # Get all context (persona, KB, intent)
            context = await self._get_draft_context(user_id, email.email_account_id, intent_id)
            
            # Build comprehensive prompt
            prompt = self._build_draft_generation_prompt(
                email=email,
                context=context,
                thread_context=thread_context,
                validation_issues=validation_issues,
                calendar_event=calendar_event,
                current_time=current_time,
                follow_up_context=follow_up_context
            )
            
            system_message = self._get_draft_system_message(context)
            
            # Call Groq API
            result = await self._call_groq_api(
                system_message=system_message,
                user_message=prompt,
                temperature=0.7,
                max_tokens=800
            )
            
            draft = result.strip()
            
            # Remove any AI-generated signature to prevent double signatures
            draft = SignatureHandler.remove_ai_signature(draft)
            
            logger.info(f"✓ Draft generated ({len(draft)} chars, signature removed)")
            
            return draft, self.tokens_used
            
        except Exception as e:
            logger.error(f"Error generating draft: {e}", exc_info=True)
            raise
    
    def _build_draft_generation_prompt(
        self,
        email: Email,
        context: Dict,
        thread_context: List[Dict],
        validation_issues: List[str],
        calendar_event,
        current_time: str,
        follow_up_context: Optional[Dict] = None
    ) -> str:
        """Build comprehensive draft generation prompt"""
        
        prompt = f"Current Date & Time: {current_time}\n\n"
        
        # Add follow-up context if this is an automated follow-up
        if follow_up_context and follow_up_context.get('is_automated_followup'):
            prompt += "🔔 THIS IS AN AUTOMATED FOLLOW-UP\n"
            prompt += "="*50 + "\n"
            prompt += f"Original Request: {follow_up_context.get('matched_text', 'N/A')}\n"
            prompt += f"Target Date User Mentioned: {follow_up_context.get('base_date', 'N/A')}\n"
            prompt += f"Original Context: {follow_up_context.get('original_context', 'N/A')}\n"
            prompt += "\nYou are now following up as requested by the sender.\n"
            prompt += "Reference the original request naturally and provide a helpful update or check-in.\n"
            prompt += "="*50 + "\n\n"
        
        # Add persona
        if context['persona']:
            prompt += f"YOUR PERSONA:\n{context['persona']}\n\n"
        
        # Add knowledge base
        if context['knowledge_base']:
            prompt += "KNOWLEDGE BASE - Use this information to answer questions:\n"
            for kb in context['knowledge_base']:
                prompt += f"\n[{kb['category']}] {kb['title']}\n{kb['content']}\n"
            prompt += "\n"
        
        # Add intent-specific instructions
        if context['intent_prompt']:
            prompt += f"INTENT-SPECIFIC INSTRUCTIONS:\n{context['intent_prompt']}\n\n"
        
        # Add thread context
        if thread_context:
            prompt += "PREVIOUS CONVERSATION:\n" + "="*50 + "\n"
            for i, msg in enumerate(thread_context, 1):
                prompt += f"Message {i}:\n"
                prompt += f"From: {msg['from']}\n"
                prompt += f"Date: {msg['received_at']}\n"
                prompt += f"Subject: {msg['subject']}\n"
                prompt += f"Body:\n{msg['body']}\n\n"
                if msg.get('draft_sent'):
                    prompt += f"Our Previous Response:\n{msg['draft_sent']}\n\n"
                prompt += "="*50 + "\n"
        
        # Add validation feedback
        if validation_issues:
            prompt += "\n⚠️ PREVIOUS DRAFT HAD ISSUES - MUST FIX:\n"
            for issue in validation_issues:
                prompt += f"- {issue}\n"
            prompt += "\n"
        
        # Add calendar event info
        if calendar_event:
            prompt += self._format_calendar_event(calendar_event)
        
        # Add current email
        if follow_up_context and follow_up_context.get('is_automated_followup'):
            prompt += f"""THIS IS A FOLLOW-UP EMAIL - NO NEW INCOMING EMAIL
Generate a follow-up message based on the conversation history above.
Reference the original request and provide a helpful check-in or update.
"""
        else:
            prompt += f"""CURRENT EMAIL TO RESPOND TO:
From: {email.from_email}
To: {', '.join(email.to_email)}
Subject: {email.subject}
Body:
{email.body}

Generate a professional email response. Only include the body text - no subject line, no greetings like "Dear [Name]" unless it's a formal business context. Be natural, helpful, and use the knowledge base to provide accurate information."""
        
        return prompt
    
    def _format_calendar_event(self, calendar_event) -> str:
        """Format calendar event details for prompt"""
        
        # Handle both dict and Pydantic model
        if hasattr(calendar_event, 'model_dump'):
            event = calendar_event.model_dump()
        else:
            event = calendar_event
        
        calendar_str = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 CALENDAR EVENT CREATED - MUST MENTION IN RESPONSE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Title: {event.get('title')}
Date & Time: {event.get('start_time')} to {event.get('end_time')} ({event.get('timezone', 'UTC')})
Location: {event.get('location') or 'Virtual Meeting'}
"""
        
        if event.get('meet_link'):
            calendar_str += f"Google Meet Link: {event.get('meet_link')}\n"
        if event.get('html_link'):
            calendar_str += f"View in Calendar: {event.get('html_link')}\n"
        if event.get('attendees'):
            calendar_str += f"Attendees: {', '.join(event.get('attendees', []))}\n"
        
        calendar_str += """━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

IMPORTANT: You MUST include in your response:
1. Confirm the meeting has been scheduled
2. Provide the date, time, and timezone
3. Include the Google Meet link if available
4. Include the calendar link
5. Make it sound natural and professional

"""
        
        return calendar_str
    
    def _get_draft_system_message(self, context: Dict) -> str:
        """Get system message for draft generation"""
        
        base_message = """You are an AI email assistant that generates professional, helpful email responses.

CORE PRINCIPLES:
1. Be professional but natural and conversational
2. Use the provided knowledge base for accurate information
3. Follow the persona and intent-specific instructions
4. Be concise but thorough
5. Never make up information - use only what's in the knowledge base
6. If you don't know something, say so professionally

FORMATTING:
- Only output the email body (no subject line, no "Subject:" prefix)
- Use proper paragraphs and formatting
- DO NOT add any sign-off, closing, signature, or "Best regards" type phrases
- DO NOT include sender name or contact information at the end
- End with the main content only - signature will be added automatically
- Use the persona's tone and style"""
        
        if context.get('persona'):
            base_message += f"\n\nYOUR STYLE: {context['persona'][:200]}"
        
        return base_message
    
    async def _get_draft_context(
        self,
        user_id: str,
        email_account_id: str,
        intent_id: Optional[str]
    ) -> Dict:
        """Get all context needed for draft generation"""
        
        context = {
            'persona': None,
            'knowledge_base': [],
            'intent_prompt': None
        }
        
        # Get persona from email account
        try:
            account = await self.db.email_accounts.find_one({"id": email_account_id})
            if account and account.get('persona'):
                context['persona'] = account['persona']
        except Exception as e:
            logger.warning(f"Could not load persona: {e}")
        
        # Get knowledge base
        try:
            kb_entries = await self.db.knowledge_base.find({
                "user_id": user_id,
                "is_active": True
            }).to_list(50)
            context['knowledge_base'] = kb_entries
        except Exception as e:
            logger.warning(f"Could not load knowledge base: {e}")
        
        # Get intent-specific prompt
        if intent_id:
            try:
                intent = await self.db.intents.find_one({"id": intent_id})
                if intent and intent.get('prompt'):
                    context['intent_prompt'] = intent['prompt']
            except Exception as e:
                logger.warning(f"Could not load intent: {e}")
        
        return context
    
    # ============================================================================
    # DRAFT VALIDATION
    # ============================================================================
    
    async def validate_draft(
        self,
        draft: str,
        original_email: Email,
        thread_context: List[Dict] = None
    ) -> Tuple[bool, List[str], int]:
        """
        Validate email draft using Groq LLM
        
        Returns:
            Tuple of (is_valid, issues, tokens_used)
            - is_valid: True if draft passes validation
            - issues: List of issues found (empty if valid)
            - tokens_used: Total tokens consumed
        """
        try:
            # Build validation prompt
            prompt = self._build_validation_prompt(draft, original_email, thread_context)
            
            system_message = """You are an email validation AI. Check email drafts for quality and appropriateness.

VALIDATION CRITERIA:
1. Professional tone and language
2. Addresses the sender's questions/concerns
3. Provides helpful, actionable information
4. No grammatical errors or typos
5. Appropriate length (not too short, not too long)
6. Does not repeat information already shared in thread
7. Does not make promises that can't be kept
8. Is not generic - shows understanding of the specific situation

Respond with JSON:
{
  "is_valid": true/false,
  "issues": ["list of specific issues found"],
  "score": 0-100
}

If draft is good, return is_valid: true with empty issues array."""
            
            # Call Groq API
            result = await self._call_groq_api(
                system_message=system_message,
                user_message=prompt,
                temperature=0.3,
                max_tokens=400
            )
            
            # Parse response
            data = self._parse_json_response(result)
            
            is_valid = data.get('is_valid', False)
            issues = data.get('issues', [])
            
            if is_valid:
                logger.info("✓ Draft validation passed")
            else:
                logger.warning(f"✗ Draft validation failed: {', '.join(issues)}")
            
            return is_valid, issues, self.tokens_used
            
        except Exception as e:
            logger.error(f"Error validating draft: {e}", exc_info=True)
            # On error, assume valid to avoid blocking
            return True, [], self.tokens_used
    
    def _build_validation_prompt(
        self,
        draft: str,
        original_email: Email,
        thread_context: List[Dict]
    ) -> str:
        """Build validation prompt"""
        
        prompt = f"""ORIGINAL EMAIL:
From: {original_email.from_email}
Subject: {original_email.subject}
Body:
{original_email.body}

"""
        
        # Add thread context
        if thread_context:
            prompt += "PREVIOUS CONVERSATION:\n"
            for msg in thread_context:
                prompt += f"- {msg['from']}: {msg['body'][:100]}...\n"
                if msg.get('draft_sent'):
                    prompt += f"  Our response: {msg['draft_sent'][:100]}...\n"
            prompt += "\n"
        
        prompt += f"""DRAFT TO VALIDATE:
{draft}

Validate this draft. Check if it:
1. Addresses the original email appropriately
2. Provides helpful information
3. Is professional and well-written
4. Does not repeat what was already said in the thread
5. Is specific to this situation (not generic)

Respond with JSON indicating if valid and any issues found."""
        
        return prompt
    
    # ============================================================================
    # GROQ API INTEGRATION
    # ============================================================================
    
    async def _call_groq_api(
        self,
        system_message: str,
        user_message: str,
        temperature: float = 0.7,
        max_tokens: int = 800
    ) -> str:
        """
        Call Groq API with error handling
        
        Returns:
            Response text from the API
        """
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY not configured")
        
        try:
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
                            {'role': 'system', 'content': system_message},
                            {'role': 'user', 'content': user_message}
                        ],
                        'temperature': temperature,
                        'max_tokens': max_tokens
                    }
                )
                
                if response.status_code != 200:
                    error_detail = response.text
                    logger.error(f"Groq API error {response.status_code}: {error_detail}")
                    raise Exception(f"Groq API error: {response.status_code}")
                
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                # Track token usage
                usage = result.get('usage', {})
                tokens = usage.get('total_tokens', 0)
                self.tokens_used += tokens
                
                return content
                
        except httpx.TimeoutException:
            logger.error("Groq API timeout")
            raise Exception("Groq API timeout")
        except Exception as e:
            logger.error(f"Groq API call failed: {e}", exc_info=True)
            raise
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    def _parse_json_response(self, content: str) -> Dict:
        """Parse JSON response, handling markdown code blocks"""
        try:
            # Remove markdown code blocks if present
            json_content = content.strip()
            if json_content.startswith('```json'):
                json_content = json_content[7:]
            if json_content.startswith('```'):
                json_content = json_content[3:]
            if json_content.endswith('```'):
                json_content = json_content[:-3]
            json_content = json_content.strip()
            
            return json.loads(json_content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {content}")
            raise ValueError(f"Invalid JSON response: {str(e)}")
    
    def _convert_datetime_fields(self, doc: Dict):
        """Convert datetime fields to ISO strings for Pydantic compatibility"""
        if isinstance(doc.get('created_at'), datetime):
            doc['created_at'] = doc['created_at'].isoformat()
        if isinstance(doc.get('updated_at'), datetime):
            doc['updated_at'] = doc['updated_at'].isoformat()
