import logging
import sys
import traceback
from pathlib import Path

import display
import layout
import decide_to_update


def _setup_logging():
    """Configure logging to write to both console and log file."""
    log_file = Path(__file__).parent / "eink_display.log"
    
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    # Remove any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    logging.info(f"Logging configured. Log file: {log_file}")


def main():
    _setup_logging()
    logging.info("")
    logging.info("-----------------------------------------------")
    logging.info("Logging started.")
    try:
        if decide_to_update.should_update_display_and_update_timestamp():
            logging.info("Cache updated - generating and displaying image")
            image = layout.make_image()
            display.display(image)
            if (image.is_red_an_error_image or image.is_black_an_error_image):
                logging.warning("Displayed image contains error image(s) - not updating timestamp")
            else:
                decide_to_update.on_successful_update()
        else:
            logging.info("Cache not updated - skipping display refresh")
    except Exception as e:
        logging.error(f"Uncaught exception occurred: {e}")
        logging.error(traceback.format_exc())
        raise
        
if __name__ == "__main__":
    main()
