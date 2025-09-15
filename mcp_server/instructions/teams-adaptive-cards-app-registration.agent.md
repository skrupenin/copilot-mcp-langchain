# Teams Adaptive Cards App Registration Guide

This guide covers creating an Azure AD app registration for accessing Microsoft Graph API to manage Teams adaptive cards.

## Prerequisites
- Azure AD tenant access (work/school account)
- Global Administrator or Application Administrator role
- Microsoft Teams access where you posted the adaptive cards

## Required Permissions for Teams Adaptive Cards Management

### Minimal Permissions for Personal 1-1 Chats (RECOMMENDED)
For updating adaptive cards you sent in personal chats with colleagues:

**Delegated Permissions Only:**
- `Chat.ReadWrite` - Read and write your personal chats (1-1 conversations)
- `User.Read` - Read your basic profile (often pre-approved)

**Why these are minimal:**
- No admin consent required in most organizations
- Only access to YOUR chats where YOU are a participant
- Can read/update messages YOU sent
- No access to other users' chats or organization-wide data

### Extended Permissions (if needed later)
If you need to access team channels or other users' content:
- `ChannelMessage.Read.All` - Read all channel messages
- `ChannelMessage.ReadWrite.All` - Read and write all channel messages

## Step-by-Step Registration Process

### 1. Azure Portal Registration
1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to "Azure Active Directory" > "App registrations"
3. Click "New registration"
4. Fill in:
   - Name: "Teams Adaptive Cards Manager"
   - Supported account types: "Accounts in this organizational directory only"
   - Redirect URI: "Web" - `http://localhost:8080/auth/callback`

### 2. Configure API Permissions (Minimal Approach)
1. Go to "API permissions" in your app
2. Click "Add a permission" > "Microsoft Graph" > "Delegated permissions"
3. Add only these minimal permissions:
   - `Chat.ReadWrite` (for accessing your 1-1 chats)
   - `User.Read` (usually pre-approved, for basic profile)
4. **Skip admin consent** - these delegated permissions typically don't require it
5. If consent is needed, you can often consent for yourself during first login

### 3. Create Client Secret
1. Go to "Certificates & secrets"
2. Click "New client secret"
3. Description: "Teams Cards API Access"
4. Expires: Choose appropriate duration (12-24 months recommended)
5. **Save the secret value immediately** - you won't see it again

### 4. Note Required Values
Save these values for your Python application:
- **Application (client) ID**: Found on "Overview" page
- **Directory (tenant) ID**: Found on "Overview" page  
- **Client secret**: The value you just created
- **Redirect URI**: `http://localhost:8080/auth/callback`

## Your Specific Use Case: Personal 1-1 Chats

### Workflow for Updating Your Adaptive Cards
1. **Authenticate** using Authorization Code Flow (user-delegated)
2. **List your chats**: GET `/me/chats` - filter for 1-1 conversations
3. **Find colleague chats**: Match by participant names you specify
4. **Get messages**: GET `/chats/{chat-id}/messages` for each relevant chat
5. **Identify adaptive cards**: Look for messages with `attachments` containing adaptive cards
6. **Check card status**: Parse adaptive card content to find "unanswered" cards
7. **Update cards**: PATCH `/chats/{chat-id}/messages/{message-id}` with new card content

### Advantages of Your Approach
- **No admin consent needed** - delegated permissions for your own data
- **Minimal scope** - only your 1-1 conversations
- **Self-service** - you can set this up without IT department involvement
- **Secure** - limited to conversations you're already part of

## Important Considerations

### Message Update Limitations
- You can only update messages you sent (perfect for your case!)
- Adaptive cards you created can be updated with new content
- You maintain full control over your messages

### Authentication Flows
- **Authorization Code Flow**: Recommended for your interactive use case
- User signs in once, gets refresh token for subsequent API calls

### Rate Limiting
- Microsoft Graph has rate limits
- Implement exponential backoff
- Consider batch operations for multiple updates

## Security Best Practices
- Store credentials securely (environment variables, Azure Key Vault)
- Use minimal required permissions
- Implement proper error handling
- Log API calls for debugging

## Next Steps
1. Complete app registration
2. Set up Python environment with required libraries
3. Implement authentication flow
4. Test with Graph API explorer
5. Build adaptive card update logic
