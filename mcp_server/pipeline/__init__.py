"""
Modern pipeline architecture for MCP tool chaining.

This module provides a comprehensive pipeline system with:
- Strategy-based architecture for extensibility
- Support for conditionals, loops, parallel execution
- Advanced expression evaluation with ternary operators
- Clean separation of concerns

Usage (recommended):
    from mcp_server.pipeline import PipelineExecutor
    
    executor = PipelineExecutor(tool_runner=run_tool)
    result = await executor.execute(pipeline_config)

Legacy usage (deprecated):
    from mcp_server.pipeline.core import LegacyPipelineExecutor
"""

# Import the main strategy-based executor (recommended)
from .strategies import PipelineExecutor, StrategyBasedExecutor

# Import data models
from .models import PipelineResult, ExecutionContext, StepType

# Import expression evaluation functions
from .expressions import evaluate_expression, substitute_expressions

# Legacy imports for backward compatibility
from .core import (
    LegacyPipelineExecutor,
    execute_pipeline,
    evaluate_js_expression,
    substitute_variables,
    parse_tool_response
)

# Export public API
__all__ = [
    # Main executor (strategy-based - recommended)
    'PipelineExecutor',
    'StrategyBasedExecutor',
    
    # Data models
    'PipelineResult',
    'ExecutionContext', 
    'StepType',
    
    # Utility functions
    'evaluate_expression',
    'substitute_expressions',
    
    # Legacy support (deprecated)
    'LegacyPipelineExecutor',
    'execute_pipeline',
    'evaluate_js_expression',
    'substitute_variables',
    'parse_tool_response'
]
