"""
Dynamic resource pack format used in Chrono Cross (PSX)

Implemented according to http://triple-tech.org/Wiki/Drp
"""

import struct
from collections import namedtuple

MAGIC = b'drp'

# TYPE## = unknown
DRP = 1 # nested DRP
MESH = 2
TIMINFO = 3
TIM = 4
MINST = 5 # music instruments
TYPE07 = 7 # found in 0018, 1967; potentially a problem
TYPE0A = 10 # graphics?
MDL = 11 # model pack
TYPE0C = 12 # graphics?
TYPE10 = 16 # meshes?
TYPE12 = 18 # found in rooms
TYPE15 = 21 # model for lens light effects?
MSEQ = 22 # music sequence
ANIM = 25 # model animation in CPTs
TYPE1A = 26 # found in battle animations, elements; attack/offensive element related?
LZSS = 37 # compressed data, found in 2416

def fileext(ft):
	if ft == DRP:
		return '.drp'
	elif ft == MESH:
		return '.mesh'
	elif ft == TIMINFO:
		return '.timinfo'
	elif ft == TIM:
		return '.tim'
	elif ft == MINST:
		return '.minst'
	elif ft == MDL:
		return '.mdl'
	elif ft == MSEQ:
		return '.mseq'
	elif ft == ANIM:
		return '.anim'
	elif ft == LZSS:
		return '.lzss'
	else:
		return '.out'

class Invalid(Exception):
	pass

Header = namedtuple('Header', [
	'magic',
	'num_files']) # calculated by yyxx/64
Header.format = '<3s5xL2x'

EntryHeader = namedtuple('EntryHeader', [
	'name', # padded with 00 if < 4 characters
	'type']) # see consts above
EntryHeader.format = '<4x4sB'
	
