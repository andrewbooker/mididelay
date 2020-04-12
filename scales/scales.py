#!/usr/bin/env python

import random

notes = {"A":  57,
		 "A#": 58,
		 "Bb": 58,
		 "B":  59,
		 "C":  60,
		 "C#": 61,
		 "Db": 61,
		 "D":  62,
		 "D#": 63,
		 "Eb": 63,
		 "E":  64, 
		 "F":  65,
		 "F#": 66,
		 "Gb": 66,
		 "G":  67,
		 "G#": 68,
		 "Ab": 68,
		 "A":  69}

class Modes:
	all = {"aeolian": [2, 1, 2, 2, 1, 2],
		   "dorian": [2, 1, 2, 2, 2, 1],
		   "ionian": [2, 2, 1, 2, 2, 2],
		   "mixolydian": [2, 2, 1, 2, 2, 1],
		   "lydian": [2, 2, 2, 1, 2, 2],
#		   "eastern": [1, 3, 1, 2, 1, 2],
#		   "diminished": [3, 3, 3],
		   "wholetone": [2, 2, 2, 2, 2],
		   "minorpentatonic": [3, 2, 2, 3],
           "majorpentatonic": [4, 1, 2, 4]}

	@staticmethod
	def modeNamed(name):
		return Modes.all[name]

	@staticmethod
	def any():
		i = random.randint(0, len(Modes.all) - 1)
		m = [k for k in Modes.all.keys()][i]
		return (m, Modes.all[m])


class Scale():
	def __init__(self, chordSize, root, mode):
		octaves = -1
		tonic = notes[root]
		base = tonic
		self.notes = []
		for n in range(chordSize):
			if ((n % (len(mode) + 1)) == 0):
				octaves += 1
				base = tonic + (octaves * 12)
			else:
				base += mode[(n - (1 + octaves)) % len(mode)]
			
			self.notes.append(base)

	def noteFrom(self, i):
		return self.notes[i]
