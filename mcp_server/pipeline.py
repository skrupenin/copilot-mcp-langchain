"""
Pipeline execution engine for MCP tools.

This module provides a flexible pipeline system for chaining tool executions
with variable substitution, conditional logic, and error handling.

Usage:
    from mcp_server.pipeline import PipelineExecutor
    
    executor = PipelineExecutor(tool_runner=run_tool)
    result = await executor.execute(pipeline_config)
"""

import json
import re
import logging
import asyncio
from typing import Any, Dict, List, Callable, Optional, Union
from dataclasses import dataclass
from enum import Enum

import mcp.types as types

logger = logging.getLogger('mcp_server.pipeline')


class StepType(Enum):
    """Pipeline step types."""
    TOOL = "tool"
    CONDITION = "condition"
    LOOP = "loop"
    PARALLEL = "parallel"
    TEMPLATE = "template"


@dataclass
class PipelineResult:
    """Result of pipeline execution."""
    success: bool
    result: Any = None
    error: Optional[str] = None
    step: Optional[int] = None
    tool: Optional[str] = None
    context: Dict[str, Any] = None
    execution_time: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "success": self.success,
            "result": self.result,
            "error": self.error,
            "step": self.step,
            "tool": self.tool,
            "context": self.context or {},
            "execution_time": self.execution_time
        }


@dataclass
class ExecutionContext:
    """Execution context for pipeline."""
    variables: Dict[str, Any]
    step_number: int = 0
    templates: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.templates is None:
            self.templates = {}


class ExpressionEvaluator:
    """Evaluates JavaScript-like expressions in Python context."""
    
    @staticmethod
    def evaluate(expression: str, variables: Dict[str, Any]) -> Any:
        """
        Evaluate a JavaScript-like expression using Python eval with available variables.
        
        Args:
            expression: JavaScript expression to evaluate
            variables: Dictionary of available variables
            
        Returns:
            Evaluated result
        """
        try:
            # Create a safe evaluation context with variables and common functions
            eval_context = {
                **variables,
                'JSON': {
                    'stringify': lambda obj: json.dumps(obj, ensure_ascii=False),
                    'parse': lambda s: json.loads(s)
                },
                'String': str,
                'Number': float,
                'Boolean': bool,
                'len': len,
                'str': str,
                'int': int,
                'float': float,
                'bool': bool,
            }
            
            # Simple replacements for JavaScript syntax
            py_expression = expression
            
            # Replace JavaScript null/undefined with Python None
            py_expression = re.sub(r'\bundefined\b', 'None', py_expression)
            py_expression = re.sub(r'\bnull\b', 'None', py_expression)
            
            # Replace JavaScript boolean literals
            py_expression = re.sub(r'\btrue\b', 'True', py_expression)
            py_expression = re.sub(r'\bfalse\b', 'False', py_expression)
            
            # Replace JavaScript || operator with Python or
            py_expression = re.sub(r'\|\|', ' or ', py_expression)
            
            # Replace JavaScript && operator with Python and
            py_expression = re.sub(r'&&', ' and ', py_expression)
            
            # Handle JSON.stringify calls
            py_expression = re.sub(r'JSON\.stringify\(([^)]+)\)', r'JSON["stringify"](\1)', py_expression)
            py_expression = re.sub(r'JSON\.parse\(([^)]+)\)', r'JSON["parse"](\1)', py_expression)
            
            # Replace JavaScript property access with Python dict access for known variables
            for var_name in variables.keys():
                # Replace var.property with var.get("property") if var is a dict
                var_value = variables[var_name]
                if isinstance(var_value, dict):
                    # Use regex to replace property access
                    pattern = rf'\b{re.escape(var_name)}\.(\w+)'
                    py_expression = re.sub(pattern, rf'{var_name}.get("\1")', py_expression)
            
            result = eval(py_expression, {"__builtins__": {}}, eval_context)
            return result
        except Exception as e:
            logger.error(f"Error evaluating JavaScript expression '{expression}': {e}")
            raise ValueError(f"JavaScript evaluation error: {str(e)}")


class VariableSubstitutor:
    """Handles variable substitution in strings."""
    
    @staticmethod
    def substitute(text: str, variables: Dict[str, Any]) -> str:
        """
        Replace ${expression} patterns in text with evaluated JavaScript expressions.
        
        Args:
            text: Text containing ${} patterns
            variables: Dictionary of available variables
            
        Returns:
            Text with substituted values
        """
        if not isinstance(text, str):
            return text
            
        def replace_expression(match):
            expression = match.group(1)
            try:
                result = ExpressionEvaluator.evaluate(expression, variables)
                return str(result) if result is not None else ""
            except Exception as e:
                logger.error(f"Error substituting expression '${{{expression}}}': {e}")
                raise
        
        # Find and replace all ${expression} patterns
        pattern = r'\$\{([^}]+)\}'
        return re.sub(pattern, replace_expression, text)
    
    @staticmethod
    def substitute_recursive(obj: Any, variables: Dict[str, Any]) -> Any:
        """Recursively substitute variables in nested structures."""
        if isinstance(obj, str):
            return VariableSubstitutor.substitute(obj, variables)
        elif isinstance(obj, dict):
            return {k: VariableSubstitutor.substitute_recursive(v, variables) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [VariableSubstitutor.substitute_recursive(item, variables) for item in obj]
        else:
            return obj


class ResponseParser:
    """Parses tool responses and converts them to appropriate format."""
    
    @staticmethod
    def parse(response: List[types.Content]) -> Any:
        """
        Parse tool response and try to convert to JSON if possible.
        
        Args:
            response: Tool response content list
            
        Returns:
            Parsed JSON object or original string
        """
        if not response:
            return ""
        
        # Get the text content from the first response item
        text_content = ""
        for content in response:
            if isinstance(content, types.TextContent):
                text_content = content.text
                break
        
        if not text_content:
            return ""
        
        # Try to parse as JSON
        try:
            return json.loads(text_content)
        except (json.JSONDecodeError, TypeError):
            # If not valid JSON, return as string
            return text_content


class PipelineExecutor:
    """Main pipeline execution engine."""
    
    def __init__(self, tool_runner: Callable[[str, Dict[str, Any]], Any]):
        """
        Initialize pipeline executor.
        
        Args:
            tool_runner: Function to execute tools (e.g., run_tool from tool_registry)
        """
        self.tool_runner = tool_runner
        self.substitutor = VariableSubstitutor()
        self.parser = ResponseParser()
    
    async def execute(self, config: Dict[str, Any]) -> PipelineResult:
        """
        Execute a pipeline configuration.
        
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
            
            # Execute pipeline steps
            for step_index, step in enumerate(pipeline_steps):
                context.step_number = step_index + 1
                
                try:
                    result = await self._execute_step(step, context)
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
                if isinstance(final_result_expr, str) and "${" in final_result_expr:
                    final_result = self.substitutor.substitute(final_result_expr, context.variables)
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
            logger.error(f"Unexpected error in pipeline execution: {e}")
            execution_time = time.time() - start_time
            return PipelineResult(
                success=False,
                error=f"Unexpected error: {str(e)}",
                context={},
                execution_time=execution_time
            )
    
    async def _execute_step(self, step: Dict[str, Any], context: ExecutionContext) -> PipelineResult:
        """Execute a single pipeline step."""
        
        # Determine step type
        step_type = self._determine_step_type(step)
        
        if step_type == StepType.TOOL:
            return await self._execute_tool_step(step, context)
        elif step_type == StepType.CONDITION:
            return await self._execute_condition_step(step, context)
        elif step_type == StepType.LOOP:
            return await self._execute_loop_step(step, context)
        elif step_type == StepType.PARALLEL:
            return await self._execute_parallel_step(step, context)
        elif step_type == StepType.TEMPLATE:
            return await self._execute_template_step(step, context)
        else:
            return PipelineResult(
                success=False,
                error=f"Unknown step type in step {context.step_number}",
                step=context.step_number,
                context=context.variables
            )
    
    def _determine_step_type(self, step: Dict[str, Any]) -> StepType:
        """Determine the type of pipeline step."""
        if "tool" in step:
            return StepType.TOOL
        elif "if" in step:
            return StepType.CONDITION
        elif "foreach" in step:
            return StepType.LOOP
        elif "parallel" in step:
            return StepType.PARALLEL
        elif "template" in step:
            return StepType.TEMPLATE
        else:
            return StepType.TOOL  # Default to tool step
    
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
        
        # Substitute variables in parameters
        substituted_params = self.substitutor.substitute_recursive(tool_params, context.variables)
        
        logger.info(f"Step {context.step_number} params after substitution: {substituted_params}")
        
        # Execute tool
        tool_response = await self.tool_runner(tool_name, substituted_params)
        
        logger.info(f"Step {context.step_number} ({tool_name}) raw response: {tool_response}")
        
        # Parse response
        parsed_response = self.parser.parse(tool_response)
        
        logger.info(f"Step {context.step_number} ({tool_name}) parsed response: {parsed_response}")
        
        # Store result in variable if output is specified
        if output_var:
            context.variables[output_var] = parsed_response
            logger.info(f"Step {context.step_number} stored result in variable '{output_var}': {type(parsed_response).__name__}")
        
        return PipelineResult(success=True)
    
    async def _execute_condition_step(self, step: Dict[str, Any], context: ExecutionContext) -> PipelineResult:
        """Execute a conditional step."""
        # TODO: Implement conditional logic
        return PipelineResult(
            success=False,
            error="Conditional steps not yet implemented",
            step=context.step_number,
            context=context.variables
        )
    
    async def _execute_loop_step(self, step: Dict[str, Any], context: ExecutionContext) -> PipelineResult:
        """Execute a loop step."""
        # TODO: Implement loop logic
        return PipelineResult(
            success=False,
            error="Loop steps not yet implemented",
            step=context.step_number,
            context=context.variables
        )
    
    async def _execute_parallel_step(self, step: Dict[str, Any], context: ExecutionContext) -> PipelineResult:
        """Execute a parallel step."""
        # TODO: Implement parallel logic
        return PipelineResult(
            success=False,
            error="Parallel steps not yet implemented",
            step=context.step_number,
            context=context.variables
        )
    
    async def _execute_template_step(self, step: Dict[str, Any], context: ExecutionContext) -> PipelineResult:
        """Execute a template step."""
        # TODO: Implement template logic
        return PipelineResult(
            success=False,
            error="Template steps not yet implemented",
            step=context.step_number,
            context=context.variables
        )


# Convenience functions for backward compatibility
async def execute_pipeline(config: Dict[str, Any], tool_runner: Callable[[str, Dict[str, Any]], Any]) -> PipelineResult:
    """
    Execute a pipeline configuration.
    
    Args:
        config: Pipeline configuration
        tool_runner: Tool execution function
        
    Returns:
        PipelineResult
    """
    executor = PipelineExecutor(tool_runner)
    return await executor.execute(config)


def evaluate_js_expression(expression: str, variables: Dict[str, Any]) -> Any:
    """Legacy function for backward compatibility."""
    return ExpressionEvaluator.evaluate(expression, variables)


def substitute_variables(text: str, variables: Dict[str, Any]) -> str:
    """Legacy function for backward compatibility."""
    return VariableSubstitutor.substitute(text, variables)


def parse_tool_response(response: List[types.Content]) -> Any:
    """Legacy function for backward compatibility."""
    return ResponseParser.parse(response)
