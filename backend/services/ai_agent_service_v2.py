"""Improved AI Agent Service with better architecture"""
import json
from typing import List, Optional, Dict, Tuple
import logging
from abc import ABC, abstractmethod

from config import config
from models.email import Email
from models.intent import Intent
from repositories.base_repository import GenericRepository
from utils.http_client import http_client_pool
from utils.cache import cache_result
from exceptions import ExternalServiceError

logger = logging.getLogger(__name__)

class AIModel(ABC):
    """Abstract AI model interface (Open/Closed Principle)"""
    
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> Tuple[str, int]:
        """Generate response"""
        pass
    
    @abstractmethod
    async def classify(self, text: str, categories: List[str]) -> Tuple[str, float]:
        """Classify text"""
        pass

class GroqModel(AIModel):
    """Groq LLM implementation"""
    
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        self.base_url = 'https://api.groq.com/openai/v1/chat/completions'
    
    async def generate(self, prompt: str, system_prompt: str = None, temperature: float = 0.7, max_tokens: int = 800) -> Tuple[str, int]:
        """Generate text using Groq"""
        try:
            client = await http_client_pool.get_client()
            
            messages = []
            if system_prompt:
                messages.append({'role': 'system', 'content': system_prompt})
            messages.append({'role': 'user', 'content': prompt})
            
            response = await client.post(
                self.base_url,
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': self.model,
                    'messages': messages,
                    'temperature': temperature,
                    'max_tokens': max_tokens
                }
            )
            
            if response.status_code != 200:
                raise ExternalServiceError('Groq', f"API error: {response.status_code}")
            
            result = response.json()
            content = result['choices'][0]['message']['content'].strip()
            tokens = result.get('usage', {}).get('total_tokens', 0)
            
            return content, tokens
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            raise ExternalServiceError('Groq', str(e))
    
    async def classify(self, text: str, categories: List[str]) -> Tuple[str, float]:
        """Simple classification using Groq"""
        prompt = f"""Classify this text into one of these categories: {', '.join(categories)}

Text: {text}

Respond with only the category name."""
        
        result, _ = await self.generate(prompt, temperature=0.2, max_tokens=50)
        
        # Find best match
        result_lower = result.lower()
        for category in categories:
            if category.lower() in result_lower:
                return category, 0.8
        
        return categories[0] if categories else "unknown", 0.5

class IntentClassifier:
    """Intent classification with multiple strategies"""
    
    def __init__(self, repository: GenericRepository):
        self.repository = repository
    
    @cache_result(ttl=300, key_prefix="intent")
    async def classify_by_keywords(self, email: Email, user_id: str) -> Tuple[Optional[str], float]:
        """Keyword-based classification (fast, no API cost)"""
        intents = await self.repository.find_many(
            {"user_id": user_id, "is_active": True},
            sort=[("priority", -1)]
        )
        
        if not intents:
            return None, 0.0
        
        email_text = f"{email.subject} {email.body}".lower()
        
        # Score each intent
        best_intent = None
        best_score = 0.0
        
        for intent_doc in intents:
            intent = Intent(**intent_doc)
            score = 0.0
            
            # Check keywords
            for keyword in intent.keywords:
                if keyword.lower() in email_text:
                    score += 1.0
            
            # Normalize score
            if intent.keywords:
                score = score / len(intent.keywords)
            
            if score > best_score:
                best_score = score
                best_intent = intent.id
        
        if best_score > 0.5:
            return best_intent, best_score
        
        return None, 0.0

class DraftGenerator:
    """Draft generation with context"""
    
    def __init__(self, model: AIModel, repositories: Dict[str, GenericRepository]):
        self.model = model
        self.repositories = repositories
    
    async def generate(self, email: Email, user_id: str, intent_id: Optional[str] = None) -> Tuple[str, int]:
        """Generate email draft"""
        current_time = config.get_datetime_string()
        context = await self._get_context(user_id, email.email_account_id, intent_id)
        
        prompt = f"""Current Date & Time: {current_time}

You are an AI email assistant. Generate a professional email response.

{context}

Incoming Email:
From: {email.from_email}
Subject: {email.subject}
Body: {email.body}

Generate a clear, professional response that:
1. Addresses all points from the email
2. Matches the persona and tone
3. Uses information from the knowledge base if relevant
4. Includes the signature
5. Is concise and actionable
6. Contains NO placeholders like [Your Name] or [Date]

Respond with ONLY the email body text, no subject line."""
        
        system_prompt = "You are a professional email writing assistant. Write clear, actionable emails with no placeholders."
        
        return await self.model.generate(prompt, system_prompt=system_prompt, temperature=0.7)
    
    async def _get_context(self, user_id: str, account_id: str, intent_id: Optional[str] = None) -> str:
        """Build context for draft generation"""
        context_parts = []
        
        # Get account details
        account_repo = self.repositories['email_accounts']
        account_doc = await account_repo.find_by_id(account_id)
        
        if account_doc:
            if account_doc.get('persona'):
                context_parts.append(f"Persona: {account_doc['persona']}")
            if account_doc.get('signature'):
                context_parts.append(f"Signature: {account_doc['signature']}")
        
        # Get intent
        if intent_id:
            intent_repo = self.repositories['intents']
            intent_doc = await intent_repo.find_by_id(intent_id)
            if intent_doc:
                context_parts.append(f"Intent: {intent_doc['name']}")
                context_parts.append(f"Response Guidelines: {intent_doc['prompt']}")
        
        # Get knowledge base
        kb_repo = self.repositories['knowledge_base']
        kb_docs = await kb_repo.find_many(
            {"user_id": user_id, "is_active": True},
            limit=5
        )
        
        if kb_docs:
            kb_text = "\n".join([f"- {doc['title']}: {doc['content'][:200]}..." for doc in kb_docs])
            context_parts.append(f"Knowledge Base:\n{kb_text}")
        
        return "\n\n".join(context_parts)

class DraftValidator:
    """Draft validation"""
    
    def __init__(self, model: AIModel):
        self.model = model
    
    async def validate(self, draft: str, email: Email, intent_prompt: Optional[str] = None) -> Tuple[bool, List[str]]:
        """Validate draft quality"""
        current_time = config.get_datetime_string()
        
        prompt = f"""Current Date & Time: {current_time}

You are a validation AI. Check if this email draft meets quality standards.

Original Email:
Subject: {email.subject}
Body: {email.body}

Generated Draft:
{draft}

{f'Intent Requirements: {intent_prompt}' if intent_prompt else ''}

Validation Checklist:
1. No placeholders like [Name], [Date], [Company]
2. All points from original email are addressed
3. Professional tone
4. Clear and concise
5. Actionable (if needed)
{f'6. Matches intent requirements' if intent_prompt else ''}

Respond in JSON:
{{
  "valid": true/false,
  "issues": ["list of issues found, empty if valid"]
}}"""
        
        try:
            result, _ = await self.model.generate(
                prompt,
                system_prompt="You are a validation AI. Always respond with valid JSON.",
                temperature=0.2,
                max_tokens=300
            )
            
            data = json.loads(result)
            return data.get('valid', False), data.get('issues', [])
        except json.JSONDecodeError:
            logger.error(f"Failed to parse validation JSON: {result}")
            return True, []  # Assume valid on parse error
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return True, []

class AIAgentServiceV2:
    """Refactored AI Agent Service with dependency injection"""
    
    def __init__(self, repositories: Dict[str, GenericRepository]):
        self.repositories = repositories
        
        # Initialize AI models
        self.groq_model = GroqModel(config.GROQ_API_KEY, config.GROQ_DRAFT_MODEL)
        
        # Initialize components
        self.intent_classifier = IntentClassifier(repositories['intents'])
        self.draft_generator = DraftGenerator(self.groq_model, repositories)
        self.draft_validator = DraftValidator(self.groq_model)
        
        self.tokens_used = 0
    
    async def classify_intent(self, email: Email, user_id: str) -> Tuple[Optional[str], float]:
        """Classify email intent"""
        return await self.intent_classifier.classify_by_keywords(email, user_id)
    
    async def generate_draft(self, email: Email, user_id: str, intent_id: Optional[str] = None) -> Tuple[str, int]:
        """Generate email draft"""
        draft, tokens = await self.draft_generator.generate(email, user_id, intent_id)
        self.tokens_used += tokens
        return draft, tokens
    
    async def validate_draft(self, draft: str, email: Email, intent_id: Optional[str] = None) -> Tuple[bool, List[str]]:
        """Validate draft"""
        intent_prompt = None
        if intent_id:
            intent_doc = await self.repositories['intents'].find_by_id(intent_id)
            if intent_doc:
                intent_prompt = intent_doc['prompt']
        
        return await self.draft_validator.validate(draft, email, intent_prompt)
    
    def get_tokens_used(self) -> int:
        """Get total tokens used"""
        return self.tokens_used
