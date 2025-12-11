"""
Lead Nurturing Integration Service
Integrates nurturing and qualification with email processing
FULLY AUTONOMOUS - Handles entire qualification flow
"""
import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timezone

from services.lead_nurturing_service import LeadNurturingService
from services.lead_qualification_service import LeadQualificationService
from services.lead_ai_service import LeadAIService

logger = logging.getLogger(__name__)

class LeadNurturingIntegrationService:
    """
    Integration service that coordinates nurturing and qualification
    """
    
    def __init__(self, db):
        self.db = db
        self.nurturing_service = LeadNurturingService(db)
        self.qualification_service = LeadQualificationService(db)
        self.ai_service = LeadAIService()
    
    async def get_nurturing_questions_for_draft(
        self,
        user_id: str,
        email_content: str,
        thread_context: List[Dict],
        intent_doc: Optional[Dict],
        existing_lead_id: Optional[str] = None
    ) -> Tuple[List[Dict], str]:
        """
        Get nurturing questions to include in draft email
        
        Returns:
            Tuple of (questions_list, formatted_questions_text)
        """
        try:
            # Check if nurturing should be applied
            nurturing_exchanges_count = 0
            questions_already_asked = []
            
            if existing_lead_id:
                # Get existing lead data
                leads_collection = self.db['inbound_leads']
                lead = await leads_collection.find_one({"id": existing_lead_id})
                if lead:
                    nurturing_exchanges_count = lead.get('nurturing_exchanges_count', 0)
                    questions_already_asked = lead.get('nurturing_questions_asked', [])
            
            # Check if should nurture
            should_nurture = await self.nurturing_service.should_nurture_lead(
                user_id,
                intent_doc,
                nurturing_exchanges_count
            )
            
            if not should_nurture:
                logger.info(f"Nurturing not enabled or max exchanges reached for user {user_id}")
                return [], ""
            
            # Get nurturing config
            users_collection = self.db['users']
            user = await users_collection.find_one({"id": user_id})
            config_id = user.get('default_nurturing_config_id') if user else None
            
            # Generate questions
            questions = await self.nurturing_service.generate_nurturing_questions(
                user_id,
                email_content,
                thread_context,
                questions_already_asked,
                config_id
            )
            
            if not questions:
                return [], ""
            
            # Get config for formatting
            config = None
            if config_id:
                config_collection = self.db['lead_nurturing_config']
                config = await config_collection.find_one({"id": config_id})
            
            natural_integration = config.get('natural_integration', True) if config else True
            
            # Format questions
            formatted_text = await self.nurturing_service.format_questions_for_draft(
                questions,
                natural_integration
            )
            
            logger.info(f"Generated {len(questions)} nurturing questions for user {user_id}")
            return questions, formatted_text
            
        except Exception as e:
            logger.error(f"Error getting nurturing questions: {e}")
            return [], ""
    
    async def check_and_qualify_lead(
        self,
        user_id: str,
        lead_id: str,
        intent_doc: Optional[Dict]
    ) -> Tuple[bool, str]:
        """
        Check if lead should be qualified and perform qualification
        
        Returns:
            Tuple of (should_create_lead, stage)
            - should_create_lead: True if lead meets criteria
            - stage: 'qualified' or 'unqualified'
        """
        try:
            # Get lead data
            leads_collection = self.db['inbound_leads']
            lead = await leads_collection.find_one({"id": lead_id})
            
            if not lead:
                logger.warning(f"Lead {lead_id} not found")
                return True, 'new'  # Default behavior
            
            nurturing_exchanges_count = lead.get('nurturing_exchanges_count', 0)
            
            # Check if should check qualification
            should_check = await self.qualification_service.should_check_qualification(
                user_id,
                intent_doc,
                nurturing_exchanges_count
            )
            
            if not should_check:
                logger.info(f"Qualification check not needed yet for lead {lead_id}")
                return True, 'new'
            
            # Get qualification criteria
            users_collection = self.db['users']
            user = await users_collection.find_one({"id": user_id})
            criteria_id = user.get('default_qualification_criteria_id') if user else None
            
            # Evaluate qualification
            is_qualified, score, reasons = await self.qualification_service.evaluate_lead_qualification(
                user_id,
                lead,
                criteria_id
            )
            
            # Update lead with qualification data
            await leads_collection.update_one(
                {"id": lead_id},
                {
                    "$set": {
                        "qualification_checked": True,
                        "qualification_score": score,
                        "qualification_reasons": reasons,
                        "qualification_criteria_id": criteria_id,
                        "stage": "qualified" if is_qualified else "unqualified",
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }
                }
            )
            
            stage = "qualified" if is_qualified else "unqualified"
            logger.info(f"Lead {lead_id} qualification: {stage} (score: {score:.2f})")
            
            # Always return True to keep lead in system, but with appropriate stage
            return True, stage
            
        except Exception as e:
            logger.error(f"Error checking lead qualification: {e}")
            return True, 'new'  # Default to creating lead on error
    
    async def track_lead_response(
        self,
        lead_id: str,
        email_content: str,
        questions_asked: List[Dict]
    ) -> bool:
        """
        Track lead's response to nurturing questions
        """
        try:
            if not questions_asked:
                return True
            
            # Extract responses from email (simple implementation)
            # In production, consider using AI for better extraction
            for question in questions_asked:
                question_key = question.get('question_key')
                question_text = question.get('question_text')
                
                # Simple response extraction - just store the email content as response
                # This is a simplified version. You can enhance with AI extraction
                await self.nurturing_service.track_nurturing_response(
                    lead_id,
                    question_key,
                    question_text,
                    email_content[:500]  # Store first 500 chars as response
                )
            
            logger.info(f"Tracked {len(questions_asked)} question responses for lead {lead_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error tracking lead response: {e}")
            return False
    
    async def should_enable_nurturing_for_intent(
        self,
        user_id: str,
        intent_doc: Optional[Dict]
    ) -> bool:
        """
        Check if nurturing is enabled globally and for this intent
        """
        try:
            # Get user settings
            users_collection = self.db['users']
            user = await users_collection.find_one({"id": user_id})
            
            if not user:
                return False
            
            # Check global setting
            global_enabled = user.get('global_lead_nurturing_enabled', False)
            if not global_enabled:
                return False
            
            # Check intent-specific setting
            if intent_doc:
                intent_enabled = intent_doc.get('enable_lead_nurturing', False)
                return intent_enabled
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking nurturing status: {e}")
            return False
    
    async def should_enable_qualification_for_intent(
        self,
        user_id: str,
        intent_doc: Optional[Dict]
    ) -> bool:
        """
        Check if qualification is enabled globally and for this intent
        """
        try:
            # Get user settings
            users_collection = self.db['users']
            user = await users_collection.find_one({"id": user_id})
            
            if not user:
                return False
            
            # Check global setting
            global_enabled = user.get('global_lead_qualification_enabled', False)
            if not global_enabled:
                return False
            
            # Check intent-specific setting
            if intent_doc:
                intent_enabled = intent_doc.get('enable_lead_qualification', False)
                return intent_enabled
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking qualification status: {e}")
            return False
