# eink-entrance-display
Show information of interest to the whole family on an eInk display near the entrance

# Setup

Create and activate a Python virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install requests pillow
```

# Add to cron

Add the following lines to a `sudo`-enabled user:

	# m h  dom mon dow   command
	0 8 * * fri    /home/pi/eink-entrance-display/update-display.sh
	0 14 * * fri   /home/pi/eink-entrance-display/update-display.sh

TODO: Move all this into a Docker image using the Dockerfile, for easy setup
