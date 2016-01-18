#! /usr/bin/python3
###############################################################################
# rbx.py
# Really Basic arXive - packer
# Sierra RBX
# by mj.Jernigan, Jan 2016
#
# Usage: python3 rbx.py <path>
#
# Loop it if you dare (assuming you made an "rbx" shell script):
#   for f in $(find * -type d); do rbx $f; done 
#
# Welcome to my lazy, convention-over-configuration tool.
# Feel free to expand it and make it friendlier.
#
# Convention is that the unpacker will extract to a subfolder of the same
# base name as the archive file.  The packer will do the opposite and put
# an .RBX suffix on it.  So, if you don't want to lose your original archive,
# rename something or work with a copy in another folder, d'oh.
#
# The next convention is that the unpacker will produce an archive directory
# pickle with the suffix of ".dir.pickle".  If the packer sees a matching
# pickle, it will use it.  If not, it will use the default sort order.
# Remember, the pickle must have the same base name of the folder being
# packed.  Thus, if you renamed the folder to "THISx" then rename the pickle
# to "THISx.dir.pickle".  The directory pickle is important if planning to
# make patch files of minimal size.  By repacking in the same order the file
# delta is minimized.  xdelta sees this better than most, including bsdiff.
#
# RBX File Format:
#   Type            Length          Contents
#   =============== =============== ================
#   unknown         4               9E 9A A9 0B
#   Int             4               Number of files in the archive: n
#	Collection      16*n            Directory [
#     String          12              Filename, null padded
#     Pointer         4               Address of file data ]
#   Collection      4*n + s[1..n]   Files [
#     Int             4               Size of file in bytes: s
#     Data            s               File binary data ]
#
# p.s.  I just guessed at the meaning of RBX.  Make your own guesses.
###############################################################################
# RBXIT - Really Basic sIerra Tools (the X is x'd out)
# Copyright (C) 2016  mj.Jernigan
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################
import sys
import os
import struct
import pickle

header = b"\x9E\x9A\xA9\x0B"

if len(sys.argv) <= 1:
	sys.exit("Usage: rbx <path>")

# Get the folder name from the command line and read in the file data.
fdir = sys.argv[1]
try:
	# If there is an archive directory pickle from unrbx, use it.
	ff = open(fdir+".dir.pickle", "rb")
except:
	# Otherwise, build the archive from all files in the folder.
	path, dirs, files = next(os.walk(fdir))
else:
	print("Pickle found!  Using it to set order.")
	xdir = pickle.load(ff)
	ff.close()
	xdir.sort()
	offsets, files = zip(*xdir)


# Build the archive name.
rbxfile = fdir + ".RBX"

with open(rbxfile, "wb") as f:

	print("Beginning Really Basic arXive packaging:")
	print("Packing {} folder to file: {}".format(fdir, rbxfile))

	# Write the header.
	#   Meaning of first 4 bytes is uknown.
	#   The next dword is the number of files in archive.
	f.write(header)
	f.write(struct.pack("<I", len(files)))  # Write as unsigned int

	# Save some space to come back and write the directory later.
	diroffset = f.tell()
	f.write(b"\0" * 16 * len(files))

	# Loop through packing the files.
	offsets = []
	for fname in files:

		if len(fname) > 12:
			sys.exit("ABORTING: Filename longer than 12 chars: " + fname)
		
		offset = f.tell()
		offsets.append(offset)

		# Read in the file.
		with open(os.path.join(fdir, fname), "rb") as ff:
			data = ff.read()
			fsize = len(data)

		# Write the size and file data into the archive.
		print("packing", os.path.join(fdir, fname), fsize, "*{}".format(offset))
		f.write(struct.pack("<I", fsize))  # Write size as unsigned int
		f.write(data)

	# Backup in the archive and write the directory
	# now that we have the offsets.
	xdir = list(zip(files, offsets))
	xdir.sort()
	print("writing file directory in archive")
	f.seek(diroffset)
	for n, o in xdir:
		f.write(n.encode("cp1252").ljust(12, b"\0"))  # Pad filename with nulls
		f.write(struct.pack("<I", o))  # Write pointer as unsigned int

print("fin")
