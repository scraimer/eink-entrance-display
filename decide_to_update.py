from datetime import datetime
import json
import logging
from pathlib import Path
import requests

logging.basicConfig(level=logging.DEBUG)

STATE_FILE = Path(__file__).parent / "display_state.json"
WHAT_HAS_CHANGED_URL = "http://10.5.1.20:8321/what-has-changed"
TIMESTAMP_FORMAT = "%Y%m%d-%H%M%S"
UNIX_EPOCH_TIMESTAMP = "19700101-000000"  # 1970-01-01 00:00:00


def _load_datetime_of_last_update():
    """Load the last display update timestamp from state file.
    
    Returns the timestamp string in format YYYYMMDD-HHMMSS.
    If file doesn't exist, returns Unix epoch (1970-01-01 00:00:00).
    """
    try:
        if STATE_FILE.exists():
            with open(STATE_FILE, 'r') as f:
                data = json.load(f)
                return data.get('last_updated_at', UNIX_EPOCH_TIMESTAMP)
    except Exception as e:
        logging.warning(f"Failed to load state file: {e}")
    return UNIX_EPOCH_TIMESTAMP


def _save_datetime_of_last_update():
    """Save the current timestamp to state file."""
    try:
        now = datetime.now().strftime(TIMESTAMP_FORMAT)
        data = {'last_updated_at': now}
        with open(STATE_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        logging.info(f"Last update timestamp updated to {now}")
    except Exception as e:
        logging.error(f"Failed to save state file: {e}")


def should_update_display_and_update_timestamp():
    """Check if relevant data has changed and warrants a display update.
    
    Queries the what-has-changed endpoint to get the status of all data sources.
    The display should update if any data source has both:
    - has_changed: true
    - is_relevant_to_display: true
    
    The timestamp is updated by calling on_successful_update() after display refresh.
    
    Returns True if display should update, False otherwise.
    On endpoint failure, returns False (skip display) to be safe.
    """
    last_timestamp = _load_datetime_of_last_update()
    
    try:
        # Build the request URL with last update timestamp
        params = {}
        params['client_last_updated_at'] = last_timestamp
        url = f"{WHAT_HAS_CHANGED_URL}?client_last_updated_at={last_timestamp}"
            
        logging.info(f"Checking what has changed: {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        # Check if any data source both changed AND is relevant to display
        changes = data.get('changes', {})
        should_update = any(
            item.get('has_changed', False) and item.get('is_relevant_to_display', False)
            for item in changes.values()
        )
        
        logging.info(f"Changes status: should_update={should_update}")
        if changes:
            for key, item in changes.items():
                logging.debug(f"  {key}: changed={item.get('has_changed')}, relevant={item.get('is_relevant_to_display')}")
        
        return bool(should_update)
        
    except requests.RequestException as e:
        logging.error(f"Failed to check what has changed: {e}")
        # Return False to skip display update (safer than failing open)
        return False
    except Exception as e:
        logging.error(f"Unexpected error checking what has changed: {e}")
        return False


def on_successful_update():
    """Called by main.py after a successful display update.
    
    Updates the timestamp in state file to record when display was last refreshed.
    """
    _save_datetime_of_last_update()

if __name__ == "__main__":
    if should_update_display_and_update_timestamp():
        logging.info("Decision: Yes. Display should refresh")
        on_successful_update()
    else:
        logging.info("Decision: No. Skipping display refresh")
