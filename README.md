# eink-entrance-display
Show information of interest to the whole family on an eInk display near the entrance

# Usage

1. Build the dockers

     cd dockers
     ./build.sh

2. Run the dockers

     ./run.sh

# Notes:

To get text directions control, you need to install `libraqm`:

     sudo python3 -m pip uninstall PIL

     python3 -m pip install --upgrade pip
     python3 -m pip install --upgrade Pillow

     TODO: This still doesn't work
