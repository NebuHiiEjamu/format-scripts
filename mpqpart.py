"""
Partial MPQ format (*.mpq.part)

Implemented according to http://zezula.net
"""

import struct

class Header:
	def __init__(self):
		self.version = 2 # 4 bytes, always 2?
		self.gamebuildnum = None # 8 byte ASCIIZ string
		self.pos0c = 0 # 4 bytes
		self.pos10 = 0 # 4 bytes
		self.pos14 = 0x1C # 4 bytes, seems to have 0x1C, which is size of header remainder
		self.pos18 = 0 # 4 bytes
		self.pos1c = 0 # 4 bytes
		self.pos20 = 0 # 4 bytes
		self.pos24 = 0 # 4 bytes, always 0?
		self.lofilelen = 0 # 4 bytes, low 32 bits of file size
		self.hifilelen = 0 # 4 bytes
		self.partlen = 0 # 4 bytes, size of 1 file part in bytes

class Entry:
	def __init__(self):
		self.flags = 0 # 4 bytes, 3 = part is present in file
		self.loblkpos = 0 # 4 bytes, lo 32 bits of part pos. in file
		self.hiblkpos = 0 # 4 bytes
		self.pos0c = 0 # 4 bytes
		self.pos10 = 0 # 4 bytes
