import mcp.types as types
import json
import logging
import os
import asyncio
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass, asdict
from langchain.agents import initialize_agent, AgentType
from langchain.callbacks.base import BaseCallbackHandler
from langchain.tools import BaseTool, tool
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from pydantic import BaseModel, Field
from mcp_server.llm import llm
from importlib import import_module

logger = logging.getLogger('mcp_server.tools.lng_multi_agent_manager')

class ConversationLogger:
    """Conversation logging for each sub-agent in a separate file"""
    
    def __init__(self, agent_id: str, agent_name: str):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.log_dir = Path("mcp_server/logs/multi_agent")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create log file name based on agent ID and name
        safe_name = "".join(c for c in agent_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_')
        self.log_file = self.log_dir / f"{safe_name}_{agent_id[:8]}.log"
        
        # Configure logger for this agent
        self.logger = logging.getLogger(f'agent_{agent_id}')
        self.logger.setLevel(logging.INFO)
        
        # Remove existing handlers to avoid duplication
        self.logger.handlers.clear()
        
        # Create file handler
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        self.logger.addHandler(file_handler)
        
        # Prevent propagation to parent logger
        self.logger.propagate = False
        
        # Write initial entry
        self.logger.info(f"=== Started conversation with agent {agent_name} (ID: {agent_id}) ===")
    
    def log_user_question(self, question: str):
        """Log user question"""
        self.logger.info(f"USER: {question}")
    
    def log_agent_response(self, response: str):
        """Log agent response"""
        self.logger.info(f"AGENT: {response}")
    
    def log_tool_usage(self, tool_name: str, parameters: dict, result: str):
        """Log tool usage"""
        self.logger.info(f"TOOL_USED: {tool_name}")
        self.logger.info(f"TOOL_PARAMS: {json.dumps(parameters, ensure_ascii=False, indent=2)}")
        self.logger.info(f"TOOL_RESULT: {result[:500]}{'...' if len(result) > 500 else ''}")
    
    def log_error(self, error_msg: str):
        """Log error"""
        self.logger.error(f"ERROR: {error_msg}")
    
    def log_session_end(self):
        """Log session end"""
        self.logger.info(f"=== Ended conversation with agent {self.agent_name} ===")

class DirectToolWrapper(BaseTool):
    """LangChain tool that directly calls MCP tool functions"""
    
    name: str = Field(description="Tool name")
    description: str = Field(description="Tool description")  
    tool_module_path: str = Field(description="Path to tool module")
    tool_function_name: str = Field(description="Tool function name", default="run_tool")
    conversation_logger: Optional[Any] = Field(default=None, description="Conversation logger instance")
    
    def __init__(self, name: str, description: str, tool_module_path: str, conversation_logger=None, **kwargs):
        super().__init__(
            name=name,
            description=description,
            tool_module_path=tool_module_path,
            conversation_logger=conversation_logger,
            **kwargs
        )
    
    def _run(self, **kwargs) -> str:
        """Synchronous tool execution"""
        try:
            # Log tool usage
            if self.conversation_logger:
                self.conversation_logger.log_tool_usage(self.name, kwargs, "Executing...")
            
            # Import tool module
            tool_module = import_module(self.tool_module_path)
            
            # Get the tool function
            if hasattr(tool_module, self.tool_function_name):
                tool_function = getattr(tool_module, self.tool_function_name)
                
                # Call the function directly                
                if asyncio.iscoroutinefunction(tool_function):
                    # If async function, run in event loop
                    try:
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            # If loop is already running, create task
                            import concurrent.futures
                            import threading
                            
                            def run_in_new_loop():
                                new_loop = asyncio.new_event_loop()
                                asyncio.set_event_loop(new_loop)
                                try:
                                    return new_loop.run_until_complete(tool_function(self.name, kwargs))
                                finally:
                                    new_loop.close()
                            
                            with concurrent.futures.ThreadPoolExecutor() as executor:
                                future = executor.submit(run_in_new_loop)
                                result = future.result()
                        else:
                            result = loop.run_until_complete(tool_function(self.name, kwargs))
                    except RuntimeError:
                        # No event loop, create new one
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        try:
                            result = loop.run_until_complete(tool_function(self.name, kwargs))
                        finally:
                            loop.close()
                else:
                    # Synchronous function
                    result = tool_function(self.name, kwargs)
                
                # Extract text from result
                result_text = ""
                if isinstance(result, list) and len(result) > 0:
                    if hasattr(result[0], 'text'):
                        result_text = result[0].text
                    else:
                        result_text = str(result[0])
                else:
                    result_text = str(result)
                
                # Log result
                if self.conversation_logger:
                    self.conversation_logger.log_tool_usage(self.name, kwargs, result_text)
                
                return result_text
                    
            else:
                error_msg = f"Error: Tool function {self.tool_function_name} not found in module {self.tool_module_path}"
                if self.conversation_logger:
                    self.conversation_logger.log_error(error_msg)
                return error_msg
                
        except Exception as e:
            error_msg = f"Error executing {self.name}: {str(e)}"
            if self.conversation_logger:
                self.conversation_logger.log_error(error_msg)
            return error_msg
    
    async def _arun(self, **kwargs) -> str:
        """Asynchronous tool execution"""
        try:
            # Log tool usage
            if self.conversation_logger:
                self.conversation_logger.log_tool_usage(self.name, kwargs, "Executing...")
            
            # Import tool module
            tool_module = import_module(self.tool_module_path)
            
            # Get the tool function
            if hasattr(tool_module, self.tool_function_name):
                tool_function = getattr(tool_module, self.tool_function_name)
                
                # Call the function
                if asyncio.iscoroutinefunction(tool_function):
                    result = await tool_function(self.name, kwargs)
                else:
                    result = tool_function(self.name, kwargs)
                
                # Extract text from result
                result_text = ""
                if isinstance(result, list) and len(result) > 0:
                    if hasattr(result[0], 'text'):
                        result_text = result[0].text
                    else:
                        result_text = str(result[0])
                else:
                    result_text = str(result)
                
                # Log result
                if self.conversation_logger:
                    self.conversation_logger.log_tool_usage(self.name, kwargs, result_text)
                
                return result_text
                    
            else:
                error_msg = f"Error: Tool function {self.tool_function_name} not found in module {self.tool_module_path}"
                if self.conversation_logger:
                    self.conversation_logger.log_error(error_msg)
                return error_msg
                
        except Exception as e:
            error_msg = f"Error executing {self.name}: {str(e)}"
            if self.conversation_logger:
                self.conversation_logger.log_error(error_msg)
            return error_msg

@dataclass
class SubAgentConfig:
    """Configuration for a sub-agent"""
    agent_id: str
    name: str
    module_path: str
    available_tools: List[str]
    description: str
    created_at: datetime
    last_active: datetime
    
    def to_dict(self):
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "module_path": self.module_path,
            "available_tools": self.available_tools,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "last_active": self.last_active.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            agent_id=data["agent_id"],
            name=data["name"],
            module_path=data["module_path"],
            available_tools=data["available_tools"],
            description=data["description"],
            created_at=datetime.fromisoformat(data["created_at"]),
            last_active=datetime.fromisoformat(data["last_active"])
        )

class SubAgentMemory:
    """Memory management for sub-agents using LangChain"""
    def __init__(self, agent_id: str, max_token_limit: int = 2000):
        self.agent_id = agent_id
        self.llm = llm()
        # Use simpler window memory to avoid deprecation warnings
        self.memory = ConversationBufferWindowMemory(
            k=10,  # Keep last 10 interactions
            return_messages=True
        )
        
    def add_interaction(self, question: str, answer: str):
        """Add a question-answer pair to memory"""
        self.memory.save_context(
            {"input": question},
            {"output": answer}
        )
    
    def get_memory_summary(self) -> str:
        """Get memory summary for context"""
        try:
            # Get conversation buffer and convert to simple string
            if hasattr(self.memory, 'chat_memory') and self.memory.chat_memory.messages:
                messages = []
                for msg in self.memory.chat_memory.messages[-5:]:  # Last 5 messages
                    if hasattr(msg, 'content'):
                        content = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
                        msg_type = type(msg).__name__.replace('Message', '')
                        messages.append(f"{msg_type}: {content}")
                return " | ".join(messages) if messages else "No conversation history"
            else:
                return "No conversation history"
        except Exception as e:
            return f"Error getting memory summary: {str(e)}"
    
    def get_conversation_history(self) -> List[BaseMessage]:
        """Get conversation history"""
        return self.memory.chat_memory.messages
    
    def clear_memory(self):
        """Clear memory"""
        self.memory.clear()

class SubAgent:
    """A sub-agent that monitors a specific module using direct tool access"""
    def __init__(self, config: SubAgentConfig):
        self.config = config
        self.memory = SubAgentMemory(config.agent_id)
        self.conversation_logger = ConversationLogger(config.agent_id, config.name)
        self.tools = []
        self.agent = None
        
        # Create LLM instance
        callback_manager = None
        self.llm = llm(callbacks=callback_manager, verbose=False)
        
        # Initialize tools directly
        self._initialize_tools()
        
        # Create LangChain agent
        self._initialize_agent()
    
    def _initialize_tools(self):
        """Initialize tools using DirectToolWrapper"""
        self.tools = []
        try:
            from mcp_server.tools.tool_registry import tool_definitions
            
            for tool_name in self.config.available_tools:
                try:
                    # Find tool in registry
                    tool_info = None
                    for tool in tool_definitions:
                        if tool["name"] == tool_name:
                            tool_info = tool
                            break
                    
                    if tool_info:
                        # Create DirectToolWrapper for each tool with logger
                        wrapper = DirectToolWrapper(
                            name=tool_info['name'],
                            description=f"Tool {tool_name} for agent {self.config.name}",
                            tool_module_path=tool_info['module_path'],
                            conversation_logger=self.conversation_logger
                        )
                        self.tools.append(wrapper)
                        logger.info(f"Agent {self.config.agent_id}: Added tool {tool_name}")
                    else:
                        logger.warning(f"Agent {self.config.agent_id}: Tool {tool_name} not found in registry")
                        
                except Exception as e:
                    logger.error(f"Agent {self.config.agent_id}: Error loading tool {tool_name}: {e}")
                    
        except Exception as e:
            logger.error(f"Agent {self.config.agent_id}: Error importing tool_registry: {e}")
    
    def _initialize_agent(self):
        """Initialize LangChain agent"""
        try:
            if self.tools:
                self.agent = initialize_agent(
                    tools=self.tools,
                    llm=self.llm,
                    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
                    verbose=False,
                    memory=self.memory.memory
                )
                logger.info(f"Agent {self.config.agent_id}: Initialized with {len(self.tools)} tools")
            else:
                logger.warning(f"Agent {self.config.agent_id}: No tools available")
                self.agent = None
        except Exception as e:
            logger.error(f"Agent {self.config.agent_id}: Error initializing agent: {e}")
            self.agent = None

    async def process_query(self, question: str) -> str:
        """Process a query and return a summary response"""
        try:
            # Log user question
            self.conversation_logger.log_user_question(question)
            
            if not self.agent:
                error_msg = f"Agent {self.config.name} failed to initialize properly."
                self.conversation_logger.log_error(error_msg)
                return error_msg
            
            # Create system prompt with context about the module
            system_context = f"""You are a specialized agent responsible for module: {self.config.module_path}
            
Your role is to:
1. Analyze and understand code in your assigned module
2. Answer questions about the module's functionality, structure, and implementation
3. Provide clear, concise summaries of your findings
4. Use available tools to read and analyze files when needed

Module Description: {self.config.description}

Available Tools: {', '.join(self.config.available_tools)}

Important: Always provide a clear summary of your analysis. Focus on answering the specific question asked."""
            
            # Combine system context with the question
            full_input = f"{system_context}\n\nQuestion: {question}"
            
            # Process with agent
            if hasattr(self.agent, 'ainvoke'):
                # Use async version if available
                result = await self.agent.ainvoke({"input": full_input})
            else:
                # Fallback to sync version
                result = self.agent.invoke({"input": full_input})
            
            # Extract the response
            response = result.get("output", "No response generated")
            
            # Create summary (this is already a summary since we ask agent to summarize)
            summary = self._create_summary(question, response)
            
            # Log agent response
            self.conversation_logger.log_agent_response(summary)
            
            # Store in memory
            self.memory.add_interaction(question, summary)
            
            # Update last active time
            self.config.last_active = datetime.now()
            
            return summary
            
        except Exception as e:
            error_msg = f"Error processing query: {str(e)}"
            logger.error(f"Agent {self.config.agent_id}: {error_msg}")
            self.conversation_logger.log_error(error_msg)
            return error_msg
    
    def _create_summary(self, question: str, response: str) -> str:
        """Create a summary of the interaction"""
        # For now, we'll return the response as-is since we ask the agent to provide summaries
        # In the future, we might want to add additional summarization
        return response
    
    def get_status(self) -> dict:
        """Get agent status"""
        return {
            "agent_id": self.config.agent_id,
            "name": self.config.name,
            "module_path": self.config.module_path,
            "available_tools": self.config.available_tools,
            "memory_summary": self.memory.get_memory_summary(),
            "last_active": self.config.last_active.isoformat(),
            "tools_count": len(self.tools)
        }
    
    def __del__(self):
        """Destructor to log session end when agent is destroyed"""
        try:
            if hasattr(self, 'conversation_logger'):
                self.conversation_logger.log_session_end()
        except Exception:
            # Ignore errors in destructor
            pass

class MultiAgentManager:
    """Manager for multiple sub-agents"""
    def __init__(self):
        self.agents: Dict[str, SubAgent] = {}
        self.config_dir = Path("mcp_server/config/multi_agent")
        self._load_configs()
    
    def _name_to_filename(self, name: str) -> str:
        """Convert agent name to filename (using hyphens instead of spaces)"""
        # Replace spaces with hyphens, convert to lowercase, remove special chars
        filename = name.lower().replace(' ', '-')
        # Keep only alphanumeric characters and hyphens
        filename = ''.join(c for c in filename if c.isalnum() or c == '-')
        # Remove multiple consecutive hyphens
        filename = '-'.join(filter(None, filename.split('-')))
        return f"{filename}.json"
    
    def _load_configs(self):
        """Load agent configurations from individual files"""
        if not self.config_dir.exists():
            logger.info("Multi-agent config directory does not exist yet")
            return
            
        for json_file in self.config_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    agent_data = json.load(f)
                
                config = SubAgentConfig.from_dict(agent_data)
                agent = SubAgent(config)
                self.agents[config.agent_id] = agent
                logger.info(f"Loaded agent {config.name} from {json_file.name}")
                
            except Exception as e:
                logger.error(f"Error loading agent from {json_file}: {e}")
        
        logger.info(f"Loaded {len(self.agents)} sub-agents total")
    
    def _save_agent_config(self, config: SubAgentConfig):
        """Save individual agent configuration to file"""
        try:
            # Ensure directory exists
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
            filename = self._name_to_filename(config.name)
            file_path = self.config_dir / filename
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config.to_dict(), f, indent=2, ensure_ascii=False)
                
            logger.info(f"Saved agent {config.name} to {filename}")
                
        except Exception as e:
            logger.error(f"Error saving agent config for {config.name}: {e}")
    
    def _remove_agent_config(self, config: SubAgentConfig):
        """Remove individual agent configuration file"""
        try:
            filename = self._name_to_filename(config.name)
            file_path = self.config_dir / filename
            
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Removed agent config file {filename}")
                
        except Exception as e:
            logger.error(f"Error removing agent config file for {config.name}: {e}")
    
    def create_agent(self, name: str, module_path: str, available_tools: List[str], description: str = "") -> str:
        """Create a new sub-agent"""
        agent_id = str(uuid.uuid4())
        
        config = SubAgentConfig(
            agent_id=agent_id,
            name=name,
            module_path=module_path,
            available_tools=available_tools,
            description=description,
            created_at=datetime.now(),
            last_active=datetime.now()
        )
        
        agent = SubAgent(config)
        self.agents[agent_id] = agent
        
        # Save individual agent config
        self._save_agent_config(config)
        
        logger.info(f"Created sub-agent {name} with ID {agent_id} for module {module_path}")
        return agent_id
    
    def remove_agent(self, agent_id: str) -> bool:
        """Remove a sub-agent"""
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            agent_name = agent.config.name
            
            # Log session end before removing agent
            agent.conversation_logger.log_session_end()
            
            # Remove config file
            self._remove_agent_config(agent.config)
            
            # Remove from memory
            del self.agents[agent_id]
            
            logger.info(f"Removed sub-agent {agent_name} with ID {agent_id}")
            return True
        return False
    
    async def query_agent(self, agent_id: str, question: str) -> str:
        """Send a query to a specific sub-agent"""
        if agent_id not in self.agents:
            return f"Agent with ID {agent_id} not found"
        
        result = await self.agents[agent_id].process_query(question)
        
        # Update last active time and save config
        self.agents[agent_id].config.last_active = datetime.now()
        self._save_agent_config(self.agents[agent_id].config)
        
        return result
    
    def list_agents(self) -> List[dict]:
        """List all sub-agents"""
        result = []
        for agent in self.agents.values():
            try:
                status = agent.get_status()
                result.append(status)
            except Exception as e:
                logger.error(f"Error getting status for agent {agent.config.agent_id}: {e}")
                # Add minimal info if status fails
                result.append({
                    "agent_id": agent.config.agent_id,
                    "name": agent.config.name,
                    "module_path": agent.config.module_path,
                    "available_tools": agent.config.available_tools,
                    "memory_summary": "Error getting memory summary",
                    "last_active": agent.config.last_active.isoformat(),
                    "tools_count": len(agent.tools),
                    "error": str(e)
                })
        return result
    
    def get_agent_by_module(self, module_path: str) -> Optional[str]:
        """Find agent responsible for a specific module"""
        for agent_id, agent in self.agents.items():
            if agent.config.module_path == module_path:
                return agent_id
        return None

# Global manager instance
manager = MultiAgentManager()

async def tool_info() -> dict:
    """Returns information about the lng_multi_agent_manager tool."""
    return {
        "description": """Multi-Agent Manager for delegating tasks to specialized sub-agents.

This tool manages a system of sub-agents, each responsible for monitoring and analyzing specific modules or directories in a codebase.

**Parameters for different operations:**

**create_agent** - Create a new sub-agent:
- `operation` (string, required): "create_agent"
- `name` (string, required): Human-readable name for the agent (can contain spaces)
- `module_path` (string, required): Path to the module this agent will monitor
- `available_tools` (array, required): List of tool names from tool_registry this agent can use
- `description` (string, optional): Description of the agent's purpose

**Important**: Agent configuration files will be created using lowercase with hyphens (-) instead of spaces in filenames:
- "Frontend Agent" → `frontend-agent.json`
- "API Manager" → `api-manager.json`
- "Database Handler" → `database-handler.json`

**query_agent** - Send query to a sub-agent:
- `operation` (string, required): "query_agent"  
- `agent_id` (string, required): ID of the agent to query
- `question` (string, required): Question to ask the agent

**list_agents** - List all sub-agents:
- `operation` (string, required): "list_agents"

**remove_agent** - Remove a sub-agent:
- `operation` (string, required): "remove_agent"
- `agent_id` (string, required): ID of the agent to remove

**find_agent** - Find agent by module path:
- `operation` (string, required): "find_agent"
- `module_path` (string, required): Module path to search for

**Example Usage:**
- Create agent: `{"operation": "create_agent", "name": "Frontend Agent", "module_path": "/src/components", "available_tools": ["lng_file_read", "lng_file_list"], "description": "Handles React components"}`
- Query agent: `{"operation": "query_agent", "agent_id": "agent-uuid", "question": "What files are in this module?"}`""",
        
        "schema": {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "description": "The operation to perform",
                    "enum": ["create_agent", "query_agent", "list_agents", "remove_agent", "find_agent"]
                },
                "name": {
                    "type": "string",
                    "description": "Name for the agent (for create_agent). Can contain spaces - the filename will automatically use hyphens instead."
                },
                "module_path": {
                    "type": "string", 
                    "description": "Path to the module (for create_agent and find_agent)"
                },
                "available_tools": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of tool names from tool_registry (for create_agent)"
                },
                "description": {
                    "type": "string",
                    "description": "Description of the agent (for create_agent)"
                },
                "agent_id": {
                    "type": "string",
                    "description": "Agent ID (for query_agent, remove_agent)"
                },
                "question": {
                    "type": "string",
                    "description": "Question to ask the agent (for query_agent)"
                }
            },
            "required": ["operation"]
        }
    }

async def run_tool(name: str, parameters: dict) -> list[types.Content]:
    """Runs the multi-agent manager tool."""
    try:
        operation = parameters.get("operation", "")
        
        if not operation:
            return [types.TextContent(type="text", text=json.dumps({"error": "operation parameter is required"}, ensure_ascii=False))]
        
        if operation == "create_agent":
            agent_name = parameters.get("name", "")
            module_path = parameters.get("module_path", "")
            available_tools = parameters.get("available_tools", [])
            description = parameters.get("description", "")
            
            if not agent_name or not module_path or not available_tools:
                return [types.TextContent(type="text", text=json.dumps({
                    "error": "name, module_path, and available_tools are required for create_agent operation"
                }, ensure_ascii=False))]
            
            agent_id = manager.create_agent(agent_name, module_path, available_tools, description)
            
            result = {
                "operation": "create_agent",
                "success": True,
                "agent_id": agent_id,
                "name": agent_name,
                "module_path": module_path,
                "available_tools": available_tools,
                "description": description
            }
            
        elif operation == "query_agent":
            agent_id = parameters.get("agent_id", "")
            question = parameters.get("question", "")
            
            if not agent_id or not question:
                return [types.TextContent(type="text", text=json.dumps({
                    "error": "agent_id and question are required for query_agent operation"
                }, ensure_ascii=False))]
            
            response = await manager.query_agent(agent_id, question)
            
            result = {
                "operation": "query_agent",
                "success": True,
                "agent_id": agent_id,
                "question": question,
                "response": response
            }
            
        elif operation == "list_agents":
            agents = manager.list_agents()
            
            result = {
                "operation": "list_agents",
                "success": True,
                "agents": agents
            }
            
        elif operation == "remove_agent":
            agent_id = parameters.get("agent_id", "")
            
            if not agent_id:
                return [types.TextContent(type="text", text=json.dumps({
                    "error": "agent_id is required for remove_agent operation"
                }, ensure_ascii=False))]
            
            success = manager.remove_agent(agent_id)
            
            result = {
                "operation": "remove_agent",
                "success": success,
                "agent_id": agent_id
            }
            
        elif operation == "find_agent":
            module_path = parameters.get("module_path", "")
            
            if not module_path:
                return [types.TextContent(type="text", text=json.dumps({
                    "error": "module_path is required for find_agent operation"
                }, ensure_ascii=False))]
            
            agent_id = manager.get_agent_by_module(module_path)
            
            result = {
                "operation": "find_agent",
                "success": True,
                "module_path": module_path,
                "agent_id": agent_id
            }
            
        else:
            return [types.TextContent(type="text", text=json.dumps({
                "error": f"Unknown operation: {operation}"
            }, ensure_ascii=False))]
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
        
    except Exception as e:
        logger.error(f"Error in multi-agent manager: {e}")
        return [types.TextContent(type="text", text=json.dumps({"error": str(e)}, ensure_ascii=False))]
