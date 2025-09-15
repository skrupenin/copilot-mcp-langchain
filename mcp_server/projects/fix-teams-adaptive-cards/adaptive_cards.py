"""
Adaptive Cards processor for detecting and updating cards
"""
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from rich.console import Console
from rich.table import Table

logger = logging.getLogger(__name__)
console = Console()

class AdaptiveCardProcessor:
    """Processes and updates adaptive cards in Teams messages"""
    
    def __init__(self):
        self.console = Console()
    
    def find_adaptive_cards_in_messages(self, messages: List[Dict]) -> List[Dict]:
        """Find messages containing adaptive cards"""
        card_messages = []
        
        for message in messages:
            # Check if message has attachments
            attachments = message.get("attachments", [])
            if not attachments:
                continue
            
            # Look for adaptive card attachments
            for attachment in attachments:
                if attachment.get("contentType") == "application/vnd.microsoft.card.adaptive":
                    # Safely extract sender information
                    from_info = message.get("from") or {}
                    user_info = from_info.get("user") or {}
                    sender_name = user_info.get("displayName", "Unknown")
                    
                    # Parse card content - it might be a JSON string or already a dict
                    raw_content = attachment.get("content", {})
                    if isinstance(raw_content, str):
                        try:
                            card_content = json.loads(raw_content)
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to parse card content as JSON: {raw_content}")
                            card_content = {}
                    else:
                        card_content = raw_content
                    
                    card_info = {
                        "message": message,
                        "message_id": message.get("id"),
                        "created_time": message.get("createdDateTime"),
                        "from": sender_name,
                        "attachment": attachment,
                        "card_content": card_content
                    }
                    card_messages.append(card_info)
        
        return card_messages
    
    def is_card_unanswered(self, card_content: Dict) -> bool:
        """Check if an adaptive card appears to be unanswered"""
        # This is a heuristic - you may need to adjust based on your card structure
        
        # Handle case where card_content might still be a string
        if isinstance(card_content, str):
            try:
                card_content = json.loads(card_content)
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse card content in is_card_unanswered: {card_content}")
                return False
        
        # Ensure card_content is a dict
        if not isinstance(card_content, dict):
            logger.warning(f"Unexpected card_content type: {type(card_content)}")
            return False
        
        # Look for common indicators of unanswered cards
        body = card_content.get("body", [])
        
        for element in body:
            # Check for text blocks that might indicate status
            if element.get("type") == "TextBlock":
                text = element.get("text", "").lower()
                if any(indicator in text for indicator in ["pending", "waiting", "unanswered", "open", "todo"]):
                    return True
            
            # Check for input elements that might need responses
            if element.get("type") in ["Input.Text", "Input.Choice", "Input.Toggle", "Input.Date"]:
                # If there are input elements, consider it potentially unanswered
                return True
        
        # Look for actions that might indicate the card needs response
        actions = card_content.get("actions", [])
        if actions:
            # If there are actions available, it might need interaction
            return True
        
        return False
    
    def create_updated_card_content(self, original_card: Dict, update_type: str = "completed") -> Dict:
        """Create updated content for an adaptive card"""
        updated_card = original_card.copy()
        
        if update_type == "completed":
            # Example: Mark card as completed
            self._add_completion_status(updated_card)
        elif update_type == "reminder":
            # Example: Add reminder information
            self._add_reminder_info(updated_card)
        elif update_type == "custom":
            # Custom update logic - you can extend this
            self._add_custom_update(updated_card)
        
        return updated_card
    
    def _add_completion_status(self, card_content: Dict):
        """Add completion status by appending timestamp to first TextBlock"""
        body = card_content.get("body", [])
        
        if not body:
            logger.warning("Card has no body elements to update")
            return
        
        # Find the first TextBlock element
        first_text_block = None
        for element in body:
            if element.get("type") == "TextBlock":
                first_text_block = element
                break
        
        if first_text_block:
            # Get current text and append timestamp
            current_text = first_text_block.get("text", "")
            timestamp = datetime.now().strftime("%H:%M:%S")
            updated_text = f"{current_text} Updated {timestamp}"
            
            # Update the text
            first_text_block["text"] = updated_text
            console.print(f"✏️  Updated text: {updated_text}", style="green")
        else:
            logger.warning("No TextBlock found in card body to update")
        
        # Optionally remove actions to indicate completion
        if "actions" in card_content:
            card_content["actions"] = []
    
    def _add_reminder_info(self, card_content: Dict):
        """Add reminder information to a card"""
        body = card_content.get("body", [])
        
        reminder_element = {
            "type": "TextBlock",
            "text": "🔔 **REMINDER** - Please review this item",
            "color": "Warning",
            "weight": "Bolder",
            "spacing": "Medium"
        }
        
        body.insert(0, reminder_element)
    
    def _add_custom_update(self, card_content: Dict):
        """Add custom update to a card"""
        body = card_content.get("body", [])
        
        custom_element = {
            "type": "TextBlock",
            "text": "Card content has been modified",
            "color": "Accent",
            "weight": "Bolder",
            "spacing": "Medium"
        }
        
        body.insert(0, custom_element)
    
    def display_cards_summary(self, colleague_chats: List[Dict]):
        """Display a summary of found adaptive cards"""
        table = Table(title="Found Adaptive Cards")
        table.add_column("Colleague", style="cyan")
        table.add_column("Cards Found", justify="center")
        table.add_column("Unanswered", justify="center", style="yellow")
        table.add_column("Last Activity", style="green")
        
        total_cards = 0
        total_unanswered = 0
        
        for chat_info in colleague_chats:
            colleague_name = chat_info["colleague_name"]
            cards = chat_info.get("cards", [])
            unanswered_cards = [card for card in cards if self.is_card_unanswered(card["card_content"])]
            
            last_activity = "No cards"
            if cards:
                # Get the most recent card date
                dates = [card["created_time"] for card in cards if card["created_time"]]
                if dates:
                    last_activity = max(dates)[:10]  # Just the date part
            
            table.add_row(
                colleague_name,
                str(len(cards)),
                str(len(unanswered_cards)),
                last_activity
            )
            
            total_cards += len(cards)
            total_unanswered += len(unanswered_cards)
        
        console.print(table)
        console.print(f"\n📊 **Summary**: {total_cards} total cards, {total_unanswered} unanswered", style="bold blue")
        
        return total_cards, total_unanswered
