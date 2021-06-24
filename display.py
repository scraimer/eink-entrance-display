#!/usr/bin/python3
# -*- coding:utf-8 -*-
import sys
import os
libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd7in5b_HD
import time
import traceback
from layout import make_image

logging.basicConfig(level=logging.DEBUG)

def display(image):
    try:
        epd = epd7in5b_HD.EPD()
        # TODO: assert that epd.height == 880 and epd.width == 528

        logging.info("init and Clear")
        epd.init()
        epd.Clear()

        epd.display(epd.getbuffer(image.black), epd.getbuffer(image.red))
        time.sleep(2)
        
        #logging.info("Clear...")
        #epd.init()
        #epd.Clear()

        logging.info("Goto Sleep...")
        epd.sleep()
        time.sleep(3)
        
        epd.Dev_exit()
        
    except IOError as e:
        logging.info(e)
        
    except KeyboardInterrupt:    
        logging.info("ctrl + c:")
        epd7in5b_HD.epdconfig.module_exit()
        exit()
 
def main():
    image = make_image()
    # XXX remove exit
    sys.exit(0)
    display(image)
        
if __name__ == "__main__":
    main()
