"""
MPQ patch file format
Implemented according to http://zezula.net
"""

import struct

MAGIC = b'BSDIFF40'

TYPE1 = b'BSD0' # Blizzard modified version of BSDIFF40 incremental patch
TYPE2 = b'BSDP'
TYPE3 = b'COPY' # plain replace
TYPE4 = b'COUP'
TYPE5 = b'CPOG'

class PatchInfo:
	def __init__(self):
		
