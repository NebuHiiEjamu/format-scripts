"""
Blizzard image format found in Warcraft III: Reign of Chaos and later titles

Implemented according to Wikipedia along with Xentax and other research
"""

import struct
from collections import namedtuple

MAGIC0 = 'BLP0'
MAGIC1 = 'BLP1'
MAGIC2 = 'BLP2'

BLP1Header = namedtuple('BLP1Header', [
	'magic',
	'type', # 0 = JPEG, 1 = paletted
	'has_alpha', # 0x8 = alpha, 0 = no alpha
	'width',
	'height',
	'has_team_color' # 3, 4 = uncomp. index list + alpha list, 5 = uncomp. index list
	'is_valid']) # Always =>0x1, if 0x0 the model that uses this texture will be messy. 
BLP1Header.format = '4s6L'

BLP2Header = namedtuple('BLP2Header', [
	'magic',
	'type', # 0 = JPEG compression, 1 = uncompressed or DirectX compression
	'encoding', # 1 = uncompressed, 2 = DirectX compression
	'alpha_depth', # 0 = none, 1 = 1 bit, 4 = 4-bit (DXT3 only), 8 = 8 bit
	'alpha_encoding', # 0 = DXT1 (0 or 1 bit), 1 = DXT2/3 (4 bit), 7 = DXT4/5 (interpolated)
	'has_mips', # boolean
	'width', # always a power of 2
	'height']) # always a power of 2
BLP2Header.format = '<4sL4B2L'


