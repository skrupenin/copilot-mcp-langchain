"""
Enhanced Pipeline execution engine with conditional logic support.

This module extends the core pipeline system with:
- Inline conditional steps (if-then-else)
- Recursive sub-pipelines
- JavaScript expression evaluation
- Nested conditions support

Usage:
    from mcp_server.pipeline import EnhancedPipelineExecutor
    
    executor = EnhancedPipelineExecutor(tool_runner=run_tool)
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
from .core import (
    PipelineExecutor, 
    PipelineResult, 
    ExpressionEvaluator,
    VariableSubstitutor,
    ResponseParser,
    ExecutionContext,
    StepType
)

logger = logging.getLogger('mcp_server.pipeline.enhanced')


class EnhancedPipelineExecutor(PipelineExecutor):
    """
    Enhanced pipeline executor with conditional logic support.
    
    Supports recursive pipeline execution with conditions:
    
    Example:
    {
        "pipeline": [
            {"tool": "lng_count_words", "params": {"input_text": "test"}, "output": "stats"},
            {
                "type": "condition",
                "condition": "${stats.wordCount > 5}",
                "then": [
                    {"tool": "lng_winapi_clipboard_set", "params": {"text": "Long text"}},
                    {
                        "type": "condition",
                        "condition": "${stats.wordCount > 20}",
                        "then": [{"tool": "lng_save_screenshot", "params": {}}],
                        "else": [{"tool": "lng_llm_chain_of_thought", "params": {...}}]
                    }
                ],
                "else": [
                    {"tool": "lng_winapi_clipboard_set", "params": {"text": "Short text"}}
                ]
            }
        ],
        "final_result": "Processing completed"
    }
    
    Features:
    - ✅ JavaScript expressions in conditions: ${variable.property > value && other.check}
    - ✅ then/else blocks as sub-pipelines with multiple steps
    - ✅ Shared variable context across all pipeline levels
    - ✅ Full pipeline stop on errors
    - ✅ Unlimited nesting depth for conditions
    - ✅ Informative error messages for missing variables
    - ✅ Backward compatibility with existing pipelines
    """
    
    def __init__(self, tool_runner: Callable[[str, Dict[str, Any]], Any]):
        """Initialize enhanced pipeline executor with conditional logic support."""
        super().__init__(tool_runner)
        # Ensure we have the expression evaluator for conditions
        self.expression_evaluator = ExpressionEvaluator()
    
    def _determine_step_type(self, step: Dict[str, Any]) -> StepType:
        """Determine the type of pipeline step with enhanced condition support."""
        if "type" in step and step["type"] == "condition":
            return StepType.CONDITION
        elif "tool" in step:
            return StepType.TOOL
        elif "if" in step:  # Alternative syntax support
            return StepType.CONDITION
        elif "foreach" in step:
            return StepType.LOOP
        elif "parallel" in step:
            return StepType.PARALLEL
        elif "template" in step:
            return StepType.TEMPLATE
        else:
            return StepType.TOOL  # Default to tool step
    
    async def _execute_condition_step(self, step: Dict[str, Any], context: ExecutionContext) -> PipelineResult:
        """
        Execute a conditional step with then/else sub-pipelines.
        
        This method supports:
        - JavaScript expression evaluation in conditions
        - Recursive execution of sub-pipelines
        - Shared variable context across all levels
        - Nested conditions with unlimited depth
        
        Args:
            step: Condition step configuration with 'condition', 'then', 'else' fields
            context: Shared execution context with variables
            
        Returns:
            Pipeline result with success/error status
        """
        try:
            # Extract condition and blocks
            condition_expr = step.get("condition", "")
            then_steps = step.get("then", [])
            else_steps = step.get("else", [])
            
            if not condition_expr:
                return PipelineResult(
                    success=False,
                    error=f"Step {context.step_number}: condition expression is required",
                    step=context.step_number,
                    context=context.variables
                )
            
            logger.info(f"Step {context.step_number}: Evaluating condition: {condition_expr}")
            
            # Evaluate condition using JavaScript-like expressions
            condition_result = self._evaluate_condition(condition_expr, context.variables)
            
            logger.info(f"Step {context.step_number}: Condition result: {condition_result}")
            
            # Choose which sub-pipeline to execute based on condition result
            if condition_result:
                if then_steps:
                    logger.info(f"Step {context.step_number}: Executing THEN block with {len(then_steps)} steps")
                    return await self._execute_sub_pipeline(then_steps, context, "THEN")
                else:
                    logger.info(f"Step {context.step_number}: THEN block is empty, skipping")
                    return PipelineResult(success=True, context=context.variables)
            else:
                if else_steps:
                    logger.info(f"Step {context.step_number}: Executing ELSE block with {len(else_steps)} steps")
                    return await self._execute_sub_pipeline(else_steps, context, "ELSE")
                else:
                    logger.info(f"Step {context.step_number}: ELSE block is empty, skipping")
                    return PipelineResult(success=True, context=context.variables)
                    
        except Exception as e:
            error_msg = f"Step {context.step_number} condition failed: {str(e)}"
            logger.error(error_msg)
            return PipelineResult(
                success=False,
                error=error_msg,
                step=context.step_number,
                context=context.variables
            )
    
    async def _execute_sub_pipeline(self, steps: List[Dict[str, Any]], context: ExecutionContext, block_type: str = "SUB") -> PipelineResult:
        """
        Execute a sub-pipeline (then/else block) within the same shared context.
        
        This enables recursive pipeline execution with:
        - Shared variable context across all levels
        - Support for any step types including nested conditions
        - Proper error propagation
        - Hierarchical step numbering for debugging
        
        Args:
            steps: List of pipeline steps to execute
            context: Shared execution context (variables persist across levels)
            block_type: Type of block for logging ("THEN", "ELSE", "SUB")
            
        Returns:
            Pipeline result (errors stop entire pipeline)
        """
        if not steps:
            return PipelineResult(success=True, context=context.variables)
        
        # Save current step number for proper restoration
        original_step = context.step_number
        
        try:
            # Execute each step in the sub-pipeline
            for i, step in enumerate(steps):
                # Update step number for hierarchical logging (e.g., 2.1, 2.2, 2.1.1, etc.)
                context.step_number = f"{original_step}.{i+1}"
                
                logger.debug(f"Executing {block_type} sub-step {context.step_number}: {step}")
                
                # Recursively execute step - this supports:
                # - Regular tool steps
                # - Nested condition steps (unlimited depth)
                # - Future step types (loops, parallel, etc.)
                result = await self._execute_step(step, context)
                
                if not result.success:
                    # Error propagation: any error stops the entire pipeline
                    logger.error(f"{block_type} sub-pipeline failed at step {context.step_number}")
                    return result
                    
            # Restore original step number
            context.step_number = original_step
            
            return PipelineResult(success=True, context=context.variables)
            
        except Exception as e:
            # Ensure step number is restored even on exception
            context.step_number = original_step
            error_msg = f"{block_type} sub-pipeline execution failed at step {context.step_number}: {str(e)}"
            logger.error(error_msg)
            return PipelineResult(
                success=False,
                error=error_msg,
                step=context.step_number,
                context=context.variables
            )
    
    def _evaluate_condition(self, condition: str, variables: Dict[str, Any]) -> bool:
        """
        Evaluate a conditional expression using JavaScript-like syntax.
        
        Supports:
        - Variable access: ${variable.property}
        - Comparison operators: >, <, >=, <=, ==, !=
        - Logical operators: &&, ||, !
        - Complex expressions: ${stats.wordCount > 5 && text.length > 0}
        - Informative error messages for debugging
        
        Args:
            condition: Condition string like "${word_count > 5 && text.length > 0}"
            variables: Variable context from pipeline execution
            
        Returns:
            True if condition is met, False otherwise
            
        Raises:
            Exception: If condition evaluation fails with detailed error message
        """
        try:
            # Remove ${ } wrapper if present
            if condition.startswith("${") and condition.endswith("}"):
                js_expr = condition[2:-1].strip()
            else:
                js_expr = condition.strip()
            
            if not js_expr:
                raise ValueError("Empty condition expression")
            
            logger.debug(f"Evaluating JS expression: {js_expr}")
            logger.debug(f"Available variables: {list(variables.keys())}")
            
            # Use existing expression evaluator with enhanced error handling
            try:
                result = self.expression_evaluator.evaluate(js_expr, variables)
            except KeyError as e:
                # Provide informative error for missing variables
                missing_var = str(e).strip("'\"")
                available_vars = ", ".join(variables.keys()) if variables else "none"
                raise ValueError(
                    f"Variable '{missing_var}' not found in condition '{js_expr}'. "
                    f"Available variables: {available_vars}"
                )
            except Exception as e:
                raise ValueError(f"Failed to evaluate condition '{js_expr}': {str(e)}")
            
            # Convert result to boolean using JavaScript-like truthiness
            if isinstance(result, bool):
                return result
            elif isinstance(result, (int, float)):
                return result != 0
            elif isinstance(result, str):
                return result.lower() not in ('false', '0', '', 'null', 'undefined')
            elif result is None:
                return False
            else:
                return bool(result)
                
        except Exception as e:
            logger.error(f"Condition evaluation error: {e}")
            raise


# Legacy compatibility: keep original PipelineExecutor available
# New code should use EnhancedPipelineExecutor
ConditionalPipelineExecutor = EnhancedPipelineExecutor  # Alias for backward compatibility

# Export enhanced executor as the default
__all__ = ['EnhancedPipelineExecutor', 'ConditionalPipelineExecutor', 'PipelineExecutor', 'PipelineResult']
