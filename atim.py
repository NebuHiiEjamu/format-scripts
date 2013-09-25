# incomplete because of unknown interspersed values in CLUT
import struct

class AtimCLUT:
	def __init__(self):
		self.length = 0 # 4 bytes, length of entire block (including header), always x*y*2
		self.x = 0 # 2 bytes
		self.y = 0 # 2 bytes
		self.palclrs = 0 # 2 bytes, palette colours
		self.numpals = 0 # 2 bytes
		self.rgbs = [] # 2 bytes each: red, green, blue, transparency, for each colour, read as nybbles, usually located between 0x1C-0x21C in ATIM

class AtimImage:
	def __init__(self):
		self.length = 0 # 4 bytes, length of entire block (including header), always x*y*2
		self.x = 0 # 2 bytes
		self.y = 0 # 2 bytes
		self.palclrs = 0 # 2 bytes, # of colours in each palette
		self.palettes = 0 # 2 bytes, # of palettes
		self.halfx = 0 # 2 bytes, literally half the value of x
		self.halfy = 0 # 2 bytes, deceptive, full value of y, not half value, unlike x
		self.pxloffs = [] # 1 byte each, offset into CLUT, usually follows address 0x22C

class AlteredTIM:
	def __init__(self):
		self.numobjs = 0 # 4 bytes
		self.clutoffs = 0 # 4 bytes
		self.imgoffs = [] # 4 bytes each
		self.clut = AtimCLUT()
		self.images = []
