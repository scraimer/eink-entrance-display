
import sys
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageColor, ImageMath, ImageOps
from urllib.parse import unquote, quote
from types import SimpleNamespace
import scrape
from pathlib import Path

titles_to_remove = [
    unquote('%D7%94%D7%A6%D7%92%D7%AA%20%D7%99%D7%9C%D7%93%D7%99%D7%9D'),
    unquote('%D7%A9%D7%99%D7%A2%D7%95%D7%A8%20%D7%9C%D7%9E%D7%91%D7%95%D7%92%D7%A8%D7%99%D7%9D'),
]

picdir = Path(os.path.dirname(os.path.realpath(__file__))) / 'pic'

def reverse(source:str):
    return source[::-1]

def paste_red_and_black_image(name:str, red_image:Image, black_image:Image, position):
    with Image.open(picdir / f"{name}-red.png") as im:
        red_image.paste(im, position)
    with Image.open(picdir / f"{name}-black.png") as im:
        black_image.paste(im, position)

def create_erev_shabbat_image(width:int, height:int):
    font_title = ImageFont.truetype(str(picdir / 'arial.ttf'), 54)
    font_text = ImageFont.truetype(str(picdir / 'arial.ttf'), 40)
    weather_font = ImageFont.truetype(str(picdir / 'Pe-icon-7-weather.ttf'),128)

    # create a single color image with black and red and white

    red_image = Image.new('1', (width, height), 255)  # 255: clear the frame
    red_draw = ImageDraw.Draw(red_image)
    black_image = Image.new('1', (width, height), 255)  # 255: clear the frame
    black_draw = ImageDraw.Draw(black_image)

    with Image.open(picdir / "black-white-landscape-5.jpg") as im:
        black_image.paste(im, (0,int(height/2)))

    weather_sunny_icon = unquote("%EE%98%8C%0A")
    red_draw.text((432, 700), weather_sunny_icon, font = weather_font, fill=0)

    y = -15
    x = 0
    LINE_SPACING = 3

    lines = []
    shabbat_items = scrape.scrape_shabbat_items()
    lines.append({
        "font":font_title,
        "text":reverse(shabbat_items['parasha_name']),
        "center": True,
        "bottom-margin": LINE_SPACING * 3
    })
    for title,times in shabbat_items['times'].items():
        if title in titles_to_remove:
            continue
        times = [t if t[-3]==':' else reverse(t) for t in times]
        lines.append({"font":font_text, "text": f"{', '.join(sorted(times, reverse=True))} :{reverse(title)}"})

    boxes = [line["font"].getbbox(line["text"]) for line in lines]
    max_line_height = max([box[3] - box[1] for box in boxes])

    for line in lines:
        box = line["font"].getbbox(line["text"])
        if line.get("center", False):
            actual_x = (width - box[2]) / 2 - x
        else:
            actual_x = width - x - box[2]
        red_draw.text((actual_x, y), line["text"], font = line["font"], fill=0)
        y = y + max_line_height + LINE_SPACING
        if line.get("bottom-margin", False):
            y = y + line["bottom-margin"]

    #draw_red.line((10, 90, 60, 140), fill = 0)
    #draw_red.line((60, 90, 10, 140), fill = 0)
    #draw_red.rectangle((10, 90, 60, 500), outline = 0)
    #draw_red.line((95, 90, 95, 140), fill = 0)
    #draw_black.line((70, 115, 120, 115), fill = 0)
    #draw_black.arc((70, 90, 120, 140), 0, 360, fill = 0)
    #draw_black.rectangle((10, 150, 60, 200), fill = 0)
    #draw_black.chord((70, 150, 120, 200), 0, 360, fill = 0)

    paste_red_and_black_image(name="sneaker", red_image=red_image, black_image=black_image, position=(30,height - 50))

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

def make_image():
    # Note: Image size is 528 width, and 880 height
    shabbat_image = create_erev_shabbat_image(width=528, height=880)
    color_image = join_image( source_black=shabbat_image.black, source_red=shabbat_image.red )

    # XXX: Debug, save to file
    color_image.save("color.png")

    return shabbat_image


