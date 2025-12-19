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
    FULLY AUTONOMOUS - Implements complete qualification flow
    """
    
    def __init__(self, db):
        self.db = db
        self.nurturing_service = LeadNurturingService(db)
        self.qualification_service = LeadQualificationService(db)
        self.ai_service = LeadAIService()
    
    async def process_lead_email(
        self,
        user_id: str,
        email_id: str,
        email_content: str,
        from_email: str,
        intent_doc: Optional[Dict],
        thread_context: List[Dict]
    ) -> Tuple[bool, Optional[str], List[Dict], str]:
        """
        MAIN AUTONOMOUS PROCESSOR - Handles entire lead qualification flow
        
        Returns:
            Tuple of (should_create_lead, lead_stage, questions_to_ask, lead_id)
            - should_create_lead: True if lead should be created/updated in inbound_leads
            - lead_stage: 'awaiting_info', 'qualified', 'unqualified', or 'new'
            - questions_to_ask: List of questions to include in draft
            - lead_id: ID of existing lead if found
        """
        try:
            # Check if nurturing/qualification is enabled
            nurturing_enabled = await self.should_enable_nurturing_for_intent(user_id, intent_doc)
            qualification_enabled = await self.should_enable_qualification_for_intent(user_id, intent_doc)
            
            if not (nurturing_enabled or qualification_enabled):
                # Feature not enabled - use old flow (immediate lead creation)
                logger.info(f"Nurturing/qualification not enabled for user {user_id}")
                return True, 'new', [], None
            
            # Check if this is a new lead or existing conversation
            lead = await self._find_existing_lead(user_id, from_email)
            
            if not lead:
                # NEW LEAD - Start qualification process
                logger.info(f"New lead detected: {from_email}")
                
                # Create lead in "awaiting_info" status
                lead_id = await self._create_awaiting_lead(
                    user_id,
                    from_email,
                    email_id,
                    intent_doc
                )
                
                # Get questions to ask (attempt #1)
                questions = await self._get_questions_for_attempt(
                    user_id,
                    email_content,
                    thread_context,
                    [],  # No previous questions
                    1  # First attempt
                )
                
                # Store questions in lead record for attempt #1
                if questions:
                    await self._increment_attempt(lead_id, 1, questions)
                
                return False, 'awaiting_info', questions, lead_id
            
            else:
                # EXISTING LEAD - Continue qualification process
                lead_id = lead['id']
                current_stage = lead.get('stage', 'awaiting_info')
                attempt = lead.get('qualification_attempt', 0)
                
                logger.info(f"Existing lead {lead_id}: stage={current_stage}, attempt={attempt}")
                
                # If already qualified or disqualified, don't reprocess
                if current_stage in ['qualified', 'unqualified', 'converted', 'lost']:
                    logger.info(f"Lead {lead_id} already processed: {current_stage}")
                    return True, current_stage, [], lead_id
                
                # Extract answers from this email using AI
                questions_asked = lead.get('last_questions_asked', [])
                answers = await self.ai_service.extract_answers_from_email(
                    email_content,
                    questions_asked
                )
                
                # Store answers
                await self._store_answers(lead_id, answers, questions_asked)
                
                # Evaluate qualification
                is_qualified, score, reasons = await self.qualification_service.evaluate_lead_qualification(
                    user_id,
                    lead,  # Pass full lead data
                    lead.get('qualification_criteria_id')
                )
                
                logger.info(f"Lead {lead_id} evaluation: score={score}, qualified={is_qualified}")
                
                # Decision tree based on score
                if score >= 60:
                    # QUALIFIED - Create inbound lead
                    await self._update_lead_status(lead_id, 'qualified', score, reasons)
                    return True, 'qualified', [], lead_id
                
                elif score < 40:
                    # DISQUALIFIED - Don't create, mark as unqualified
                    await self._update_lead_status(lead_id, 'unqualified', score, reasons)
                    return True, 'unqualified', [], lead_id
                
                else:
                    # NEEDS MORE INFO (40 <= score < 60)
                    if attempt >= 3:
                        # Max attempts reached - make final decision
                        if score >= 50:
                            # Borderline - give benefit of doubt
                            await self._update_lead_status(lead_id, 'qualified', score, reasons + ["Max attempts reached - borderline qualified"])
                            return True, 'qualified', [], lead_id
                        else:
                            # Below 50 after 3 attempts - disqualify
                            await self._update_lead_status(lead_id, 'unqualified', score, reasons + ["Max attempts reached - insufficient score"])
                            return True, 'unqualified', [], lead_id
                    
                    else:
                        # Ask follow-up questions (rephrased)
                        new_attempt = attempt + 1
                        questions = await self._get_questions_for_attempt(
                            user_id,
                            email_content,
                            thread_context,
                            questions_asked,
                            new_attempt
                        )
                        
                        # Update attempt counter
                        await self._increment_attempt(lead_id, new_attempt, questions)
                        
                        return False, 'awaiting_info', questions, lead_id
                        
        except Exception as e:
            logger.error(f"Error in autonomous lead processing: {e}")
            # On error, default to old behavior
            return True, 'new', [], None
    
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
    
    # ========================================================================
    # HELPER METHODS FOR AUTONOMOUS PROCESSING
    # ========================================================================
    
    async def _find_existing_lead(self, user_id: str, from_email: str) -> Optional[Dict]:
        """Find existing lead by email"""
        try:
            leads_collection = self.db['inbound_leads']
            lead = await leads_collection.find_one({
                "user_id": user_id,
                "lead_email": from_email,
                "stage": {"$in": ["awaiting_info", "new", "contacted"]}
            })
            return lead
        except Exception as e:
            logger.error(f"Error finding lead: {e}")
            return None
    
    async def _create_awaiting_lead(
        self,
        user_id: str,
        from_email: str,
        email_id: str,
        intent_doc: Optional[Dict]
    ) -> str:
        """Create new lead in awaiting_info status"""
        try:
            from models.inbound_lead import InboundLead
            import uuid
            
            lead = InboundLead(
                id=str(uuid.uuid4()),
                user_id=user_id,
                lead_email=from_email,
                initial_email_id=email_id,
                intent_id=intent_doc.get('id') if intent_doc else None,
                intent_name=intent_doc.get('name') if intent_doc else None,
                stage='awaiting_info',
                qualification_attempt=0,
                nurturing_enabled=True,
                email_ids=[email_id]
            )
            
            leads_collection = self.db['inbound_leads']
            await leads_collection.insert_one(lead.model_dump())
            
            logger.info(f"Created awaiting lead: {lead.id}")
            return lead.id
            
        except Exception as e:
            logger.error(f"Error creating awaiting lead: {e}")
            return None
    
    async def _get_questions_for_attempt(
        self,
        user_id: str,
        email_content: str,
        thread_context: List[Dict],
        previous_questions: List[Dict],
        attempt: int
    ) -> List[Dict]:
        """Get questions for specific attempt (with AI rephrasing)"""
        try:
            # Get base questions from config
            users_collection = self.db['users']
            user = await users_collection.find_one({"id": user_id})
            config_id = user.get('default_nurturing_config_id') if user else None
            
            questions = await self.nurturing_service.generate_nurturing_questions(
                user_id,
                email_content,
                thread_context,
                previous_questions,
                config_id
            )
            
            if not questions or attempt == 1:
                return questions
            
            # For attempts 2 and 3, rephrase questions using AI
            previous_versions = [q.get('question_text', '') for q in previous_questions]
            rephrased = await self.ai_service.rephrase_questions(
                questions,
                previous_versions,
                attempt
            )
            
            return rephrased
            
        except Exception as e:
            logger.error(f"Error getting questions for attempt: {e}")
            return []
    
    async def _store_answers(
        self,
        lead_id: str,
        answers: Dict[str, str],
        questions_asked: List[Dict]
    ) -> bool:
        """Store extracted answers"""
        try:
            leads_collection = self.db['inbound_leads']
            
            # Create answer records
            answer_records = []
            for question in questions_asked:
                question_key = question.get('question_key')
                answer = answers.get(question_key)
                
                if answer:
                    answer_records.append({
                        "question_key": question_key,
                        "question_text": question.get('question_text'),
                        "response": answer,
                        "answered_at": datetime.now(timezone.utc).isoformat()
                    })
            
            if answer_records:
                await leads_collection.update_one(
                    {"id": lead_id},
                    {
                        "$push": {
                            "nurturing_questions_asked": {"$each": answer_records}
                        },
                        "$set": {
                            "updated_at": datetime.now(timezone.utc).isoformat()
                        }
                    }
                )
                logger.info(f"Stored {len(answer_records)} answers for lead {lead_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error storing answers: {e}")
            return False
    
    async def _update_lead_status(
        self,
        lead_id: str,
        stage: str,
        score: int,
        reasons: List[str]
    ) -> bool:
        """Update lead status after qualification"""
        try:
            leads_collection = self.db['inbound_leads']
            
            await leads_collection.update_one(
                {"id": lead_id},
                {
                    "$set": {
                        "stage": stage,
                        "qualification_checked": True,
                        "qualification_score": score,
                        "qualification_reasons": reasons,
                        "stage_changed_at": datetime.now(timezone.utc).isoformat(),
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    },
                    "$push": {
                        "stage_history": {
                            "from_stage": "awaiting_info",
                            "to_stage": stage,
                            "changed_at": datetime.now(timezone.utc).isoformat(),
                            "reason": f"Qualification score: {score}",
                            "performed_by": "system"
                        },
                        "activities": {
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "activity_type": "qualification_completed",
                            "description": f"Lead {stage} with score {score}",
                            "details": {"score": score, "reasons": reasons},
                            "performed_by": "system"
                        }
                    }
                }
            )
            
            logger.info(f"Updated lead {lead_id} to {stage} (score: {score})")
            return True
            
        except Exception as e:
            logger.error(f"Error updating lead status: {e}")
            return False
    
    async def _increment_attempt(
        self,
        lead_id: str,
        new_attempt: int,
        questions: List[Dict]
    ) -> bool:
        """Increment qualification attempt"""
        try:
            leads_collection = self.db['inbound_leads']
            
            await leads_collection.update_one(
                {"id": lead_id},
                {
                    "$set": {
                        "qualification_attempt": new_attempt,
                        "last_questions_asked": questions,
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }
                }
            )
            
            logger.info(f"Incremented lead {lead_id} to attempt {new_attempt}")
            return True
            
        except Exception as e:
            logger.error(f"Error incrementing attempt: {e}")
            return False
