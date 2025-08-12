import json
import logging
from typing import Any, Dict, List
from mcp import types
from mcp_server.tools.tool_registry import run_tool as execute_tool
from mcp_server.pipeline import StrategyBasedExecutor

logger = logging.getLogger('mcp_server.tools.lng_batch_run')

async def tool_info() -> dict:
    return {
        "description": """Executes a batch pipeline of tool calls with variable substitution using JavaScript expressions.

**⚡ Now powered by strategy-based architecture for maximum extensibility!**

**Pipeline Structure:**
```json
{
  "pipeline": [
    {
      "tool": "tool_name",
      "params": {
        "param1": "${variable_name}",
        "param2": "${variable_name.property || 'default'}"
      },
      "output": "variable_name"
    },
    {
      "type": "condition",
      "condition": "${variable_name.property > 5}",
      "then": [
        {"tool": "tool_if_true", "params": {...}}
      ],
      "else": [
        {"tool": "tool_if_false", "params": {...}}
      ]
    },
    {
      "type": "forEach",
      "forEach": "${collection}",
      "item": "current_item",
      "do": [
        {"tool": "process_item", "params": {"input": "${current_item}"}}
      ]
    }
  ],
  "final_result": "${last_variable || 'ok'}"
}
```

**Strategy-Based Features:**
🔧 **Tool Execution** - Sequential tool calls with variable passing
🔀 **Conditional Logic** - if-then-else with JavaScript expressions  
🔄 **Loops** - forEach, while, repeat iterations
⚡ **Parallel Execution** - Run multiple steps concurrently
⏱️ **Timing Control** - Delays and sleep functionality
📦 **Modular Design** - Easy to extend with new strategies

**Variable Substitution:**
• `${variable}` - Direct variable value
• `${variable.property}` - Object property access
• `${variable || 'default'}` - Fallback values
• `${variable ? value1 : value2}` - Conditional expressions
• `${JSON.stringify(variable)}` - JSON serialization

**Available Step Types:**
• `{"tool": "name", "params": {}, "output": "var"}` - Tool execution
• `{"type": "condition", "condition": "${expr}", "then": [...], "else": [...]}` - Conditional logic
• `{"type": "forEach", "forEach": "${collection}", "item": "var", "do": [...]}` - Loop over collection
• `{"type": "while", "while": "${condition}", "do": [...]}` - While loop
• `{"type": "repeat", "repeat": 3, "do": [...]}` - Repeat N times
• `{"type": "parallel", "parallel": [...]}` - Parallel execution
• `{"type": "delay", "delay": 1.5}` - Sleep/wait

**Example with Multiple Strategies:**
```json
{
  "pipeline": [
    {"tool": "lng_winapi_clipboard_get", "params": {}, "output": "clipboard"},
    {
      "type": "condition",
      "condition": "${clipboard.success}",
      "then": [
        {
          "type": "parallel",
          "parallel": [
            {"tool": "lng_count_words", "params": {"input_text": "${clipboard.content}"}, "output": "stats"},
            {"tool": "lng_save_screenshot", "params": {}}
          ]
        }
      ],
      "else": [
        {"tool": "lng_winapi_clipboard_set", "params": {"text": "Clipboard empty"}}
      ]
    }
  ]
}
```

**Architecture Benefits:**
• Modular strategy system (composition over inheritance)
• Easy to add new step types without modifying existing code
• Each strategy handles specific functionality independently
• Full backward compatibility with existing pipelines

**Error Handling:**
Returns error details with failed tool name and variable context when any step fails.""",
        "schema": {
            "type": "object",
            "properties": {
                "pipeline": {
                    "type": "array",
                    "description": "Array of pipeline steps with tools, parameters, and variable mappings (optional if pipeline_file is provided)",
                    "items": {
                        "type": "object",
                        "properties": {
                            "tool": {
                                "type": "string",
                                "description": "Name of the tool to execute"
                            },
                            "type": {
                                "type": "string", 
                                "description": "Step type: 'tool', 'condition', 'forEach', 'while', 'repeat', 'parallel', 'delay'",
                                "enum": ["tool", "condition", "forEach", "while", "repeat", "parallel", "delay"]
                            },
                            "params": {
                                "type": "object",
                                "description": "Parameters to pass to the tool"
                            },
                            "output": {
                                "type": "string",
                                "description": "Variable name to store the tool result"
                            },
                            "output_log": {
                                "type": "string", 
                                "description": "Optional log name to save output data as timestamped file in mcp_server/logs/pipeline_debug/"
                            },
                            "condition": {
                                "type": "string",
                                "description": "Condition expression for conditional steps"
                            },
                            "then": {
                                "type": "array",
                                "items": {
                                    "type": "object"
                                },
                                "description": "Steps to execute if condition is true"
                            },
                            "else": {
                                "type": "array", 
                                "items": {
                                    "type": "object"
                                },
                                "description": "Steps to execute if condition is false"
                            },
                            "forEach": {
                                "type": "string",
                                "description": "Collection expression for forEach loops"
                            },
                            "while": {
                                "type": "string",
                                "description": "Condition expression for while loops"
                            },
                            "repeat": {
                                "type": ["integer", "string"],
                                "description": "Count expression for repeat loops"
                            },
                            "parallel": {
                                "type": "array",
                                "items": {
                                    "type": "object"
                                },
                                "description": "Steps to execute in parallel"
                            },
                            "delay": {
                                "type": ["number", "string"],
                                "description": "Delay duration in seconds"
                            }
                        }
                    }
                },
                "pipeline_file": {
                    "type": "string",
                    "description": "Path to JSON file containing pipeline configuration (alternative to pipeline parameter)"
                },
                "final_result": {
                    "type": "string",
                    "description": "Expression or value for the final result (default: 'ok')"
                },
                "context_fields": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "Array of context field names to include in output. If empty or not provided, no context will be shown (saves tokens). Use ['*'] to show all context fields, or specify field names like ['var1', 'var2'] to show only those variables."
                }
            },
            "required": []
        }
    }

async def run_tool(name: str, arguments: dict) -> list[types.Content]:
    """Execute a batch pipeline using strategy-based architecture."""
    
    try:
        # Create strategy-based pipeline executor
        executor = StrategyBasedExecutor(execute_tool)
        
        # Log available strategies
        strategies = executor.get_strategies()
        logger.info(f"Available strategies: {', '.join(strategies)}")
        
        # Check if pipeline_file is provided
        if "pipeline_file" in arguments:
            pipeline_file = arguments["pipeline_file"]
            logger.info(f"Loading pipeline from file: {pipeline_file}")
            
            try:
                import os
                # Read pipeline configuration from file
                if not os.path.isabs(pipeline_file):
                    # Make relative paths relative to the project root
                    import mcp_server
                    project_root = os.path.dirname(os.path.dirname(mcp_server.__file__))
                    pipeline_file = os.path.join(project_root, pipeline_file)
                
                with open(pipeline_file, 'r', encoding='utf-8') as f:
                    pipeline_config = json.load(f)
                
                # Merge file config with arguments, giving priority to direct arguments
                merged_arguments = pipeline_config.copy()
                merged_arguments.update({k: v for k, v in arguments.items() if k != "pipeline_file"})
                
                logger.info(f"Successfully loaded pipeline from {pipeline_file}")
                
            except FileNotFoundError:
                return [types.TextContent(
                    type="text", 
                    text=json.dumps({
                        "success": False,
                        "error": f"Pipeline file not found: {pipeline_file}",
                        "context": {},
                        "architecture": "strategy-based"
                    }, ensure_ascii=False, indent=2)
                )]
            except json.JSONDecodeError as e:
                return [types.TextContent(
                    type="text", 
                    text=json.dumps({
                        "success": False,
                        "error": f"Invalid JSON in pipeline file {pipeline_file}: {str(e)}",
                        "context": {},
                        "architecture": "strategy-based"
                    }, ensure_ascii=False, indent=2)
                )]
        else:
            # Use arguments directly if no file specified
            merged_arguments = arguments
            
        # Validate that we have either pipeline or pipeline_file
        if "pipeline" not in merged_arguments and "pipeline_file" not in arguments:
            return [types.TextContent(
                type="text", 
                text=json.dumps({
                    "success": False,
                    "error": "Either 'pipeline' parameter or 'pipeline_file' parameter is required",
                    "context": {},
                    "architecture": "strategy-based"
                }, ensure_ascii=False, indent=2)
            )]
        
        # Execute pipeline using the strategy-based system
        result = await executor.execute(merged_arguments)
        
        # Add architecture info to result
        result_dict = result.to_dict()
        result_dict["architecture"] = "strategy-based"
        result_dict["available_strategies"] = strategies
        if "pipeline_file" in arguments:
            result_dict["pipeline_source"] = arguments["pipeline_file"]
        
        # Filter context fields if specified
        context_fields = merged_arguments.get("context_fields", [])
        if "context" in result_dict:
            original_context = result_dict["context"]
            
            if not context_fields:
                # No context_fields specified - hide all context to save tokens
                result_dict["context"] = {}
                result_dict["context_filtered"] = True
                result_dict["total_context_fields"] = len(original_context)
                result_dict["shown_context_fields"] = 0
            elif context_fields == ["*"]:
                # Show all context
                result_dict["context_filtered"] = False
            else:
                # Show only specified fields
                filtered_context = {}
                for field in context_fields:
                    if field in original_context:
                        filtered_context[field] = original_context[field]
                result_dict["context"] = filtered_context
                result_dict["context_filtered"] = True
                result_dict["total_context_fields"] = len(original_context)
                result_dict["shown_context_fields"] = len(filtered_context)
        
        # Return result in the expected format
        return [types.TextContent(
            type="text", 
            text=json.dumps(result_dict, ensure_ascii=False, indent=2)
        )]
        
    except Exception as e:
        logger.error(f"Unexpected error in lng_batch_run: {e}")
        return [types.TextContent(
            type="text", 
            text=json.dumps({
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "context": {},
                "architecture": "strategy-based"
            }, ensure_ascii=False, indent=2)
        )]
