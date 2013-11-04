"""
This PAC format is used in the PS2 game Legaia 2 Dual Saga and is simply multiple
files lumped together. The metadata is stored in little endian.The header starts
with 8 bytes that seem to be padding (always 0?), followed by the file count (4 bytes),
the PAC's total file size (4 bytes), and then a dictionary of file pointers (4 bytes)
paired with a 32 byte filepath. After that, the file content are dumped in one after
another.
"""

import struct, os
from collections import namedtuple

Header = namedtuple('Header', [
	'num_files',
	'size']) # initially 16: 8 pad bytes + Header
Header.format = '<8x2L'

Metadata = namedtuple('Metadata', [
	'offset',
	'path'])
Metadata.format = '<L32s'
