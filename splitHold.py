#!/usr/bin/env python



import os
import sys
def checkImport(lib):
    parentDir = os.path.dirname(os.getcwd())
    sys.path.append(parentDir)
    if not os.path.exists(os.path.join(parentDir, lib)):
        print("%s library not found." % lib)
        print("please clone github.com/andrewbooker/%s.git into %s" % (lib, parentDir))
        exit()

checkImport("mediautils")
from mediautils.mididevices import UsbMidiDevices, MidiIn, MidiOut
devs = UsbMidiDevices()
ioOut = MidiOut(devs)
ioIn = MidiIn(devs)


import threading
import readchar
def waitForStop(shouldStop):
    c = readchar.readchar()
    if c == "q":
        shouldStop.set()

shouldStop = threading.Event()
threads = []
threads.append(threading.Thread(target=waitForStop, args=(shouldStop,), daemon=True))
[t.start() for t in threads]

import time
while not shouldStop.is_set():
    if ioIn.io.poll():
        e = ioIn.io.read(1)
        msg = e[0][0]
        note = msg[1]
        vel = msg[2]
        if vel > 0:
            ioOut.io.note_on(note, vel, 0)
        else:
            ioOut.io.note_off(note, 0, 0)

[t.join() for t in threads]
del ioOut
del ioIn
del devs

