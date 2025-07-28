# Terminal Chat Scripts

This folder contains scripts for terminal chat with LLM that use MCP (Model Context Protocol) server to process commands and questions.

## Scripts

### 1. `ask.ps1` - PowerShell Script (Windows)
Script for Windows PowerShell with colored output support and automatic virtual environment activation.

**Usage:**
```powershell
.\ask.ps1 "What is Python?"
.\ask.ps1 "dir" "How many files are in the directory?"
.\ask.ps1 "Get-Process" "Which processes use the most memory?"
```

### 2. `ask` - Bash Script (Linux/macOS/Git Bash)
Script for Unix-like systems and Git Bash on Windows with colored output support.

**Usage:**
```bash
bash ask "How does Git work?"
bash ask "ls -la" "How many files are in the directory?"
bash ask "ps aux" "Which processes use the most CPU?"
```

### 3. `ask.bat` - Batch Script (Windows Command Prompt)
Pure batch script for Windows Command Prompt without PowerShell dependencies.

**Usage:**
```cmd
ask.bat "Explain Windows commands"
ask.bat "dir" "How many files are in the directory?"
ask.bat "tasklist" "Which programs are running?"
```

## Features

### Two Operation Modes:

1. **Simple Question** - ask LLM directly:
   - Only one parameter is passed (the question)
   - LLM answers the question without executing commands

2. **Command Analysis** - execute command and analyze the result:
   - Two parameters are passed: command and question
   - Command is executed, result is passed to LLM along with the question
   - LLM analyzes command output and answers the question

### Automatic Virtual Environment Activation

All scripts automatically:
- Check if virtual environment is already activated
- If not, activate `.virtualenv` from parent directory
- Display activation status messages
- Continue working or exit with error