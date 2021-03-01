#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pic')
libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd7in5b_HD
import time
from PIL import Image,ImageDraw,ImageFont
import traceback
from urllib.parse import unquote 

logging.basicConfig(level=logging.DEBUG)

def create_image():
    font24 = ImageFont.truetype(os.path.join(picdir, 'arial.ttf'), 24)
    font18 = ImageFont.truetype(os.path.join(picdir, 'arial.ttf'), 18)
    
    image_black = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
    image_red = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
    draw_black = ImageDraw.Draw(image_black)
    draw_red = ImageDraw.Draw(image_red)
    draw_black.text((2, 0), 'hello world', font = font18, fill = 0)
    draw_black.text((2, 20), '7.5inch epd', font = font18, fill = 0)
    hebrew_text = unquote("%D7%A9%D7%91%D7%AA%20%D7%A9%D7%9C%D7%95%D7%9D%21")
    #draw_red.text((20, 50), hebrew_text, font = font18, fill = 0, direction = "rtl")
    draw_red.text((20, 50), hebrew_text, font = font18, fill = 0)
    draw_red.line((10, 90, 60, 140), fill = 0)
    draw_red.line((60, 90, 10, 140), fill = 0)
    draw_red.rectangle((10, 90, 60, 140), outline = 0)
    draw_red.line((95, 90, 95, 140), fill = 0)
    draw_black.line((70, 115, 120, 115), fill = 0)
    draw_black.arc((70, 90, 120, 140), 0, 360, fill = 0)
    draw_black.rectangle((10, 150, 60, 200), fill = 0)
    draw_black.chord((70, 150, 120, 200), 0, 360, fill = 0)
    
    image_black.save("black.png")
    image_red.save("red.png")
    
    return (image_black, image_red)

try:
    logging.info("epd7in5b_HD Demo")

    epd = epd7in5b_HD.EPD()
    
    image_black, image_red = create_image();

    logging.info("init and Clear")
    epd.init()
    epd.Clear()

    epd.display(epd.getbuffer(image_black), epd.getbuffer(image_red))
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
