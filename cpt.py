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
		self.filecount = 0 # 4 bytes
		self.fileoffs = [] # 4 bytes each
		self.eof = None
		self._offs = 8 # file offset pointer
		self._filepaths = [] # files to be packed
	
	def log(self):
		print('Files: ', self.filecount)
		print('File offsets: ', self.fileoffs)
		print('End of file: ', self.eof)
	
	def add(self, filepath):
		if os.path.exists(filepath):
			si = os.stat(filepath)
			self.fileoffs.append(self._offs)
			self._offs += (4 + si.st_size)
			self._filepaths.append(filepath)
			self.filecount += 1
	
	def pack(self):
		buf = struct.pack('<L', self.filecount)
		
		# file offset
		for i in range(self.filecount):
			buf += struct.pack('<L', self.fileoffs[i])
		
		# sequential file content dump
		for i in range(self.filecount):
			f = open(self._filepaths[i], 'r+b')
			buf += f.read()
			f.close()
		
		return buf
	
def unpack(buf):
	cpt = CptFile()
	offs = 0
	
	# Unpack CPT metadata
	tmp = struct.unpack_from('<L', buf, offs)
	cpt.filecount = tmp[0] # tmp is always a tuple
	offs += 4
	
	# Unpack file offsets
	for i in range(cpt.filecount):
		tmp = struct.unpack_from('<L', buf, offs)
		cpt.fileoffs.append(tmp[0])
		offs += 4
	
	# Unpack files
	for i in range(cpt.filecount):
		nextoffs = offs
		
		# last file in sequence?
		if i == (cpt.filecount-1):
			tmp = open(str(i)+'.out', 'w+b')
			tmp.write(buf[offs:])
			tmp.close()
		else:
			nextoffs = cpt.fileoffs[i+1]
			tmp = open(str(i)+'.out', 'w+b')
			tmp.write(buf[offs:nextoffs])
			tmp.close
		
		offs = nextoffs

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
