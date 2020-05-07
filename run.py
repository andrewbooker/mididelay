#!/usr/bin/env python

import time
import readchar
import random

from multiprocessing import Value
import threading

class Repeater():
    repeaters = []

    def __init__(self, player, playedNote, vel, currentScale):
        self.playedNote = playedNote
        Repeater.repeaters.append(self)
        self.note = Value('i', (random.randint(-1, 2) * 12) + currentScale.noteFrom(self.playedNote))
        self.playedVelocity = vel
        self.finished = False
        self.player = player
        t = threading.Thread(target = self.start, args = (), daemon = True)
        t.start()

    def __del__(self):
        self.player.note_off(self.note.value, 0, 0)
        Repeater.repeaters.remove(self)
        
    def _setNote(self, setTo):
        with self.note.get_lock():
            self.note.value = setTo

    def transpose(self, scale):
        self._setNote(scale.noteFrom(self.playedNote))

    def playOne(self, velocity):
        note = self.note.value
        self.player.note_on(note, velocity, 0)
        time.sleep(0.1)
        self.player.note_off(note, 0, 0)

    def start(self):
        self.playOne(self.playedVelocity)

        dv = self.playedVelocity / 10.0
        velocity = self.playedVelocity - dv

        while velocity > 0:
            time.sleep(1.9)
            self.playOne(int(velocity))
            velocity -= dv

        self.finished = True

        del(self)


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
checkImport("compositionutils")
from mediautils.mididevices import UsbMidiDevices, MidiIn, MidiOut
devs = UsbMidiDevices()
ioOut = MidiOut(devs)
ioIn = MidiIn(devs)

from compositionutils.scale import Scale, Modes

def waitForStop(shouldStop):
    c = readchar.readchar()
    if c == "q":
        shouldStop.set()


class Key():
    def __init__(self):
        self.lastMode = None
        self.setScale("C", Modes.any())
        
    def setScale(self, tonic, mode):
        print("using", tonic, mode[0])
        self.scale = Scale(8, tonic, mode[1])
        
    def transpose(self):
        m = Modes.any()
        if m[0] == self.lastMode:
            self.transpose()
        
        self.setScale("C", m)
        self.lastMode = m[0]
        for r in Repeater.repeaters:
            r.transpose(self.scale)
            
key = Key()
shouldStop = threading.Event()
controller = threading.Thread(target=waitForStop, args=(shouldStop,), daemon=True)
controller.start()


while not shouldStop.is_set():
    if ioIn.io.poll():
        e = ioIn.io.read(1)
        msg = e[0][0]
        note = msg[1]
        vel = msg[2]
        if vel > 0:
            if note == 8:
                key.transpose()
            else:
                Repeater(ioOut.io, note, vel, key.scale)

controller.join()
for r in Repeater.repeaters[:]:
    del(r)

del ioOut
del ioIn
del devs
