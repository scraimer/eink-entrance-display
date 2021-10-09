# eink-entrance-display
Show information of interest to the whole family on an eInk display near the entrance

# Usage

1. Build the dockers

     cd dockers
     ./build.sh

2. Run the dockers

     ./run.sh

# Plan for display

Have different display formats:

- Chol
- Erev Shabbat / Erev Yom Tov
- Shabbat (switch as soon as shabbat comes in, but still show shabbat time)

I want to see:

- Weather forcast (can I put hourly? Or summarize interesting events during the day? Like when it might rain, or when it will be sunny, and the temperatures)
- Zmanim: Shabbat/Yom Tov entrance, exit time, shul times (shachrit(s))
- Next events from a Google Calendar that me and Miriam Malka can edit (e.g. next zoom lesson, etc)
- Maybe a tiny clock with the time of the last update

Data collection:

Collect data with one process, that updates each segment at a relevant frequency (zmanim, update once a day. Weather, 4 times a day. Calendar, every 15 minutes)

Another process should read the data, build the bitmaps (red and black) and throw them on the screen. Once every 5 minutes. (Have this run by cron, instead of relying on the process - unless tests show that keeping the process up reduces refresh time.)


# Notes:

To get text directions control, you need to install `libraqm`:

     sudo python3 -m pip uninstall PIL

     python3 -m pip install --upgrade pip
     python3 -m pip install --upgrade Pillow

     TODO: This still doesn't work

# Add to cron

Add the following lines to a `sudo`-enabled user:

	# m h  dom mon dow   command
	0 8 * * fri    /home/pi/eink-entrance-display/update-display.sh
	0 14 * * fri   /home/pi/eink-entrance-display/update-display.sh

TODO: Move all this into a Docker image using the Dockerfile, for easy setup
