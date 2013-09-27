"""
A cpt file is a container used for other files. Unlike the drp format,
it doesn't give any information about what those files are, leaving us to guess.
A cpt begins with a four-byte little-endian giving the number of subfiles it contains,
followed by a series of four-byte pointers indicating the beginning of each subfile relative to the beginning of the cpt.
A true cpt has an end-of-file pointer as well, but the Chrono Cross CDs also include variations on the format which lack one.
After that, the files are packed in one after the other.
-- http://triple-tech.org/Wiki/Cpt
"""

import struct, os, argparse

class CptFile:
	def __init__(self):
		self.filenum = 0 # 4 bytes
		self.filepos = [] # 4 bytes each
		self.eof = None
		self._pos = 8 # file poset pointer
		self._filepaths = [] # files to be packed
	
	def log(self):
		print('Files: ', self.filenum)
		print('File offsets: ', self.filepos)
		print('End of file: ', self.eof)
	
	def add(self, filepath):
		if os.path.exists(filepath):
			si = os.stat(filepath)
			self.filepos.append(self._pos)
			self._pos += (4 + si.st_size)
			self._filepaths.append(filepath)
			self.filenum += 1
	
	def pack(self):
		buf = struct.pack('<L', self.filenum)
		
		# file offset
		for i in range(self.filenum):
			buf += struct.pack('<L', self.filepos[i])
		
		# sequential file content dump
		for i in range(self.filenum):
			f = open(self._filepaths[i], 'r+b')
			buf += f.read()
			f.close()
		
		return buf
	
def unpack(buf):
	cpt = CptFile()
	pos = 0
	
	# Unpack CPT metadata
	tmp = struct.unpack_from('<L', buf, pos)
	cpt.filenum = tmp[0] # tmp is always a tuple
	pos += 4
	
	# Unpack file posets
	for i in range(cpt.filenum):
		tmp = struct.unpack_from('<L', buf, pos)
		cpt.filepos.append(tmp[0])
		pos += 4
	
	# Unpack files
	for i in range(cpt.filenum):
		nextpos = pos
		
		# last file in sequence?
		if i == (cpt.filenum-1):
			tmp = open(str(i)+'.out', 'w+b')
			tmp.write(buf[pos:])
			tmp.close()
		else:
			nextpos = cpt.filepos[i+1]
			tmp = open(str(i)+'.out', 'w+b')
			tmp.write(buf[pos:nextpos])
			tmp.close
		
		pos = nextpos

	return cpt

def main():
	parser = argparse.ArgumentParser(description='PlayStation CPT file utility')
	parser.add_argument('-x', metavar='CPT_archive', type=str, help='Extract files')
	parser.add_argument('-c', metavar='filename', type=str, nargs='+', help='Create CPT file')
	parser.add_argument('-o', metavar='filename', type=str, help='Output CPT name')
	args = parser.parse_args()
	
	if (args.c == None) and (args.x == None):
		parser.print_help()
	
	if (args.c != None) and (args.x != None):
		parser.print_help()
	
	if (args.c == None) and (args.x != None):
		f = open(args.x, 'r+b')
		unpack(f.read())
		f.close()
	
	if (args.c != None) and (args.x == None):
		p = CptFile()
		for i in range(len(args.c)):
			p.add(args.c[i])
		f = open(args.o, 'w+b')
		f.write(p.pack())
		f.close()
		p.log()

if __name__ == '__main__':
	main()
