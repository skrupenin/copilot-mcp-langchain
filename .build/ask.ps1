param(
    [Parameter(Position=0, Mandatory=$false)]
    [string]$Command,
    
    [Parameter(Position=1, Mandatory=$false)]
    [string]$Question
)

# Function to ensure virtual environment is activated
function Ensure-VirtualEnv {
    $venvPath = "$PSScriptRoot\..\.virtualenv"
    $activateScript = "$venvPath\Scripts\Activate.ps1"
    
    # Check if virtual environment is already active
    if (-not $env:VIRTUAL_ENV) {
        if (Test-Path $activateScript) {
            Write-Host "Activating virtual environment..." -ForegroundColor Cyan
            & $activateScript
        } else {
            Write-Host "Error: Virtual environment not found at $venvPath" -ForegroundColor Red
            exit 1
        }
    }
}

# Function to get system information
function Get-SystemInfo {
    # Disable progress bar for system info gathering
    $ProgressPreference = 'SilentlyContinue'
    
    $osInfo = Get-CimInstance -ClassName Win32_OperatingSystem -ErrorAction SilentlyContinue
    $computerInfo = Get-ComputerInfo -Property WindowsProductName, WindowsVersion, TotalPhysicalMemory -ErrorAction SilentlyContinue
    
    $systemInfo = @"
System Context:
- OS: $($osInfo.Caption) (Build $($osInfo.BuildNumber))
- PowerShell Version: $($PSVersionTable.PSVersion)
- Console: Windows PowerShell Terminal
- Architecture: $($env:PROCESSOR_ARCHITECTURE)
- Current Directory: $($PWD.Path)
"@
    
    return $systemInfo
}

# Function to install PowerShell alias
function Install-AskAlias {
    $ASK_SCRIPT_PATH = $PSCommandPath
    $ASK_PROFILE = Join-Path -Path $(Split-Path -Path $PROFILE -Parent) -ChildPath "ask-alias.ps1"

    # Create the alias profile script
    $aliasContent = @"
# Ask Terminal Chat Function
# Generated automatically by ask.ps1 install

function ask {
    param(
        [Parameter(Position=0, Mandatory=`$false)]
        [string]`$Command,
        
        [Parameter(Position=1, Mandatory=`$false)]
        [string]`$Question
    )
    
    `$askScriptPath = "$ASK_SCRIPT_PATH"
    
    if (-not (Test-Path `$askScriptPath)) {
        Write-Host "Error: ask.ps1 script not found at `$askScriptPath" -ForegroundColor Red
        Write-Host "Please make sure the ask.ps1 script is available at the correct location." -ForegroundColor Yellow
        return
    }
    
    if (`$Command -and `$Question) {
        # Command analysis mode
        & `$askScriptPath `$Command `$Question
    } elseif (`$Command) {
        # Simple question mode or special commands
        if (`$Command -eq "install") {
            & `$askScriptPath install
        } elseif (`$Command -eq "uninstall") {
            & `$askScriptPath uninstall
        } else {
            & `$askScriptPath `$Command
        }
    } else {
        # Show usage if no parameters
        Write-Host "Usage:" -ForegroundColor Red
        Write-Host "  ask `"question`"                           # Simple question mode" -ForegroundColor Yellow
        Write-Host "  ask `"command`" `"question about result`"   # Command analysis mode" -ForegroundColor Yellow
        Write-Host "  ask install                               # Install global alias" -ForegroundColor Yellow
        Write-Host "  ask uninstall                             # Remove global alias" -ForegroundColor Yellow
        Write-Host "Examples:" -ForegroundColor Cyan
        Write-Host "  ask `"What is Python?`"" -ForegroundColor Cyan
        Write-Host "  ask `"dir`" `"How many files are there?`"" -ForegroundColor Cyan
        Write-Host "  ask `"Get-Process`" `"Which process uses most memory?`"" -ForegroundColor Cyan
    }
}

Write-Host "Ask Terminal Chat function loaded. Use 'ask' command from anywhere!" -ForegroundColor Cyan
"@

    # Write the alias content to the profile file
    Write-Host "Creating ask alias profile at: $ASK_PROFILE" -ForegroundColor Cyan
    $aliasContent | Out-File -FilePath $ASK_PROFILE -Encoding UTF8 -Force

    # Check if PROFILE exists, create if not
    if (-not (Test-Path $PROFILE)) {
        Write-Host "Creating PowerShell profile at: $PROFILE" -ForegroundColor Cyan
        New-Item -Path $PROFILE -ItemType File -Force | Out-Null
    }

    # Check if our alias is already sourced in the profile
    $profileContent = Get-Content $PROFILE -ErrorAction SilentlyContinue
    $sourceCommand = ". `"$ASK_PROFILE`""

    if ($profileContent -notcontains $sourceCommand) {
        Write-Host "Adding ask alias to PowerShell profile..." -ForegroundColor Cyan
        Add-Content -Path $PROFILE -Value $sourceCommand -Encoding UTF8
        Write-Host "Ask alias added to profile successfully!" -ForegroundColor Cyan
    } else {
        Write-Host "Ask alias already exists in profile." -ForegroundColor Cyan
    }

    Write-Host "Installation complete!" -ForegroundColor Cyan
    
    # Automatically load the alias in the current session
    Write-Host "Loading ask function in current session..." -ForegroundColor Cyan
    try {
        . $ASK_PROFILE
        Write-Host "Ask function is now available! Try: ask `"Hello!`"" -ForegroundColor Cyan
    } catch {
        Write-Host "Warning: Could not load alias automatically. Please restart PowerShell." -ForegroundColor Cyan
        Write-Host "Or run manually: . `"$ASK_PROFILE`"" -ForegroundColor Cyan
    }
        
    Write-Host ""
    Write-Host "Usage examples:" -ForegroundColor Yellow
    Write-Host "  ask `"What is Git?`"" -ForegroundColor Cyan
    Write-Host "  ask `"dir`" `"How many files?`"" -ForegroundColor Cyan
    Write-Host "  ask `"Get-Process`" `"Top memory usage?`"" -ForegroundColor Cyan
    
    Write-Host ""
    Write-Host "Please restart your PowerShell session for changes to take effect." -ForegroundColor Yellow

    exit 0
}

# Function to uninstall PowerShell alias
function Uninstall-AskAlias {
    $ASK_PROFILE = Join-Path -Path $(Split-Path -Path $PROFILE -Parent) -ChildPath "ask-alias.ps1"
    $sourceCommand = ". `"$ASK_PROFILE`""

    Write-Host "Removing ask alias..." -ForegroundColor Cyan

    # Remove the alias profile file
    if (Test-Path $ASK_PROFILE) {
        Remove-Item $ASK_PROFILE -Force
        Write-Host "Removed ask alias profile: $ASK_PROFILE" -ForegroundColor Cyan
    } else {
        Write-Host "Ask alias profile not found: $ASK_PROFILE" -ForegroundColor Cyan
    }

    # Remove the source command from PowerShell profile
    if (Test-Path $PROFILE) {
        $profileContent = Get-Content $PROFILE
        $newContent = $profileContent | Where-Object { $_ -ne $sourceCommand }
        
        if ($profileContent.Count -ne $newContent.Count) {
            $newContent | Out-File -FilePath $PROFILE -Encoding UTF8 -Force
            Write-Host "Removed ask alias from PowerShell profile." -ForegroundColor Cyan
        } else {
            Write-Host "Ask alias not found in PowerShell profile." -ForegroundColor Cyan
        }
    } else {
        Write-Host "PowerShell profile not found: $PROFILE" -ForegroundColor Cyan
    }

    Write-Host "Uninstallation complete!" -ForegroundColor Cyan
    Write-Host "Please restart your PowerShell session for changes to take effect." -ForegroundColor Yellow
    
    exit 0
}

# Check for special commands first
if ($Command -eq "install") {
    Install-AskAlias
} elseif ($Command -eq "uninstall") {
    Uninstall-AskAlias
} elseif (-not $Command) {
    # Show usage if no parameters
    Write-Host "Usage:" -ForegroundColor Red
    Write-Host "  .\ask.ps1 `"question`"                           # Simple question mode" -ForegroundColor Yellow
    Write-Host "  .\ask.ps1 `"command`" `"question about result`"   # Command analysis mode" -ForegroundColor Yellow
    Write-Host "  .\ask.ps1 install                               # Install global alias" -ForegroundColor Yellow
    Write-Host "  .\ask.ps1 uninstall                             # Remove global alias" -ForegroundColor Yellow
    Write-Host "Examples:" -ForegroundColor Cyan
    Write-Host "  .\ask.ps1 `"What is Python?`"" -ForegroundColor Cyan
    Write-Host "  .\ask.ps1 `"dir`" `"How many files are there?`"" -ForegroundColor Cyan
    Write-Host "  .\ask.ps1 `"Get-Process`" `"Which process uses most memory?`"" -ForegroundColor Cyan
    exit 0
}

# Ensure virtual environment is activated (only for normal operation)
Ensure-VirtualEnv

# Set console encoding to UTF-8 to handle Unicode properly
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"

# Color functions
function Write-ColoredText {
    param(
        [string]$Message,
        [string]$Color
    )
    Write-Host $Message -ForegroundColor $Color
}

# Check if this is a simple question mode (only one parameter)
if (-not $Question) {
    # Simple question mode - first parameter is actually the question
    $actualQuestion = $Command
    
    Write-Host "Question: $actualQuestion" -ForegroundColor Yellow
    
    # Change to the project root directory to find mcp_server module
    $originalLocation = Get-Location
    Set-Location "$PSScriptRoot\.."
    
    # Create a temporary file with simple question for LLM
    $tempFile = [System.IO.Path]::GetTempFileName()
    
    # Create JSON object for simple LLM query with special prompt
    $systemInfo = Get-SystemInfo
    $jsonObject = @{
        command = "echo 'Simple question mode'"
        command_output = "This is a direct question to the LLM without executing any command."
        question = $actualQuestion
        system_info = $systemInfo
    }
    
    # Convert to JSON and save to temp file
    $jsonContent = $jsonObject | ConvertTo-Json -Compress
    [System.IO.File]::WriteAllText($tempFile, $jsonContent, [System.Text.Encoding]::UTF8)
    
    # Fix path for Python (replace backslashes with forward slashes)
    $pythonTempFile = $tempFile -replace '\\', '/'
    
    # Call MCP tool by reading JSON from temp file (using utf-8-sig to handle BOM)
    $response = & python -c "import json; import sys; data=json.load(open('$pythonTempFile', 'r', encoding='utf-8-sig')); import subprocess; result=subprocess.run([sys.executable, '-m', 'mcp_server.run', 'run', 'lng_terminal_chat', json.dumps(data)], capture_output=True, text=True, encoding='utf-8'); print(result.stdout); sys.exit(result.returncode)" 2>&1
    $mcpExitCode = $LASTEXITCODE
    
    # Cleanup temp file and return to original location
    Remove-Item $tempFile -Force
    Set-Location $originalLocation
    
    if ($mcpExitCode -ne 0) {
        Write-ColoredText "Error: $response" "Red"
        exit 1
    }
    
    # Extract just the result from the MCP output (remove debug info)
    $lines = $response -split "`n"
    $resultStarted = $false
    $result = ""
    
    foreach ($line in $lines) {
        if ($line -match "Result:") {
            $resultStarted = $true
            $result = $line -replace ".*Result:\s*", ""
            continue
        }
        if ($resultStarted -and $line.Trim() -ne "") {
            if ($result -ne "") {
                $result += "`n"
            }
            $result += $line
        }
    }
    
    # If we couldn't parse the result, use the full response
    if ($result.Trim() -eq "") {
        $result = $response
    }
    
    # Display the answer with "Answer:" prefix in green
    Write-ColoredText "Answer: $($result.Trim())" "Green"
    exit 0
}

# Standard command + question mode
if (-not $Command -or -not $Question) {
    Write-ColoredText "Usage:" "Red"
    Write-ColoredText "  .\gpt.ps1 '<question>'                    # Simple question mode" "Yellow"
    Write-ColoredText "  .\gpt.ps1 '<command>' '<question>'        # Command analysis mode" "Yellow"
    Write-ColoredText "Examples:" "Cyan"
    Write-ColoredText "  .\gpt.ps1 'What is the capital of France?'" "Cyan"
    Write-ColoredText "  .\gpt.ps1 'docker ps -a' 'How many containers are running?'" "Cyan"
    exit 1
}

try {
    # Display the question with "Question:" prefix in yellow
    Write-Host "Question: $Question" -ForegroundColor Yellow
    
    # Display the command with ">" prefix in blue
    Write-ColoredText "> $Command" "Blue"
    
    # Execute command and capture output
    $output = Invoke-Expression $Command 2>&1 | Out-String
    $exitCode = $LASTEXITCODE
    
    # Display the command output in light cyan (more light blue)
    Write-ColoredText $output.Trim() "White"
    
    # Change to the project root directory to find mcp_server module
    $originalLocation = Get-Location
    Set-Location "$PSScriptRoot\.."
    
    # Create a temporary file with JSON parameters to avoid escaping issues
    $tempFile = [System.IO.Path]::GetTempFileName()
    
    # Create JSON object with three separate parameters
    $systemInfo = Get-SystemInfo
    $jsonObject = @{
        command = $Command
        command_output = $output.Trim()
        question = $Question
        system_info = $systemInfo
    }
    
    # Convert to JSON and save to temp file
    $jsonContent = $jsonObject | ConvertTo-Json -Compress
    [System.IO.File]::WriteAllText($tempFile, $jsonContent, [System.Text.Encoding]::UTF8)
    
    # Fix path for Python (replace backslashes with forward slashes)
    $pythonTempFile = $tempFile -replace '\\', '/'
    
    # Call MCP tool by reading JSON from temp file (using utf-8-sig to handle BOM)
    $response = & python -c "import json; import sys; data=json.load(open('$pythonTempFile', 'r', encoding='utf-8-sig')); import subprocess; result=subprocess.run([sys.executable, '-m', 'mcp_server.run', 'run', 'lng_terminal_chat', json.dumps(data)], capture_output=True, text=True, encoding='utf-8'); print(result.stdout); sys.exit(result.returncode)" 2>&1
    $mcpExitCode = $LASTEXITCODE
    
    # Cleanup temp file and return to original location
    Remove-Item $tempFile -Force
    Set-Location $originalLocation
    
    if ($mcpExitCode -ne 0) {
        Write-ColoredText "Error: $response" "Red"
        exit 1
    }
    
    # Extract just the result from the MCP output (remove debug info)
    $lines = $response -split "`n"
    $resultStarted = $false
    $result = ""
    
    foreach ($line in $lines) {
        if ($line -match "Result:") {
            $resultStarted = $true
            $result = $line -replace ".*Result:\s*", ""
            continue
        }
        if ($resultStarted -and $line.Trim() -ne "") {
            if ($result -ne "") {
                $result += "`n"
            }
            $result += $line
        }
    }
    
    # If we couldn't parse the result, use the full response
    if ($result.Trim() -eq "") {
        $result = $response
    }
    
    # Display the answer with "Answer:" prefix in green
    Write-ColoredText "Answer: $($result.Trim())" "Green"
}
catch {
    Write-ColoredText "Error executing command: $($_.Exception.Message)" "Red"
    exit 1
}
