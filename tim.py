import struct

MAGIC = b'\x10\x00\x00\x00' # 4 bytes, second byte is version, only ver. 0 known to exist

BPP4 = 0x08 # 4 bits paletted
BPP8 = 0x09 # 8 bits paletted
BPP16 = 0x02 # 16 bits true colour

class TimImage:
	def __init__(self):
		self.bpp = 0 # 4 bytes
		self.clutlen = 0 # 4 bytes, length of entire CLUT (including header), always palx*paly*2
		self.palx = 0 # 2 bytes, palette width
		self.paly = 0 # 2 bytes, palette height
		self.palclrs = 0 # 2 bytes, # of palette colours
		self.palettes = 0 # 2 bytes, # of palettes
