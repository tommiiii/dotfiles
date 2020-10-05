#!/usr/bin/env sh

## Add this to your wm startup file.

# Terminate already running bar instances
killall -q polybar

# Wait until the processes have been shut down
while pgrep -u $UID -x polybar >/dev/null; do sleep 1; done

# Python script to automatically change the padding on the right to allow space for the tray
python3 $HOME/.config/polybar/scripts/tray-pad.py

# Launch bar1 and bar2
polybar -c ~/.config/polybar/config.ini main &
