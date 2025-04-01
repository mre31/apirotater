import unittest
import os
import time
from datetime import datetime, timedelta
import sys
import importlib

# Add package path first
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import module
import apirotater
from apirotater.core import APIRotater, RateLimitExceeded

class TestAPIRotater(unittest.TestCase):
    
    def setUp(self):
        # Clear environment variables and add test keys
        for key in list(os.environ.keys()):
            if key.startswith('API_'):
                del os.environ[key]
        
        # Set test API keys
        os.environ["API_KEY_1"] = "test_api_key_1"
        os.environ["API_KEY_2"] = "test_api_key_2"
        os.environ["API_KEY_3"] = "test_api_key_3"
        
        # Restart APIRotater class
        importlib.reload(apirotater)
        
        # Reset APIRotater singleton (for testing)
        APIRotater._instance = None
    
    def test_key_loading(self):
        """Check that API keys are loaded correctly."""
        keys = apirotater.get_all_keys()
        self.assertEqual(len(keys), 3)
        self.assertIn("test_api_key_1", keys)
        self.assertIn("test_api_key_2", keys)
        self.assertIn("test_api_key_3", keys)
    
    def test_key_rotation(self):
        """Check that keys are used in rotation."""
        # Use first key
        key1 = apirotater.key()
        apirotater.hit(key1)
        
        # Use second key (should be different)
        key2 = apirotater.key()
        self.assertNotEqual(key1, key2)
        apirotater.hit(key2)
        
        # Use third key (should be different)
        key3 = apirotater.key()
        self.assertNotEqual(key1, key3)
        self.assertNotEqual(key2, key3)
    
    def test_usage_stats(self):
        """Check that usage statistics are tracked correctly."""
        # Use first key
        key1 = apirotater.key()
        apirotater.hit(key1)
        apirotater.hit(key1)
        
        # Use second key
        key2 = apirotater.key()
        apirotater.hit(key2)
        
        # Check statistics
        usage = apirotater.usage()
        self.assertEqual(usage[key1], 2)
        self.assertEqual(usage[key2], 1)
        self.assertEqual(usage["test_api_key_3"], 0)
    
    def test_rate_limit(self):
        """Check that rate limit control works."""
        # Set a low rate limit
        time_window = 2
        max_uses = 1
        
        # Use first key
        key1 = apirotater.key(time_window=time_window, max_uses=max_uses)
        apirotater.hit(key1)
        
        # When requesting again, should get a different key
        key2 = apirotater.key(time_window=time_window, max_uses=max_uses)
        self.assertNotEqual(key1, key2)
        apirotater.hit(key2)
        
        # When requesting again, should get a 3rd key
        key3 = apirotater.key(time_window=time_window, max_uses=max_uses)
        self.assertNotEqual(key1, key3)
        self.assertNotEqual(key2, key3)
        apirotater.hit(key3)
        
        # When all keys are used, should throw RateLimitExceeded
        with self.assertRaises(RateLimitExceeded):
            key4 = apirotater.key(time_window=time_window, max_uses=max_uses)
        
        # After time window passes, keys should be usable again
        time.sleep(time_window + 0.1)  # Pass the time window
        
        # Now should be able to get a key
        try:
            key4 = apirotater.key(time_window=time_window, max_uses=max_uses)
        except RateLimitExceeded:
            self.fail("RateLimitExceeded exception thrown even though time window has passed")

if __name__ == '__main__':
    unittest.main() 