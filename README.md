# xi2ev4vc

## Xinput2-to-uinput for use with USB4VC

Receives Xinput2 events (X11/Input, not gamepad XInput), such as from a VNC session, and repeats it via uinput to `/dev/input` to be read and translated by USB4VC

## Background

When I first saw the [USB4VC](https://github.com/dekuNukem/USB4VC), I wanted to set up [Barrier](https://github.com/debauchee/barrier) in a headless configuration so that I could control my retro PCs the same way I do my modern PCs. Mostly so that I wouldn't have to keep switching keyboards and mice to move between machines, especially when doing "admin" tasks (as opposed to gaming)

I did some experimenting, but I was unable to get Barrier to properly handle mouse movements when running on a headless virtual display (I tried both Xvfb and xorg-video-dummy). However, I could run x11vnc on the virtual display, and read the Xinput2 events with `xinput test-xi2 --root`. 

So I did more research and found a few existing tools which let me capture Xinput2 events and transmit them back through `uinput` to a `/dev/input/` device, which the USB4VC would then interpret as normal input and output to the protocol card, letting me control my retro machines over the network via a VNC viewer window which is transmitting the events. As long as my VNC window has focus, the inputs are streamed to the USB4VC, and out over the protocol card, to the retro machine. 

The script is in very bare-bones state and is in need of much work and improvement. However, I have successfully sent mouse movement and button press events over serial to my Compaq 286. 

Still, as a proof of concept, I'm happy, and will try to keep working on it. 

## Prerequisites

You will need `xvfb`, `x11vnc`, [`python-xlib`](https://github.com/python-xlib/python-xlib), and [`python-uinput`](https://github.com/tuomasjjrasanen/python-uinput) on the host (raspi)

You will also need a VNC client on another machine from which to send inputs. Pretty much any one will do. I use RealVNC on Windows 10

### ssh into your USBVC and then:

### install `xvfb`, `x11vnc`

```
sudo apt install xvfb x11vnc
```

### install `python-xlib`, `python-uinput`

1. Clone the repos
2. Install the packages

```
cd ~
git clone https://github.com/python-xlib/python-xlib.git
cd python-xlib
sudo python setup.py install
cd ~
git clone https://github.com/tuomasjjrasanen/python-uinput.git
cd python-uinput
sudo python setup.py install
```

## Run `xi2ev`

```
cd ~
git clone https://github.com/queenkjuul/xi2ev4vc.git
cd xi2ev4vc
./run.sh
```

You can then connect to your USB4VC with a VNC viewer. Any input events sent from your VNC client should print to the terminal. Mouse events should be sent through to the USB4VC protocol card and any client retro machines. You can open the "Show input events" screen on the USB4VC and watch for `python-uinput` events. 

## Wins

- Typing is great - Latency is low, signal is pretty reliable, touch typing at full speed will only occasionally result in problems
- Modifier keys and such work: keyDown and keyUp events are sent separately so the client (vintage) machine handles state of modifier keys directly. Thus menus and key combos work in DOS, for example. 
- Mouse input mostly works
- x11vnc has lots of options for remapping keys or handling lock keys, etc


## Gotchas

 - Mouse movement can be weird
 - ~~Double click can be weird~~ pretty well fixed it seems
 - Key repeat does not really work (would have to be implemented in software - `x11vnc -repeat` only sends repeated keyDowns, not keyUps, which seem to be needed - `Xvfb r` option breaks things)
 - Mouse wheel is more or less untested (middle click works)
 - Numberpad "+" key is not implemented by python-uinput so can't be used
 - No differentiation between LSHIFT and RSHIFT from VNC client
 - I mapped every key on my keyboard, which means many keys are missing (PrtScr, ScrLk, others)
 - Please somebody tell me there's a proper Xinput keycode to evdev keycode map somewhere??

## Notes

Xinput/Xinput2 - X11/Xlib input events, not to be confused with Xinput gamepad interface (gamepads not at all supported here yet, though uinput supports joysticks)

This entire thing might be totally unnecessary - x11vnc supports routing its inputs to `uinput` directly - however this needs a raw framebuffer device, which is not present in a default USB4VC install. This might eliminate a lot of issues (and the need for the xi2ev script entirely - x11vnc will handle everything at that point). I couldn't immediately figure out how to get a framebuffer device set up.

Should x11vnc be able to take over everything via its own `rawfb` and `uinput` support, in theory we could use a V4L capture device as the `rawfb` device, and use said capture device to do a proper Network KVM - streaming video to the modern machine, and input to the vintage machine, albeit with video lag. 

I would still like to get Barrier working, as this would eliminate the need to have a full VNC server, and focus/unfocus would be handled by Barrier, rather than having to focus the VNC viewer window. This code should work just as well with Barrier as with VNC, as it listens to any Xinput2 events on the root window. 

I could get Barrier to work for sending keypresses and mouse button presses, but not mouse movements. Once Barrier on the USB4VC captured the mouse, I got no movement events, and it was impossible to move the mouse back to any other machine connected with Barrier, short of killing the server. If someone can get Barrier to register mouse movements when using an Xvfb display, that would rock. 

Latency seems OKish. Plenty good for typing, not bad for mouse. I have looked into [`netevent`](https://github.com/Blub/netevent) but have not done any testing. The requirement of a Linux host kind of rules it out for me. 

~~Maybe VNC can be skipped by using a remote X server as the DISPLAY. Again though, this makes use on Windows trickier (or at least less intuitive) so I haven't tested it yet.~~ yes, since it just listens to X events on the env-defined DISPLAY, you can point it at a remote X server and it will use those inputs

~~I am also looking into [`evsieve`](https://github.com/KarsMulder/evsieve) as a way to remap keyboard keys on the USB4VC (in hopes of setting up WASD on certain old DOS games)~~ actually X11VNC can do this already (actually [`evsieve`](https://github.com/KarsMulder/evsieve) is probably still a good choice for remapping USB keyboards)

There are -repeat and pointer threshold settings for Xvfb that might help but haven't tried

## TODO

Graceful exit from shell script? 

Proper Xinput to uinput event code mapping (not just the map of my own keyboard)