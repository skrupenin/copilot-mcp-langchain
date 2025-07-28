param(
    [Parameter(Mandatory=$true)]
    [string]$Command,
    
    [Parameter(Mandatory=$false)]
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

# Ensure virtual environment is activated
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
    
    Write-ColoredText "Question: $actualQuestion" "Yellow"
    
    # Change to the project root directory to find mcp_server module
    $originalLocation = Get-Location
    Set-Location "$PSScriptRoot\.."
    
    # Create a temporary file with simple question for LLM
    $tempFile = [System.IO.Path]::GetTempFileName()
    
    # Create JSON object for simple LLM query with special prompt
    $jsonObject = @{
        command = "echo 'Simple question mode'"
        command_output = "This is a direct question to the LLM without executing any command."
        question = $actualQuestion
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
    Write-ColoredText "Examples:" "Red"
    Write-ColoredText "  .\gpt.ps1 'What is the capital of France?'" "Cyan"
    Write-ColoredText "  .\gpt.ps1 'docker ps -a' 'How many containers are running?'" "Cyan"
    exit 1
}

try {
    # Display the question with "Question:" prefix in yellow
    Write-ColoredText "Question: $Question" "Yellow"
    
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
    $jsonObject = @{
        command = $Command
        command_output = $output.Trim()
        question = $Question
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
