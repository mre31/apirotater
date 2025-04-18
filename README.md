# APIRotater

APIRotater is a Python library that helps you manage your API keys and control rate limits. By managing multiple API keys, it automatically performs key rotation in case of rate limit exceedance.

## Key Features

- **Automatic API Key Rotation:** Uses multiple API keys in rotation.
- **Rate Limit Control:** You can set a maximum number of uses for each API key within a specific time window.
- **Automatic .env File Loading:** Automatically loads API keys from .env files located in the current working directory or parent directory.
- **Usage Statistics:** Tracks usage counts of API keys by variable names.
- **RateLimitExceeded Exception:** Throws an error when all keys have exceeded their rate limit.

## Installation

```bash
pip install apirotater
```

## Usage

Define your API keys in a `.env` file as follows:

```
API_KEY_1=your_api_key_1
API_KEY_2=your_api_key_2
API_KEY_3=your_api_key_3
```

### Basic Usage

```python
import apirotater

# Get an API key
api_key = apirotater.key()

# Make API request
# ...

# Report API key usage
apirotater.hit(api_key)

# Next time you call key(), it will automatically use a different key
next_api_key = apirotater.key()  # This will be a different key due to rotation
```

### Automatic Key Rotation

APIRotater automatically rotates through your API keys to ensure even distribution and avoid rate limit issues:

1. When you call `key()`, it returns the most suitable key based on current usage
2. After you call `hit(api_key)`, the library automatically moves to the next key
3. The next `key()` call will use a different key, maintaining rotation
4. If a key has reached its rate limit, it will be skipped automatically


### Usage With Rate Limit

```python
import apirotater

# Get a key with maximum 2 uses in 60 seconds
api_key = apirotater.key(time_window=60, max_uses=2)

# Make API request
# ...

# Report API key usage - this also rotates to the next key
apirotater.hit(api_key)
```

### Manuel Olarak .env Dosyasının Konumunu Belirtme

Uygulamanızı .exe olarak paketlediğinizde veya farklı bir konumda .env dosyanız bulunduğunda, dosya yolunu manuel olarak belirtebilirsiniz:

```python
import apirotater

# .env dosyasının konumunu belirt
env_path = "C:/path/to/your/.env"
apirotater.load_env_file(env_path)

# Sonra normal şekilde kullan
api_key = apirotater.key()
```

### Handling Rate Limit Exceedance

```python
import apirotater
import time

try:
    # Get a key with rate limit
    api_key = apirotater.key(time_window=60, max_uses=2)
    
    # Make API request
    # ...
    
    # Report API key usage
    apirotater.hit(api_key)
    
except apirotater.RateLimitExceeded as e:
    print(f"Rate limit exceeded: {e}")
    # Wait for a while and try again
    time.sleep(60)
```

### Checking Usage Statistics

```python
import apirotater

# Get and use an API key
api_key = apirotater.key()
apirotater.hit(api_key)

# Get all usage statistics (returns a dictionary with API_KEY_* names)
all_stats = apirotater.usage()
print(all_stats)  # {'API_KEY_1': 1, 'API_KEY_2': 0, ...}

# Get usage for a specific key by index (0-based)
first_key_usage = apirotater.usage(0)
print(first_key_usage)  # 1

# Get usage for a specific key by name
usage_of_key1 = apirotater.usage("API_KEY_1")
print(usage_of_key1)  # 1

# Alternative way to get all statistics
all_stats_alt = apirotater.usage("all")
print(all_stats_alt)  # {'API_KEY_1': 1, 'API_KEY_2': 0, ...}

# Check the current key being used
current_key = apirotater.get_current_key_name()
print(f"Current key: {current_key}")  # Current key: API_KEY_2
```

## API

- `key(time_window=60, max_uses=100)`: Gets an API key (with rate limit)
- `hit(api_key)`: Reports API key usage and rotates to the next key in sequence
- `usage(key_index=None)`: Returns usage statistics:
  - `usage()` or `usage("all")`: All keys' usage statistics
  - `usage(0)`, `usage(1)`, etc.: Usage of a specific key by index
  - `usage("API_KEY_1")`: Usage of a specific key by name
- `get_all_keys()`: Lists all loaded API keys
- `get_key_names()`: Returns a mapping of API keys to their variable names
- `get_current_key_name()`: Returns the variable name of the currently selected API key

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
