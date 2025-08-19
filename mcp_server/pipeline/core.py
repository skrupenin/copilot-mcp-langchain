"""
Legacy pipeline execution core (deprecated).

This module contains legacy pipeline executor for backward compatibility.
New code should use the strategy-based architecture from mcp_server.pipeline.strategies

The strategy-based system provides:
- Better modularity and extensibility
- Full implementation of conditionals, loops, parallel execution
- Cleaner separation of concerns

Usage (recommended):
    from mcp_server.pipeline import PipelineExecutor
    
    executor = PipelineExecutor(tool_runner=run_tool)
    result = await executor.execute(pipeline_config)
"""

from typing import Any, Dict, List, Callable, Optional
import logging
import asyncio

from .models import PipelineResult, ExecutionContext, StepType
from .expressions import evaluate_expression, substitute_expressions

logger = logging.getLogger('mcp_server.pipeline.core')


class LegacyPipelineExecutor:
    """
    Legacy pipeline execution engine (deprecated).
    
    This class is kept for backward compatibility only.
    It only supports basic tool execution - advanced features
    like conditionals, loops, and parallel execution are not implemented.
    
    Use StrategyBasedExecutor from mcp_server.pipeline.strategies instead.
    """
    
    def __init__(self, tool_runner: Callable[[str, Dict[str, Any]], Any]):
        """
        Initialize legacy pipeline executor.
        
        Args:
            tool_runner: Function to execute tools (e.g., run_tool from tool_registry)
        """
        self.tool_runner = tool_runner
        
        # Warn about deprecation
        logger.warning(
            "LegacyPipelineExecutor is deprecated. "
            "Use StrategyBasedExecutor from mcp_server.pipeline.strategies instead."
        )
    
    async def execute(self, config: Dict[str, Any]) -> PipelineResult:
        """
        Execute a pipeline configuration (basic tool execution only).
        
        Args:
            config: Pipeline configuration dictionary
            
        Returns:
            PipelineResult with execution outcome
        """
        import time
        start_time = time.time()
        
        try:
            # Extract configuration
            pipeline_steps = config.get("pipeline", [])
            final_result_expr = config.get("final_result", "ok")
            templates = config.get("templates", {})
            
            if not pipeline_steps:
                return PipelineResult(
                    success=False,
                    error="Pipeline must contain at least one step",
                    context={}
                )
            
            if not isinstance(pipeline_steps, list):
                return PipelineResult(
                    success=False,
                    error="Pipeline must be an array of steps",
                    context={}
                )
            
            # Initialize execution context
            context = ExecutionContext(
                variables={},
                templates=templates
            )
            
            # Execute pipeline steps (only tool steps supported)
            for step_index, step in enumerate(pipeline_steps):
                context.step_number = step_index + 1
                
                try:
                    # Only tool steps are supported in legacy executor
                    if "tool" not in step:
                        return PipelineResult(
                            success=False,
                            error=f"Step {context.step_number}: Only tool steps are supported in legacy executor. Use StrategyBasedExecutor for advanced features.",
                            step=context.step_number,
                            context=context.variables
                        )
                    
                    result = await self._execute_tool_step(step, context)
                    if not result.success:
                        return result
                        
                except Exception as e:
                    logger.error(f"Error executing step {context.step_number}: {e}")
                    return PipelineResult(
                        success=False,
                        error=f"Step {context.step_number} failed: {str(e)}",
                        step=context.step_number,
                        context=context.variables
                    )
            
            # Calculate final result
            try:
                if isinstance(final_result_expr, str) and ("{!" in final_result_expr or "[!" in final_result_expr):
                    final_result = substitute_expressions(final_result_expr, context.variables, expected_result_type="python")
                else:
                    final_result = final_result_expr
            except Exception as e:
                logger.error(f"Error calculating final result: {e}")
                return PipelineResult(
                    success=False,
                    error=f"Final result calculation failed: {str(e)}",
                    context=context.variables
                )
            
            execution_time = time.time() - start_time
            
            # Return success result
            return PipelineResult(
                success=True,
                result=final_result,
                context=context.variables,
                execution_time=execution_time
            )
            
        except Exception as e:
            logger.error(f"Unexpected error in legacy pipeline execution: {e}")
            execution_time = time.time() - start_time
            return PipelineResult(
                success=False,
                error=f"Unexpected error: {str(e)}",
                context={},
                execution_time=execution_time
            )
    
    async def _execute_tool_step(self, step: Dict[str, Any], context: ExecutionContext) -> PipelineResult:
        """Execute a tool step."""
        tool_name = step.get("tool", "")
        tool_params = step.get("params", {})
        output_var = step.get("output")
        
        if not tool_name:
            return PipelineResult(
                success=False,
                error=f"Step {context.step_number}: tool name is required",
                step=context.step_number,
                tool=tool_name,
                context=context.variables
            )
        
        logger.info(f"Executing step {context.step_number}: {tool_name}")
        
        # Substitute variables in parameters using new expression system
        try:
            # Simple recursive substitution for tool parameters
            substituted_params = self._substitute_recursive(tool_params, context.variables)
        except Exception as e:
            return PipelineResult(
                success=False,
                error=f"Step {context.step_number}: Parameter substitution failed: {str(e)}",
                step=context.step_number,
                tool=tool_name,
                context=context.variables
            )
        
        logger.info(f"Step {context.step_number} params after substitution: {substituted_params}")
        
        # Execute tool
        tool_response = await self.tool_runner(tool_name, substituted_params)
        
        logger.info(f"Step {context.step_number} ({tool_name}) raw response: {tool_response}")
        
        # Parse response - simple parsing
        if isinstance(tool_response, list) and len(tool_response) > 0:
            parsed_response = tool_response[0]  # Take first element
        else:
            parsed_response = tool_response
        
        logger.info(f"Step {context.step_number} ({tool_name}) parsed response: {parsed_response}")
        
        # Store result in variable if output is specified
        if output_var:
            context.variables[output_var] = parsed_response
            logger.info(f"Step {context.step_number} stored result in variable '{output_var}': {type(parsed_response).__name__}")
        
        return PipelineResult(success=True)

    def _substitute_recursive(self, obj: Any, variables: Dict[str, Any]) -> Any:
        """Recursively substitute expressions in an object."""
        if isinstance(obj, dict):
            return {k: self._substitute_recursive(v, variables) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._substitute_recursive(item, variables) for item in obj]
        elif isinstance(obj, str):
            if "{!" in obj or "[!" in obj:
                return substitute_expressions(obj, variables, expected_result_type="python")
            return obj
        else:
            return obj


# Backward compatibility aliases
PipelineExecutor = LegacyPipelineExecutor  # Keep old name for compatibility


# Legacy convenience functions for backward compatibility
async def execute_pipeline(config: Dict[str, Any], tool_runner: Callable[[str, Dict[str, Any]], Any]) -> PipelineResult:
    """
    Execute a pipeline configuration (legacy function).
    
    Args:
        config: Pipeline configuration
        tool_runner: Tool execution function
        
    Returns:
        PipelineResult
    """
    logger.warning("execute_pipeline function is deprecated. Use StrategyBasedExecutor instead.")
    executor = LegacyPipelineExecutor(tool_runner)
    return await executor.execute(config)


def evaluate_js_expression(expression: str, variables: Dict[str, Any]) -> Any:
    """Legacy function for backward compatibility."""
    logger.warning("evaluate_js_expression function is deprecated. Use evaluate_expression from expressions instead.")
    return evaluate_expression(expression, variables, expected_result_type="python")


def substitute_variables(text: str, variables: Dict[str, Any]) -> str:
    """Legacy function for backward compatibility."""
    logger.warning("substitute_variables function is deprecated. Use substitute_expressions from expressions instead.")
    return substitute_expressions(text, variables, expected_result_type="python")


def parse_tool_response(response: List) -> Any:
    """Legacy function for backward compatibility."""
    logger.warning("parse_tool_response function is deprecated. Parse responses directly.")
    # Simple response parsing - return first element if it's a list, otherwise return as-is
    if isinstance(response, list) and len(response) > 0:
        return response[0]
    return response


# Export legacy classes and functions for backward compatibility
__all__ = [
    # Legacy classes
    'LegacyPipelineExecutor',
    'PipelineExecutor',  # Alias for compatibility
    
    # Legacy functions
    'execute_pipeline',
    'evaluate_js_expression',
    'substitute_variables', 
    'parse_tool_response'
]
