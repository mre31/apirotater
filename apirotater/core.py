import os
import time
import dotenv
import sys
from typing import Dict, List, Tuple, Optional, Union, Any
from datetime import datetime, timedelta

class RateLimitExceeded(Exception):
    """Exception thrown when all API keys have exceeded their rate limit."""
    pass

class APIRotater:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(APIRotater, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._api_keys = []
        self._key_names = {}  # Map api key values to their variable names
        self._usage_stats = {}
        self._rate_limits = {}
        self._current_key_index = 0  # Track the currently active key
        self._time_window = 60  # Default time window
        self._max_uses = 100  # Default max uses
        self._load_api_keys()
        self._initialized = True
    
    def _load_api_keys(self):
        """Loads API keys from .env files."""
        # Directories to check
        paths = [
            os.getcwd(),                  # Current working directory
            os.path.dirname(os.getcwd()), # Parent directory
            os.path.dirname(os.path.abspath(sys.argv[0])), # Executable directory for Windows exe support
        ]
        
        for path in paths:
            env_path = os.path.join(path, '.env')
            if os.path.exists(env_path):
                dotenv.load_dotenv(env_path)
                break
        
        # Accept all environment variables starting with API_ as API keys
        for key, value in os.environ.items():
            if key.startswith('API_KEY_') and value:
                self._api_keys.append(value)
                self._key_names[value] = key  # Store variable name for this key
                self._usage_stats[value] = 0
                self._rate_limits[value] = []
    
    def load_env_file(self, env_path: str) -> bool:
        """
        Loads API keys from the specified .env file location.
        
        Args:
            env_path: Path to the .env file
            
        Returns:
            bool: True if the file was loaded successfully, False otherwise
        """
        if not os.path.exists(env_path):
            return False
            
        # Load the .env file
        dotenv.load_dotenv(env_path)
        
        # Clear existing keys
        self._api_keys = []
        self._key_names = {}
        self._usage_stats = {}
        self._rate_limits = {}
        self._current_key_index = 0
        
        # Load all API keys from environment
        for key, value in os.environ.items():
            if key.startswith('API_KEY_') and value:
                self._api_keys.append(value)
                self._key_names[value] = key  # Store variable name for this key
                self._usage_stats[value] = 0
                self._rate_limits[value] = []
                
        return True
    
    def _get_available_key(self, time_window: int, max_uses: int) -> str:
        """
        Gets an available API key that hasn't reached its rate limit.
        
        Args:
            time_window: Time window (seconds)
            max_uses: Maximum number of uses in this time window
            
        Returns:
            An available API key
            
        Raises:
            RateLimitExceeded: When all keys have exceeded their rate limit
        """
        if not self._api_keys:
            raise ValueError("No API keys found. Add keys starting with API_ to your .env file.")
        
        # Save these values for hit() to use later
        self._time_window = time_window
        self._max_uses = max_uses
        
        now = datetime.now()
        available_keys = []
        
        # Try keys starting from current index first
        reordered_keys = self._api_keys[self._current_key_index:] + self._api_keys[:self._current_key_index]
        
        for api_key in reordered_keys:
            # Clean up expired rate limit records
            self._rate_limits[api_key] = [
                timestamp for timestamp in self._rate_limits[api_key] 
                if now - timestamp < timedelta(seconds=time_window)
            ]
            
            # Check if the API key is within rate limit
            if len(self._rate_limits[api_key]) < max_uses:
                available_keys.append((api_key, len(self._rate_limits[api_key])))
        
        if not available_keys:
            raise RateLimitExceeded(f"All API keys have exceeded the usage limit of {max_uses} in {time_window} seconds.")
        
        # Choose the least used key
        available_keys.sort(key=lambda x: x[1])
        selected_key = available_keys[0][0]
        
        # Update current key index
        self._current_key_index = self._api_keys.index(selected_key)
        
        return selected_key
    
    def key(self, time_window: int = 60, max_uses: int = 100) -> str:
        """
        Returns an available API key.
        
        Args:
            time_window: Time window (seconds)
            max_uses: Maximum number of uses in this time window
            
        Returns:
            An available API key
            
        Raises:
            RateLimitExceeded: When all keys have exceeded their rate limit
        """
        return self._get_available_key(time_window, max_uses)
    
    def hit(self, api_key: str) -> None:
        """
        Reports that an API key has been used and rotates to the next available key.
        
        Args:
            api_key: The API key that was used
        """
        if api_key not in self._api_keys:
            return
        
        # Update usage statistics
        self._usage_stats[api_key] += 1
        
        # Update rate limit status
        self._rate_limits[api_key].append(datetime.now())
        
        # Move to the next key index
        next_index = (self._api_keys.index(api_key) + 1) % len(self._api_keys)
        self._current_key_index = next_index
        
        # Pre-check if we need to prepare for the next key
        try:
            # This won't return the key, just validate that one is available for next call
            self._get_available_key(self._time_window, self._max_uses)
        except RateLimitExceeded:
            # We'll raise this on the next key() call, not during hit()
            pass
    
    def usage(self, key_index: Union[int, str] = None) -> Union[Dict[str, int], int]:
        """
        Returns usage statistics for API keys by their variable names.
        
        Args:
            key_index: Optional index or identifier to get usage for a specific key:
                      - None: returns all usage statistics (default)
                      - int: returns usage for the key at that index (0-based)
                      - "all": returns all usage statistics
        
        Returns:
            Usage count or dictionary of usage counts
        """
        # Create usage stats with variable names
        named_stats = {}
        for key, count in self._usage_stats.items():
            var_name = self._key_names.get(key, "UNKNOWN_KEY")
            named_stats[var_name] = count
        
        # Handle different key_index options
        if key_index is None or key_index == "all":
            return named_stats
        
        # If key_index is an integer, return usage for that specific key
        if isinstance(key_index, int):
            if key_index < 0 or key_index >= len(self._api_keys):
                raise IndexError(f"API key index out of range: {key_index}")
            api_key = self._api_keys[key_index]
            var_name = self._key_names.get(api_key, "UNKNOWN_KEY")
            return named_stats[var_name]
        
        # If key_index is a string and matches a key name, return its usage
        if isinstance(key_index, str) and key_index in named_stats:
            return named_stats[key_index]
        
        # Otherwise return all stats
        return named_stats
    
    def get_all_keys(self) -> List[str]:
        """
        Returns all API keys.
        
        Returns:
            List of API keys
        """
        return self._api_keys.copy()
    
    def get_key_names(self) -> Dict[str, str]:
        """
        Returns a mapping of API keys to their variable names.
        
        Returns:
            Dictionary mapping API key values to their variable names
        """
        return self._key_names.copy()
    
    def get_current_key_name(self) -> str:
        """
        Returns the variable name of the current API key.
        
        Returns:
            Variable name of the current API key (e.g., API_KEY_1)
        """
        if not self._api_keys:
            return None
        
        current_key = self._api_keys[self._current_key_index]
        return self._key_names.get(current_key, "UNKNOWN_KEY")

# Singleton instance
_apirotater = APIRotater()

# Public API
def key(time_window: int = 60, max_uses: int = 100) -> str:
    """Gets an API key."""
    return _apirotater.key(time_window, max_uses)

def hit(api_key: str) -> None:
    """
    Reports API key usage and rotates to the next available key.
    This ensures each call to key() after hit() will use a different key
    until all keys have been rotated through.
    """
    _apirotater.hit(api_key)

def usage(key_index: Union[int, str] = None) -> Union[Dict[str, int], int]:
    """
    Returns usage statistics for API keys.
    
    Args:
        key_index: Optional index or identifier to get usage for a specific key:
                  - None: returns all usage statistics (default)
                  - int: returns usage for the key at that index (0-based)
                  - "all": returns all usage statistics
    
    Returns:
        Usage count or dictionary of usage counts
    """
    return _apirotater.usage(key_index)

def get_all_keys() -> List[str]:
    """Lists all loaded API keys."""
    return _apirotater.get_all_keys()

def get_key_names() -> Dict[str, str]:
    """Returns a mapping of API keys to their variable names."""
    return _apirotater.get_key_names()

def get_current_key_name() -> str:
    """Returns the variable name of the current API key."""
    return _apirotater.get_current_key_name()

def load_env_file(env_path: str) -> bool:
    """
    Loads API keys from the specified .env file location.
    
    Args:
        env_path: Path to the .env file
        
    Returns:
        bool: True if the file was loaded successfully, False otherwise
    """
    return _apirotater.load_env_file(env_path) 