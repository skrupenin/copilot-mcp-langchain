"""
Common logging configuration for MCP server components.
Provides unified logging setup for both server.py and run.py.
"""
import os
import logging
from pathlib import Path

def setup_logging(component_name: str, log_level: int = logging.DEBUG) -> logging.Logger:
    """
    Setup logging configuration for MCP server components.
    
    Args:
        component_name: Name of the component (used for logger name and log file)
        log_level: Logging level (default: DEBUG)
    
    Returns:
        Configured logger instance
    """
    # Determine log file path
    current_dir = Path(__file__).parent
    log_dir = current_dir / "logs"
    log_file = log_dir / f"{component_name}.log"
    
    # Ensure logs directory exists
    log_dir.mkdir(exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(component_name)
    
    # Clear any existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Set logging level
    logger.setLevel(log_level)
    
    # Create file handler
    file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    file_handler.setLevel(log_level)
    
    # Create console handler for run.py (when not in MCP mode)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    
    # Add console handler only for run.py (not for server.py to avoid MCP protocol interference)
    if component_name != "mcp_server":
        logger.addHandler(console_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    logger.info(f"Logging initialized for {component_name}")
    logger.info(f"Log file: {log_file}")
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Logger name (usually __name__)
    
    Returns:
        Logger instance
    """
    return logging.getLogger(name)
