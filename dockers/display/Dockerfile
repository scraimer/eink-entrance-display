# You must use a SHA256 digest, since the platform is incorrectly marked as
# "linux/arm" instead of "linux/arm/v6".
FROM --platform=linux/arm alpine@sha256:096ebf69d65b5dcb3756fcfb053e6031a3935542f20cd7a8b7c59e1b3cb71558

RUN apk update

RUN apk update && apk --update add \
    py3-pip \
    ttf-dejavu \
    py3-pillow \
    && rm -rf /var/cache/apk/*

RUN pip3 install adafruit-circuitpython-epd

#RUN wget https://github.com/adafruit/Adafruit_CircuitPython_framebuf/raw/master/examples/font5x8.bin
#COPY font5x8.bin

# TODO: move this stuff up
RUN apk update 
RUN apk --update add \
	py3-rpigpio \
	bash

WORKDIR /root
