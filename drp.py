import struct, os, argparse

MAGIC = b'drp\x00\x00\x00\x00\x00'

# TYPE## = unknown
DRP = 1 # nested DRP
MESH = 2
TIMINFO = 3
TIM = 4
MINST = 5 # music instruments
TYPE07 = 7 # found in 0018, 1967; potentially a problem
TYPE0A = 10 # graphics?
MDL = 11 # model pack
TYPE0C = 12 # graphics?
TYPE10 = 16 # meshes?
TYPE12 = 18 # found in rooms
TYPE15 = 21 # model for lens light effects?
MSEQ = 22 # music sequence
ANIM = 25 # model animation in CPTs
TYPE1A = 26 # found in battle animations, elements; attack/offensive element related?
LZSS = 37 # compressed data, found in 2416

def fileext(ft):
	if ft == DRP:
		return '.drp'
	elif ft == MESH:
		return '.mesh'
	elif ft == TIMINFO:
		return '.timinfo'
	elif ft == TIM:
		return '.tim'
	elif ft == MINST:
		return '.minst'
	elif ft == MDL:
		return '.mdl'
	elif ft == MSEQ:
		return '.mseq'
	elif ft == ANIM:
		return '.anim'
	elif ft == LZSS:
		return '.lzss'
	else:
		return '.out'

class DrpInvalid(Exception):
	pass

class DynResPack:
	def __init__(self):
		self.filecount = 0 # 4 bytes, calculated by yyxx/64
		self.fileoffs = [] # 4 bytes each
		self.filenames = [] # 4 bytes each, padded with 00 if < 4 characters
		self.filetypes = [] # 1 byte each, see consts above
		self.filelens = [] # 3 bytes each, equal to 16 times length of file
		self.filebufs = []
	
	def log(self):
		print('Files: ', self.filecount)
		print('File offsets: ', self.fileoffs)
		print('File names: ', self.filenames)
		print('File types: ', self.filetypes)
		print('File sizes: ', self.filelens)
	
def unpack(buf):
	drp = DynResPack()
	offs = 0
	
	# validate magic
	if buf[0:8] != MAGIC:
		raise DrpInvalid()
	offs += 8
	
	# calculate and obtain file count
	tmp = struct.unpack_from('<H', buf, offs)
	drp.filecount = int(tmp[0] / 64) # filecount is stored as itself multiplied by 64
	offs += 4 # skip the 2 pad bytes as well
	
	# file offsets
	for i in range(drp.filecount):
		tmp = struct.unpack_from('<L', buf, offs)
		drp.fileoffs.append(tmp[0])
		offs += 4
	
	# file headers + data
	for i in range(drp.filecount):
		offs += 4 # pad bytes
		tmp = struct.unpack_from('<4sB', buf, offs)
		drp.filenames.append(tmp[0])
		drp.filetypes.append(tmp[1])
		offs += 5
		#tmp = struct.unpack('<3b', buf[offs:offs+3])
		drp.filelens.append(int.from_bytes(buf[offs:offs+3], byteorder='little', signed=False))
		drp.filelens[i] = int(drp.filelens[i] / 16) # filelen stored as itself multiplied by 16
		offs += 3
		drp.filebufs.append(buf[offs:(offs+drp.filelens[i])])
		offs += drp.filelens[i]
	
	# write extracted files
	for i in range(drp.filecount):
		tmp = open(str(drp.filenames[i])[2:-1].replace('\\x00', '')+fileext(drp.filetypes[i]), 'w+b')
		tmp.write(drp.filebufs[i])
		tmp.close()
	
	return drp

def main():
	parser = argparse.ArgumentParser(description='PlayStation Dynamic Resource Pack extractor')
	parser.add_argument('archive', metavar='<archive>', type=str, help='DRP file')
	args = parser.parse_args()
	
	if (args.archive == None):
		parser.print_help()
	else:
		f = open(args.archive, 'r+b')
		p = unpack(f.read())
		f.close()
		p.log()

if __name__ == '__main__':
	main()
