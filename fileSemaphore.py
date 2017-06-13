#!/usr/bin/python

import os
import os.path
import time
import random

# print os.getpid()

def isLocked(filename):
	if not os.path.isfile(filename):
		return False

	with open(filename, 'r') as f:
		fPid = f.read()
		return len(fPid) > 0 and fPid != str(os.getpid())

def lock(filename):
	with open(filename, 'w') as f:
		f.write(str(os.getpid()))

def unlock(filename):
	if not isLocked(filename) and os.path.isfile(filename):
		os.remove(filename)

def waitLock(filename):
	
	while True:
		while isLocked(filename):
			time.sleep(0.5 + (random.random()/2))

		lock(filename)
		time.sleep(1)

		if not isLocked(filename):
			break

class fSem:

	def __init__(self, fi):
		self.filename = fi

	def __enter__(self):
		waitLock(self.filename)
	
	def __exit__(self, type, value, tb):
		unlock(self.filename)

# print("Starting")
# with fSem("db.lock"):
# 	print("Locked")
# 	raise ValueError("asdf")
# print("Unlocked")

# print(isLocked("db.lock"))
# unlock("db.lock")
# print(isLocked("db.lock"))