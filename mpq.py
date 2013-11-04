"""
Mopaq archive format found in Blizzard titles Diablo 1.0 and later

Implemented according to info from http://www.zezula.net
"""

import struct, hashlib, sys
from collections import namedtuple

USERDATA_MAGIC = b'MPQ\x1A'
FILEHEADER_MAGIC = b'MPQ\x1B'
HET_MAGIC = b'HET\x1A'
BET_MAGIC = b'BET\x1A'
BITMAP_MAGIC = b'ptv3'
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

UserDataHeader = namedtuple('UserDataHeader', [
	'magic',
	'data_size',
	'header_offset',
	'header_size'])
UserDataHeader.format = '<4s3L'

Header = namedtuple('Header', [
	'magic',
	'header_size',
	'archive_size', # archive size, deprecated in ver. 2, calced as length from beg. of archive to end of hash table/block table/ext. block table (whichever is largest)
	'version', # 0 = up to WoW:BC, 1 = WoW:BC-WoW:CT beta, 2/3 = WoW:CT beta and later
	'block_size',
	'hash_table_pos',
	'block_table_pos',
	'hash_table_size',
	'block_table_size'])
Header.format = '<4s2L2H4L'

Header2 = namedtuple('Header2', [
	'hi_block_table_pos',
	'hash_table_pos_hi',
	'block_table_pos_hi'])
Header2.format = '<Q2H'

Header3 = namedtuple('Header3', [
	'archive_size64',
	'bet_table_pos',
	'het_table_pos'])
Header3.format = '<Q3'

Header4 = namedtuple('Header4', [
	'hash_table_size64',
	'block_table_size64',
	'hi_block_table_size',
	'het_table_size',
	'bet_table_size',
	'raw_chunk_size'])
Header4.format = '<Q5L'

if sys.byteorder == 'little':
	Hash = namedtuple('Hash', [
		'name1',
		'name2',
		'locale',
		'platform',
		'block_index'])
else:
	Hash = namedtuple('Hash', [
		'name1',
		'name2',
		'platform',
		'locale',
		'block_index'])
Hash.format = '<2L2HL'

Block = namedtuple('Block', [
	'file_pos',
	'comp_size',
	'uncomp_size',
	'flags'])
Block.format = '<4L'

PatchInfo = namedtuple('PatchInfo', [
	'length',
	'flags',
	'uncomp_size',
	'md5'])
PatchInfo.format = '<3L16s'

PatchHeader = namedtuple('PatchHeader', [
	'header_magic',
	'size',
	'size_before_patch',
	'size_after_patch',
	'md5',
	'md5_block_size',
	'md5_before_patch',
	'md5_after_patch',
	'xfrm_magic',
	'xfrm_block_size',
	'type'])
PatchHeader.format = '<4s3L4sL16s16s4sL4s'

FileEntry = namedtuple('FileEntry', [
	'byte_offset',
	'file_time',
	'bet_hash',
	'hash_index',
	'het_index',
	'file_size',
	'comp_size',
	'flags',
	'locale',
	'platform',
	'crc32',
	'md5'])
FileEntry.format = '<3Q5L2HL16s'

ExtTable = namedtuple('ExtTable', [
	'magic',
	'version',
	'size'])
ExtTable.format = '<4s2L'

Bitmap = namedtuple('Bitmap', [
	'magic',
	'unknown',
	'game_build_num',
	'map_offset_lo',
	'map_offset_hi',
	'block_size'])
Bitmap.format = '<4s5L'

HashEntryTable = namedtuple('HashEntryTable', [
	'and_mask',
	'or_mask',
	'index_size_total',
	'index_size_extra',
	'index_size',
	'file_num',
	'hash_table_size',
	'hash_bit_size'])
HashEntryTable.format = '<2Q6L'

BlockEntryTable = namedtuple('BlockEntryTable', [
	'table_entry_size',
	'bit_index_file_pos',
	'bit_index_file_size',
	'bit_index_comp_size',
	'bit_index_flag_index',
	'bit_index_unknown',
	'bit_count_file_pos',
	'bit_count_file_size',
	'bit_count_comp_size',
	'bit_count_flag_index',
	'bit_count_unknown',
	'bet_hash_size_total',
	'bet_hash_size_extra',
	'bet_hash_size',
	'file_num',
	'flag_num'])
BlockEntryTable.format = '<16L'
