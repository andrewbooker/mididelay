#!/usr/bin/env python

import time
import keyboard
import random


from multiprocessing import Value
import threading
from scales.scales import *
		

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

import sys
import os
sys.path.append(os.path.dirname(os.getcwd()))
from mediautils.usbdevices import UsbMidiDevices, MidiIn, MidiOut
devs = UsbMidiDevices()
ioOut = MidiOut(devs)
ioIn = MidiIn(devs)

shouldStop = threading.Event()
def stop(e):
	shouldStop.set()
	print("stop called")

keyboard.on_press_key("q", stop, suppress = True)


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

for r in Repeater.repeaters[:]:
	del(r)

del ioOut
del ioIn
del devs
