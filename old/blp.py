"""
Blizzard image format found in Warcraft III: Reign of Chaos and later titles

Implemented according to Wikipedia along with Xentax and other research
"""

MAGIC0 = 'BLP0'
MAGIC1 = 'BLP1'
MAGIC2 = 'BLP2'

class Jpeg: # if BLP compression = 0
	def __init__(self):
		self.jpghdrlen = 0 # 4 bytes, JPEG header length
		self.jpghdr = [] # byte array of jpghdrlen
		self.mipmap = [] # array of JPEG data byte arrays, 16 items

class UncmpIdxAlpha: # if BLP imgtype = 3 or 4
	def __init__(self):
		self.palette = [] # ? bytes each, 256 items
		self.mipmap = [] # 16 items, each entry is 2 byte arrays, both are cur. width * cur. height in length

class Format1:
	def __init__(self):
		self.compression = 0 # 4 bytes, 0 = JPEG compression, 1 = uses palettes (uncompressed)
		self.flags = 0 # 4 bytes, 8 = uses alpha channel?
		self.width = 0 # 4 bytes
		self.height = 0 # 4 bytes
		self.imgtype = 0 # 4 bytes, 3, 4 = uncomp. index list + alpha list, 5 = uncomp. index list
		self.imgsubtype = 0 # 4 bytes, 1 = ?
		self.mipmappos = [] # 4 bytes each, 16 items
		self.mipmaplens = [] # 4 bytes each, 16 items

class Format2:
	def __init__(self):
		self.type = 0 # 4 bytes, 0 = JPEG compression, 1 = uncompressed or DirectX compression
		self.encoding = 0 # 1 byte, 1 = uncompressed, 2 = DirectX compression
		self.alphadepth = 0 # 1 byte, 0 = none, 1 = 1 bit, 4 = 4-bit (DXT3 only), 8 = 8 bit
		self.alphaenc = 0 # 1 byte, 0 = DXT1 (0 or 1 bit), 1 = DXT2/3 (4 bit), 7 = DXT4/5 (interpolated)
		self.hasmips = 0 # 1 byte, boolean
		self.width = 0 # 4 bytes, always a power of 2
		self.height = 0 # 4 bytes, always a power of 2
		self.offsets = [] # 4 bytes each, 16 items, index 0 is image data offset
		self.lengths = [] # 4 bytes each, 16 items
		self.palette = [] # 4 byte BGRA colours, 256 items, present regardless if or not texture uses palettes
