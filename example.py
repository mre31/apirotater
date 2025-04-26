import apirotater
import time

def make_request():
    """Basic usage example."""
    #This will demonstrate 10 requests to the api.
    for _ in range(10):
        api_key = apirotater.key()  # Get a new api key from the apirotater

        print(api_key)  # Use the api key to make a request. We will print the api key to the console for testing purposes.
        
        apirotater.hit(api_key)  # Report usage of the api key to the apirotater

        # Next api key will be a different one from the .env file you don't need to do anything with it.
        # Run this script and look at the output to see the api keys rotate.
        time.sleep(2)

        #if you want to use other functions you can check the documentation. Examples are still work in progress.

if __name__ == "__main__":
    make_request()