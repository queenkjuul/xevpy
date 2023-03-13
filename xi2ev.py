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
from kbevents import uinputKeyboardEvents
from mevents import uinputMouseEvents
from getMappedChar import getMappedChar, getMappedCode


def main(argv):
    verbose = len(argv) > 1 and argv[1] == "-v"
    display = Display()
    screen = display.screen()
    mask = xinput.KeyPressMask + xinput.KeyReleaseMask + \
        xinput.ButtonPressMask + xinput.ButtonReleaseMask + xinput.MotionMask
    screen.root.xinput_select_events([
        (xinput.AllDevices,
         [mask])
    ])
    gc = screen.root.create_gc(
        foreground=screen.white_pixel, background=screen.black_pixel)

    def handleBtn(code, state=1, syn=True):
      # state == 1: buttonPress
      # state == 0: buttonRelease
        if (code == 1):
            vmouse.emit(uinput.BTN_LEFT, state, syn)
        elif (code == 2):
            vmouse.emit(uinput.BTN_MIDDLE, state, syn)
        elif (code == 3):
            vmouse.emit(uinput.BTN_RIGHT, state, syn)
        elif (code == 4):
            vmouse.emit(uinput.BTN_4, state, syn)
        elif (code == 5):
            vmouse.emit(uinput.BTN_5, state, syn)

        screenPrint("button %s" % code)

        if (verbose):
            if (state == 1):
                print("mousebuttonpress %s" % code)
            else:
                print("mousebuttonrelease %s" % code)

    def handleKey(code, state=1, syn=True):
      # state == 1: keypress
      # state == 0: keyrelease
        keycode = code
        keysym = display.keycode_to_keysym(keycode, 0)
        keystr = display.lookup_string(keysym)
        eventCode = getMappedChar(keystr)
        if (eventCode == None or eventCode == ""):
            eventCode = getMappedCode(keycode)
            keystr = str(keycode)

        if (eventCode != None):
            vboard.emit(eventCode, state, syn)
        else:
            print("no valid event code, X event code was %s" % keycode)

        screenPrint("key %s" % keystr)

        if (verbose):
            if (state == 1):
                print("Keypress %s" % keystr)
            else:
                print("Keyrelease %s" % keystr)

    def screenPrint(string, x=100, y=100):
        screen.root.clear_area()
        screen.root.draw_text(
            gc, 100, 50, "This window is sending inputs to USB4VC")
        screen.root.draw_text(gc, x, y, str(string))
        display.flush()

    try:
        if (verbose):
            version_info = display.xinput_query_version()
            print('Found XInput version %u.%u' % (
                version_info.major_version,
                version_info.minor_version,
            ))
            print('Using display %s' % (display.get_display_name()))
        print("Listening for events...")

        prevMouse = [0, 0]
        with uinput.Device(uinputMouseEvents) as vmouse:
            with uinput.Device(uinputKeyboardEvents) as vboard:
                while True:
                    event = display.next_event()
                    if event.type == display.extension_event.GenericEvent:
                        if (event.evtype == xinput.Motion):
                            newMouse = [event.data.event_x, event.data.event_y]
                            relMouseX = newMouse[0] - prevMouse[0]
                            relMouseY = newMouse[1] - prevMouse[1]
                            relMouse = [relMouseX, relMouseY]
                            prevMouse = newMouse
                            if (relMouse != [0, 0]):
                                vmouse.emit(uinput.REL_X, int(
                                    relMouse[0]), syn=False)
                                vmouse.emit(uinput.REL_Y, int(relMouse[1]))
                                screenPrint("mousemove %s" % relMouse)
                                if (verbose):
                                    print("mousemove %s" % (relMouse))

                        elif (event.evtype == xinput.KeyPress):
                            handleKey(event.data.detail, 1)
                        elif (event.evtype == xinput.KeyRelease):
                            handleKey(event.data.detail, 0)
                        elif (event.evtype == xinput.ButtonPress):
                            handleBtn(event.data.detail, 1)
                        elif (event.evtype == xinput.ButtonRelease):
                            handleBtn(event.data.detail, 0)
    finally:
        display.close()


if __name__ == '__main__':
    sys.exit(main(sys.argv))
