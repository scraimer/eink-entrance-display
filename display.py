#!/usr/bin/python3
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
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageColor
import traceback
from urllib.parse import unquote 

logging.basicConfig(level=logging.DEBUG)

class Shabbat:
    def __init__(self):
        # TODO: read this data
        self.parasha_name = "%D7%A7%D7%A8%D7%97"
        self.early_shabbat = "18:00"
        self.candle_lighting = "19:30"
        self.mincha = "19:40"
        self.shacharit = ["8:30", "6:45"]
        self.shabbat_end = "20:27"

def create_erev_shabbat_image(width:int, height:int, data:Shabbat):
    font24 = ImageFont.truetype(os.path.join(picdir, 'arial.ttf'), 24)
    font18 = ImageFont.truetype(os.path.join(picdir, 'arial.ttf'), 18)
    weather_font = ImageFont.truetype(os.path.join(picdir, 'Pe-icon-7-weather.ttf'),128)
    
    # create a single color image with black and red and white

    out = Image.new('RGB', (width, height), ImageColor.getrgb("white"))  # 255: clear the frame
    draw = ImageDraw.Draw(out)
    
    with Image.open(os.path.join(picdir,"black-white-landscape-5.jpg")) as im:
        out.paste(im)
    
    #draw_black.text((2, 0), 'hello world', font = font18, fill = 0)
    #draw_black.text((2, 20), '7.5inch epd', font = font18, fill = 0)
    
    red = ImageColor.getrgb("red")
    black = ImageColor.getrgb("black")

    weather_sunny_icon = unquote("%EE%98%8C%0A")
    draw.text((2, 0), weather_sunny_icon, font = weather_font, fill=red)
    
    hebrew_text = unquote("%D7%A7%D7%91%D7%9C%D7%AA+%D7%A9%D7%91%D7%AA+%D7%9E%D7%95%D7%A7%D7%93%D7%9E%D7%AA:" + " 17:50")
    draw.text((20, 50), hebrew_text, font = font18, fill=red)
    #draw_red.text((20, 50), hebrew_text, font = font18, fill = 0, direction = "rtl")
    
    #draw_red.line((10, 90, 60, 140), fill = 0)
    #draw_red.line((60, 90, 10, 140), fill = 0)
    #draw_red.rectangle((10, 90, 60, 500), outline = 0)
    #draw_red.line((95, 90, 95, 140), fill = 0)
    #draw_black.line((70, 115, 120, 115), fill = 0)
    #draw_black.arc((70, 90, 120, 140), 0, 360, fill = 0)
    #draw_black.rectangle((10, 150, 60, 200), fill = 0)
    #draw_black.chord((70, 150, 120, 200), 0, 360, fill = 0)
    
    return out

def extract_red_and_black(source:Image):
    width, height = source.size
    
    color_red = ImageColor.getrgb("red")
    color_black = ImageColor.getrgb("black")
    red = Image.new('1', (width, height), 255) # 255: clear the frame
    black = Image.new('1', (width, height), 255) # 255: clear the frame
    for i,px in enumerate(source.getdata()):
        #print(px)
        x = i % width
        y = int( i / width )
        percentage = (int((y*10000)/height)*1)/100
        if x == 0:
            print(f"line: {y} [{percentage}%]")
        if px == color_red:
            red.putpixel(xy=(x, y), value=0)
            #black.putpixel(xy=(x, y), value=1)
        elif px == color_black:
            black.putpixel(xy=(x, y), value=0)
            #red.putpixel(xy=(x, y), value=1)
        #else:
        #    black.putpixel(xy=(x, y), value=1)
        #    red.putpixel(xy=(x, y), value=1)
    return red, black

try:
    shabbat = Shabbat()
    # Note: Image size is 528 width, and 880 height
    
    shabbat_image = create_erev_shabbat_image(width=528, height=880, data=shabbat);
    
    # XXX: Debug, save to file
    shabbat_image.save("color.png")
    
    image_black, image_red = extract_red_and_black(source=shabbat_image)
    
    # XXX: Debug, save to file
    image_black.save("black.png")
    image_red.save("red.png")
    
    # XXX
    sys.exit(1)
    
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
