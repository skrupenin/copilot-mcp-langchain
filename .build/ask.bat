@echo off
REM GPT Terminal Chat for Windows
REM Usage: 
REM   gpt.bat "question"                 - Simple question mode
REM   gpt.bat "command" "question"       - Command analysis mode

setlocal enabledelayedexpansion

REM Set UTF-8 code page
chcp 65001 >nul

if "%~1"=="" (
    echo Usage:
    echo   gpt.bat "question"                    # Simple question mode
    echo   gpt.bat "command" "question"          # Command analysis mode
    echo Examples:
    echo   gpt.bat "What is the capital of France?"
    echo   gpt.bat "dir" "How many files are there?"
    exit /b 1
)

REM Change to script directory to find mcp_server module
cd /d "%~dp0\.."

if "%~2"=="" (
    REM Simple question mode
    set "question=%~1"
    
    echo Question: !question!
    
    REM Create temporary file for JSON to avoid escaping issues
    set "tempfile=%TEMP%\gpt_temp_%RANDOM%.json"
    
    REM Create JSON content for simple question
    set "json_content={\"command\":\"echo 'Simple question mode'\",\"command_output\":\"This is a direct question to the LLM without executing any command.\",\"question\":\"!question!\"}"
    
    REM Call MCP tool with UTF-8 encoding - pass JSON as argument
    set PYTHONIOENCODING=utf-8
    python -m mcp_server.run run lng_terminal_chat "!json_content!" > "%TEMP%\gpt_result.txt" 2>&1
    set "exitcode=!errorlevel!"
    
    REM Clean up temp file (if exists)
    if exist "!tempfile!" del "!tempfile!" >nul 2>&1
    
    if !exitcode! neq 0 (
        echo Error:
        type "%TEMP%\gpt_result.txt"
        del "%TEMP%\gpt_result.txt" >nul 2>&1
        exit /b 1
    )
    
    REM Extract and display result more robustly
    set "found_result="
    echo|set /p="Answer: "
    for /f "usebackq delims=" %%i in ("%TEMP%\gpt_result.txt") do (
        set "line=%%i"
        if "!line:📤 Result:=!" neq "!line!" set "found_result=1"
        if "!line:Result:=!" neq "!line!" set "found_result=1"
        if defined found_result (
            if "!line!" neq "" if "!line:Result:=!" equ "!line!" if "!line:📤 Result:=!" equ "!line!" (
                echo %%i
            )
        )
    )
    
    del "%TEMP%\gpt_result.txt" >nul 2>&1
    
) else (
    REM Command analysis mode
    set "command=%~1"
    set "question=%~2"
    
    echo Question: !question!
    echo ^> !command!
    
    REM Execute command and capture output
    !command! > "%TEMP%\cmd_output.txt" 2>&1
    set "cmd_exitcode=!errorlevel!"
    
    REM Display command output
    echo.
    type "%TEMP%\cmd_output.txt"
    echo.
    
    REM Read command output for JSON (read into variable)
    set "output="
    for /f "usebackq delims=" %%i in ("%TEMP%\cmd_output.txt") do (
        if defined output (
            set "output=!output! %%i"
        ) else (
            set "output=%%i"
        )
    )
    
    REM Escape quotes and backslashes in output for JSON
    set "output=!output:\=\\!"
    set "output=!output:"=\"!"
    
    REM Escape quotes and backslashes in command for JSON  
    set "command=!command:"=\"!"
    set "command=!command:\=\\!"
    
    REM Create JSON content with proper escaping
    set "json_content={\"command\":\"!command!\",\"command_output\":\"!output!\",\"question\":\"!question!\"}"
    
    REM Call MCP tool with UTF-8 encoding - pass JSON as argument
    set PYTHONIOENCODING=utf-8
    python -m mcp_server.run run lng_terminal_chat "!json_content!" > "%TEMP%\gpt_result.txt" 2>&1
    set "exitcode=!errorlevel!"
    
    REM Clean up temp files
    del "%TEMP%\cmd_output.txt" >nul 2>&1
    
    if !exitcode! neq 0 (
        echo Error:
        type "%TEMP%\gpt_result.txt"
        del "%TEMP%\gpt_result.txt" >nul 2>&1
        exit /b 1
    )
    
    REM Extract and display result
    set "found_result="
    echo|set /p="Answer: "
    for /f "usebackq delims=" %%i in ("%TEMP%\gpt_result.txt") do (
        set "line=%%i"
        if "!line:📤 Result:=!" neq "!line!" set "found_result=1"
        if "!line:Result:=!" neq "!line!" set "found_result=1"
        if defined found_result (
            if "!line!" neq "" if "!line:Result:=!" equ "!line!" if "!line:📤 Result:=!" equ "!line!" (
                echo %%i
            )
        )
    )
    
    del "%TEMP%\gpt_result.txt" >nul 2>&1
)
