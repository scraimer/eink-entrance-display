import logging

import display
import layout
import decide_to_update

logging.basicConfig(level=logging.DEBUG)

def main():
    if decide_to_update.should_update_display_and_update_timestamp():
        logging.info("Cache updated - generating and displaying image")
        image = layout.make_image()
        display.display(image)
        decide_to_update.on_successful_update()
    else:
        logging.info("Cache not updated - skipping display refresh")
        
if __name__ == "__main__":
    main()
