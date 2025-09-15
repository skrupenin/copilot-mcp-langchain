"""
Main application for fixing Teams adaptive cards
"""
import csv
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List

import click
from rich.console import Console
from rich.prompt import Confirm, Prompt

from config import Config
from graph_client import GraphClient
from adaptive_cards import AdaptiveCardProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
console = Console()

class TeamsCardFixer:
    """Main application class for fixing Teams adaptive cards"""
    
    def __init__(self):
        self.config = Config()
        self.graph_client = GraphClient()
        self.card_processor = AdaptiveCardProcessor()
    
    def validate_setup(self) -> bool:
        """Validate application setup"""
        console.print("🔧 Validating application setup...", style="blue")
        
        if not self.config.validate():
            console.print("❌ Configuration validation failed", style="red")
            console.print("Please check your .env file or environment variables", style="yellow")
            return False
        
        console.print("✅ Configuration validated", style="green")
        return True
    
    def authenticate(self) -> bool:
        """Authenticate with Microsoft Graph"""
        console.print("🔐 Authenticating with Microsoft Graph...", style="blue")
        
        if not self.graph_client.authenticate():
            console.print("❌ Authentication failed", style="red")
            return False
        
        # Test authentication by getting user profile
        user_profile = self.graph_client.get_user_profile()
        if user_profile:
            user_name = user_profile.get("displayName", "Unknown")
            console.print(f"✅ Authenticated as: {user_name}", style="green")
            return True
        else:
            console.print("❌ Failed to get user profile", style="red")
            return False
    
    def find_and_analyze_cards(self, colleague_names: List[str]) -> List[dict]:
        """Find and analyze adaptive cards in colleague chats"""
        console.print(f"🔍 Searching for adaptive cards...", style="blue")
        
        # Find colleague chats
        colleague_chats = self.graph_client.find_colleague_chats(colleague_names)
        
        if not colleague_chats:
            console.print("❌ No chats found with specified colleagues", style="red")
            return []
        
        # Get messages and find adaptive cards for each chat
        for chat_info in colleague_chats:
            chat_id = chat_info["chat_id"]
            colleague_name = chat_info["colleague_name"]
            
            console.print(f"📱 Analyzing chat with {colleague_name}...", style="blue")
            
            # Get recent messages
            messages = self.graph_client.get_chat_messages(chat_id, limit=100)
            
            # Find adaptive cards
            card_messages = self.card_processor.find_adaptive_cards_in_messages(messages)
            chat_info["cards"] = card_messages
            
            console.print(f"Found {len(card_messages)} adaptive cards", style="green")
        
        # Display summary
        self.card_processor.display_cards_summary(colleague_chats)
        
        return colleague_chats
    
    def export_cards_to_csv(self, colleague_chats: List[dict], filename: str = None) -> str:
        """Export adaptive cards information to CSV file"""
        # Get the directory where main.py resides
        script_dir = Path(__file__).parent
        output_dir = script_dir / "Output"
        
        # Create Output directory if it doesn't exist
        output_dir.mkdir(exist_ok=True)
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"teams_adaptive_cards_{timestamp}.csv"
        
        # Construct full path to output file
        output_path = output_dir / filename
        
        csv_data = []
        
        for chat_info in colleague_chats:
            colleague_name = chat_info["colleague_name"]
            conversation_id = chat_info["chat_id"]
            cards = chat_info.get("cards", [])
            
            # Filter for unanswered cards only
            unanswered_cards = [
                card for card in cards 
                if self.card_processor.is_card_unanswered(card["card_content"])
            ]
            
            for card in unanswered_cards:
                message_id = card["message_id"]
                created_time = card["created_time"]
                
                # Parse the ISO datetime and format it nicely
                try:
                    dt = datetime.fromisoformat(created_time.replace('Z', '+00:00'))
                    formatted_date = dt.strftime("%Y-%m-%d %H:%M:%S")
                except:
                    formatted_date = created_time  # Fallback to original if parsing fails
                
                csv_data.append({
                    "contact_name": colleague_name,
                    "conversation_id": conversation_id,
                    "message_date_time": formatted_date,
                    "message_id": message_id
                })
        
        # Write to CSV file
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ["contact_name", "conversation_id", "message_date_time", "message_id"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
                
                # Write header
                writer.writeheader()
                
                # Write data rows
                for row in csv_data:
                    writer.writerow(row)
            
            console.print(f"✅ Exported {len(csv_data)} cards to: {output_path.name}", style="green")
            console.print(f"📁 File saved in: {output_path.parent}", style="blue")
            
            return str(output_path)
            
        except Exception as e:
            console.print(f"❌ Error writing CSV file: {e}", style="red")
            return None

@click.command()
@click.option('--colleagues', '-c', required=True, help='Comma-separated list of colleague names to search for')
@click.option('--output', '-o', help='Output CSV filename (optional, auto-generated if not provided)')
@click.option('--dry-run', '-d', is_flag=True, help='Show what would be exported without creating the file')
def main(colleagues: str, output: str, dry_run: bool):
    """Export Teams adaptive cards information to CSV file"""
    
    console.print("🚀 Teams Adaptive Cards Exporter", style="bold blue")
    console.print("=" * 50)
    
    # Initialize application
    app = TeamsCardFixer()
    
    # Validate setup
    if not app.validate_setup():
        sys.exit(1)
    
    # Authenticate
    if not app.authenticate():
        sys.exit(1)
    
    # Parse colleague names
    colleague_names = [name.strip() for name in colleagues.split(',')]
    console.print(f"👥 Looking for chats with: {', '.join(colleague_names)}", style="blue")
    
    # Find and analyze cards
    colleague_chats = app.find_and_analyze_cards(colleague_names)
    
    if not colleague_chats:
        console.print("🤷 No chats or cards found", style="yellow")
        sys.exit(0)
    
    # Count total unanswered cards
    total_unanswered = sum(
        len([card for card in chat.get("cards", []) 
             if app.card_processor.is_card_unanswered(card["card_content"])])
        for chat in colleague_chats
    )
    
    if total_unanswered == 0:
        console.print("✅ No unanswered cards found!", style="green")
        sys.exit(0)
    
    console.print(f"\n📋 Found {total_unanswered} unanswered cards to export", style="yellow")
    
    if dry_run:
        console.print("🧪 DRY RUN MODE: Showing what would be exported", style="yellow")
        console.print("📄 CSV structure: contact_name;conversation_id;message_date_time;message_id", style="blue")
        
        # Show output directory
        script_dir = Path(__file__).parent
        output_dir = script_dir / "Output"
        if not output:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            preview_filename = f"teams_adaptive_cards_{timestamp}.csv"
        else:
            preview_filename = output
        preview_path = output_dir / preview_filename
        
        console.print(f"📁 File would be saved to: {preview_path}", style="blue")
        console.print("🔍 Preview of cards that would be exported:", style="blue")
        
        for chat_info in colleague_chats:
            colleague_name = chat_info["colleague_name"]
            conversation_id = chat_info["chat_id"]
            cards = [card for card in chat_info.get("cards", []) 
                    if app.card_processor.is_card_unanswered(card["card_content"])]
            
            for card in cards:
                message_id = card["message_id"]
                created_time = card["created_time"]
                try:
                    dt = datetime.fromisoformat(created_time.replace('Z', '+00:00'))
                    formatted_date = dt.strftime("%Y-%m-%d %H:%M:%S")
                except:
                    formatted_date = created_time
                
                console.print(f"  📝 {colleague_name};{conversation_id};{formatted_date};{message_id}", style="dim cyan")
        
        console.print("\n� Remove --dry-run flag to create the actual CSV file", style="green")
        sys.exit(0)
    
    # Export to CSV
    filename = app.export_cards_to_csv(colleague_chats, output)
    
    if filename:
        console.print(f"\n🎉 Successfully exported {total_unanswered} cards to CSV!", style="bold green")
        console.print(f"📄 File: {filename}", style="green")
        console.print(f"📊 Structure: contact_name;conversation_id;message_date_time;message_id", style="blue")
    else:
        console.print("❌ Export failed", style="red")
        sys.exit(1)

if __name__ == "__main__":
    main()
