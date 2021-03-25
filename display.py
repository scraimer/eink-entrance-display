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
from PIL import Image,ImageDraw,ImageFont, ImageFilter
import traceback
from urllib.parse import unquote 

logging.basicConfig(level=logging.DEBUG)

def create_erev_shabbat_image(out_width, out_height):
    font24 = ImageFont.truetype(os.path.join(picdir, 'arial.ttf'), 24)
    font18 = ImageFont.truetype(os.path.join(picdir, 'arial.ttf'), 18)
    weather_font = ImageFont.truetype(os.path.join(picdir, 'Pe-icon-7-weather.ttf'),128)
    
    # Note: Image size is 528 width, and 880 height

    image_black = Image.new('1', (out_height, out_width), 255)  # 255: clear the frame
    image_red = Image.new('1', (out_height, out_width), 255)  # 255: clear the frame
    draw_black = ImageDraw.Draw(image_black)
    draw_red = ImageDraw.Draw(image_red)
    
    #draw_black.text((2, 0), 'hello world', font = font18, fill = 0)
    #draw_black.text((2, 20), '7.5inch epd', font = font18, fill = 0)
    
    weather_sunny = unquote("%EE%98%8C%0A")
    draw_red.text((2, 0), weather_sunny, font = weather_font)
    
    #hebrew_text = unquote("%D7%A9%D7%91%D7%AA%20%D7%A9%D7%9C%D7%95%D7%9D%21")
    #draw_red.text((20, 50), hebrew_text, font = font18, fill = 0)
    #draw_red.text((20, 50), hebrew_text, font = font18, fill = 0, direction = "rtl")
    
    #draw_red.line((10, 90, 60, 140), fill = 0)
    #draw_red.line((60, 90, 10, 140), fill = 0)
    #draw_red.rectangle((10, 90, 60, 500), outline = 0)
    #draw_red.line((95, 90, 95, 140), fill = 0)
    #draw_black.line((70, 115, 120, 115), fill = 0)
    #draw_black.arc((70, 90, 120, 140), 0, 360, fill = 0)
    #draw_black.rectangle((10, 150, 60, 200), fill = 0)
    #draw_black.chord((70, 150, 120, 200), 0, 360, fill = 0)
    
    with Image.open(os.path.join(picdir,"black-white-landscape-5.jpg")) as im:
        image_black.paste(im)

    image_black.save("black.png")
    image_red.save("red.png")
    
    return (image_black, image_red)

try:
    image_black, image_red = create_erev_shabbat_image(880, 528);
    #sys.exit(1)
    
    epd = epd7in5b_HD.EPD()
    # TODO: assert that epd.height == 880 and epd.width == 528

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
