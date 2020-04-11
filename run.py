#!/usr/bin/env python

import pygame.midi as midi


class UsingMidiDevices():
	def __init__(self):
		print("listing usable devices")
		midi.init()
		self.outputs = []
		self.inputs = []
		count = midi.get_count()
		print("found", count, "devices")
		for d in range(count):
			info = midi.get_device_info(d)
			name = info[1].decode("utf-8")
			
			isOutput = (info[3] == 1)
			isInput = (info[2] == 1)
			if isOutput and "USB" in name: self.outputs.append((d, name))
			if isInput and "SPD-SX MIDI" in name: self.inputs.append((d, name))
				
		print("inputs:", self.inputs)
		print("outputs:", self.outputs)
		
	def __del__(self):
		midi.quit()
		print("exiting")


devs = UsingMidiDevices()
del devs
