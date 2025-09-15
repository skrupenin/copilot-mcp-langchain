# Fix Teams Adaptive Cards

A Python application to fix/update adaptive cards posted in Microsoft Teams 1-1 chats.

## Overview

This tool helps you update adaptive cards that you've sent in personal Teams chats with colleagues. It uses minimal Microsoft Graph API permissions to access only your own chats and update messages you originally sent.

## Features

- **Minimal Permissions**: Only requires `Chat.ReadWrite` and `User.Read` delegated permissions
- **Personal Chats Only**: Works with 1-1 conversations where you sent the adaptive cards
- **Colleague Filtering**: Specify colleague names to target specific chats
- **Unanswered Cards Detection**: Identifies adaptive cards that need updates
- **Batch Updates**: Update multiple cards across different chats

## Prerequisites

1. Azure AD app registration (see instructions in `../../instructions/teams-adaptive-cards-app-registration.agent.md`)
2. Python 3.8+ with required packages
3. Access to Teams chats where you sent the adaptive cards

## Setup

1. Complete Azure AD app registration
2. Install dependencies: `pip install -r requirements.txt`
3. Configure environment variables in `.env` file
4. Run the application: `python main.py`

## Configuration

Create a `.env` file with your Azure AD app details:

```
CLIENT_ID=your_client_id_here
CLIENT_SECRET=your_client_secret_here
TENANT_ID=your_tenant_id_here
REDIRECT_URI=http://localhost:8080/auth/callback
```

## Usage

```bash
python main.py --colleagues "John Smith,Jane Doe" --update-type "status"
```

## Security

- Credentials stored in environment variables
- Uses OAuth2 Authorization Code Flow
- Minimal required permissions
- Only accesses your own chat data
