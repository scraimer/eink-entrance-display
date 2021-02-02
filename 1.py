# From https://learn.adafruit.com/adafruit-eink-display-breakouts/python-code

import digitalio
import busio
import board
from adafruit_epd.epd import Adafruit_EPD

spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
ecs = digitalio.DigitalInOut(board.CE0)
dc = digitalio.DigitalInOut(board.D22)
rst = digitalio.DigitalInOut(board.D27)
busy = digitalio.DigitalInOut(board.D17)
srcs = None

# For 2.13 tri-color
from adafruit_epd.il0373 import Adafruit_IL0373
display = Adafruit_IL0373(104, 212, spi, cs_pin=ecs, dc_pin=dc, sramcs_pin=srcs,
                          rst_pin=rst, busy_pin=busy)


display.fill(Adafruit_EPD.WHITE)

display.fill_rect(20, 20, 50, 60, Adafruit_EPD.RED)
display.hline(80, 30, 60, Adafruit_EPD.BLACK)
display.vline(80, 30, 60, Adafruit_EPD.BLACK)

display.display()

