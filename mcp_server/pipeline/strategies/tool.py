"""
Tool execution strategy.

This strategy handles basic tool execution with parameter substitution
and result storage. It's the fundamental building block of the pipeline system.
"""

import asyncio
import logging
from typing import Any, Dict, Callable

from .base import ExecutionStrategy
from ..models import PipelineResult, ExecutionContext
from ..utils import VariableSubstitutor, ResponseParser

logger = logging.getLogger('mcp_server.pipeline.strategies.tool')


class ToolStrategy(ExecutionStrategy):
    """Strategy for executing tool calls - the basic pipeline functionality."""
    
    def __init__(self, tool_runner: Callable[[str, Dict[str, Any]], Any]):
        self.tool_runner = tool_runner
        self.variable_substitutor = VariableSubstitutor()
        self.response_parser = ResponseParser()
    
    def can_handle(self, step: Dict[str, Any]) -> bool:
        """Handle steps that have a 'tool' field."""
        return "tool" in step and step.get("type", "tool") == "tool"
    
    async def execute(self, step: Dict[str, Any], context: ExecutionContext, executor) -> PipelineResult:
        """Execute a tool call with parameter substitution."""
        try:
            tool_name = step["tool"]
            params = step.get("params", {})
            output_var = step.get("output")
            
            logger.info(f"Step {context.step_number}: Executing tool '{tool_name}'")
            
            # Substitute variables in parameters
            substituted_params = self.variable_substitutor.substitute_recursive(params, context.variables)
            logger.debug(f"Tool parameters after substitution: {substituted_params}")
            
            # Execute the tool
            if asyncio.iscoroutinefunction(self.tool_runner):
                tool_result = await self.tool_runner(tool_name, substituted_params)
            else:
                tool_result = self.tool_runner(tool_name, substituted_params)
            
            # Parse and store result
            parsed_result = self.response_parser.parse(tool_result)
            
            if output_var:
                context.variables[output_var] = parsed_result
                logger.debug(f"Stored result in variable '{output_var}': {type(parsed_result).__name__}")
            
            return PipelineResult(success=True, context=context.variables)
            
        except Exception as e:
            error_msg = f"Step {context.step_number} tool '{tool_name}' failed: {str(e)}"
            logger.error(error_msg)
            return PipelineResult(
                success=False,
                error=error_msg,
                step=context.step_number,
                tool=tool_name,
                context=context.variables
            )
    
    @property
    def strategy_name(self) -> str:
        return "Tool"
