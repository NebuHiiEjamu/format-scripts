"""
Mopaq archive format found in Blizzard titles Diablo 1.0 and later

Implemented according to info from http://www.zezula.net
"""

import struct, hashlib

USERDATA_MAGIC = 0x1B51504D # MPQ\x1A
FILEHEADER_MAGIC = 0x1A51504D # MPQ\x1B
HET_MAGIC = 0x1A544548 # HET\x1A
BET_MAGIC = 0x1A544542 # BET\x1A
BITMAP_MAGIC = 0x33767470 # ptv3
PATCH_MAGIC = b'BSDIFF40' # offset 0x0000
MD5_MAGIC = b'MD5_'
XFRM_MAGIC = b'XFRM'

V1LEN = 0x20
V2LEN = 0x2C
V3LEN = 0x44 # or greater
V4LEN = 0xD0

L_N = 0 # neutral/American English
L_CNTW = 0x404 # Chinese (Taiwan)
L_CZ = 0x405 # Czech
L_DE = 0x407 # German
L_EN = 0x409 # English
L_ES = 0x40A # Spanish
L_FR = 0x40C # French
L_IT = 0x410 # Italian
L_JP = 0x411 # Japanese
L_KR = 0x412 # Korean
L_PL = 0x415 # Polish
L_PT = 0x416 # Portuguese
L_RU = 0x419 # Russian
L_ENUK = 0x809 # UK English

BF_IMPL = 0x00000100 # File is compressed using PKWARE Data compression library
BF_COMP = 0x00000200 # File is compressed using combination of compression methods
BF_ENCR = 0x00010000 # File is encrypted
BF_FKEY = 0x00020000 # The decryption key for the file is altered according to the position of the file in the archive
BF_PTCH = 0x00100000 # The file contains incremental patch for an existing file in base MPQ
BF_SNGL = 0x01000000 # Instead of being divided to 0x1000-bytes blocks, the file is stored as single unit
BF_DMRK = 0x02000000 # File is a deletion marker, indicating that the file no longer exists. This is used to allow patch archives to delete files present in lower-priority archives in the search chain. The file usually has length of 0 or 1 byte and its name is a hash
BF_SCRC = 0x04000000 # File has checksums for each sector (explained in the File Data section). Ignored if file is not compressed or imploded.
BF_EXST = 0x80000000 # Set if file exists, reset when the file was deleted

AF_READ = 0x00000001 # MPQ opened read only
AF_CHNG = 0x00000002 # tables were changed
AF_PROT = 0x00000004 # protected MPQs like W3M maps
AF_CHKS = 0x00000008 # checking sector CRC when reading files
AF_FIXS = 0x00000010 # need fix size, used during archive open
AF_IVLF = 0x00000020 # (listfile) invalidated
AF_IVAT = 0x00000040 # (attributes) invalidated

ATR_CRC32 = 0x00000001 # contains CRC32 for each file
ATR_FTIME = 0x00000002 # file time for each file
ATR_MD5 = 0x00000004 # MD5 for each file
ATR_PATCHBIT = 0x00000008 # patch bit for each file
ATR_ALL = 0x0000000F

CF_HUFF = 0x01 # Huffman compression, WAVE files only
CF_ZLIB = 0x02
CF_PKWR = 0x08 # PKWARE
CF_BZP2 = 0x10 # BZip2, added in Warcraft 3
CF_SPRS = 0x20 # Sparse, added in Starcraft 2
CF_MONO = 0x40 # IMA ADPCM (mono)
CF_STER = 0x80 # IMA ADPCM (stereo)
CF_LZMA = 0x12 # added in Starcraft 2, not a combination
CF_SAME = 0xFFFFFFFF # Same

K_HASH = 0xC3AF3770
K_BLCK = 0xEC83B3A3

PTYPE1 = b'BSD0' # Blizzard modified version of BSDIFF40 incremental patch
PTYPE2 = b'BSDP'
PTYPE3 = b'COPY' # plain replace
PTYPE4 = b'COUP'
PTYPE5 = b'CPOG'

class UserData:
	def __init__(self):
		self.size = 0 # 4 bytes, max size of user data
		self.hdrpos = 0 # 4 bytes, header offset
		self.hdrlen = 0 # 4 bytes, header size

class Header: # must begin at file offs. aligned to 512 (0x200)
	def __init__(self):
		self.hdrlen = 0 # 4 bytes, header size
		self.archlen = 0 # 4 bytes, archive size, deprecated in ver. 2, calced as length from beg. of archive to end of hash table/block table/ext. block table (whichever is largest)
		self.fmtver = 0 # 2 bytes, 0 = up to WoW:BC, 1 = WoW:BC-WoW:CT beta, 2/3 = WoW:CT beta and later
		self.blklen = 0 # 2 bytes, block size
		self.hashtblpos = 0 # 4 bytes, hash table offset
		self.blktblpos = 0 # 4 bytes, block table offset
		self.hashtbllen = 0 # 4 bytes, hash table entries, must be power of 2 and: ver 1 = must be < 2^16, ver 2 = must be < 2^20
		self.blktbllen = 0 # 4 bytes, block table entries
		# version 2
		self.hiblktblpos = 0 # 8 bytes, offset to array of 16 bit hi parts of file offsets
		self.hashtblposhi = 0 # 2 bytes, hi 16 bits of hash table offset for large archives
		self.blktblposhi = 0 # 2 bytes, hi 16 bits of block table offset for large archives
		# version 3
		self.archlen64 = 0 # 8 bytes, 64 bit size of archive
		self.bettblpos = 0 # 8 bytes, BET table offset
		self.hettblpos = 0 # 8 bytes, HET table offset
		# version 4
		self.hashtbllen64 = 0 # 8 bytes, compressed size of hash table
		self.blktbllen64 = 0 # 8 bytes, compressed size of block table
		self.hiblktbllen = 0 # 8 bytes, compressed size of hi block table
		self.hettbllen = 0 # 8 bytes, compressed size of HET table
		self.bettbllen = 0 # 8 bytes, comp. size of BET table
		self.rawchunklen = 0 # 4 bytes, raw chunk size
		self.blktblmd5 = None
		self.hashtblmd5 = None
		self.hiblktblmd5 = None
		self.bettblmd5 = None
		self.hettblmd5 = None
		self.md5 = None # MD5 of the header from magic to hettblmd5

class HashEntryTable:
	def __init__(self):
		self.version = 1 # 4 bytes, always 1?
		self.datalen = 0 # 4 bytes, size of contained table
		self.size = 0 # 4 bytes, size of entire hash table, including header
		self.filenum = 0 # 4 bytes, # of files in MPQ
		self.hashtbllen = 0 # 4 bytes, hash table size in bytes
		self.hashentrylen = 0 # 4 bytes, hash entry size in bits
		self.totalidxlen = 0 # 4 bytes, total size of file index in bits
		self.idxlenext = 0 # 4 bytes, extra bits in file index
		self.idxlen = 0 # 4 bytes, file index size in bits
		self.blktbllen = 0 # 4 bytes, block index subtable size in bytes
		self.hashtbl = [] # 1 byte each, hashtbllen items

class BlockEntryTable:
	def __init__(self):
		self.version = 1 # 4 bytes, always 1?
		self.datalen = 0 # 4 bytes, size of contained table
		self.size = 0 # 4 bytes
		self.filenum = 0 # 4 bytes
		self.pos08 = 0x10 # 4 bytes, unknown, always 0x10?
		self.entrylen = 0 # 4 bytes, size of 1 table entry in bits
		self.bifilepos = 0 # 4 bytes, bit index of file position within entry record
		self.bifilelen = 0 # 4 bytes
		self.bicmplen = 0 # 4 bytes, file compressed size in entry rec.
		self.biflagidx = 0 # 4 bytes
		self.biunknown = 0 # 4 bytes
		self.bcfilepos = 0 # 4 bytes, bit size of file pos. in entry rec.
		self.bcfilelen = 0 # 4 bytes
		self.bccmplen = 0 # 4 bytes
		self.bcflagidx = 0 # 4 bytes
		self.bcunknown = 0 # 4 bytes
		self.totalhashlen = 0 # 4 bytes, total size of BET hash
		self.hashlenext = 0 # 4 bytes, extra bits # in BET hash
		self.hashlen = 0 # 4 bytes, BET hash size in bits
		self.hasharraylen = 0 # 4 bytes, size of BET hashes array in bytes
		self.flagnum = 0 # 4 bytes, # of flags in following array
		self.flags = [] # 4 bytes each, flagnum items

class Hash:
	def __init__(self):
		self.name1 = 0 # 4 bytes, hash of full file name part A
		self.name2 = 0 # 4 bytes, hash of full file name part B
		self.lang = 0 # 2 bytes, language of file, see L_* consts above
		self.platform = 0 # 2 bytes, platform file is used for, 0 = default platform, no other values?
		self.blkidx = 0 # 4 bytes, 0xFFFFFFFF = empty and was always empty (terminate search), 0xFFFFFFFE = empty but once was valid file (don't terminate search)

class Block:
	def __init__(self):
		self.filepos = 0 # 4 bytes
		self.cmplen = 0 # 4 bytes, compressed size
		self.filelen = 0 # 4 bytes, uncompressed size, only valid if block is file, else 0
		self.flags = 0 # 4 bytes, see BF_* consts

class PatchInfo:
	def __init__(self):
		self.size = 0 # 4 bytes, header length in bytes
		self.flags = 0 # 4 bytes, 0x80000000 = MD5?
		self.datalen = 0 # 4 bytes, uncomp. size of patch file
		self.md5 = None # MD5 of entire file after decomp.

class PatchHeader:
	def __init__(self):
		self.datalen = 0 # 4 bytes, size of entire patch decomp'd
		self.beforelen = 0 # 4 bytes, size of file before patch
		self.afterlen = 0 # 4 bytes, size after patch
		self.md5blklen = 0 # 4 bytes, size of MD5 block, including magic and size itself
		self.beforemd5 = None # MD5 of file before patch
		self.aftermd5 = None # MD5 of file after patch
		self.xfrmblklen = 0 # 4 bytes, size of XFRM block including header and patch data
		self.type = 0 # 4 bytes, type of patch (BSD0 or COPY)

class BsDiff40: # if BSD0
	def __init__(self):
		self.ctrlblklen = 0 # 8 bytes, offset 0x0008, size of CTRL block in bytes
		self.datablklen = 0 # 8 bytes, offset 0x0010, size of DATA block in bytes
		self.afterlen = 0 # 8 bytes, offset 0x0018, size of file after patch, in bytes
		self.ctrl = [] # 0x0C bytes each, ctrlblklen items, offset 0x0020
		self.data = None
		self.extra = None # extra bytes beyond DATA block until end of patch

class Bitmap:
	def __init__(self):
		self.unknown = 3 # 4 bytes, always 3?
		self.gamebuild = 0 # 4 bytes, game build # for MPQ
		self.mapposlo = 0 # 4 bytes, lo map offset
		self.mapposhi = 0 # 4 bytes
		self.blklen = 0 # 4 bytes, size of one block

class Archive:
	def __init__(self):
		self.stream = None
		self.udpos = 0 # 8 bytes, user data offset
		self.hdrpos = 0 # 8 bytes, header offset
		self.patch = None # patch archive, if any
