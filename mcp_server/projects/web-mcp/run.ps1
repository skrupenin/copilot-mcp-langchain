# MCP Tools Web Interface - Startup Script
# This script starts both webhook servers (main interface + execution API)

Write-Host "Starting MCP Tools Web Interface (Dual Server Mode)..." -ForegroundColor Green

# Получаем путь к корню проекта (ищем hello-langchain директорию)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Функция для поиска корня проекта
function Find-ProjectRoot {
    param($StartPath)
    
    $CurrentPath = $StartPath
    $MaxLevels = 10  # Максимум 10 уровней вверх
    $Level = 0
    
    while ($Level -lt $MaxLevels) {
        # Проверяем наличие характерных файлов проекта
        $McpServerPath = Join-Path $CurrentPath "mcp_server"
        $VenvPath = Join-Path $CurrentPath ".virtualenv"
        $WebMcpPath = Join-Path $CurrentPath "mcp_server\projects\web-mcp"
        
        if ((Test-Path $McpServerPath) -and (Test-Path $VenvPath) -and (Test-Path $WebMcpPath)) {
            return $CurrentPath
        }
        
        # Переходим на уровень выше
        $ParentPath = Split-Path -Parent $CurrentPath
        if ($ParentPath -eq $CurrentPath) {
            break  # Достигли корня диска
        }
        $CurrentPath = $ParentPath
        $Level++
    }
    
    return $null
}

# Ищем корень проекта
$ProjectRoot = Find-ProjectRoot $ScriptDir

# Переходим в корень проекта
if ($ProjectRoot) {
    Set-Location $ProjectRoot
    Write-Host "[OK] Found project root: $ProjectRoot" -ForegroundColor Green
} else {
    Write-Host "Error: Could not find hello-langchain project root" -ForegroundColor Red
    Write-Host "Make sure you're running this script from within the hello-langchain project" -ForegroundColor Yellow
    Write-Host "Current script location: $ScriptDir" -ForegroundColor Yellow
    exit 1
}

# Проверяем что мы в правильной директории
$WebhookConfigPath = "mcp_server\projects\web-mcp\config\webhook_config.json"
$ExecutionConfigPath = "mcp_server\projects\web-mcp\config\execution_api.json"

if (-not (Test-Path $WebhookConfigPath)) {
    Write-Host "Error: Could not find main webhook config" -ForegroundColor Red
    Write-Host "Expected: $WebhookConfigPath" -ForegroundColor Yellow
    Write-Host "Current:  $(Get-Location)" -ForegroundColor Yellow
    exit 1
}

if (-not (Test-Path $ExecutionConfigPath)) {
    Write-Host "Error: Could not find execution webhook config" -ForegroundColor Red
    Write-Host "Expected: $ExecutionConfigPath" -ForegroundColor Yellow
    Write-Host "Current:  $(Get-Location)" -ForegroundColor Yellow
    exit 1
}

# Активируем виртуальное окружение
$VenvPath = Join-Path $ProjectRoot ".virtualenv\Scripts\activate.ps1"
if (Test-Path $VenvPath) {
    . $VenvPath
    Write-Host "[OK] Virtual environment activated" -ForegroundColor Green
} else {
    Write-Host "Warning: Virtual environment not found at: $VenvPath" -ForegroundColor Yellow
    Write-Host "Continuing without virtual environment..." -ForegroundColor Yellow
}

# Check if lng_webhook_server tool is available
Write-Host "Checking MCP server availability..." -ForegroundColor Yellow

try {
    # Start both webhook servers
    Write-Host "Starting main web interface on http://localhost:8080" -ForegroundColor Green
    Write-Host "Starting execution API on http://localhost:8081" -ForegroundColor Green
    Write-Host "Config 1: $WebhookConfigPath" -ForegroundColor Blue
    Write-Host "Config 2: $ExecutionConfigPath" -ForegroundColor Blue
    Write-Host "" 
    Write-Host "Press Ctrl+C to stop both servers" -ForegroundColor Yellow
    Write-Host "=================================" -ForegroundColor Cyan

    # Start main web interface (port 8080)
    Write-Host "Starting main web interface server..." -ForegroundColor Yellow
    $json1 = '{\"operation\": \"start\", \"config_file\": \"mcp_server/projects/web-mcp/config/webhook_config.json\"}'
    Start-Process -NoNewWindow -FilePath "python" -ArgumentList "-m", "mcp_server.run", "run", "lng_webhook_server", $json1
    
    Start-Sleep -Seconds 2
    
    # Start execution API (port 8081)
    Write-Host "Starting execution API server..." -ForegroundColor Yellow
    $json2 = '{\"operation\": \"start\", \"config_file\": \"mcp_server/projects/web-mcp/config/execution_api.json\"}'
    Start-Process -NoNewWindow -FilePath "python" -ArgumentList "-m", "mcp_server.run", "run", "lng_webhook_server", $json2
    
    Start-Sleep -Seconds 2
    
    Write-Host "" 
    Write-Host "🚀 Both servers started successfully!" -ForegroundColor Green
    Write-Host "📱 Web Interface: http://localhost:8080" -ForegroundColor Cyan
    Write-Host "🔧 Execution API:  http://localhost:8081" -ForegroundColor Cyan
    Write-Host "" 
    Write-Host "Press any key to stop servers..." -ForegroundColor Yellow
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

} catch {
    Write-Host "Error starting webhook servers: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "" 
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "   1. Ensure virtual environment is activated" -ForegroundColor White
    Write-Host "   2. Check that MCP server is running properly" -ForegroundColor White
    Write-Host "   3. Verify webhook config files syntax" -ForegroundColor White
    Write-Host "   4. Check if ports 8080 and 8081 are available" -ForegroundColor White
    exit 1
} finally {
    # Stop both servers
    Write-Host "" 
    Write-Host "Stopping webhook servers..." -ForegroundColor Yellow
    
    # Stop servers by name
    try {
        $stopJson1 = '{\"operation\": \"stop\", \"name\": \"web-mcp-interface\"}'
        python -m mcp_server.run run lng_webhook_server $stopJson1
        
        $stopJson2 = '{\"operation\": \"stop\", \"name\": \"execution-api\"}'
        python -m mcp_server.run run lng_webhook_server $stopJson2
        
        Write-Host "[OK] Both servers stopped" -ForegroundColor Green
    } catch {
        Write-Host "Note: Some servers may still be running" -ForegroundColor Yellow
    }
}

Write-Host "Web interface shutdown complete" -ForegroundColor Green
