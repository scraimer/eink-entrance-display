# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportUnknownLambdaType=false
from dataclasses import dataclass
from enum import Enum
import logging
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageMath, ImageOps
import requests
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


def error_image(ex: Exception, stage:MakeImageStage) -> Image.Image:
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


def join_image(source_red:Image.Image, source_black:Image.Image) -> Image.Image:
    red_rgb: Image.Image = ImageMath.eval("convert(a,'RGB')", a=source_red) # type: ignore
    red_mask, _, _ = red_rgb.split()
    red_inverted = ImageOps.invert(red_rgb)
    red_r,red_g,red_b = red_inverted.split()
    #zero = ImageMath.eval("convert(band ^ band,'L')", band=red_g)

    black_r, black_g, black_b = (ImageMath.eval("convert(img,'RGB')", img=source_black)).split() # type: ignore

    out_r: Image.Image = ImageMath.eval("convert(red | black, 'L')", red=red_r, black=black_r, red_mask=red_mask) # type: ignore
    out_b: Image.Image = ImageMath.eval("convert((black & red_mask), 'L')", red=red_b, black=black_b, red_mask=red_mask) # type: ignore
    out_g: Image.Image = ImageMath.eval("convert((black & red_mask), 'L')", red=red_g, black=black_g, red_mask=red_mask) # type: ignore

    out: Image.Image = Image.merge("RGB", (out_r,out_b,out_g))
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
    #URL_BASE = "http://hinge-iot:8321/render/"
    URL_BASE = "http://10.5.1.20:8321/render/"
    url = URL_BASE + color
    logging.info(f"Rendering image: {url}")
    response = requests.get(url, timeout=10)
    response.raise_for_status()

def download_image(color:str) -> Image.Image:
    #URL_BASE = "http://hinge-iot:8321/eink/"
    URL_BASE = "http://10.5.1.20:8321/eink/"
    url = URL_BASE + color
    logging.info(f"Downloading image: {url}")
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    
    try:
        from io import BytesIO
        image_data = BytesIO(response.content)
        return Image.open(image_data)
    except Exception as e:
        # Log first 1000 bytes of response for debugging
        try:
            raw_data = response.content[:1000]
            # Escape binary data for readable logging using repr
            escaped_data = repr(raw_data)
            logging.error(f"Failed to open image from {url}: {e}")
            logging.error(f"First 1000 bytes of response: {escaped_data}")
        except Exception as log_ex:
            logging.error(f"Failed to log raw data: {log_ex}")
        raise


def make_image() -> EinkImage:
    stage = MakeImageStage.INITIALIZATION
    red_image = None
    black_image = None
    
    try:
        stage = MakeImageStage.RENDER
        logging.info("Rendering 'red'")
        render_image("red")
        logging.info("Rendering 'black'")
        render_image("black")

        stage = MakeImageStage.DOWNLOAD
        try:
            logging.info("Downloading red image")
            red_image = image_to_mono(download_image("red"))
            logging.info("Red image downloaded successfully")
        except Exception as ex:
            logging.error(f"Failed to download red image: {ex}")
            logging.error(traceback.format_exc())
            red_image = error_image(ex, stage)
        
        try:
            logging.info("Downloading black image")
            black_image = image_to_mono(download_image("black"))
            logging.info("Black image downloaded successfully")
        except Exception as ex:
            logging.error(f"Failed to download black image: {ex}")
            logging.error(traceback.format_exc())
            black_image = error_image(ex, stage)
        
        stage = MakeImageStage.AFTER_DOWNLOAD
        
    except Exception as ex:
        logging.error(f"Exception in make_image: {ex}")
        logging.error(traceback.format_exc())
        if red_image is None:
            red_image = error_image(ex, stage)
        if black_image is None:
            black_image = error_image(ex, stage)
    
    out = EinkImage(red=red_image, black=black_image)

    # XXX: Debug, save to file
    # color_image = join_image(source_black=black_image, source_red=red_image)
    # color_image.save("color.png")

    return out

if __name__ == "__main__":
    make_image()

