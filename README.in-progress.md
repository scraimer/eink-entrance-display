# Usage

sudo python3 display.py


# Development Plan

1. Create an image with three colors: `black`, `red` and `white` (background)

2. Extract a "red" image of all the red pixels, and a "black" image of all the black pixel.

3. Write those images to the eInk display

## Image viewer

Use `mirage` to view images

## Notes

### Possible source for zmanim

https://www.hebcal.com/home/197/shabbat-times-rest-api

example:

	https://www.hebcal.com/shabbat?cfg=json&geonameid=283991&M=42

283991 = Geo ID of Efrat

https://www.hebcal.com/home/1663/zmanim-halachic-times-api

example:

	Friday: https://www.hebcal.com/zmanim?cfg=json&geonameid=283991&date=2021-06-11
	Shabbat: https://www.hebcal.com/zmanim?cfg=json&geonameid=283991&date=2021-06-12
