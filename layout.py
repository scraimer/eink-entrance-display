
import sys
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageColor, ImageMath, ImageOps
from urllib.parse import unquote, quote
from types import SimpleNamespace


picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pic')

class Shabbat:
    def __init__(self):
        # TODO: read this data
        self.parasha_name = quote("פנחס")
        self.early_shabbat = "18:00"
        self.candle_lighting = "19:34"
        self.mincha = "19:44"
        self.shacharit = ["8:30", "6:45"]
        self.shabbat_end = "20:31"

def reverse(source:str):
    return source[::-1]

def create_erev_shabbat_image(width:int, height:int, data:Shabbat):
    font_title = ImageFont.truetype(os.path.join(picdir, 'arial.ttf'), 54)
    font_text = ImageFont.truetype(os.path.join(picdir, 'arial.ttf'), 40)
    weather_font = ImageFont.truetype(os.path.join(picdir, 'Pe-icon-7-weather.ttf'),128)
    
    # create a single color image with black and red and white

    red_image = Image.new('1', (width, height), 255)  # 255: clear the frame
    red_draw = ImageDraw.Draw(red_image)
    black_image = Image.new('1', (width, height), 255)  # 255: clear the frame
    black_draw = ImageDraw.Draw(black_image)
    
    with Image.open(os.path.join(picdir,"black-white-landscape-5.jpg")) as im:
        black_image.paste(im, (0,int(height/2)))
    
    #draw_black.text((2, 0), 'hello world', font = font_text, fill = 0)
    #draw_black.text((2, 20), '7.5inch epd', font = font_text, fill = 0)
    
    weather_sunny_icon = unquote("%EE%98%8C%0A")
    red_draw.text((432, 700), weather_sunny_icon, font = weather_font, fill=0)
    
    y = 50
    x = 20
    
    hebrew_text = reverse(unquote("%D7%A4%D7%A8%D7%A9%D7%AA") + " " + unquote(data.parasha_name))
    red_draw.text((x, y), hebrew_text, font = font_title, fill=0)
    box = font_title.getbbox(hebrew_text)
    y = y + box[3]

    hebrew_text = data.early_shabbat + " " + reverse(unquote("%D7%A7%D7%91%D7%9C%D7%AA %D7%A9%D7%91%D7%AA %D7%9E%D7%95%D7%A7%D7%93%D7%9E%D7%AA:"))
    red_draw.text((x, y), hebrew_text, font = font_text, fill=0)
    box = font_text.getbbox(hebrew_text)
    y = y + box[3]
    
    hebrew_text =  data.candle_lighting + " " + reverse(unquote("%D7%94%D7%93%D7%9C%D7%A7%D7%AA%20%D7%A0%D7%A8%D7%95%D7%AA"))
    red_draw.text((x, y), hebrew_text, font = font_text, fill=0)
    box = font_text.getbbox(hebrew_text)
    y = y + box[3]
    
    hebrew_text = data.shabbat_end + " " + reverse(unquote("%D7%A2%D7%A8%D7%91%D7%99%D7%AA:"))
    red_draw.text((x, y), hebrew_text, font = font_text, fill=0)
    

    #draw_red.text((20, 50), hebrew_text, font = font_text, fill = 0, direction = "rtl")
    
    #draw_red.line((10, 90, 60, 140), fill = 0)
    #draw_red.line((60, 90, 10, 140), fill = 0)
    #draw_red.rectangle((10, 90, 60, 500), outline = 0)
    #draw_red.line((95, 90, 95, 140), fill = 0)
    #draw_black.line((70, 115, 120, 115), fill = 0)
    #draw_black.arc((70, 90, 120, 140), 0, 360, fill = 0)
    #draw_black.rectangle((10, 150, 60, 200), fill = 0)
    #draw_black.chord((70, 150, 120, 200), 0, 360, fill = 0)
    
    return SimpleNamespace(red=red_image, black=black_image)

def join_image(source_red:Image, source_black:Image):
    red_rgb = ImageMath.eval("convert(a,'RGB')", a=source_red)
    red_mask, _, _ = red_rgb.split()
    red_inverted = ImageOps.invert(red_rgb)
    red_r,red_g,red_b = red_inverted.split()
    #zero = ImageMath.eval("convert(band ^ band,'L')", band=red_g)

    black_r, black_g, black_b = (ImageMath.eval("convert(img,'RGB')", img=source_black)).split()

    out_r = ImageMath.eval("convert(red | black, 'L')", red=red_r, black=black_r, red_mask=red_mask)
    out_b = ImageMath.eval("convert((black & red_mask), 'L')", red=red_b, black=black_b, red_mask=red_mask)
    out_g = ImageMath.eval("convert((black & red_mask), 'L')", red=red_g, black=black_g, red_mask=red_mask)

    out = Image.merge("RGB", (out_r,out_b,out_g))
    return out

def join_image_slow(source_red:Image, source_black:Image):
    width, height = source_red.size
    
    color_red = ImageColor.getrgb("red")
    color_black = ImageColor.getrgb("black")
    color_white = ImageColor.getrgb("white")
    out_image = Image.new('RGB', (width, height), color_white) # 255: clear the frame
    red_data = source_red.getdata()
    black_data = source_black.getdata()
    out_data = list(out_image.getdata())
    for i,px in enumerate(red_data):
        x = i % width
        y = int( i / width )
        percentage = (int((y*10000)/height)*1)/100
        if x == 0 and y % 10 == 0:
            print(f"line: {y} [{percentage}%]")
            
        if red_data[i] == 0:
            out_data[i] = color_red
        elif black_data[i] == 0:
            out_data[i] = color_black
        else:
            out_data[i] = color_white
            
    out_image.putdata( out_data )
    return out_image

def make_image():
    shabbat = Shabbat()
    # Note: Image size is 528 width, and 880 height
    
    shabbat_image = create_erev_shabbat_image(width=528, height=880, data=shabbat)
    
    # XXX: Debug, save to file
    shabbat_image.black.save("black.png")
    shabbat_image.red.save("red.png")
    
    color_image = join_image( source_black=shabbat_image.black, source_red=shabbat_image.red )
    
    # XXX
    # XXX: Debug, save to file
    color_image.save("color.png")
    
    return shabbat_image


