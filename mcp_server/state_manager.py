"""
State Manager for MCP Server Tools

This module provides a centralized state storage mechanism for all tools in the MCP server.
The state is stored as a dictionary that persists for the lifetime of the application.
"""

class StateManager:
    """
    A singleton class that manages shared state across all tools.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StateManager, cls).__new__(cls)
            cls._instance._state = {}
        return cls._instance
    
    def get(self, key, default=None):
        """
        Get a value from the state by key.
        
        Args:
            key: The key to look up
            default: The default value to return if key is not found
            
        Returns:
            The value associated with the key, or the default value if not found
        """
        return self._state.get(key, default)
    
    def set(self, key, value):
        """
        Set a value in the state.
        
        Args:
            key: The key to store the value under
            value: The value to store
            
        Returns:
            The value that was stored
        """
        self._state[key] = value
        return value
    
    def delete(self, key):
        """
        Delete a value from the state.
        
        Args:
            key: The key to delete
            
        Returns:
            True if the key was deleted, False if it didn't exist
        """
        if key in self._state:
            del self._state[key]
            return True
        return False
    
    def has(self, key):
        """
        Check if a key exists in the state.
        
        Args:
            key: The key to check
            
        Returns:
            True if the key exists, False otherwise
        """
        return key in self._state
    
    def get_all(self):
        """
        Get a copy of the entire state dictionary.
        
        Returns:
            A copy of the state dictionary
        """
        return self._state.copy()
    
    def clear(self):
        """
        Clear all state data.
        
        Returns:
            None
        """
        self._state.clear()

# Create a singleton instance to be imported by other modules
state_manager = StateManager()
