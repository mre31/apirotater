import os
import time
import dotenv
from typing import Dict, List, Tuple, Optional
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
        self._load_api_keys()
        self._initialized = True
    
    def _load_api_keys(self):
        """Loads API keys from .env files."""
        # Directories to check
        paths = [
            os.getcwd(),                  # Current working directory
            os.path.dirname(os.getcwd()), # Parent directory
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
        if not self._api_keys:
            raise ValueError("No API keys found. Add keys starting with API_ to your .env file.")
        
        now = datetime.now()
        available_keys = []
        
        for api_key in self._api_keys:
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
        return available_keys[0][0]
    
    def hit(self, api_key: str) -> None:
        """
        Reports that an API key has been used.
        
        Args:
            api_key: The API key that was used
        """
        if api_key not in self._api_keys:
            return
        
        # Update usage statistics
        self._usage_stats[api_key] += 1
        
        # Update rate limit status
        self._rate_limits[api_key].append(datetime.now())
    
    def usage(self) -> Dict[str, int]:
        """
        Returns usage statistics for API keys by their variable names.
        
        Returns:
            Usage counts for API keys, mapped by variable names (e.g., API_KEY_1)
        """
        # Return usage stats with variable names instead of actual keys
        named_stats = {}
        for key, count in self._usage_stats.items():
            var_name = self._key_names.get(key, "UNKNOWN_KEY")
            named_stats[var_name] = count
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

# Singleton instance
_apirotater = APIRotater()

# Public API
def key(time_window: int = 60, max_uses: int = 100) -> str:
    """Gets an API key."""
    return _apirotater.key(time_window, max_uses)

def hit(api_key: str) -> None:
    """Reports API key usage."""
    _apirotater.hit(api_key)

def usage() -> Dict[str, int]:
    """Returns usage statistics for all keys by their variable names."""
    return _apirotater.usage()

def get_all_keys() -> List[str]:
    """Lists all loaded API keys."""
    return _apirotater.get_all_keys()

def get_key_names() -> Dict[str, str]:
    """Returns a mapping of API keys to their variable names."""
    return _apirotater.get_key_names() 