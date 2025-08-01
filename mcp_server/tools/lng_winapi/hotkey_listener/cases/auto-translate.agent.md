# Auto-Translate Hotkey

**Important:** 
- Use MCP (do not use terminal). 
- Don't do any checks, just initialize the solution - I need minimum MCP calls.

**Scenario:** 
Create Ctrl+Shift+Insert hotkey that:
- Takes text from clipboard
- Translates to English B2 level via prompt
- Puts result back to clipboard

**Critical fix:** 
- Use `${clipboard_text.content}` not `${clipboard_text.unicode_text}`
