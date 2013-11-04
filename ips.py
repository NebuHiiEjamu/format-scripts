"""
IPS ROM patch file formal
Implemented according to http://zerosoft.zophar.net/ips.php
"""

import struct
from collections import namedtuple

MAGIC = b'PATCH'
EOF = b'EOF'

EntryHeader = namedtuple('EntryHeader', [
	'size',
	'rle_size'])
EntryHeader.format = '2H'
