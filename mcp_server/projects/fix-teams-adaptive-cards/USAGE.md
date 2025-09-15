# Teams Adaptive Cards Fixer - Usage Guide

## Quick Start

1. **Complete Azure AD App Registration** (see instructions in `../../instructions/teams-adaptive-cards-app-registration.agent.md`)

2. **Configure the Application**
   ```bash
   python setup.py
   ```
   Then edit the `.env` file with your Azure AD app details.

3. **Run the Application**
   ```bash
   # Dry run to see what would be updated (recommended first)
   python main.py --colleagues "John Smith,Jane Doe" --dry-run
   
   # Actually update the cards
   python main.py --colleagues "John Smith,Jane Doe" --update-type completed
   ```

## Command Line Options

### Required
- `--colleagues` / `-c`: Comma-separated list of colleague names to search for
  - Example: `"John Smith,Jane Doe,Bob Wilson"`
  - The tool will find 1-1 chats with these people

### Optional
- `--update-type` / `-t`: How to update the cards (default: `completed`)
  - `completed`: Mark cards as completed with timestamp
  - `reminder`: Add reminder notice to cards
  - `custom`: Add custom update message
  
- `--dry-run` / `-d`: Preview what would be updated without making changes

## Usage Examples

### 1. Preview Changes (Recommended First)
```bash
python main.py --colleagues "John Smith,Jane Doe" --dry-run
```
This will:
- Show you which chats are found
- Display how many adaptive cards are detected
- Show which cards would be updated
- **Not make any actual changes**

### 2. Mark Cards as Completed
```bash
python main.py --colleagues "John Smith,Jane Doe" --update-type completed
```
This will:
- Find unanswered adaptive cards in chats with specified colleagues
- Add a "✅ COMPLETED" status with timestamp
- Remove action buttons (since they're completed)

### 3. Add Reminder to Cards
```bash
python main.py --colleagues "John Smith" --update-type reminder
```
This will:
- Add a "🔔 REMINDER" notice to the top of cards
- Keep the original content and actions

### 4. Custom Update
```bash
python main.py --colleagues "Jane Doe" --update-type custom
```
This will:
- Add a "📝 UPDATED" notice to cards
- You can modify the `_add_custom_update` method in `adaptive_cards.py` for custom logic

## What the Tool Does

1. **Authenticates** you with Microsoft Graph API using minimal permissions
2. **Finds your 1-1 chats** with the specified colleagues
3. **Scans recent messages** (last 100) in each chat
4. **Identifies adaptive cards** that you sent
5. **Detects "unanswered" cards** based on content patterns
6. **Updates the cards** with new status information
7. **Shows progress** and results with a nice summary table

## Card Detection Logic

The tool considers a card "unanswered" if it has:
- Text containing words like "pending", "waiting", "unanswered", "open", "todo"
- Input elements (Input.Text, Input.Choice, etc.)
- Action buttons available

You can customize this logic in `adaptive_cards.py` -> `is_card_unanswered()` method.

## Security & Permissions

✅ **Minimal Permissions**: Only `Chat.ReadWrite` and `User.Read`
✅ **Your Data Only**: Only accesses 1-1 chats where you're a participant  
✅ **Your Messages Only**: Can only update messages you originally sent
✅ **No Admin Consent**: Works with standard user permissions

## Troubleshooting

### Authentication Issues
- Make sure your Azure AD app has the correct redirect URI: `http://localhost:8080/auth/callback`
- Verify your CLIENT_ID, CLIENT_SECRET, and TENANT_ID are correct
- Try clearing browser cache if authentication fails

### No Cards Found
- Check that colleague names match exactly (or partially) with their display names in Teams
- Verify you actually sent adaptive cards to these people
- Try increasing the message limit in `get_chat_messages()` if cards are older

### Permission Denied
- Make sure you're using **delegated permissions**, not application permissions
- Verify the Azure AD app has `Chat.ReadWrite` permission
- Try re-authenticating: delete cached credentials and run again

### Update Failures
- You can only update messages you sent (Teams/Graph API limitation)
- Some very old messages might not be updatable
- Check the console output for specific error messages

## Customization

### Custom Card Detection
Edit `adaptive_cards.py` -> `is_card_unanswered()` to change how cards are detected.

### Custom Update Logic
Edit `adaptive_cards.py` -> `_add_custom_update()` to implement your own update logic.

### Different Update Types
Add new update types by:
1. Adding to the `click.Choice` in `main.py`
2. Adding a new method in `adaptive_cards.py`
3. Adding the case in `create_updated_card_content()`

## File Structure
```
fix-teams-adaptive-cards/
├── main.py              # Main application entry point
├── config.py            # Configuration management
├── graph_client.py      # Microsoft Graph API client
├── adaptive_cards.py    # Adaptive card processing logic
├── examples.py          # Example card templates
├── setup.py             # Setup and configuration script
├── requirements.txt     # Python dependencies
├── .env.example         # Environment template
├── .env                 # Your actual configuration (created by setup)
└── README.md           # Project documentation
```
