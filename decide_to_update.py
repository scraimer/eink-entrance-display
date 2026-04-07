from dataclasses import dataclass
from datetime import datetime, timezone
import json
import logging
from pathlib import Path
import requests

STATE_FILE = Path(__file__).parent / "display_state.json"
WHAT_HAS_CHANGED_URL = "http://10.5.1.20:8321/what-has-changed"
TIMESTAMP_FORMAT = "%Y%m%d-%H%M%S"
UNIX_EPOCH_TIMESTAMP = "19700101-000000"  # 1970-01-01 00:00:00


@dataclass
class MyState:
    last_updated_at: str
    data_relevance: dict[str, bool]

def _load_state() -> MyState:
    """Load state from file.
    
    Returns a MyState object with:
    - last_updated_at: timestamp string in format YYYYMMDD-HHMMSS (UTC)
    - data_relevance: dict mapping data source names to their is_relevant_to_display status
    
    If file doesn't exist, returns defaults with Unix epoch timestamp and empty relevance dict.
    """
    default_state = MyState(
        last_updated_at=UNIX_EPOCH_TIMESTAMP,
        data_relevance={}
    )
    try:
        if STATE_FILE.exists():
            with open(STATE_FILE, 'r') as f:
                data = json.load(f)
                return MyState(
                    last_updated_at=data.get('last_updated_at', UNIX_EPOCH_TIMESTAMP),
                    data_relevance=data.get('data_relevance', {})
                )
    except Exception as e:
        logging.warning(f"Failed to load state file: {e}")
    return default_state


def _save_state(state: MyState):
    """Save state including timestamp and data relevance tracking.
    
    Args:
        state: MyState object containing last_updated_at and data_relevance
    """
    try:
        now_utc = datetime.now(timezone.utc).strftime(TIMESTAMP_FORMAT)
        data = {
            'last_updated_at': now_utc,
            'timezone': 'UTC',
            'data_relevance': state.data_relevance
        }
        with open(STATE_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        logging.info(f"State updated at {now_utc} (UTC)")
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
    state = _load_state()
    last_timestamp = state.last_updated_at
    previous_relevance = state.data_relevance
    
    try:
        # Build the request URL with last update timestamp
        url = f"{WHAT_HAS_CHANGED_URL}?client_last_updated_at={last_timestamp}"
            
        logging.info(f"Checking what has changed: {url} (UTC)")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        changes = data.get('changes', {})
        
        # Extract current relevance status for all data sources
        current_relevance = {
            key: item.get('is_relevant_to_display', False)
            for key, item in changes.items()
        }
        
        # Check if any data source changed and is relevant
        has_changed_and_relevant = any(
            item.get('has_changed', False) and item.get('is_relevant_to_display', False)
            for item in changes.values()
        )
        
        # Check if any relevance switched from false to true
        relevance_switched_on = any(
            previous_relevance.get(key, False) == False and current_relevance[key] == True
            for key in current_relevance.keys()
        )
        
        should_update = has_changed_and_relevant or relevance_switched_on
        
        logging.info(f"Changes status: should_update={should_update}")
        logging.debug(f"  has_changed_and_relevant={has_changed_and_relevant}")
        logging.debug(f"  relevance_switched_on={relevance_switched_on}")
        if changes:
            for key, item in changes.items():
                prev_rel = previous_relevance.get(key, False)
                curr_rel = item.get('is_relevant_to_display', False)
                switched = "*" if (prev_rel == False and curr_rel == True) else ""
                logging.debug(f"  {key}: changed={item.get('has_changed')}, relevant={curr_rel} (was {prev_rel}){switched}")
        
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
    
    Updates the state file with current timestamp and data relevance tracking.
    """
    try:
        # Fetch current data to store relevance status
        state = _load_state()
        last_timestamp = state.last_updated_at
        url = f"{WHAT_HAS_CHANGED_URL}?client_last_updated_at={last_timestamp}"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        changes = data.get('changes', {})
        current_relevance = {
            key: item.get('is_relevant_to_display', False)
            for key, item in changes.items()
        }
        
        _save_state(MyState(last_updated_at=datetime.now(timezone.utc).strftime(TIMESTAMP_FORMAT), data_relevance=current_relevance))
    except Exception as e:
        logging.error(f"Failed to update state on successful display update: {e}")
        # Still save state even if we can't fetch updates
        _save_state(MyState(last_updated_at=datetime.now(timezone.utc).strftime(TIMESTAMP_FORMAT), data_relevance={}))

if __name__ == "__main__":
    if should_update_display_and_update_timestamp():
        logging.info("Decision: Yes. Display should refresh")
        on_successful_update()
    else:
        logging.info("Decision: No. Skipping display refresh")
