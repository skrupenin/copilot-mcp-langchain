# MCP Tools Web Interface - Startup Script
# This script starts the lng_webhook_server with the web interface configuration

Write-Host "Starting MCP Tools Web Interface..." -ForegroundColor Green

# Получаем путь к корню проекта (3 уровня вверх от скрипта)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $ScriptDir))

# Переходим в корень проекта
Set-Location $ProjectRoot

# Проверяем что мы в правильной директории
$currentDir = Get-Location
if (-not (Test-Path "mcp_server\projects\web-mcp\config\webhook_config.json")) {
    Write-Host "Error: Could not find web-mcp configuration" -ForegroundColor Red
    Write-Host "Expected: hello-langchain root with mcp_server/" -ForegroundColor Yellow
    Write-Host "Current:  $currentDir" -ForegroundColor Yellow
    Write-Host "ProjectRoot: $ProjectRoot" -ForegroundColor Blue
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
    # Start the webhook server using MCP tool
    Write-Host "Starting webhook server on http://localhost:8080" -ForegroundColor Green
    Write-Host "Config: mcp_server/projects/web-mcp/config/webhook_config.json" -ForegroundColor Blue
    Write-Host "" 
    Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
    Write-Host "=========================" -ForegroundColor Cyan

    # Call lng_webhook_server through MCP for Phase 2 testing
    Write-Host "Starting lng_webhook_server with thread_mode..." -ForegroundColor Yellow
    
    # Запускаем webhook server через MCP tool
    $json = '{\"operation\": \"start\", \"config_file\": \"mcp_server/projects/web-mcp/config/webhook_config.json\"}'
    python -m mcp_server.run run lng_webhook_server $json

} catch {
    Write-Host "Error starting webhook server: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "" 
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "   1. Ensure virtual environment is activated" -ForegroundColor White
    Write-Host "   2. Check that MCP server is running properly" -ForegroundColor White
    Write-Host "   3. Verify webhook_config.json syntax" -ForegroundColor White
    Write-Host "   4. Check if port 8080 is available" -ForegroundColor White
    exit 1
}

Write-Host "Web interface shutdown complete" -ForegroundColor Green
