"""
Pipeline package for MCP server.

Provides core and enhanced pipeline execution capabilities:
- Core: Basic tool chaining with variable substitution
- Enhanced: Adds conditional logic, nested pipelines, JavaScript expressions

Usage:
    # For basic pipelines
    from mcp_server.pipeline import PipelineExecutor
    
    # For enhanced pipelines with conditions
    from mcp_server.pipeline import EnhancedPipelineExecutor
    
    # Backward compatibility
    from mcp_server.pipeline import ConditionalPipelineExecutor
"""

# Import core classes
from .core import (
    PipelineExecutor,
    PipelineResult,
    ExpressionEvaluator,
    VariableSubstitutor,
    ResponseParser,
    ExecutionContext,
    StepType
)

# Import enhanced classes
from .enhanced import (
    EnhancedPipelineExecutor,
    ConditionalPipelineExecutor  # Alias for backward compatibility
)

# Default export for backward compatibility
# Existing code using: from mcp_server.pipeline import PipelineExecutor
# Will get the enhanced version automatically
PipelineExecutor = EnhancedPipelineExecutor

__all__ = [
    # Core classes
    'PipelineResult',
    'ExpressionEvaluator', 
    'VariableSubstitutor',
    'ResponseParser',
    'ExecutionContext',
    'StepType',
    
    # Main executors
    'PipelineExecutor',  # Enhanced by default
    'EnhancedPipelineExecutor',
    'ConditionalPipelineExecutor',  # Alias
]
