from typing import Optional, Dict, List
import httpx
import logging
from datetime import datetime, timezone
from dateutil import parser
from motor.motor_asyncio import AsyncIOMotorDatabase

from services.oauth_service import OAuthService

logger = logging.getLogger(__name__)

class OutlookCalendarService:
    """Service for handling Outlook/Microsoft calendar operations via Microsoft Graph API"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.oauth_service = OAuthService(db)
        self.graph_base_url = "https://graph.microsoft.com/v1.0"
    
    async def ensure_token_valid(self, provider: Dict) -> Dict:
        """Check if access token is expired and refresh if needed"""
        try:
            # Parse token expiry time
            expires_at_str = provider.get('token_expires_at')
            if not expires_at_str:
                logger.warning(f"No token_expires_at for provider {provider.get('email')}")
                return provider
            
            expires_at = parser.isoparse(expires_at_str)
            now = datetime.now(timezone.utc)
            
            # If token expires in less than 5 minutes, refresh it
            if expires_at <= now:
                logger.info(f"Token expired for provider {provider.get('email')}, refreshing...")
                
                refresh_token = provider.get('refresh_token')
                if not refresh_token:
                    logger.error(f"No refresh token for provider {provider.get('email')}")
                    return provider
                
                # Refresh the token
                new_tokens = await self.oauth_service.refresh_microsoft_token(refresh_token)
                if new_tokens:
                    # Update provider in database
                    await self.db.calendar_providers.update_one(
                        {"id": provider['id']},
                        {"$set": {
                            "access_token": new_tokens['access_token'],
                            "refresh_token": new_tokens['refresh_token'],
                            "token_expires_at": new_tokens['token_expires_at'],
                            "updated_at": datetime.now(timezone.utc).isoformat()
                        }}
                    )
                    
                    # Update provider dict
                    provider['access_token'] = new_tokens['access_token']
                    provider['refresh_token'] = new_tokens['refresh_token']
                    provider['token_expires_at'] = new_tokens['token_expires_at']
                    
                    logger.info(f"Token refreshed successfully for provider {provider.get('email')}")
                else:
                    logger.error(f"Failed to refresh token for provider {provider.get('email')}")
            
            return provider
        except Exception as e:
            logger.error(f"Error ensuring token valid: {e}")
            return provider
    
    async def create_event(
        self,
        provider: Dict,
        title: str,
        start_time: datetime,
        end_time: datetime,
        attendees: List[str] = None,
        description: str = "",
        location: str = ""
    ) -> Optional[Dict]:
        """
        Create a calendar event in Outlook using Microsoft Graph API
        
        Args:
            provider: Calendar provider dict with access_token
            title: Event title
            start_time: Event start datetime (timezone-aware)
            end_time: Event end datetime (timezone-aware)
            attendees: List of attendee email addresses
            description: Event description
            location: Event location
        
        Returns:
            Dict with event details or None if failed
        """
        try:
            # Ensure token is valid
            provider = await self.ensure_token_valid(provider)
            access_token = provider['access_token']
            
            # Build event data
            event_data = {
                "subject": title,
                "start": {
                    "dateTime": start_time.strftime('%Y-%m-%dT%H:%M:%S'),
                    "timeZone": "UTC"
                },
                "end": {
                    "dateTime": end_time.strftime('%Y-%m-%dT%H:%M:%S'),
                    "timeZone": "UTC"
                },
                "body": {
                    "contentType": "Text",
                    "content": description
                },
                "location": {
                    "displayName": location
                },
                "isOnlineMeeting": True,
                "onlineMeetingProvider": "teamsForBusiness"
            }
            
            # Add attendees
            if attendees:
                event_data["attendees"] = [
                    {
                        "emailAddress": {
                            "address": email
                        },
                        "type": "required"
                    }
                    for email in attendees
                ]
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.graph_base_url}/me/events",
                    headers={
                        'Authorization': f'Bearer {access_token}',
                        'Content-Type': 'application/json'
                    },
                    json=event_data
                )
            
            if response.status_code in [200, 201]:
                event = response.json()
                
                # Extract online meeting URL
                online_meeting = event.get('onlineMeeting', {})
                join_url = online_meeting.get('joinUrl', '')
                
                result = {
                    'event_id': event.get('id'),
                    'title': event.get('subject'),
                    'start_time': event.get('start', {}).get('dateTime'),
                    'end_time': event.get('end', {}).get('dateTime'),
                    'meet_link': join_url,
                    'html_link': event.get('webLink', ''),
                    'status': 'confirmed',
                    'attendees': attendees or []
                }
                
                logger.info(f"Successfully created Outlook event: {title}")
                return result
            else:
                logger.error(f"Failed to create Outlook event: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating Outlook event: {e}")
            return None
    
    async def update_event(
        self,
        provider: Dict,
        event_id: str,
        title: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        attendees: Optional[List[str]] = None,
        description: Optional[str] = None,
        location: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Update an existing calendar event in Outlook
        
        Args:
            provider: Calendar provider dict with access_token
            event_id: ID of the event to update
            title: New event title (optional)
            start_time: New start datetime (optional)
            end_time: New end datetime (optional)
            attendees: New list of attendees (optional)
            description: New description (optional)
            location: New location (optional)
        
        Returns:
            Dict with updated event details or None if failed
        """
        try:
            # Ensure token is valid
            provider = await self.ensure_token_valid(provider)
            access_token = provider['access_token']
            
            # Build update data with only provided fields
            update_data = {}
            
            if title is not None:
                update_data["subject"] = title
            
            if start_time is not None:
                update_data["start"] = {
                    "dateTime": start_time.strftime('%Y-%m-%dT%H:%M:%S'),
                    "timeZone": "UTC"
                }
            
            if end_time is not None:
                update_data["end"] = {
                    "dateTime": end_time.strftime('%Y-%m-%dT%H:%M:%S'),
                    "timeZone": "UTC"
                }
            
            if description is not None:
                update_data["body"] = {
                    "contentType": "Text",
                    "content": description
                }
            
            if location is not None:
                update_data["location"] = {
                    "displayName": location
                }
            
            if attendees is not None:
                update_data["attendees"] = [
                    {
                        "emailAddress": {
                            "address": email
                        },
                        "type": "required"
                    }
                    for email in attendees
                ]
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.patch(
                    f"{self.graph_base_url}/me/events/{event_id}",
                    headers={
                        'Authorization': f'Bearer {access_token}',
                        'Content-Type': 'application/json'
                    },
                    json=update_data
                )
            
            if response.status_code == 200:
                event = response.json()
                
                # Extract online meeting URL
                online_meeting = event.get('onlineMeeting', {})
                join_url = online_meeting.get('joinUrl', '')
                
                result = {
                    'event_id': event.get('id'),
                    'title': event.get('subject'),
                    'start_time': event.get('start', {}).get('dateTime'),
                    'end_time': event.get('end', {}).get('dateTime'),
                    'meet_link': join_url,
                    'html_link': event.get('webLink', ''),
                    'status': 'confirmed'
                }
                
                logger.info(f"Successfully updated Outlook event: {event_id}")
                return result
            else:
                logger.error(f"Failed to update Outlook event: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error updating Outlook event: {e}")
            return None
    
    async def delete_event(self, provider: Dict, event_id: str) -> bool:
        """
        Delete a calendar event from Outlook
        
        Args:
            provider: Calendar provider dict with access_token
            event_id: ID of the event to delete
        
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            # Ensure token is valid
            provider = await self.ensure_token_valid(provider)
            access_token = provider['access_token']
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.delete(
                    f"{self.graph_base_url}/me/events/{event_id}",
                    headers={'Authorization': f'Bearer {access_token}'}
                )
            
            if response.status_code == 204:
                logger.info(f"Successfully deleted Outlook event: {event_id}")
                return True
            else:
                logger.error(f"Failed to delete Outlook event: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting Outlook event: {e}")
            return False
    
    async def get_event(self, provider: Dict, event_id: str) -> Optional[Dict]:
        """
        Get details of a specific calendar event from Outlook
        
        Args:
            provider: Calendar provider dict with access_token
            event_id: ID of the event to retrieve
        
        Returns:
            Dict with event details or None if not found
        """
        try:
            # Ensure token is valid
            provider = await self.ensure_token_valid(provider)
            access_token = provider['access_token']
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.graph_base_url}/me/events/{event_id}",
                    headers={'Authorization': f'Bearer {access_token}'}
                )
            
            if response.status_code == 200:
                event = response.json()
                
                # Extract online meeting URL
                online_meeting = event.get('onlineMeeting', {})
                join_url = online_meeting.get('joinUrl', '')
                
                result = {
                    'event_id': event.get('id'),
                    'title': event.get('subject'),
                    'start_time': event.get('start', {}).get('dateTime'),
                    'end_time': event.get('end', {}).get('dateTime'),
                    'meet_link': join_url,
                    'html_link': event.get('webLink', ''),
                    'status': 'confirmed'
                }
                
                return result
            else:
                logger.error(f"Failed to get Outlook event: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting Outlook event: {e}")
            return None
