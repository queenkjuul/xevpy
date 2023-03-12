# Input translation from VNC to /dev/input proof of concept

When I first saw the USB4VC, I wanted to set up [Barrier](https://github.com/debauchee/barrier) in a headless configuration so that I could control my retro PCs the same way I do my modern PCs. 

I did some experimenting, but I was unable to get Barrier to properly handle mouse movements when running on a headless virtual display (I tried both Xvfb and xorg-video-dummy). However, I could run x11vnc on the virtual display, and read the Xinput2 events with `xinput test-xi2 --root`. 

So I did more research and found a few existing tools which let me capture Xinput2 events and transmit them back through `uinput` to a `/dev/input/eventX` device, which the USB4VC would then interpret as normal input and output to the protocol card, letting me control my retro machines over the network via a VNC viewer window which is transmitting the events. As long as my VNC window has focus, the inputs are streamed to the USB4VC, and out over the protocol card, to the retro machine. 

The script is in very bare-bones state and is in need of much work and improvement. However, I have successfully sent mouse movement and button press events over serial to my Compaq 286, albeit inconsistently and improperly. 

Still, as a proof of concept, I'm happy, and will try to keep working on it. 

## Prerequisites

You will need `xvfb`, `x11vnc`, [`python-xlib`](https://github.com/python-xlib/python-xlib), and [`python-uinput`](https://github.com/tuomasjjrasanen/python-uinput) on the host (raspi)

You will also need a VNC client on another machine from which to send inputs. Pretty much any one will do. I use RealVNC on Windows 10

### ssh into your USBVC and then:

### install `xvfb`, `x11vnc`

```
sudo apt install xvfb x11vnc
```

### install `python-xlib`, `pythin-uinput`

1. Clone the repo
2. Install the package
3. Repeat for `python-uinput`

```
cd ~
git clone https://github.com/python-xlib/python-xlib.git
cd python-xlib
sudo python setup.py install
cd ..
git clone https://github.com/tuomasjjrasanen/python-uinput.git
cd python-uinput
sudo python setup.py install
```

## Run `xevpy`

```
cd ~
git clone https://github.com/queenkjuul/xevpy.git
cd xevpy
sudo modprobe -i uinput
export DISPLAY=:0
Xvfb $DISPLAY & x11vnc -forever -nopw & sudo python xevpy.py
```

You can then connect to your USB4VC with a VNC viewer. Any input events sent from your VNC client should print to the terminal. Mouse events should be sent through to the USB4VC protocol card and any client retro machines. You can open the "Show input events" screen on the USB4VC and watch for `python-uinput` events. 