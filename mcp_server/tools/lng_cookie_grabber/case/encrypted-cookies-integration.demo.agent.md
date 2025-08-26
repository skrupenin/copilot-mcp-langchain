## Info
- This case demonstrates the complete corporate-grade encrypted cookies workflow with browser-side AES-256-GCM encryption, secure storage, and HTTP client integration for protected API access

## How to ask for demo in chat  
Use this case to make demo:
```
Show me demo from file:
I need to set up encrypted cookie grabbing system with browser-side encryption, secure storage, and HTTP client integration for corporate APIs.
```

## 🤖 AI Instructions
1. Start cookie grabber servers using batch run
2. Guide user through Chrome extension setup
3. Demonstrate cookie encryption in browser
4. Show HTTP client integration with encrypted cookies
5. Explain security features and file locations

**Key Features**: Browser-side AES-256-GCM encryption, PBKDF2 key derivation (100k iterations), corporate paranoia mode, secure password prompts, encrypted storage, HTTP client integration

## Important Security Notes
- ⚠️ **Corporate Grade Security**: AES-256-GCM with PBKDF2 (100,000 iterations)
- 🔐 **Browser-Side Encryption**: All encryption happens in browser, never sends plaintext cookies
- 🛡️ **Password Required**: Each decryption requires password input (corporate paranoia mode)
- 📁 **Encrypted Storage**: Cookies stored encrypted on disk, password needed for access
- 🚫 **No Plaintext Logs**: All logs and outputs censor cookie values

## Complete Workflow

### Step 1: Start Cookie Grabber Servers
```bash
# Using MCP batch run (recommended)
lng_batch_run:
{
  "pipeline": [
    {
      "tool": "lng_cookie_grabber",
      "params": {
        "operation": "start"
      },
      "output": "servers_started"
    }
  ]
}
```

**Alternative terminal command:**
```powershell
python -m mcp_server.run run lng_cookie_grabber '{\"operation\":\"start\"}'
```

**Alternative using batch run:**
```powershell
python -m mcp_server.run run lng_batch_run '{\"pipeline\":[{\"tool\":\"lng_cookie_grabber\",\"params\":{\"operation\":\"start\"},\"output\":\"servers_started\"}]}'
```

**Expected result:** WebSocket server on port 9001 and Webhook server on port 9000 started

### Step 2: Access Cookie Grabber Status Page
Open browser and navigate to:
```
http://localhost:9000/?sessionId=debug-session-123
```

**Features on status page:**
- Session information with corporate security indicators
- Portal list configuration
- Chrome extension file downloads
- "🔐 Run Encrypted Cookie Grabber" button

### Step 3: Download and Install Chrome Extension

**Download files from status page:**
1. Click "Download background.js" - saves the main extension script
2. Click "Download manifest.json" - saves the extension manifest

**Install Chrome Extension:**
1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top right)
3. Create a new folder (e.g., "cookie-grabber-extension")
4. Place both downloaded files in the folder
5. Click "Load unpacked" and select the folder
6. Extension should appear in Chrome extensions list

**Verify installation:**
- Extension icon should appear in Chrome toolbar
- No errors should show in developer console

### Step 4: Run Encrypted Cookie Grabber

**From status page:**
1. Click "🔐 Run Encrypted Cookie Grabber" button
2. **Corporate Security Prompt** will appear:
   ```
   🔐 Corporate Cookie Encryption
   
   Enter password to encrypt cookies for session 'debug-session-123':
   
   ⚠️  Password will be required for decryption in HTTP requests.
   🛡️ Using AES-256-GCM encryption with PBKDF2 (100k iterations).
   ```
3. Enter a secure password (minimum 4 characters)
4. Extension will:
   - Collect cookies from all domains
   - Encrypt them using AES-256-GCM in browser
   - Send encrypted data via WebSocket to server
   - Display success status: "[✅ cookies encrypted and sent]"

**Security Process:**
- Browser generates random salt and IV
- PBKDF2 derives encryption key from password (100,000 iterations)
- AES-256-GCM encrypts cookie data
- Only encrypted data transmitted to server
- Original cookies never leave browser unencrypted

### Step 5: Verify Encrypted Storage

**Check encrypted files:**
```powershell
# List session directory
Get-ChildItem "mcp_server\config\cookies\debug-session-123\"

# Should show: all_domains.encrypted
```

**File structure:**
```json
{
  "encrypted_data": {
    "ciphertext": [162, 75, 239, ...], // Encrypted cookie data as integer array
    "iv": [152, 150, 171, ...],        // Initialization vector
    "salt": [107, 199, 92, ...],       // PBKDF2 salt
    "algorithm": "AES-256-GCM",
    "iterations": 100000
  },
  "metadata": {
    "encrypted_by": "browser",
    "encryption_method": "AES-256-GCM + PBKDF2",
    "domains_count": 15,
    "timestamp": "2025-08-26T10:30:15.123Z",
    "session_id": "debug-session-123",
    "version": "1.0"
  }
}
```

### Step 6: HTTP Client Integration with Encrypted Cookies

**Basic usage with auto-domain detection:**
```powershell
python -m mcp_server.run run lng_http_client '{
  \"mode\": \"request\",
  \"url\": \"https://next.telescope.epam.com/apps/menu/api/users/me\",
  \"method\": \"GET\",
  \"use_encrypted_cookies\": {
    \"auto_detect_domain\": true,
    \"session\": \"debug-session-123\"
  },
  \"headers\": {
    \"User-Agent\": \"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\"
  }
}'
```

**Manual domain specification:**
```powershell
python -m mcp_server.run run lng_http_client '{
  \"mode\": \"request\",
  \"url\": \"https://next.telescope.epam.com/apps/menu/api/users/me\",
  \"method\": \"GET\",
  \"use_encrypted_cookies\": {
    \"domain\": \"next.telescope.epam.com\",
    \"session\": \"debug-session-123\"
  }
}'
```

**Using MCP batch run:**
```powershell
python -m mcp_server.run run lng_batch_run '{
  \"pipeline\": [
    {
      \"tool\": \"lng_http_client\",
      \"params\": {
        \"mode\": \"request\",
        \"url\": \"https://next.telescope.epam.com/protected/endpoint\",
        \"method\": \"GET\",
        \"use_encrypted_cookies\": {
          \"domain\": \"next.telescope.epam.com\",
          \"session\": \"debug-session-123\"
        },
        \"headers\": {
          \"User-Agent\": \"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\"
        }
      }
    }
  ]
}'
```json
{
  "pipeline": [
    {
      "tool": "lng_http_client",
      "params": {
        "mode": "request",
        "url": "https://next.telescope.epam.com/apps/menu/api/users/me",
        "method": "GET",
        "use_encrypted_cookies": {
          "auto_detect_domain": true,
          "session": "debug-session-123"
        },
        "headers": {
          "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
      },
      "output": "api_response"
    }
  ]
}
```

**Security during HTTP requests:**
1. System prompts for password: "Enter password to decrypt browser-encrypted cookies"
2. Enter the same password used during encryption
3. Cookies are decrypted in memory only
4. HTTP request includes decrypted cookies
5. Response headers show cookies as `<censored>` for security
6. Decrypted cookies are immediately cleared from memory

### Step 7: Monitoring and Logs

**WebSocket server logs:**
```powershell
Get-Content "mcp_server\logs\websocket\cookie-websocket-server.log" -Tail 10
```

**Expected log entries:**
```
[2025-08-26T10:30:00.000Z] CONNECT: Client ws_client_001 connected from 127.0.0.1
[2025-08-26T10:30:15.123Z] MESSAGE: Type=encrypted_cookies, Content-Length=null, Session=debug-session-123
[2025-08-26T10:30:15.125Z] DISCONNECT: Client ws_client_001 disconnected
```

**MCP server logs:**
```powershell
Get-Content "mcp_server\logs\mcp_server.log" -Tail 20
```

**HTTP client usage logs:**
- Cookie count logged (without values): "🔐 Using 8 encrypted cookies for domain: telescope.epam.com"
- Response headers censored: `"Set-Cookie": "<censored>"`
- No plaintext cookie values in any logs

### Step 8: Security Verification

**Test decryption manually:**
```powershell
python -m mcp_server.run run lng_cookie_grabber '{
  "operation": "decrypt",
  "session": "debug-session-123",
  "domain": "all_domains"
}'
```

**Verify password requirement:**
- System should prompt for password every time
- Wrong password should fail with "Browser decryption failed - wrong password or corrupted data"
- Correct password should show success with cookie count

**Check censored headers in HTTP response:**
```json
{
  "success": true,
  "status_code": 200,
  "headers": {
    "Content-Type": "application/json",
    "Set-Cookie": "<censored>",
    "Authorization": "<censored>"
  }
}
```

## Supported API Endpoints

**Cookie Grabber Operations:**
- `{"operation": "start"}` - Start WebSocket/Webhook servers
- `{"operation": "stop"}` - Stop servers
- `{"operation": "store_encrypted", "encrypted_data": "...", "session": "..."}` - Store browser-encrypted cookies
- `{"operation": "decrypt", "session": "...", "domain": "..."}` - Decrypt cookies for domain

**HTTP Client Parameters:**
- `use_encrypted_cookies.session` - Session ID (required)
- `use_encrypted_cookies.domain` - Specific domain (optional)
- `use_encrypted_cookies.auto_detect_domain` - Auto-detect from URL (default: true)

## Troubleshooting

**Common Issues:**

1. **"WebSocket connection failed"**
   - Ensure cookie grabber servers are running
   - Check port 9001 is not blocked
   - Restart servers: `{"operation": "stop"}` then `{"operation": "start"}`

2. **"Password input cancelled"**
   - Extension shows password prompt, don't cancel it
   - Use minimum 4 character password
   - Try disabling popup blockers

3. **"Browser decryption failed - wrong password"**
   - Use exact same password as during encryption
   - Check for typos or case sensitivity
   - Re-encrypt with new session if password forgotten

4. **"No cookies found for domain"**
   - Use `"domain": "all_domains"` to see all available domains
   - Check domain spelling matches exactly
   - Verify cookies were actually encrypted for that domain

5. **"tkinter not available"**
   - Normal warning, console password input will be used
   - Password will be hidden during input (getpass)
   - Type password and press Enter

## File Locations

**Configuration:**
- WebSocket config: `mcp_server/tools/lng_cookie_grabber/websocket.json`
- Webhook config: `mcp_server/tools/lng_cookie_grabber/webhook.json`
- Status page: `mcp_server/tools/lng_cookie_grabber/status.html`

**Storage:**
- Encrypted cookies: `mcp_server/config/cookies/{session}/all_domains.encrypted`
- Session directories: `mcp_server/config/cookies/`

**Logs:**
- WebSocket: `mcp_server/logs/websocket/cookie-websocket-server.log`
- MCP server: `mcp_server/logs/mcp_server.log`

**Extension Templates:**
- Background script: `mcp_server/tools/lng_cookie_grabber/templates/background.js`
- Manifest: `mcp_server/tools/lng_cookie_grabber/templates/manifest.json`

## Security Architecture

**Browser-Side (Client):**
- Web Crypto API for encryption
- PBKDF2 key derivation (100,000 iterations)
- AES-256-GCM authenticated encryption
- Random salt and IV generation
- Secure password prompting

**Server-Side (MCP):**
- Encrypted storage only
- Password required for all decryptions
- Censored logging and responses
- Memory cleanup after use
- No plaintext cookie persistence

**Transport Security:**
- WebSocket connection for encrypted data
- No plaintext cookies transmitted
- Metadata-only logging
- Connection cleanup after transmission

This workflow provides enterprise-grade security for cookie handling while maintaining ease of use for developers working with protected APIs.