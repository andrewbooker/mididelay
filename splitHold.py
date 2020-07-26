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


MAIN_CHANNEL = 0
HOLD_CHANNEL = 1

import random

class Splitter():
    def __init__(self, reader, player):
        self.reader = reader.io
        self.player = player.io
        self.played = []
        self.nextLen = 0

    def _stopCurrentHeld(self):
        if len(self.played) > 0:
            self.player.note_off(self.played[0], 0, HOLD_CHANNEL)

    def __del__(self):
        self._stopCurrentHeld()

    def _newNote(self, n):
        if len(self.played) in [self.nextLen]:
            self._stopCurrentHeld()
            self.player.note_on(n, 81, HOLD_CHANNEL)
            self.played = []
            self.nextLen = random.randint(2, 12)

        self.played.append(n)
    
    def start(self, shouldStop):
        while not shouldStop.is_set():
            if ioIn.io.poll():
                e = self.reader.read(1)
                msg = e[0][0]
                note = msg[1]
                vel = msg[2]
                if vel > 0:
                    self.player.note_on(note, vel, MAIN_CHANNEL)
                    self._newNote(note)
                else:
                    self.player.note_off(note, 0, MAIN_CHANNEL)

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
del splitter
del ioOut
del ioIn
del devs

