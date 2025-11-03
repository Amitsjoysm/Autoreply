import imaplib
import smtplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional, Dict
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone
import asyncio
import logging
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import base64

from config import config
from models.email import Email, EmailSend
from models.email_account import EmailAccount
from services.oauth_service import OAuthService
from services.email_formatter import EmailFormatter

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.oauth_service = OAuthService(db)
    
    async def ensure_token_valid(self, account: EmailAccount) -> EmailAccount:
        """Check and refresh OAuth token if expired"""
        if not account.token_expires_at or not account.refresh_token:
            return account
        
        try:
            # Parse token expiry
            from dateutil import parser
            expires_at = parser.isoparse(account.token_expires_at)
            now = datetime.now(timezone.utc)
            
            # Check if token expires within next 5 minutes
            if expires_at <= now:
                logger.info(f"Token expired for account {account.email}, refreshing...")
                
                # Refresh token
                new_tokens = await self.oauth_service.refresh_google_token(account.refresh_token)
                if new_tokens:
                    # Update account with new tokens
                    await self.db.email_accounts.update_one(
                        {"id": account.id},
                        {"$set": {
                            "access_token": new_tokens['access_token'],
                            "token_expires_at": new_tokens['token_expires_at'],
                            "updated_at": datetime.now(timezone.utc).isoformat()
                        }}
                    )
                    
                    # Update account object
                    account.access_token = new_tokens['access_token']
                    account.token_expires_at = new_tokens['token_expires_at']
                    
                    logger.info(f"Token refreshed successfully for {account.email}")
                else:
                    logger.error(f"Failed to refresh token for {account.email}")
                    raise Exception("Token refresh failed")
        except Exception as e:
            logger.error(f"Error checking/refreshing token: {e}")
            raise
        
        return account
    
    async def get_account(self, account_id: str) -> Optional[EmailAccount]:
        doc = await self.db.email_accounts.find_one({"id": account_id})
        if doc:
            return EmailAccount(**doc)
        return None
    
    async def fetch_emails_oauth_gmail(self, account: EmailAccount) -> List[Dict]:
        """Fetch emails using Gmail API (OAuth)"""
        try:
            # Ensure token is valid
            account = await self.ensure_token_valid(account)
            
            creds = Credentials(
                token=account.access_token,
                refresh_token=account.refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=config.GOOGLE_CLIENT_ID,
                client_secret=config.GOOGLE_CLIENT_SECRET
            )
            
            service = build('gmail', 'v1', credentials=creds)
            
            # Build query to only fetch emails received after account was connected
            from dateutil import parser
            created_at = parser.isoparse(account.created_at)
            
            # Use last_sync if available, otherwise use created_at
            if account.last_sync:
                after_date = parser.isoparse(account.last_sync)
            else:
                after_date = created_at
            
            # Format date for Gmail query (YYYY/MM/DD)
            date_query = after_date.strftime('%Y/%m/%d')
            
            # Fetch unread messages received after the specified date
            query = f'is:unread after:{date_query} -category:promotions -category:social -category:forums -is:sent'
            
            results = service.users().messages().list(
                userId='me',
                q=query,
                maxResults=50
            ).execute()
            
            messages = results.get('messages', [])
            emails = []
            
            for msg in messages:
                message = service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='full'
                ).execute()
                
                # Parse email
                headers = {h['name']: h['value'] for h in message['payload']['headers']}
                
                # Get body
                body = ''
                if 'parts' in message['payload']:
                    for part in message['payload']['parts']:
                        if part['mimeType'] == 'text/plain':
                            body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                            break
                elif 'body' in message['payload']:
                    body = base64.urlsafe_b64decode(message['payload']['body']['data']).decode('utf-8')
                
                # Extract thread information
                thread_id = message.get('threadId')
                in_reply_to = headers.get('In-Reply-To')
                references = headers.get('References', '').split() if headers.get('References') else []
                
                emails.append({
                    'message_id': message['id'],
                    'thread_id': thread_id,
                    'in_reply_to': in_reply_to,
                    'references': references,
                    'from': headers.get('From', ''),
                    'to': headers.get('To', '').split(','),
                    'subject': headers.get('Subject', ''),
                    'body': body,
                    'received_at': headers.get('Date', '')
                })
            
            return emails
        except Exception as e:
            logger.error(f"Error fetching Gmail OAuth emails: {e}")
            return []
    
    async def fetch_emails_imap(self, account: EmailAccount) -> List[Dict]:
        """Fetch emails using IMAP"""
        try:
            # Run IMAP in thread pool since it's blocking
            loop = asyncio.get_event_loop()
            emails = await loop.run_in_executor(
                None,
                self._fetch_imap_sync,
                account
            )
            return emails
        except Exception as e:
            logger.error(f"Error fetching IMAP emails: {e}")
            return []
    
    def _fetch_imap_sync(self, account: EmailAccount) -> List[Dict]:
        """Synchronous IMAP fetch"""
        try:
            from dateutil import parser
            
            mail = imaplib.IMAP4_SSL(account.imap_host, account.imap_port)
            mail.login(account.email, account.password)
            mail.select('inbox')
            
            # Determine the date to search from
            if account.last_sync:
                after_date = parser.isoparse(account.last_sync)
            else:
                after_date = parser.isoparse(account.created_at)
            
            # Format date for IMAP SINCE query (DD-MMM-YYYY)
            date_str = after_date.strftime('%d-%b-%Y')
            
            # Search for unread emails received after the specified date
            status, messages = mail.search(None, f'(UNSEEN SINCE {date_str})')
            email_ids = messages[0].split()
            
            emails = []
            for email_id in email_ids[-50:]:  # Last 50 unread
                status, msg_data = mail.fetch(email_id, '(RFC822)')
                
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        
                        subject = msg['subject']
                        from_email = msg['from']
                        to_email = msg['to']
                        date = msg['date']
                        
                        # Get body
                        body = ''
                        if msg.is_multipart():
                            for part in msg.walk():
                                if part.get_content_type() == 'text/plain':
                                    body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                                    break
                        else:
                            body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                        
                        emails.append({
                            'message_id': str(email_id),
                            'from': from_email,
                            'to': [to_email] if to_email else [],
                            'subject': subject or '',
                            'body': body,
                            'received_at': date or ''
                        })
            
            mail.close()
            mail.logout()
            
            return emails
        except Exception as e:
            logger.error(f"IMAP sync error: {e}")
            return []
    
    async def send_email_oauth_gmail(self, account: EmailAccount, email_data: EmailSend, thread_id: Optional[str] = None) -> bool:
        """Send email using Gmail API with thread support"""
        try:
            # Ensure token is valid
            account = await self.ensure_token_valid(account)
            
            def _send_gmail():
                """Synchronous Gmail send function"""
                creds = Credentials(
                    token=account.access_token,
                    refresh_token=account.refresh_token,
                    token_uri="https://oauth2.googleapis.com/token",
                    client_id=config.GOOGLE_CLIENT_ID,
                    client_secret=config.GOOGLE_CLIENT_SECRET
                )
                
                service = build('gmail', 'v1', credentials=creds)
                
                message = MIMEMultipart()
                message['to'] = ', '.join(email_data.to_email)
                message['subject'] = email_data.subject
                
                if email_data.cc:
                    message['cc'] = ', '.join(email_data.cc)
                
                message.attach(MIMEText(email_data.body, 'plain'))
                
                raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
                
                # Build message body with thread support
                message_body = {'raw': raw_message}
                if thread_id and not thread_id.startswith('test-'):
                    # Only use thread_id if it's a real Gmail thread (not a test thread)
                    message_body['threadId'] = thread_id
                
                try:
                    service.users().messages().send(
                        userId='me',
                        body=message_body
                    ).execute()
                    return True
                except Exception as e:
                    # If thread_id error, try without thread_id
                    if 'Invalid thread_id' in str(e) and thread_id:
                        logger.info("Retrying without thread_id...")
                        message_body = {'raw': raw_message}
                        service.users().messages().send(
                            userId='me',
                            body=message_body
                        ).execute()
                        return True
                    raise
            
            # Run synchronous Gmail API call in executor
            result = await asyncio.to_thread(_send_gmail)
            return result
        except Exception as e:
            logger.error(f"Error sending Gmail OAuth email: {e}")
            return False
    
    async def send_email_smtp(self, account: EmailAccount, email_data: EmailSend) -> bool:
        """Send email using SMTP"""
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self._send_smtp_sync,
                account,
                email_data
            )
            return result
        except Exception as e:
            logger.error(f"Error sending SMTP email: {e}")
            return False
    
    def _send_smtp_sync(self, account: EmailAccount, email_data: EmailSend) -> bool:
        """Synchronous SMTP send"""
        try:
            message = MIMEMultipart()
            message['From'] = account.email
            message['To'] = ', '.join(email_data.to_email)
            message['Subject'] = email_data.subject
            
            if email_data.cc:
                message['Cc'] = ', '.join(email_data.cc)
            
            message.attach(MIMEText(email_data.body, 'plain'))
            
            server = smtplib.SMTP_SSL(account.smtp_host, account.smtp_port)
            server.login(account.email, account.password)
            
            recipients = email_data.to_email + (email_data.cc or []) + (email_data.bcc or [])
            server.sendmail(account.email, recipients, message.as_string())
            
            server.quit()
            return True
        except Exception as e:
            logger.error(f"SMTP sync error: {e}")
            return False
    
    async def save_email(self, user_id: str, account_id: str, email_data: Dict) -> Email:
        """Save email to database"""
        # Check if this is a reply to our sent email
        is_reply = False
        if email_data.get('in_reply_to'):
            # Check if in_reply_to matches any of our sent emails
            sent_email = await self.db.emails.find_one({
                "message_id": email_data['in_reply_to'],
                "user_id": user_id,
                "direction": "outbound"
            })
            is_reply = sent_email is not None
        
        # Also check if this is a response in an existing thread where we processed emails
        if not is_reply and email_data.get('thread_id'):
            # Check if we have any other inbound emails in this thread that were already processed
            # This helps detect replies even if we don't have the outbound record
            previous_emails = await self.db.emails.count_documents({
                "thread_id": email_data['thread_id'],
                "user_id": user_id,
                "direction": "inbound",
                "from_email": email_data['from']  # Same sender
            })
            
            # If there's at least one previous email from the same sender in this thread,
            # and we replied to it (indicated by replied=True), this is a reply
            if previous_emails > 0:
                previous_replied = await self.db.emails.find_one({
                    "thread_id": email_data['thread_id'],
                    "user_id": user_id,
                    "direction": "inbound",
                    "from_email": email_data['from'],
                    "replied": True  # We sent a reply to their email
                })
                is_reply = previous_replied is not None
        
        email_obj = Email(
            user_id=user_id,
            email_account_id=account_id,
            message_id=email_data['message_id'],
            thread_id=email_data.get('thread_id'),
            in_reply_to=email_data.get('in_reply_to'),
            references=email_data.get('references', []),
            from_email=email_data['from'],
            to_email=email_data['to'] if isinstance(email_data['to'], list) else [email_data['to']],
            subject=email_data['subject'],
            body=email_data['body'],
            received_at=email_data.get('received_at', datetime.now(timezone.utc).isoformat()),
            direction='inbound',
            is_reply=is_reply,
            action_history=[{
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "action": "received",
                "details": {"source": "email_polling"},
                "status": "success"
            }]
        )
        
        doc = email_obj.model_dump()
        await self.db.emails.insert_one(doc)
        
        # If this is a reply, cancel all pending follow-ups for the thread
        if is_reply and email_data.get('thread_id'):
            await self.cancel_followups_for_thread(user_id, email_data['thread_id'])
        
        return email_obj
    
    async def cancel_followups_for_thread(self, user_id: str, thread_id: str):
        """Cancel all pending follow-ups for a thread when reply is received"""
        try:
            # Find all emails in this thread
            emails_in_thread = await self.db.emails.find({
                "user_id": user_id,
                "thread_id": thread_id
            }).to_list(100)
            
            email_ids = [e['id'] for e in emails_in_thread]
            
            # Cancel all pending follow-ups for these emails
            result = await self.db.follow_ups.update_many(
                {
                    "user_id": user_id,
                    "email_id": {"$in": email_ids},
                    "status": "pending"
                },
                {
                    "$set": {
                        "status": "cancelled",
                        "cancelled_reason": "Reply received in thread",
                        "cancelled_at": datetime.now(timezone.utc).isoformat()
                    }
                }
            )
            
            if result.modified_count > 0:
                logger.info(f"Cancelled {result.modified_count} follow-ups for thread {thread_id}")
        except Exception as e:
            logger.error(f"Error cancelling follow-ups: {e}")
    
    async def get_thread_context(self, email: Email) -> List[Dict]:
        """Get all emails in the thread for context"""
        try:
            if not email.thread_id:
                return []
            
            # Get all emails in thread, sorted by received_at
            emails = await self.db.emails.find({
                "thread_id": email.thread_id,
                "user_id": email.user_id
            }).sort("received_at", 1).to_list(100)
            
            # Return simplified context
            thread_context = []
            for e in emails:
                thread_context.append({
                    "from": e['from_email'],
                    "to": e['to_email'],
                    "subject": e['subject'],
                    "body": e['body'],
                    "received_at": e['received_at'],
                    "direction": e['direction'],
                    "draft_sent": e.get('draft_content') if e.get('direction') == 'outbound' else None
                })
            
            return thread_context
        except Exception as e:
            logger.error(f"Error getting thread context: {e}")
            return []

