from typing import List, Optional, Dict
import httpx
import logging
import base64
from datetime import datetime, timezone
from dateutil import parser
from motor.motor_asyncio import AsyncIOMotorDatabase

from services.oauth_service import OAuthService

logger = logging.getLogger(__name__)

class OutlookEmailService:
    """Service for handling Outlook/Microsoft email operations via Microsoft Graph API"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.oauth_service = OAuthService(db)
        self.graph_base_url = "https://graph.microsoft.com/v1.0"
    
    async def ensure_token_valid(self, account: Dict) -> Dict:
        """Check if access token is expired and refresh if needed"""
        try:
            # Parse token expiry time
            expires_at_str = account.get('token_expires_at')
            if not expires_at_str:
                logger.warning(f"No token_expires_at for account {account.get('email')}")
                return account
            
            expires_at = parser.isoparse(expires_at_str)
            now = datetime.now(timezone.utc)
            
            # If token expires in less than 5 minutes, refresh it
            if expires_at <= now:
                logger.info(f"Token expired for account {account.get('email')}, refreshing...")
                
                refresh_token = account.get('refresh_token')
                if not refresh_token:
                    logger.error(f"No refresh token for account {account.get('email')}")
                    return account
                
                # Refresh the token
                new_tokens = await self.oauth_service.refresh_microsoft_token(refresh_token)
                if new_tokens:
                    # Update account in database
                    await self.db.email_accounts.update_one(
                        {"id": account['id']},
                        {"$set": {
                            "access_token": new_tokens['access_token'],
                            "refresh_token": new_tokens['refresh_token'],
                            "token_expires_at": new_tokens['token_expires_at'],
                            "updated_at": datetime.now(timezone.utc).isoformat()
                        }}
                    )
                    
                    # Update account dict
                    account['access_token'] = new_tokens['access_token']
                    account['refresh_token'] = new_tokens['refresh_token']
                    account['token_expires_at'] = new_tokens['token_expires_at']
                    
                    logger.info(f"Token refreshed successfully for account {account.get('email')}")
                else:
                    logger.error(f"Failed to refresh token for account {account.get('email')}")
            
            return account
        except Exception as e:
            logger.error(f"Error ensuring token valid: {e}")
            return account
    
    async def fetch_emails(self, account: Dict, since: Optional[datetime] = None) -> List[Dict]:
        """
        Fetch emails from Outlook using Microsoft Graph API
        
        Args:
            account: Email account dict with access_token
            since: Fetch emails received after this datetime
        
        Returns:
            List of email dicts
        """
        try:
            # Ensure token is valid
            account = await self.ensure_token_valid(account)
            access_token = account['access_token']
            
            # Build query parameters
            params = {
                '$select': 'id,subject,from,toRecipients,receivedDateTime,body,internetMessageId,conversationId',
                '$orderby': 'receivedDateTime DESC',
                '$top': 50
            }
            
            # Add filter for emails received after 'since'
            if since:
                since_str = since.strftime('%Y-%m-%dT%H:%M:%SZ')
                params['$filter'] = f"receivedDateTime ge {since_str}"
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.graph_base_url}/me/messages",
                    headers={'Authorization': f'Bearer {access_token}'},
                    params=params
                )
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch Outlook emails: {response.status_code} - {response.text}")
                return []
            
            data = response.json()
            messages = data.get('value', [])
            
            # Convert to our email format
            emails = []
            for msg in messages:
                try:
                    from_email = msg.get('from', {}).get('emailAddress', {}).get('address', '')
                    from_name = msg.get('from', {}).get('emailAddress', {}).get('name', '')
                    
                    to_recipients = []
                    for recipient in msg.get('toRecipients', []):
                        to_recipients.append(recipient.get('emailAddress', {}).get('address', ''))
                    
                    email_dict = {
                        'message_id': msg.get('internetMessageId', msg.get('id')),
                        'thread_id': msg.get('conversationId'),
                        'subject': msg.get('subject', ''),
                        'from_email': from_email,
                        'from_name': from_name,
                        'to': ', '.join(to_recipients),
                        'received_at': msg.get('receivedDateTime'),
                        'body': msg.get('body', {}).get('content', ''),
                        'body_type': msg.get('body', {}).get('contentType', 'text'),
                        'raw_headers': {},
                        'labels': []
                    }
                    
                    emails.append(email_dict)
                except Exception as e:
                    logger.error(f"Error parsing Outlook message: {e}")
                    continue
            
            logger.info(f"Fetched {len(emails)} emails from Outlook account {account.get('email')}")
            return emails
            
        except Exception as e:
            logger.error(f"Error fetching Outlook emails: {e}")
            return []
    
    async def send_email(
        self,
        account: Dict,
        to: str,
        subject: str,
        body: str,
        thread_id: Optional[str] = None,
        in_reply_to: Optional[str] = None
    ) -> bool:
        """
        Send email via Outlook using Microsoft Graph API
        
        Args:
            account: Email account dict with access_token
            to: Recipient email address
            subject: Email subject
            body: Email body (plain text)
            thread_id: Thread/conversation ID for replies
            in_reply_to: Message ID being replied to
        
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # Ensure token is valid
            account = await self.ensure_token_valid(account)
            access_token = account['access_token']
            
            # Build email message
            message = {
                "subject": subject,
                "body": {
                    "contentType": "Text",
                    "content": body
                },
                "toRecipients": [
                    {
                        "emailAddress": {
                            "address": to
                        }
                    }
                ]
            }
            
            # If replying to a message, use reply endpoint
            if in_reply_to:
                # Use reply endpoint
                async with httpx.AsyncClient(timeout=30.0) as client:
                    # First, find the message in the conversation
                    search_response = await client.get(
                        f"{self.graph_base_url}/me/messages",
                        headers={'Authorization': f'Bearer {access_token}'},
                        params={
                            '$filter': f"internetMessageId eq '{in_reply_to}'",
                            '$select': 'id',
                            '$top': 1
                        }
                    )
                    
                    if search_response.status_code == 200:
                        search_data = search_response.json()
                        messages = search_data.get('value', [])
                        
                        if messages:
                            message_id = messages[0]['id']
                            
                            # Send reply
                            reply_data = {
                                "message": message,
                                "comment": ""
                            }
                            
                            response = await client.post(
                                f"{self.graph_base_url}/me/messages/{message_id}/reply",
                                headers={
                                    'Authorization': f'Bearer {access_token}',
                                    'Content-Type': 'application/json'
                                },
                                json=reply_data
                            )
                            
                            if response.status_code in [200, 201, 202]:
                                logger.info(f"Successfully sent reply via Outlook to {to}")
                                return True
                            else:
                                logger.error(f"Failed to send Outlook reply: {response.status_code} - {response.text}")
                                # Fall through to regular send if reply fails
            
            # Send as new message or if reply failed
            send_data = {
                "message": message,
                "saveToSentItems": "true"
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.graph_base_url}/me/sendMail",
                    headers={
                        'Authorization': f'Bearer {access_token}',
                        'Content-Type': 'application/json'
                    },
                    json=send_data
                )
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"Successfully sent email via Outlook to {to}")
                return True
            else:
                logger.error(f"Failed to send Outlook email: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending Outlook email: {e}")
            return False
