from datetime import datetime
import json
import logging
from pathlib import Path
import requests

logging.basicConfig(level=logging.DEBUG)

CACHE_FILE = Path(__file__).parent / "display_cache.json"
CACHE_STATUS_URL = "http://10.5.1.20:8321/cache-status"
TIMESTAMP_FORMAT = "%Y%m%d-%H%M%S"


def load_cache_timestamp():
    """Load the last display update timestamp from cache file.
    
    Returns the timestamp string in format YYYYMMDD-HHMMSS, or None if file doesn't exist.
    """
    try:
        if CACHE_FILE.exists():
            with open(CACHE_FILE, 'r') as f:
                data = json.load(f)
                return data.get('last_updated_at')
    except Exception as e:
        logging.warning(f"Failed to load cache file: {e}")
    return None


def save_cache_timestamp():
    """Save the current timestamp to cache file."""
    try:
        now = datetime.now().strftime(TIMESTAMP_FORMAT)
        data = {'last_updated_at': now}
        with open(CACHE_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        logging.info(f"Cache timestamp updated to {now}")
    except Exception as e:
        logging.error(f"Failed to save cache file: {e}")


def should_update_display_and_update_timestamp():
    """Check if cache has been updated since last display run.
    
    Queries the cache-status endpoint with the last update timestamp.
    Updates the timestamp in cache file regardless of the result.
    
    Returns True if cache has been updated (display should run), False otherwise.
    On endpoint failure, returns False (skip display) to be safe.
    """
    last_timestamp = load_cache_timestamp()
    
    try:
        # Build the request URL with last update timestamp
        params = {}
        if last_timestamp:
            params['client_last_updated_at'] = last_timestamp
            url = f"{CACHE_STATUS_URL}?client_last_updated_at={last_timestamp}"
        else:
            # First run - no previous timestamp
            url = CACHE_STATUS_URL
            
        logging.info(f"Checking cache status: {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        # Check if any cache data needs updating
        cache_data = data.get('cache_data', {})
        cache_updated = any(
            item.get('client_should_update', False) 
            for item in cache_data.values()
        )
        
        logging.info(f"Cache status: updated={cache_updated}")
        
        # Update timestamp in cache file (always, regardless of cache status)
        save_cache_timestamp()
        
        return bool(cache_updated)
        
    except requests.RequestException as e:
        logging.error(f"Failed to check cache status: {e}")
        # Save timestamp anyway to record that we attempted to check
        save_cache_timestamp()
        # Return False to skip display update (safer than failing open)
        return False
    except Exception as e:
        logging.error(f"Unexpected error checking cache status: {e}")
        # Save timestamp anyway
        save_cache_timestamp()
        return False

if __name__ == "__main__":
    if should_update_display_and_update_timestamp():
        logging.info("Cache updated - display should refresh")
    else:
        logging.info("Cache not updated - skipping display refresh")
