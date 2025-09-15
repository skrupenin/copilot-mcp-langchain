"""
Microsoft Graph API client for Teams operations
"""
import json
import logging
from typing import Dict, List, Optional

import msal
import requests
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from config import Config

logger = logging.getLogger(__name__)
console = Console()

class GraphClient:
    """Microsoft Graph API client for Teams operations"""
    
    def __init__(self):
        self.config = Config()
        self.access_token = None
        self.app = None
        self._initialize_msal_app()
    
    def _initialize_msal_app(self):
        """Initialize MSAL application"""
        # Use PublicClientApplication for desktop app with delegated permissions
        self.app = msal.PublicClientApplication(
            client_id=self.config.CLIENT_ID,
            authority=self.config.get_authority()
        )
    
    def authenticate(self) -> bool:
        """Authenticate user and get access token"""
        console.print("🔐 Starting authentication process...", style="blue")
        
        # Try to get token from cache first
        accounts = self.app.get_accounts()
        if accounts:
            console.print("Found cached account, attempting silent authentication...")
            result = self.app.acquire_token_silent(
                scopes=self.config.SCOPES,
                account=accounts[0]
            )
            if result and "access_token" in result:
                self.access_token = result["access_token"]
                console.print("✅ Silent authentication successful!", style="green")
                return True
        
        # Interactive user authentication (browser-based)
        console.print("Starting interactive user authentication...")
        console.print("🌐 Opening browser for Microsoft login...")
        
        try:
            # Use interactive authentication for user context
            result = self.app.acquire_token_interactive(
                scopes=self.config.SCOPES,
                parent_window_handle=None,  # Will open in default browser
                prompt="select_account"  # Allow user to select account
            )
            
            if "access_token" in result:
                self.access_token = result["access_token"]
                console.print("✅ User authentication successful!", style="green")
                return True
            else:
                error_msg = result.get("error_description", "Unknown authentication error")
                console.print(f"❌ User authentication failed: {error_msg}", style="red")
                return False
                
        except Exception as e:
            console.print(f"❌ Interactive authentication error: {str(e)}", style="red")
            
            # Fallback to device code flow if interactive fails
            console.print("📱 Falling back to device code flow...", style="yellow")
            
            flow = self.app.initiate_device_flow(scopes=self.config.SCOPES)
            if "user_code" not in flow:
                error_msg = flow.get("error_description", "Failed to create device flow")
                console.print(f"❌ Device flow initiation failed: {error_msg}", style="red")
                return False
            
            console.print(f"\n🔑 Please go to: [bold blue]{flow['verification_uri']}[/bold blue]")
            console.print(f"📝 And enter code: [bold yellow]{flow['user_code']}[/bold yellow]\n")
            console.print("⏳ Waiting for you to complete authentication...")
            
            result = self.app.acquire_token_by_device_flow(flow)
            
            if "access_token" in result:
                self.access_token = result["access_token"]
                console.print("✅ Authentication successful!", style="green")
                return True
            else:
                error_msg = result.get("error_description", "Unknown authentication error")
                console.print(f"❌ Authentication failed: {error_msg}", style="red")
                return False
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def get_user_profile(self) -> Optional[Dict]:
        """Get current user profile"""
        url = f"{self.config.GRAPH_API_BASE}/me"
        
        try:
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting user profile: {e}")
            return None
    
    def get_chats(self) -> List[Dict]:
        """Get first 10 chats for the current user"""
        url = f"{self.config.GRAPH_API_BASE}/me/chats"
        chats = []
        max_chats = 10000

        console.print(f"📱 Fetching your Teams chats (first {max_chats})...", style="blue")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Loading chats...", total=None)
            
            try:
                while url and len(chats) < max_chats:
                    response = requests.get(url, headers=self._get_headers())
                    response.raise_for_status()
                    data = response.json()
                    
                    # Get the chats from this page
                    page_chats = data.get("value", [])
                    
                    # Add chats up to our limit
                    remaining_slots = max_chats - len(chats)
                    chats.extend(page_chats[:remaining_slots])
                    
                    progress.update(task, description=f"Loaded {len(chats)} chats...")
                    
                    # Check if we need more chats and if there's a next page
                    if len(chats) >= max_chats:
                        break
                    
                    url = data.get("@odata.nextLink")  # Get next page if available
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Error getting chats: {e}")
                console.print(f"❌ Error loading chats: {e}", style="red")
                return []
        
        progress.update(task, description=f"✅ Loaded {len(chats)} chats")
        
        return chats
    
    def get_chat_messages(self, chat_id: str, limit: int = 50) -> List[Dict]:
        """Get messages from a specific chat"""
        url = f"{self.config.GRAPH_API_BASE}/chats/{chat_id}/messages"
        messages = []
        
        try:
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            data = response.json()
            all_messages = data.get("value", [])
            
            # Sort messages by createdDateTime descending (most recent first) and limit
            all_messages.sort(key=lambda x: x.get("createdDateTime", ""), reverse=True)
            messages = all_messages[:limit]
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting messages for chat {chat_id}: {e}")
        
        return messages
    
    def update_message(self, chat_id: str, message_id: str, new_content: Dict) -> bool:
        """Update a message with new content - try different approaches"""
        
        # Create Teams deep link for the chat
        teams_link = self._create_teams_chat_link(chat_id, message_id)
        console.print("🔗 Teams link:", style="blue")
        console.print(teams_link, style="bright_blue", no_wrap=True, overflow="ignore")
        print(teams_link)  # Also print plain link for easy copying
        
        # Also show API details for debugging
        api_url = f"{self.config.GRAPH_API_BASE}/chats/{chat_id}/messages/{message_id}"
        console.print(f"� API URL: {api_url}", style="dim blue")
        console.print(f"📝 Message ID: {message_id}", style="dim blue")
        
        # Try the direct update approach
        return self._try_direct_message_update(chat_id, message_id, new_content)
    
    def _create_teams_chat_link(self, chat_id: str, message_id: str) -> str:
        """Create a Teams deep link to open the specific chat message"""
        try:
            # Use the exact format from working Teams links
            # Format: https://teams.microsoft.com/l/message/{chat_id}/{message_id}?context=%7B%22contextType%22%3A%22chat%22%7D
            # Where %7B%22contextType%22%3A%22chat%22%7D is URL-encoded {"contextType":"chat"}
            
            teams_link = f"https://teams.microsoft.com/l/message/{chat_id}/{message_id}?context=%7B%22contextType%22%3A%22chat%22%7D"
            return teams_link
            
        except Exception as e:
            logger.warning(f"Failed to create Teams link: {e}")
            # Fallback: Basic chat link without message ID
            return f"https://teams.microsoft.com/l/message/{chat_id}?context=%7B%22contextType%22%3A%22chat%22%7D"
    
    def _try_direct_message_update(self, chat_id: str, message_id: str, new_content: Dict) -> bool:
        """Try to directly update the message with PowerAutomate-style payloads"""
        url = f"{self.config.GRAPH_API_BASE}/chats/{chat_id}/messages/{message_id}"
        headers = self._get_headers()
        
        # Debug: Show what we're trying to send
        console.print("🔍 DEBUG: Payload structure:", style="yellow")
        console.print(f"new_content keys: {list(new_content.keys())}", style="dim yellow")
        if "attachments" in new_content:
            attachments = new_content["attachments"]
            console.print(f"attachments count: {len(attachments)}", style="dim yellow")
            if attachments:
                first_attachment = attachments[0]
                console.print(f"first attachment keys: {list(first_attachment.keys())}", style="dim yellow")
                if "content" in first_attachment:
                    content = first_attachment["content"]
                    if isinstance(content, dict):
                        console.print(f"card content keys: {list(content.keys())}", style="dim yellow")
                        # Check if it's a valid adaptive card
                        if "type" not in content:
                            console.print("⚠️  Missing 'type' field in card content!", style="red")
                        if "body" not in content:
                            console.print("⚠️  Missing 'body' field in card content!", style="red")
                    else:
                        console.print(f"card content type: {type(content)}", style="dim yellow")
        
        try:
            # Based on PowerAutomate success, try these payload structures
            payloads_to_try = [
                # Method 1: Direct attachments update (current approach)
                new_content,
                
                # Method 2: Body with embedded card (PowerAutomate style)
                {
                    "body": {
                        "contentType": "html",
                        "content": f"<attachment id=\"{message_id}\"></attachment>"
                    },
                    "attachments": new_content.get("attachments", [])
                },
                
                # Method 3: Full message structure with body and attachments
                {
                    "body": {
                        "contentType": "text", 
                        "content": ""
                    },
                    "attachments": new_content.get("attachments", [])
                },
                
                # Method 4: Just the card content directly (no wrapper)
                new_content.get("attachments", [{}])[0] if new_content.get("attachments") else {},
                
                # Method 5: PowerAutomate-style with messageType
                {
                    "messageType": "message",
                    "body": {
                        "contentType": "html",
                        "content": ""
                    },
                    "attachments": new_content.get("attachments", [])
                }
            ]
            
            for i, payload in enumerate(payloads_to_try):
                try:
                    console.print(f"🔍 Trying payload variant {i+1}...", style="dim yellow")
                    response = requests.patch(url, headers=headers, data=json.dumps(payload))
                    
                    console.print(f"🔍 Variant {i+1} response: {response.status_code}", style="dim yellow")
                    
                    if response.status_code == 200:
                        console.print(f"✅ Success with payload variant {i+1}!", style="green")
                        return True
                    elif response.status_code == 403:
                        console.print(f"🔍 Variant {i+1}: Permission denied (403)", style="dim red")
                    elif response.status_code == 400:
                        try:
                            error_detail = response.json()
                            console.print(f"🔍 Variant {i+1} error: {error_detail.get('error', {}).get('message', 'Bad Request')}", style="dim red")
                        except:
                            console.print(f"🔍 Variant {i+1}: Bad Request (400)", style="dim red")
                    else:
                        console.print(f"🔍 Variant {i+1}: Status {response.status_code}", style="dim red")
                        
                except requests.exceptions.RequestException as e:
                    console.print(f"🔍 Variant {i+1} failed: {str(e)[:100]}...", style="dim red")
                    continue
            
            console.print("❌ All update attempts failed", style="red")
            console.print("💡 Note: Microsoft Graph API may not support updating adaptive cards", style="yellow")
            return False
            
        except Exception as e:
            logger.error(f"Error in direct message update: {e}")
            console.print(f"❌ Unexpected error: {e}", style="red")
            return False
    
    def find_colleague_chats(self, colleague_names: List[str]) -> List[Dict]:
        """Find 1-1 chats with specific colleagues"""
        all_chats = self.get_chats()
        colleague_chats = []
        
        console.print(f"🔍 Looking for chats with: {', '.join(colleague_names)}", style="blue")
        
        for chat in all_chats:
            # Filter for 1-1 chats only
            if chat.get("chatType") != "oneOnOne":
                continue
            
            # Get chat ID and debug info
            chat_id = chat.get("id")
            chat_topic = chat.get("topic") or "No topic"
            chat_type = chat.get("chatType", "unknown")
            
            
            if not chat_id:
                continue
                
            # Get members for this chat using separate API call
            try:
                members_url = f"{self.config.GRAPH_API_BASE}/chats/{chat_id}/members"
                response = requests.get(members_url, headers=self._get_headers())
                response.raise_for_status()
                members_data = response.json()
                members = members_data.get("value", [])
                
                if len(members) != 2:  # Should be exactly 2 for 1-1 chat
#                    console.print(f"  ⚠️  Skipping chat with {len(members)} members (expected 2 for 1-1 chat)", style="dim yellow")
                    continue
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Error getting members for chat {chat_id}: {e}")
                console.print(f"  ❌ Error getting members for chat '{chat_topic}': {e}", style="dim red")
                continue
            
            # Debug: Print chat information
            console.print(f"💬 Checking chat: '{chat_topic}' (type: {chat_type}, id: {chat_id[:20] if chat_id else 'N/A'}...)", style="dim blue")

            # Check if any colleague name matches
            for member in members:
                display_name = member.get("displayName", "") or ""
                email = member.get("email", "") or ""
                
                # Debug: Print participant info
                console.print(f"🔍 Checking participant: '{display_name}' (email: {email or 'N/A'})", style="dim")
                
                # Skip if display_name is empty or None
                if not display_name:
                    continue
                
                # Check if any colleague name matches
                for target_name in colleague_names:
                    if target_name.lower() in display_name.lower():
                        colleague_chats.append({
                            "chat": chat,
                            "colleague_name": display_name,
                            "chat_id": chat.get("id")
                        })
                        console.print(f"✅ Found chat with {display_name} (matched: '{target_name}')", style="green")
                        break
                else:
                    continue  # No match found for this member
                break  # Match found, exit member loop
        
        console.print(f"📊 Found {len(colleague_chats)} matching chats", style="blue")
        return colleague_chats
