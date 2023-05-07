import datetime
from dataclasses import dataclass
from enum import Enum
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageColor, ImageMath, ImageOps
import requests
import sys
from textwrap import wrap
import traceback

   
EINK_WIDTH = 528
EINK_HEIGHT = 880
FONTDIR = Path(os.path.dirname(os.path.realpath(__file__)))


class MakeImageStage(Enum):
    INITIALIZATION = 1
    RENDER = 2
    DOWNLOAD = 3
    AFTER_DOWNLOAD = 4


def error_image(ex: Exception, stage:MakeImageStage) -> Image:
    font = ImageFont.truetype(str(FONTDIR / 'arial.ttf'), 50)
    image = Image.new('1', (EINK_WIDTH, EINK_HEIGHT), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(image)
    msg_raw = f"Error during stage {stage}: {ex}"
    msg = "\n".join(wrap(msg_raw, width=60))
    box = font.getbbox(msg)
    x = 20
    y = 20
    draw.text((x, y), msg, fill=0)
    return image


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

def render_image(color:str):
    URL_BASE = "http://hinge-iot:8321/render/"
    URL_BASE = "http://10.5.1.20:8321/render/"
    requests.get(URL_BASE + color)

def download_image(color:str) -> Image.Image:
    URL_BASE = "http://hinge-iot:8321/eink/"
    URL_BASE = "http://10.5.1.20:8321/eink/"
    return Image.open(requests.get(URL_BASE + color, stream=True).raw)


def make_image() -> EinkImage:
    stage = MakeImageStage.INITIALIZATION
    try:
        stage = MakeImageStage.RENDER
        print("Rendering 'red'")
        render_image("red")
        print("Rendering 'black'")
        render_image("black")

        stage = MakeImageStage.DOWNLOAD
        red_image = image_to_mono(download_image("red"))
        black_image = image_to_mono(download_image("black"))
        stage = MakeImageStage.AFTER_DOWNLOAD
    except Exception as ex:
        traceback.print_exc()
        red_image = error_image(ex, stage)
        black_image = error_image(ex, stage)
    out = EinkImage(red=red_image, black=black_image)

    # XXX: Debug, save to file
    color_image = join_image(source_black=black_image, source_red=red_image)
    color_image.save("color.png")

    return out

if __name__ == "__main__":
    make_image()

