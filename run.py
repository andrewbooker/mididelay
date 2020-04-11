#!/usr/bin/env python

import pygame.midi as midi
import time


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
			if isInput and "USB" in name: self.inputs.append((d, name))
				
		print("inputs:", self.inputs)
		print("outputs:", self.outputs)
		if len(self.inputs) == 0 or len(self.outputs) == 0:
			print("need both input and output USB devices")
			exit()
		
	def forInput(self):
		return self.inputs[0][0] if len(self.inputs) > 0 else None

	def forOutput(self):
		return self.outputs[0][0] if len(self.outputs) > 0 else None

	def __del__(self):
		midi.quit()
		print("exiting")


class MidiIo():
	def __init__(self, forInput, forOutput):
		self.receiver = midi.Input(forInput)
		self.player = midi.Output(forOutput, latency = 0)

	def __del__(self):
		self.player.close()
		self.receiver.close()
		del self.player
		del self.receiver

devs = UsingMidiDevices()
io = MidiIo(devs.forInput(), devs.forOutput())


received = 0
while received < 10:
	if io.receiver.poll():
		e = io.receiver.read(1)
		io.player.write(e)
		print(e)
		received += 1


del io
del devs
