#!/bin/bash

if [ "$DISPLAY" = "" ]; then
  export DISPLAY=:0
fi
XV_X=1440
XV_Y=1080
XV_D=8

VERBOSE=""

X11VNC_ARGS=""

HELP=false

while getopts "x:y:d:a:vh" flag; do
  case $flag in 
    x) XV_X=${OPTARG};;
    y) XV_Y=${OPTARG};;
    d) XV_D=${OPTARG};;
    v) VERBOSE="-v";;
    a) X11VNC_ARGS=${OPTARG};;
    h) HELP=true;;
  esac
done

echo $DISPLAY

function cleanup {
  kill $x11vnc_pid
  kill $xvfb_pid
}

if $HELP; then
  echo "You can provide some options:"
  echo "  -h    print this help"
  echo "  -v    verbose output (prints every event)"
  echo "  -x    Xvfb screen width (default 1920)"
  echo "  -y    Xvfb screen height (default 1080)"
  echo "  -d    Xvfb screen depth (default 8, shouldn't matter?)"
  echo "  -a    additional x11vnc arguments (in addition to ./x11vncrc)"
  echo "        for example: run.sh -a '-remap remapfile'"
  exit 0
fi

# kill subprocesses on CTRL-C or similar
trap cleanup SIGHUP SIGINT SIGTERM

if lsmod | grep -wq "uinput"; then
  echo "uinput found"
else
  echo "uinput missing - trying to install"
  if sudo modprobe -i 'uinput'; then
    echo "uinput installed"
  else
    echo "uinput failed"
    exit 1
  fi 
fi

echo "starting Xvfb on display "$DISPLAY
Xvfb $DISPLAY r -screen $DISPLAY $XV_X"x"$XV_Y"x"$XV_D &
xvfb_pid=$!
echo "Xvfb started with PID: "$xvfb_pid
echo "starting x11vnc"
x11vnc -display $DISPLAY -rc ./x11vncrc $X11VNC_ARGS &
x11vnc_pid=$!
echo "x11vnc started with PID: "$x11vnc_pid
echo "starting xi2ev"
sudo python xi2ev.py $VERBOSE &
echo "started xi2ev"

echo "connect to VNC at "`hostname -I`

if wait $xvfb_pid && wait $x11vnc_pid && wait $xi2ev_pid; then
  echo "all done"
  echo "live long and prosper, love"
  cleanup
  exit 0
else
  echo "uh oh wuh woh there was a oopsie woopsie"
  cleanup
  exit 1
fi