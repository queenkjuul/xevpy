#!/usr/bin/python
#

# This file is derived from 
# examples/xinput.py -- demonstrate the XInput extension
# from the python-xlib library which is 
#    Copyright (C) 2012 Outpost Embedded, LLC
#      Forest Bond <forest.bond@rapidrollout.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation; either version 2.1
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the
#    Free Software Foundation, Inc.,
#    59 Temple Place,
#    Suite 330,
#    Boston, MA 02111-1307 USA

# Python 2/3 compatibility.
from __future__ import print_function
from Xlib.ext import xinput
from Xlib.display import Display

import sys
import uinput


def main(argv):
    display = Display()
    try:
        version_info = display.xinput_query_version()
        print('Found XInput version %u.%u' % (
            version_info.major_version,
            version_info.minor_version,
        ))
        print('Using display %s' % (display.get_display_name()))

        screen = display.screen()
        # 0000 0100 = KeyPressMask
        # 0000 1000 = KeyReleaseMask
        # 0001 0000 = ButtonPressMask
        # 0010 0000 = ButtonReleaseMask
        # 0100 0000 = MotionMask
        # 0111 1100 = 124
        mask = xinput.KeyPressMask + xinput.KeyReleaseMask + \
            xinput.ButtonPressMask + xinput.ButtonReleaseMask + xinput.MotionMask
        screen.root.xinput_select_events([
            (xinput.AllDevices,
             [mask])
        ])

        uinputMouseEvents = (
            uinput.REL_X,
            uinput.REL_Y,
            uinput.BTN_LEFT,
            uinput.BTN_MIDDLE,
            uinput.BTN_RIGHT
        )

        prevMouse = [0, 0]
        with uinput.Device(uinputMouseEvents) as device:
            while True:
                event = display.next_event()
                print("event type: %u data: %s" % (event.evtype, event.data))
                if (event.evtype == xinput.Motion):
                    newMouse = [event.data.event_x, event.data.event_y]
                    relMouseX = newMouse[0] - prevMouse[0]
                    relMouseY = newMouse[1] - prevMouse[1]
                    relMouse = [relMouseX, relMouseY]
                    prevMouse = newMouse
                    print("mousemove %s" % (relMouse))
                    device.emit(uinput.REL_X, int(relMouse[0]), syn=False)
                    device.emit(uinput.REL_Y, int(relMouse[1]))
                elif (event.evtype == xinput.KeyPress):
                    print("keypress %s" % event.data.detail)
                elif (event.evtype == xinput.ButtonPress):
                    if (event.data.detail == 1):
                        print("button_left")
                        device.emit_click(uinput.BTN_LEFT)
                    elif (event.data.detail == 2):
                        device.emit_click(uinput.BTN_MIDDLE)
                    elif (event.data.detail == 3):
                        device.emit_click(uinput.BTN_RIGHT)

    finally:
        display.close()


if __name__ == '__main__':
    sys.exit(main(sys.argv))
