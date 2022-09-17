
import sys
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageColor, ImageMath, ImageOps
import datetime
from dataclasses import dataclass
import requests
   

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


@dataclass
class EinkImage:
    red : Image.Image
    black : Image.Image


def image_to_mono(src:Image.Image):
    THRESH = 200
    fn = lambda x : 255 if x > THRESH else 0
    return src.convert('L').point(fn, mode='1')

def download_image(url:str) -> Image.Image:
    return Image.open(requests.get(url, stream=True).raw)

def make_image() -> EinkImage:
    # TODO: trigger the image generation, then fetch it.
    URL_BASE = "http://hinge-iot:8321/eink/"
    SRC_URL_RED = URL_BASE + "red"
    SRC_URL_BLACK = URL_BASE + "black"
    red_image = image_to_mono(download_image(SRC_URL_RED))
    black_image = image_to_mono(download_image(SRC_URL_BLACK))
    out = EinkImage(red=red_image, black=black_image)

    # XXX: Debug, save to file
    color_image = join_image(source_black=black_image, source_red=red_image)
    color_image.save("color.png")

    return out

