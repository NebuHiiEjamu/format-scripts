"""
This is the altered TIM image format found in Chrono Cross for PSX.

Implemented according to http://triple-tech.org/Wiki/Atim
"""

# incomplete because of unknown interspersed values in CLUT
import struct
from collections import namedtuple

Header = namedtuple('Header', [
	'num_entries',
	'clut_pos'])
Header.format = '<2L'

CLUTHeader = namedtuple('CLUTHeader', [
	'size', # length of entire block (including header), always width*height*2
	'width',
	'height',
	'palette_colors',
	'num_palettes'])
CLUTHeader.format = '<L4H'

ImageHeader = namedtuple('ImageHeader', [
	'size', # length of entire block (including header), always width*height*2
	'width',
	'height'
	'palette_colors',
	'num_palettes'.
	'half_width', # literally half the width
	'half_height']) # deceptive, full width, not half
ImageHeader.format = '<L6H'
