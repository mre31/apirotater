import apirotater
import time
import requests

def make_api_request(api_key):
    """Example API request function."""
    print(f"Making API request, using key: {api_key}")
    
    # A real API request could be made here
    # Example:
    # response = requests.get(
    #     "https://api.example.com/endpoint",
    #     headers={"Authorization": f"Bearer {api_key}"}
    # )
    
    # Report that API key has been used
    apirotater.hit(api_key)
    
    return "API request result"

def simple_example():
    """Basic usage example."""
    print("\n--- Basic Usage Example ---")
    
    # Get an API key
    api_key = apirotater.key()
    
    # Make API request
    result = make_api_request(api_key)
    
    # Show statistics
    print("Usage statistics:", apirotater.usage())
    print("All keys:", apirotater.get_all_keys())

def rate_limit_example():
    """Rate limit usage example."""
    print("\n--- Rate Limit Example ---")
    
    # Get a key with maximum 2 uses in 5 seconds
    time_window = 5
    max_uses = 2
    
    print(f"Rate limit: {max_uses} uses in {time_window} seconds")
    
    try:
        # Make 3 API requests (rate limit will be exceeded)
        for i in range(3):
            print(f"\nRequest {i+1}:")
            api_key = apirotater.key(time_window=time_window, max_uses=max_uses)
            result = make_api_request(api_key)
            print("Usage statistics:", apirotater.usage())
            
            # We're not waiting to simulate concurrent requests
    
    except apirotater.RateLimitExceeded as e:
        print(f"\nRate limit exceeded: {e}")
        print("Waiting...")
        time.sleep(time_window)
        
        # Try again after waiting
        print("\nNew request after waiting:")
        api_key = apirotater.key(time_window=time_window, max_uses=max_uses)
        result = make_api_request(api_key)
        print("Usage statistics:", apirotater.usage())

if __name__ == "__main__":
    # Don't forget to add your keys to the .env file
    # API_KEY_1=your_api_key_1
    # API_KEY_2=your_api_key_2
    
    # Example: Create .env file (remove this part in real usage)
    if apirotater.get_all_keys() == []:
        print("Creating temporary API keys for example...")
        import os
        os.environ["API_KEY_1"] = "test_key_1"
        os.environ["API_KEY_2"] = "test_key_2"
        # Restart APIRotater class
        import importlib
        importlib.reload(apirotater)
    
    # Run example scenarios
    simple_example()
    rate_limit_example() 