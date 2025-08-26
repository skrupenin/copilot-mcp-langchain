import mcp.types as types
import json
import logging
import os
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import getpass

# Optional GUI support
try:
    import tkinter as tk
    from tkinter import simpledialog
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False

logger = logging.getLogger('mcp_server.tools.lng_cookie_grabber')

# Warn about GUI availability after logger is defined
if not GUI_AVAILABLE:
    logger.warning("tkinter not available - using console password input only")

# Cryptographic constants for corporate-grade security
ENCRYPTION_KEY_LENGTH = 32  # AES-256
PBKDF2_ITERATIONS = 100000  # OWASP recommended minimum
TAG_LENGTH = 16  # GCM authentication tag

def secure_password_prompt(prompt_text: str) -> str:
    """Show secure password input dialog."""
    import platform
    
    try:
        if GUI_AVAILABLE and platform.system() == "Windows":
            # Use tkinter for Windows GUI
            root = tk.Tk()
            root.withdraw()  # Hide main window
            root.attributes('-topmost', True)  # Always on top
            
            password = simpledialog.askstring(
                "Cookie Decryption",
                prompt_text,
                show='*'  # Hide password characters
            )
            root.destroy()
            
            if not password:
                raise ValueError("Password input cancelled")
            return password
        else:
            # Use console input for Linux/Mac or when GUI not available
            return getpass.getpass(prompt_text + ": ")
    except Exception as e:
        logger.error(f"Failed to get password input: {e}")
        # Fallback to console input
        try:
            return getpass.getpass(prompt_text + " (console fallback): ")
        except:
            raise ValueError("Password input failed")

async def decrypt_browser_data(encrypted_package: dict) -> str:
    """Decrypt browser-encrypted data using Web Crypto API compatible method."""
    try:
        # Get password from user (corporate paranoia mode - ALWAYS ask!)
        password = secure_password_prompt("Enter password to decrypt browser-encrypted cookies")
        
        # For browser-encrypted data, we need to use the same method as browser
        # Browser uses PBKDF2 with salt, not master key
        
        # Get salt from package - browser sends as integer array
        salt = bytes(encrypted_package["salt"])
        logger.info(f"Salt length: {len(salt)} bytes")
        
        # Derive key using same method as browser (PBKDF2 only, no master key)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=ENCRYPTION_KEY_LENGTH,
            salt=salt,
            iterations=encrypted_package.get("iterations", PBKDF2_ITERATIONS),
            backend=default_backend()
        )
        
        decryption_key = kdf.derive(password.encode('utf-8'))
        logger.info(f"Key derived successfully, length: {len(decryption_key)} bytes")
        
        # Decode ciphertext and IV - browser sends as integer arrays
        ciphertext_bytes = bytes(encrypted_package["ciphertext"])
        iv_bytes = bytes(encrypted_package["iv"])
        logger.info(f"Ciphertext length: {len(ciphertext_bytes)}, IV length: {len(iv_bytes)}")
        
        # Browser AES-GCM includes auth tag in ciphertext (last 16 bytes)
        actual_ciphertext = ciphertext_bytes[:-TAG_LENGTH]
        tag = ciphertext_bytes[-TAG_LENGTH:]
        logger.info(f"Actual ciphertext length: {len(actual_ciphertext)}, Tag length: {len(tag)}")
        
        # Create cipher with tag for authentication
        cipher = Cipher(
            algorithms.AES(decryption_key),
            modes.GCM(iv_bytes, tag),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        
        # Decrypt and verify
        plaintext = decryptor.update(actual_ciphertext) + decryptor.finalize()
        logger.info(f"Decryption successful, plaintext length: {len(plaintext)} bytes")
        
        return plaintext.decode('utf-8')
        
    except Exception as e:
        logger.error(f"Browser decryption failed: {e}")
        raise ValueError("Browser decryption failed - wrong password or corrupted data")

async def tool_info() -> dict:
    return {
        "description": """Cookie Grabber Tool for Managing WebSocket/Webhook Servers and Processing Cookie Data.

**Universal Cookie Grabber Management System**
Complete solution for cookie collection with Chrome extension and server management.

**Operations:**
• `start` - Start webhook and websocket servers for cookie collection (stops existing first)
• `stop` - Stop webhook and websocket servers
• `decrypt` - Decrypt saved cookie data for use in HTTP requests  
• `store_encrypted` - Store pre-encrypted cookie data from browser

**Features:**
**Direct Server Management** - Direct Python imports for deterministic control
**Cookie Processing** - Parse and organize cookie data by domain
**File Organization** - Save cookies to config/cookies/<sessionId>/<domain>.txt
**Session Support** - Support for sessionId-based cookie organization
**Error Handling** - Comprehensive error handling and logging

**Start Operation:**
Starts both webhook (port 9000) and websocket (port 9001) servers using 
the configuration files from the cookie grabber directory. Automatically
stops existing servers first for clean restart.

**Stop Operation:**
Stops both webhook and websocket servers cleanly.

**Store Encrypted Operation:**
Receives and stores pre-encrypted cookie data from browser.
Browser performs AES-256-GCM encryption with user password,
server just organizes and saves the encrypted files.

**Decrypt Operation:**
Decrypts cookie data for use in HTTP requests. Shows secure password
prompt for each decryption (corporate paranoia mode).

**Example Usage:**

Start servers:
```json
{
  "operation": "start"
}
```

Decrypt cookies:
```json
{
  "operation": "decrypt",
  "session": "my_session_123", 
  "domain": "domain1.com"
}
```

Store pre-encrypted cookies:
```json
{
  "operation": "store_encrypted",
  "encrypted_data": "{\"type\":\"encrypted_cookies\",\"sessionId\":\"...\",\"encrypted\":{...}}",
  "session": "my_session_123"
}
```

Stop servers:
```json
{
  "operation": "stop"
}
```
""",
        "schema": {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "description": "Operation to perform",
                    "enum": ["start", "stop", "decrypt", "store_encrypted"]
                },
                "cookies": {
                    "type": "string", 
                    "description": "DEPRECATED - Cookie data (legacy process operation)"
                },
                "session": {
                    "type": "string",
                    "description": "Session ID for organizing cookie files (required for 'decrypt', 'store_encrypted' operations)"
                },
                "domain": {
                    "type": "string",
                    "description": "Domain to decrypt cookies for (required for 'decrypt' operation)"
                },
                "encrypted_data": {
                    "type": "string",
                    "description": "Pre-encrypted cookie data from browser (required for 'store_encrypted' operation)"
                }
            },
            "required": ["operation"]
        }
    }

async def run_tool(name: str, parameters: dict) -> list[types.Content]:
    """Execute cookie grabber operations."""
    
    try:
        operation = parameters.get("operation")
        
        if operation == "start":
            return await start_servers()
        elif operation == "stop":
            return await stop_servers()
        elif operation == "decrypt":
            session = parameters.get("session")
            domain = parameters.get("domain")
            
            if not session:
                raise ValueError("'session' parameter is required for decrypt operation")
            if not domain:
                raise ValueError("'domain' parameter is required for decrypt operation")
                
            return await decrypt_cookies(session, domain)
        elif operation == "store_encrypted":
            encrypted_data = parameters.get("encrypted_data")
            session = parameters.get("session")
            
            if not encrypted_data:
                raise ValueError("'encrypted_data' parameter is required for store_encrypted operation")
            if not session:
                raise ValueError("'session' parameter is required for store_encrypted operation")
                
            return await store_encrypted_cookies(encrypted_data, session)
        else:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": f"Unknown operation: {operation}"
                }, indent=2)
            )]
            
    except Exception as e:
        logger.error(f"Error in lng_cookie_grabber: {e}")
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": str(e)
            }, indent=2)
        )]

async def start_servers() -> list[types.Content]:
    """Start webhook and websocket servers. Stops existing servers first."""
    try:
        logger.info("Starting cookie grabber servers (stopping existing first)...")
        
        # Stop existing servers first
        try:
            await stop_servers()
            logger.info("Existing servers stopped")
        except Exception as e:
            logger.warning(f"Error stopping existing servers (may not exist): {e}")
        
        results = []
        
        # Start webhook server
        try:
            from ..lng_webhook_server.tool import run_tool as run_webhook_tool
            
            webhook_params = {
                "operation": "start",
                "config_file": "mcp_server/tools/lng_cookie_grabber/webhook.json",
                "name": "cookie-status-server",
                "thread_mode": True
            }
            
            webhook_result = await run_webhook_tool("lng_webhook_server", webhook_params)
            webhook_data = json.loads(webhook_result[0].text)
            results.append({
                "service": "webhook",
                "status": "started" if webhook_data.get("success") else "failed",
                "details": webhook_data
            })
            
            logger.info(f"Webhook server: {webhook_data.get('message', 'Unknown result')}")
            
        except Exception as e:
            logger.error(f"Failed to start webhook server: {e}")
            results.append({
                "service": "webhook", 
                "status": "failed",
                "error": str(e)
            })
        
        # Start websocket server
        try:
            from ..lng_websocket_server.tool import run_tool as run_websocket_tool
            
            websocket_params = {
                "operation": "server_start",
                "config_file": "mcp_server/tools/lng_cookie_grabber/websocket.json",
                "name": "cookie-websocket-server"
            }
            
            websocket_result = await run_websocket_tool("lng_websocket_server", websocket_params)
            websocket_data = json.loads(websocket_result[0].text)
            results.append({
                "service": "websocket",
                "status": "started" if websocket_data.get("success") else "failed", 
                "details": websocket_data
            })
            
            logger.info(f"WebSocket server: {websocket_data.get('message', 'Unknown result')}")
            
        except Exception as e:
            logger.error(f"Failed to start websocket server: {e}")
            results.append({
                "service": "websocket",
                "status": "failed", 
                "error": str(e)
            })
        
        # Determine overall success
        all_started = all(r["status"] == "started" for r in results)
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "success": all_started,
                "message": f"Cookie grabber servers {'started successfully' if all_started else 'failed to start'}",
                "operation": "start",
                "timestamp": datetime.now().isoformat(),
                "services": results
            }, indent=2)
        )]
        
    except Exception as e:
        logger.error(f"Failed to start cookie grabber servers: {e}")
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": str(e),
                "operation": "start"
            }, indent=2)
        )]

async def stop_servers() -> list[types.Content]:
    """Stop webhook and websocket servers."""
    try:
        logger.info("Stopping cookie grabber servers...")
        
        results = []
        
        # Stop webhook server
        try:
            from ..lng_webhook_server.tool import run_tool as run_webhook_tool
            
            webhook_params = {
                "operation": "stop",
                "name": "cookie-status-server"
            }
            
            webhook_result = await run_webhook_tool("lng_webhook_server", webhook_params)
            webhook_data = json.loads(webhook_result[0].text)
            results.append({
                "service": "webhook",
                "status": "stopped" if webhook_data.get("success") else "failed",
                "details": webhook_data
            })
            
            logger.info(f"Webhook server: {webhook_data.get('message', 'Unknown result')}")
            
        except Exception as e:
            logger.error(f"Failed to stop webhook server: {e}")
            results.append({
                "service": "webhook",
                "status": "failed",
                "error": str(e)
            })
        
        # Stop websocket server
        try:
            from ..lng_websocket_server.tool import run_tool as run_websocket_tool
            
            websocket_params = {
                "operation": "server_stop", 
                "name": "cookie-websocket-server"
            }
            
            websocket_result = await run_websocket_tool("lng_websocket_server", websocket_params)
            websocket_data = json.loads(websocket_result[0].text)
            results.append({
                "service": "websocket",
                "status": "stopped" if websocket_data.get("success") else "failed",
                "details": websocket_data
            })
            
            logger.info(f"WebSocket server: {websocket_data.get('message', 'Unknown result')}")
            
        except Exception as e:
            logger.error(f"Failed to stop websocket server: {e}")
            results.append({
                "service": "websocket",
                "status": "failed",
                "error": str(e)
            })
        
        # Determine overall success  
        all_stopped = all(r["status"] == "stopped" for r in results)
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "success": all_stopped,
                "message": f"Cookie grabber servers {'stopped successfully' if all_stopped else 'failed to stop'}",
                "operation": "stop",
                "timestamp": datetime.now().isoformat(),
                "services": results
            }, indent=2)
        )]
        
    except Exception as e:
        logger.error(f"Failed to stop cookie grabber servers: {e}")
        return [types.TextContent(
            type="text", 
            text=json.dumps({
                "success": False,
                "error": str(e),
                "operation": "stop"
            }, indent=2)
        )]

async def decrypt_cookies(session: str, domain: str) -> list[types.Content]:
    """Decrypt cookie data for use in HTTP requests (corporate paranoia mode)."""
    try:
        logger.info(f"Decrypting cookies for session: {session}, domain: {domain}")
        
        # Look for browser-encrypted file first (new format)
        browser_encrypted_file = f"mcp_server/config/cookies/{session}/all_domains.encrypted"
        
        if os.path.exists(browser_encrypted_file):
            # Handle browser-encrypted format
            logger.info("Found browser-encrypted file, processing...")
            
            # Load encrypted storage package
            with open(browser_encrypted_file, 'r', encoding='utf-8') as f:
                storage_package = json.load(f)
            
            # Extract encrypted data from storage package
            encrypted_package = storage_package.get("encrypted_data")
            if not encrypted_package:
                raise ValueError("Invalid storage package format")
            
            # Browser data is already in correct format - pass directly to decrypt_browser_data
            decrypted_cookies = await decrypt_browser_data(encrypted_package)
            
            # Parse decrypted cookies to extract specific domain or all domains
            cookie_lines = decrypted_cookies.strip().split('\n')
            
            if domain == 'all_domains':
                # Return all cookies from all domains
                domain_cookies = decrypted_cookies.strip()
                success_message = f"Successfully decrypted cookies for all domains (browser encryption)"
            else:
                # Look for specific domain
                domain_cookies = None
                for i, line in enumerate(cookie_lines):
                    if line.strip() == domain:
                        # Found the domain, next line should be cookies
                        if i + 1 < len(cookie_lines):
                            domain_cookies = cookie_lines[i + 1]
                            break
                
                if not domain_cookies:
                    raise ValueError(f"No cookies found for domain '{domain}' in decrypted data")
                    
                success_message = f"Successfully decrypted cookies for domain '{domain}' (browser encryption)"
            
            # Clear password from memory immediately
            password = None
            
            result = {
                "success": True,
                "message": success_message,
                "operation": "decrypt",
                "session": session,
                "domain": domain,
                "timestamp": datetime.now().isoformat(),
                "cookies": domain_cookies,
                "cookie_length": len(domain_cookies),
                "encryption_source": "browser",
                "security_note": "Cookies decrypted in memory - will be cleared after use"
            }
            
        else:
            # No encrypted cookies found for this session/domain
            raise ValueError(f"No encrypted cookies found for domain '{domain}' in session '{session}'")
        
        logger.info(f"Decrypted {len(result['cookies'])} characters of cookie data for {domain}")
        
        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
        
    except Exception as e:
        logger.error(f"Failed to decrypt cookies: {e}")
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": str(e),
                "operation": "decrypt",
                "session": session,
                "domain": domain
            }, indent=2)
        )]

async def store_encrypted_cookies(encrypted_data: str, session: str) -> list[types.Content]:
    """Store pre-encrypted cookie data from browser (browser-side encryption)."""
    try:
        logger.info(f"Storing pre-encrypted cookies for session: {session}")
        
        # Parse encrypted message from browser
        try:
            encrypted_message = json.loads(encrypted_data)
            if encrypted_message.get('type') != 'encrypted_cookies':
                raise ValueError("Invalid encrypted message format")
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format in encrypted_data")
        
        # Extract data from message
        sessionId = encrypted_message.get('sessionId', session)
        encrypted_package = encrypted_message.get('encrypted')
        domains_count = encrypted_message.get('domains_count', 0)
        timestamp = encrypted_message.get('timestamp')
        
        # Create session directory
        session_dir = f"mcp_server/config/cookies/{sessionId}"
        os.makedirs(session_dir, exist_ok=True)
        
        # Save encrypted package as a single file for the session
        encrypted_file = os.path.join(session_dir, "all_domains.encrypted")
        
        # Enhance encrypted package with metadata
        storage_package = {
            "encrypted_data": encrypted_package,
            "metadata": {
                "encrypted_by": "browser",
                "encryption_method": "AES-256-GCM + PBKDF2",
                "domains_count": domains_count,
                "timestamp": timestamp,
                "session_id": sessionId,
                "version": "1.0"
            }
        }
        
        with open(encrypted_file, 'w', encoding='utf-8') as f:
            json.dump(storage_package, f, indent=2)
        
        logger.info(f"Stored encrypted cookies for {domains_count} domains in {encrypted_file}")
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "message": f"Successfully stored encrypted cookies for {domains_count} domains",
                "operation": "store_encrypted", 
                "session": sessionId,
                "timestamp": datetime.now().isoformat(),
                "encrypted_file": encrypted_file,
                "domains_count": domains_count,
                "encryption_source": "browser",
                "security_level": "Corporate (Browser AES-256-GCM + PBKDF2)"
            }, indent=2)
        )]
        
    except Exception as e:
        logger.error(f"Failed to store encrypted cookies: {e}")
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": str(e),
                "operation": "store_encrypted",
                "session": session
            }, indent=2)
        )]
