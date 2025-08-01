"""
Common logging configuration for MCP server components.
Provides unified logging setup for both server.py and run.py.
"""
import os
import logging
import sys
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
    # Determine log file path based on component name
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
    
    # Create detailed formatter with maximum information
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(funcName)s() - %(message)s'
    )
    file_handler.setFormatter(formatter)
    
    # Add file handler (always)
    logger.addHandler(file_handler)
    
    # Detect if we're running in MCP server mode
    is_mcp_server = (
        component_name == "mcp_server" or 
        "mcp" in sys.argv[0].lower() or 
        any("mcp" in arg for arg in sys.argv) or
        os.getenv("MCP_MODE") == "true"
    )
    
    # Add console handler only when NOT in MCP server mode
    if not is_mcp_server and component_name == "mcp_runner":
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    logger.info(f"Logging initialized for {component_name}")
    logger.info(f"Log file: {log_file}")
    
    return logger