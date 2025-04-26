# APIRotater

A simple Python library that automatically manages and rotates multiple API keys to prevent rate limit issues.

## What It Does

- **Automatically rotates between multiple API keys** so you don't hit rate limits
- **Tracks usage** of each API key
- **Manages rate limits** by specifying max uses in a time window
- **Loads API keys from .env files** in current directory, parent directory, or executable location
- **Works with Windows EXE applications** when packaged

## Installation

```bash
pip install apirotater
```

## Quick Start

### 1. Create a .env file with your API keys

```
API_KEY_1=your_first_api_key
API_KEY_2=your_second_api_key
API_KEY_3=your_third_api_key
```

### 2. Use in your code

```python
import apirotater

# Get an API key
api_key = apirotater.key()

# Use the API key for your request
response = make_your_api_request(api_key)

# IMPORTANT: Always report when you've used a key
apirotater.hit(api_key)
```

## Basic Example

```python
import apirotater
import time

# Simple usage loop
for _ in range(10):
    # Get a new API key (rotates automatically)
    api_key = apirotater.key()
    
    # Use the key for your API request
    print(f"Making request with key: {api_key}")
    
    # IMPORTANT: Report that you used the key
    apirotater.hit(api_key)
    
    # Wait before next request
    time.sleep(1)
```

## Rate Limiting

```python
import apirotater

# Get a key with maximum 5 uses in 60 seconds
api_key = apirotater.key(time_window=60, max_uses=5)

# Use the key
print(f"Using key: {api_key}")

# Report usage
apirotater.hit(api_key)
```

## Custom .env File Location

For Windows EXE applications or custom setups, you can specify the .env file location:

```python
import apirotater
import os
import sys

# For regular applications - use current directory
env_path = os.path.join(os.getcwd(), ".env")

# For Windows EXE applications - use executable directory
# env_path = os.path.dirname(os.path.abspath(sys.argv[0]))

# Load API keys from specific location
apirotater.load_env_file(env_path)

# Then use normally
api_key = apirotater.key()
```

## API Reference

- `key(time_window=60, max_uses=100)` - Get an API key
- `hit(api_key)` - Report that you've used an API key (ALWAYS call this)
- `load_env_file(path)` - Load API keys from a specific .env file
- `usage()` - Get usage statistics for all keys
- `get_all_keys()` - Get a list of all loaded API keys
- `get_current_key_name()` - Get the name of the current API key

## Error Handling

```python
import apirotater
import time

try:
    api_key = apirotater.key()
    # Use the key...
    apirotater.hit(api_key)
except apirotater.RateLimitExceeded:
    # All keys exceeded rate limits
    print("All API keys reached rate limit")
    time.sleep(60)  # Wait and try again
```

## License

MIT License

Copyright (c) 2025 APIRotater

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
