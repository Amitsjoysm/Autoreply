"""
Emergent LLM Service - Wrapper for emergentintegrations LLM Chat
Provides a clean interface for AI operations in the email assistant
"""
import json
import logging
import uuid
from typing import Dict, Any, Optional
from emergentintegrations.llm.chat import LlmChat, UserMessage
from config import config

logger = logging.getLogger(__name__)


class EmergentLLMService:
    """Service for interacting with Emergent LLM API"""
    
    def __init__(self):
        self.api_key = config.EMERGENT_LLM_KEY
        if not self.api_key:
            logger.warning("EMERGENT_LLM_KEY not configured")
        self.default_model = "gpt-4o-mini"  # Cost-effective model
        self.default_provider = "openai"
        
    def _create_chat(self, system_message: str, session_id: Optional[str] = None) -> LlmChat:
        """Create a new chat instance"""
        if not session_id:
            session_id = str(uuid.uuid4())
            
        chat = LlmChat(
            api_key=self.api_key,
            session_id=session_id,
            system_message=system_message
        )
        
        # Use default model and provider
        chat.with_model(self.default_provider, self.default_model)
        
        return chat
    
    async def generate_completion(
        self,
        prompt: str,
        system_message: str = "You are a helpful AI assistant.",
        session_id: Optional[str] = None,
        temperature: float = 0.7
    ) -> str:
        """
        Generate a completion for the given prompt
        
        Args:
            prompt: User prompt/message
            system_message: System message to guide the AI
            session_id: Optional session ID for conversation context
            temperature: Temperature for generation (0.0 to 1.0)
            
        Returns:
            Generated text response
        """
        try:
            chat = self._create_chat(system_message, session_id)
            
            user_message = UserMessage(text=prompt)
            response = await chat.send_message(user_message)
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating completion: {e}", exc_info=True)
            raise
    
    async def generate_json_completion(
        self,
        prompt: str,
        system_message: str = "You are a helpful AI assistant. Always respond with valid JSON.",
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a JSON completion
        
        Args:
            prompt: User prompt/message
            system_message: System message to guide the AI
            session_id: Optional session ID
            
        Returns:
            Parsed JSON response as dictionary
        """
        try:
            response = await self.generate_completion(
                prompt=prompt,
                system_message=system_message,
                session_id=session_id,
                temperature=0.3  # Lower temperature for structured output
            )
            
            # Clean response
            json_content = response.strip()
            
            # Remove markdown code blocks if present
            if json_content.startswith('```json'):
                json_content = json_content[7:]
            if json_content.startswith('```'):
                json_content = json_content[3:]
            if json_content.endswith('```'):
                json_content = json_content[:-3]
            
            json_content = json_content.strip()
            
            # Parse JSON
            return json.loads(json_content)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {response}")
            raise ValueError(f"Invalid JSON response from LLM: {str(e)}")
        except Exception as e:
            logger.error(f"Error generating JSON completion: {e}", exc_info=True)
            raise
    
    async def generate_draft(
        self,
        context: str,
        system_message: str,
        session_id: Optional[str] = None
    ) -> str:
        """
        Generate an email draft
        
        Args:
            context: Full context including email, thread, knowledge base
            system_message: System message for draft generation
            session_id: Optional session ID
            
        Returns:
            Generated email draft
        """
        return await self.generate_completion(
            prompt=context,
            system_message=system_message,
            session_id=session_id,
            temperature=0.7
        )
    
    async def validate_draft(
        self,
        draft: str,
        validation_prompt: str,
        system_message: str,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Validate an email draft
        
        Args:
            draft: Email draft to validate
            validation_prompt: Validation instructions
            system_message: System message for validation
            session_id: Optional session ID
            
        Returns:
            Validation result as dictionary
        """
        return await self.generate_json_completion(
            prompt=validation_prompt,
            system_message=system_message,
            session_id=session_id
        )
    
    async def detect_meeting(
        self,
        detection_prompt: str,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Detect meeting information from email
        
        Args:
            detection_prompt: Meeting detection prompt
            session_id: Optional session ID
            
        Returns:
            Meeting detection result as dictionary
        """
        system_message = "You are a meeting detection AI. Always respond with valid JSON."
        return await self.generate_json_completion(
            prompt=detection_prompt,
            system_message=system_message,
            session_id=session_id
        )


# Global instance
emergent_llm_service = EmergentLLMService()
