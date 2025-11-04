# AI Agent Service Updates - Copy these methods to ai_agent_service.py

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
    """Generate email draft with thread context and validation feedback"""
    try:
        # Get user's knowledge base
        kb_docs = await self.db.knowledge_base.find({"user_id": user_id}).to_list(100)
        kb_context = "\n".join([f"- {kb['content']}" for kb in kb_docs]) if kb_docs else "No knowledge base entries."
        
        # Get intent details
        intent_context = ""
        if intent_id:
            intent = await self.db.intents.find_one({"id": intent_id})
            if intent:
                intent_context = f"""\nIntent: {intent.get('name')}\nGuidelines: {intent.get('description', '')}\nPrompt: {intent.get('prompt', '')}"""
        
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
            feedback_str = f"\n\nPrevious draft had these issues (FIX THEM):\n" + "\n".join([f"- {issue}" for issue in validation_issues])
        
        prompt = f"""You are an AI email assistant. Generate a professional email reply.

Knowledge Base:
{kb_context}
{intent_context}
{thread_str}

Incoming Email:
From: {email.from_email}
Subject: {email.subject}
Body:
{email.body}
{feedback_str}

IMPORTANT:
1. Use the thread context to avoid repeating information already discussed
2. Reference previous messages naturally when relevant
3. Keep the response focused on the current message while maintaining conversation continuity
4. Do NOT repeat meeting details or information already sent in previous messages
5. If validation issues are provided, address them specifically

Generate a professional, helpful response:"""
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                'https://api.groq.com/openai/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {self.groq_api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': config.GROQ_DRAFT_MODEL,
                    'messages': [
                        {'role': 'system', 'content': 'You are a helpful email assistant. Generate clear, professional email responses.'},
                        {'role': 'user', 'content': prompt}
                    ],
                    'temperature': 0.7,
                    'max_tokens': 1000
                }
            )
        
        if response.status_code == 200:
            result = response.json()
            draft = result['choices'][0]['message']['content']
            usage = result.get('usage', {})
            tokens = usage.get('total_tokens', 0)
            return draft, tokens
        else:
            logger.error(f"Groq API error in draft generation: {response.status_code}")
            return "Error generating draft", 0
    except Exception as e:
        logger.error(f"Error generating draft: {e}")
        return f"Error: {str(e)}", 0

async def validate_draft(self, draft: str, email: Email, user_id: str, intent_id: Optional[str] = None,
                        thread_context: List[Dict] = None) -> Tuple[bool, List[str]]:
    """Validate draft with thread context to check for repetition"""
    try:
        # Get intent
        intent_context = ""
        if intent_id:
            intent = await self.db.intents.find_one({"id": intent_id})
            if intent:
                intent_context = f"Intent guidelines: {intent.get('description', '')}"
        
        # Build thread context for validation
        thread_str = ""
        if thread_context and len(thread_context) > 0:
            thread_str = "\n\nPrevious messages in thread:\n"
            for msg in thread_context:
                if msg.get('draft_sent'):
                    thread_str += f"We already sent: {msg['draft_sent'][:200]}...\n"
        
        prompt = f"""Validate this email draft for quality and appropriateness.

Original Email:
From: {email.from_email}
Subject: {email.subject}
Body: {email.body}

{intent_context}
{thread_str}

Proposed Draft:
{draft}

Check for:
1. Professional tone
2. Clear and complete response
3. Proper grammar and spelling
4. Addresses the main points
5. NOT repeating information already sent in previous messages
6. NOT sending duplicate meeting details or calendar information

Respond in JSON format:
{{
  "valid": true/false,
  "issues": ["list of specific issues if any"]
}}

If the draft is good, return {{}"valid": true, "issues": []}}."""
        
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
                        {'role': 'system', 'content': 'You are a draft validation AI. Always respond with valid JSON.'},
                        {'role': 'user', 'content': prompt}
                    ],
                    'temperature': 0.3,
                    'max_tokens': 300
                }
            )
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            try:
                data = json.loads(content)
                valid = data.get('valid', False)
                issues = data.get('issues', [])
                return valid, issues
            except json.JSONDecodeError:
                logger.error(f"Failed to parse validation JSON: {content}")
                return False, ["Validation service error"]
        else:
            logger.error(f"Groq API error in validation: {response.status_code}")
            return False, ["Validation service unavailable"]
    except Exception as e:
        logger.error(f"Error validating draft: {e}")
        return False, [f"Validation error: {str(e)}"]
