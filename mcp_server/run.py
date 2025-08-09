"""
Universal tool runner for MCP tools.
Allows quick testing and execution of any tool without MCP server overhead.
Usage: python -m mcp_server.run run <tool_name> [json_args]
"""
import asyncio
import json
import sys
import os
import subprocess
import yaml
import logging
import traceback
from typing import Dict, Any, Optional, Set
from pathlib import Path
from mcp_server.tools.tool_registry import tool_definitions, run_tool, get_tool_info

# Setup logging for server
from mcp_server.logging_config import setup_logging
logger = setup_logging("mcp_runner", logging.DEBUG)

async def test_tool(tool_name: str, arguments: Optional[Dict[str, Any]] = None) -> Any:
    """
    Test a tool with given arguments.
    
    Args:
        tool_name: Name of the tool to test
        arguments: Dictionary of arguments to pass to the tool (optional)
    
    Returns:
        Tool execution result
    """
    if arguments is None:
        arguments = {}
    
    try:
        # Check if tool exists
        tool_exists = any(tool["name"] == tool_name for tool in tool_definitions)
        if not tool_exists:
            available_tools = [tool["name"] for tool in tool_definitions]
            logger.error(f"Tool '{tool_name}' not found. Available tools: {', '.join(available_tools)}")
            print(f"❌ Tool '{tool_name}' not found.")
            print(f"📋 Available tools: {', '.join(available_tools)}")
            return None
        
        logger.info(f"Testing tool: {tool_name} with arguments: {arguments}")
        print(f"🔧 Testing tool: {tool_name}")
        if arguments:
            print(f"📥 Arguments: {json.dumps(arguments, indent=2)}")
        
        # Run the tool
        result = await run_tool(tool_name, arguments)
        logger.info(f"Tool {tool_name} executed successfully")
        
        print("📤 Result:")
        if isinstance(result, list) and len(result) > 0:
            # Most tools return a list with TextContent
            for i, item in enumerate(result):
                if hasattr(item, 'text'):
                    try:
                        # Try to parse JSON for pretty printing
                        parsed = json.loads(item.text)
                        print(json.dumps(parsed, indent=2, ensure_ascii=False))
                    except (json.JSONDecodeError, TypeError):
                        # If not JSON, print as is
                        print(item.text)
                else:
                    print(f"[{i}] {item}")
        else:
            print(str(result))
        
        return result
        
    except Exception as e:
        logger.error(f"Error testing tool '{tool_name}': {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        print(f"❌ Error testing tool '{tool_name}': {e}")
        import traceback
        traceback.print_exc()
        return None

def run_test(tool_name: str, arguments: Optional[Dict[str, Any]] = None) -> Any:
    """
    Synchronous wrapper for test_tool.
    
    Args:
        tool_name: Name of the tool to test
        arguments: Dictionary of arguments to pass to the tool (optional)
    
    Returns:
        Tool execution result
    """
    return asyncio.run(test_tool(tool_name, arguments))

def install_dependencies():
    """Install dependencies for all enabled tools based on their settings.yaml files."""
    print("🔍 Scanning for tool dependencies...")
    
    # Get the tools directory path
    tools_dir = Path(__file__).parent / "tools"
    
    # Collect all dependencies from enabled tools
    all_dependencies: Set[str] = set()
    enabled_tools = []
    disabled_tools = []
    
    def scan_directory(path: Path, prefix: str = ""):
        """Recursively scan directories for settings.yaml files and tool.py files."""
        for item in path.iterdir():
            if item.is_dir() and not item.name.startswith('__'):
                current_prefix = f"{prefix}{item.name}" if prefix else item.name
                settings_file = item / "settings.yaml"
                tool_file = item / "tool.py"
                
                # If this directory contains a tool.py, it's an actual tool
                if tool_file.exists():
                    # Check for settings.yaml in this directory or parent directories
                    tool_enabled = True
                    tool_dependencies = []
                    tool_description = f"Tool: {current_prefix}"
                    
                    # Look for settings.yaml in current directory and walk up to find applicable settings
                    search_path = item
                    while search_path != tools_dir.parent and search_path.name != 'tools':
                        potential_settings = search_path / "settings.yaml"
                        if potential_settings.exists():
                            try:
                                with open(potential_settings, 'r', encoding='utf-8') as f:
                                    settings = yaml.safe_load(f)
                                
                                # If tool is explicitly disabled at any level, respect that
                                if not settings.get('enabled', True):
                                    tool_enabled = False
                                
                                # Collect dependencies and description
                                if 'dependencies' in settings:
                                    tool_dependencies.extend(settings.get('dependencies', []))
                                if 'description' in settings:
                                    tool_description = settings.get('description', tool_description)
                                
                                break  # Use the first settings.yaml we find
                            except Exception as e:
                                print(f"⚠️  Warning: Could not read {potential_settings}: {e}")
                        search_path = search_path.parent
                    
                    # Add tool to appropriate list
                    if tool_enabled:
                        enabled_tools.append((current_prefix, tool_dependencies, tool_description))
                        all_dependencies.update(tool_dependencies)
                    else:
                        disabled_tools.append((current_prefix, tool_description))
                
                # Always recurse into subdirectories to find more tools
                scan_directory(item, f"{current_prefix}_")
    
    # Scan the tools directory
    scan_directory(tools_dir)
    
    print("\n📋 Tool Status Report:")
    print("=" * 60)
    
    if enabled_tools:
        print("✅ Enabled Tools:")
        for tool_name, deps, description in enabled_tools:
            print(f"  🔧 {tool_name}")
            if deps:
                print(f"     Dependencies: {', '.join(deps)}")
            print(f"     Description: {description}")
            print()
    
    if disabled_tools:
        print("❌ Disabled Tools:")
        for tool_name, description in disabled_tools:
            print(f"  🔧 {tool_name}")
            print(f"     Description: {description}")
            print()
    
    if not all_dependencies:
        print("✅ No additional dependencies needed - all enabled tools are standalone!")
        return
    
    print(f"📦 Dependencies to install: {', '.join(sorted(all_dependencies))}")
    print("\n🚀 Installing dependencies...")
    
    # Install each dependency
    failed_packages = []
    builtin_modules = {'ssl', 'os', 'sys', 'json', 'sqlite3', 'datetime', 'collections', 're', 'math', 'random', 'urllib', 'http', 'socket', 'threading', 'multiprocessing', 'asyncio', 'logging', 'unittest', 'csv', 'xml', 'html'}
    
    for i, package in enumerate(sorted(all_dependencies), 1):
        try:
            print(f"📥 Installing {package} ({i}/{len(all_dependencies)})...")
            
            # Check if it's a built-in module
            if package in builtin_modules:
                try:
                    __import__(package)
                    print(f"   📦 {package} is a built-in Python module (already available)")
                    print(f"   ✅ {package} installation completed")
                    print(f"   🎯 {package} ready for use!")
                    print()
                    continue
                except ImportError:
                    pass  # Fall through to pip installation
            
            # First check if package is already installed
            check_result = subprocess.run([
                sys.executable, "-m", "pip", "show", package
            ], capture_output=True, text=True)
            
            if check_result.returncode == 0:
                # Package already installed, get version info
                version_info = check_result.stdout
                version_line = [line for line in version_info.split('\n') if line.startswith('Version:')]
                version = version_line[0].split(':')[1].strip() if version_line else "unknown"
                print(f"   📦 {package} v{version} already installed")
            else:
                print(f"   🔄 Downloading and installing {package}...")
            
            # Install/upgrade the package with verbose output
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", package, "--upgrade"
            ], capture_output=True, text=True, check=True)
            
            # Show installation summary
            if "Successfully installed" in result.stdout:
                installed_info = [line for line in result.stdout.split('\n') if 'Successfully installed' in line]
                if installed_info:
                    print(f"   ✅ {installed_info[0].replace('Successfully installed', 'Installed:')}")
            else:
                print(f"   ✅ {package} installation completed")
                
            # Show size information if available
            if "Downloading" in result.stdout:
                download_lines = [line for line in result.stdout.split('\n') if 'Downloading' in line and 'MB' in line]
                if download_lines:
                    print(f"   📊 Downloaded: {download_lines[-1].split('(')[1].split(')')[0] if '(' in download_lines[-1] else 'package data'}")
                    
            print(f"   🎯 {package} ready for use!")
            print()
            
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to install {package}")
            print(f"   🔍 Error details:")
            if e.stdout:
                print(f"      stdout: {e.stdout}")
            if e.stderr:
                print(f"      stderr: {e.stderr}")
            failed_packages.append(package)
            print()
    
    if failed_packages:
        print(f"\n❌ Failed to install: {', '.join(failed_packages)}")
        print("💡 You may need to install these manually or check your Python environment")
    else:
        print("\n✅ All dependencies installed successfully!")
        print("🎉 You can now use all enabled tools")

def list_tools():
    """List all available tools with their descriptions."""
    print("📋 Available MCP Tools:")
    print("=" * 60)
    
    for tool in tool_definitions:
        print(f"🔧 {tool['name']}")
        # Try to get tool info for description
        try:
            info = asyncio.run(get_tool_info(tool['name']))
            desc = info.get('description', 'No description available')
            
            # Extract just the first line or sentence of description
            lines = desc.split('\n')
            first_line = lines[0].strip()
            
            # If first line is too long, truncate it
            if len(first_line) > 80:
                first_line = first_line[:80] + "..."
            
            print(f"   {first_line}")
        except:
            print(f"   (Description unavailable)")
        print()

def show_tool_schema(tool_name: str):
    """Show the schema/parameters for a specific tool."""
    try:
        info = asyncio.run(get_tool_info(tool_name))
        print(f"🔧 Tool: {tool_name}")
        print(f"Description: {info.get('description', 'No description')}")
        print("\n📋 Parameters Schema:")
        schema = info.get('schema', {})
        print(json.dumps(schema, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"❌ Error getting schema for '{tool_name}': {e}")

def main():
    """Command line interface for testing tools."""
    if len(sys.argv) < 2:
        print("🚀 MCP Tool Runner")
        print("=" * 40)
        print("Usage:")
        print("  python -m mcp_server.run list                                    # List all tools")
        print("  python -m mcp_server.run schema <tool_name>                      # Show tool schema")
        print("  python -m mcp_server.run run <tool_name> 'args'                  # Run tool")
        print("  python -m mcp_server.run batch tool1 'args1' tool2 'args2'       # Run multiple tools")
        print("  python -m mcp_server.run install_dependencies                    # Install tool dependencies")
        print("  python -m mcp_server.run analyze_libs <lib1> [lib2] ...          # Analyze Python libraries")
        print("")
        print("Examples:")
        print("  python -m mcp_server.run run lng_count_words '{\\\"input_text\\\":\\\"Hello world\\\"}'")
        print("  python -m mcp_server.run run lng_math_calculator '{\\\"expression\\\":\\\"2+3*4\\\"}'")
        print("  python -m mcp_server.run run lng_get_tools_info")
        print("  python -m mcp_server.run batch lng_count_words '{\\\"input_text\\\":\\\"Hello\\\"}' lng_math_calculator '{\\\"expression\\\":\\\"2+3\\\"}'")
        print("  python -m mcp_server.run analyze_libs langchain requests numpy")
        print("")
        print("📋 Quick tool list:")
        for tool in tool_definitions:
            print(f"  🔧 {tool['name']}")
        return
    
    command = sys.argv[1]
    
    if command == 'list':
        list_tools()
    
    elif command == 'install_dependencies':
        install_dependencies()
    
    elif command == 'schema':
        if len(sys.argv) < 3:
            print("❌ Tool name required for schema command")
            return
        show_tool_schema(sys.argv[2])
    
    elif command == 'run':
        if len(sys.argv) < 3:
            print("❌ Tool name required for run command")
            return
        
        tool_name = sys.argv[2]
        tool_args = {}
        
        if len(sys.argv) >= 4:
            # Join all remaining arguments into one string (handles spaces in JSON)
            json_str = ' '.join(sys.argv[3:])
            
            # Try to parse JSON arguments
            try:
                tool_args = json.loads(json_str)
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON arguments: {e}")
                print(f"💡 Received: {json_str}")
                print("💡 Try using double quotes for property names and values")
                print('💡 Example: {"input_text":"Hello world"}')
                return
        
        # Run the tool
        run_test(tool_name, tool_args)
    
    elif command == 'analyze_libs':
        if len(sys.argv) < 3:
            print("❌ At least one library name required for analyze_libs command")
            print("💡 Usage: python -m mcp_server.run analyze_libs <lib1> [lib2] ...")
            print("💡 Example: python -m mcp_server.run analyze_libs langchain requests numpy")
            return
        
        # Import and run library analyzer
        try:
            from mcp_server.libs.analyzer import LibraryAnalyzer
            libraries = sys.argv[2:]
            
            print(f"🔍 Starting analysis of {len(libraries)} library(ies)...")
            print(f"Libraries to analyze: {', '.join(libraries)}")
            
            analyzer = LibraryAnalyzer()
            results = analyzer.analyze_libraries(libraries)
            analyzer.print_detailed_report(results)
            
        except ImportError as e:
            print(f"❌ Could not import library analyzer: {e}")
            print("💡 Make sure requests library is installed")
        except Exception as e:
            print(f"❌ Error running library analysis: {e}")
            import traceback
            traceback.print_exc()
    
    elif command == 'batch':
        if len(sys.argv) < 4:
            print("❌ At least one tool name and arguments required for batch command")
            print("💡 Usage: python -m mcp_server.run batch <tool1> [args1] <tool2> [args2] ...")
            return
        
        # Parse batch arguments more intelligently
        args = sys.argv[2:]
        commands = []
        
        i = 0
        while i < len(args):
            # Current argument should be a tool name
            tool_name = args[i]
            
            # Check if this looks like a tool name (not JSON)
            if not tool_name.startswith('{'):
                # Next argument might be JSON args
                if i + 1 < len(args) and args[i + 1].startswith('{'):
                    # Try to reconstruct the JSON string by joining until we have balanced braces
                    json_parts = []
                    brace_count = 0
                    j = i + 1
                    
                    while j < len(args):
                        part = args[j]
                        json_parts.append(part)
                        
                        # Count braces to find complete JSON
                        for char in part:
                            if char == '{':
                                brace_count += 1
                            elif char == '}':
                                brace_count -= 1
                        
                        if brace_count == 0:
                            break
                        j += 1
                    
                    if brace_count == 0:
                        # We have complete JSON
                        json_str = ' '.join(json_parts)
                        try:
                            tool_args = json.loads(json_str)
                            commands.append((tool_name, tool_args))
                            i = j + 1
                        except json.JSONDecodeError as e:
                            print(f"❌ Invalid JSON for tool '{tool_name}': {e}")
                            return
                    else:
                        print(f"❌ Incomplete JSON for tool '{tool_name}'")
                        return
                else:
                    # No JSON args for this tool
                    commands.append((tool_name, {}))
                    i += 1
            else:
                print(f"❌ Expected tool name but got: {tool_name}")
                return
        
        if not commands:
            print("❌ No valid commands found")
            return
        
        # Execute all commands in sequence
        print(f"🔄 Running {len(commands)} tools in batch...")
        print("=" * 60)
        
        for idx, (tool_name, tool_args) in enumerate(commands, 1):
            print(f"\n📍 Step {idx}/{len(commands)}: {tool_name}")
            print("-" * 40)
            run_test(tool_name, tool_args)
            
            if idx < len(commands):
                print("\n" + "⏭️  " * 20)
    
    else:
        print(f"❌ Unknown command: {command}")
        print("Available commands: list, schema, run, batch, install_dependencies")

if __name__ == "__main__":
    main()
