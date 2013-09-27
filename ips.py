"""
IPS ROM patch file formal
Implemented according to http://zerosoft.zophar.net/ips.php
"""

MAGIC = b'PATCH'
EOF = b'EOF'


class Record:
	def __init__(self):
		self.pos = 0 # 3 bytes, The offset where the patch will be placed in the file to patch
		self.size = 0 # 2 bytes, The size of the data to put from the specified offset in the patching file, 0 = RLE encoding
		self.rlelen = 0 # 2 bytes
		self.data = None # size bytes
		self.value = 0 # 1 byte, value to write rlelen times starting from pos (if encoded)
