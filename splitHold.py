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


class Splitter():
    def __init__(self, reader, player):
        self.reader = reader.io
        self.player = player.io
    
    def start(self, shouldStop):
        while not shouldStop.is_set():
            if ioIn.io.poll():
                e = self.reader.read(1)
                msg = e[0][0]
                note = msg[1]
                vel = msg[2]
                if vel > 0:
                    self.player.note_on(note, vel, 0)
                else:
                    self.player.note_off(note, 0, 0)

splitter = Splitter(ioIn, ioOut)

import threading

shouldStop = threading.Event()
threads = []
threads.append(threading.Thread(target=splitter.start, args=(shouldStop,), daemon=True))
[t.start() for t in threads]

import readchar
print("Started. Press 'q' to exit")
while not shouldStop.is_set():
    c = readchar.readchar()
    if c == "q":
        shouldStop.set()

[t.join() for t in threads]
del ioOut
del ioIn
del devs

