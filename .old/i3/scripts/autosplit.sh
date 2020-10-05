#!/bin/sh
RES=$(xwininfo -id `xdotool getwindowfocus` | grep -E '(Width|Height)' | awk '{print $2}')
IFS=" " read var1 var2 <<< $RES
if [ $var1 -gt $var2 ]; then
    i3-msg "split h"
    i3-msg "move right"
    i3-msg "move down"
else
    i3-msg "split v"
    i3-msg "move right"
    i3-msg "move down"
fi
