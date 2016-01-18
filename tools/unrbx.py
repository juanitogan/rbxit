#! /usr/bin/python3
###############################################################################
# unrbx.py
# Really Basic arXive - unpacker
# Sierra RBX
# by mj.Jernigan, Jan 2016
#
# Usage: python3 unrbx.py <filename.rbx>
#
# Loop it if you dare (assuming you made an "unrbx" shell script):
#   for f in *.RBX; do unrbx $f; done
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
# See rbx.py for notes on the RBX file format.
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

if len(sys.argv) <= 1:
	sys.exit("Usage: unrbx <filename.rbx>")

# Get the filename from the command line.
rbxfile = sys.argv[1]

# Strip off the suffix to get the folder name.
fdir = rbxfile.rsplit(".", maxsplit=1)[0]

with open(rbxfile, "rb") as f:

	print("Beginning Really Basic arXive extraction:")
	print("Extracting {} to subfolder: {}".format(rbxfile, fdir))

	# Read the header.
	#   Meaning of first 4 bytes is uknown.
	#   The next dword is the number of files in archive.
	data = f.read(8)
	fields = struct.unpack("<II", data)
	header, count = fields
	print("foo:   ", header)
	print("files: ", count)

	# Read the file directory.
	data = f.read(16 * count)
	files = struct.iter_unpack("<12sI", data)

	# Prepare the output folder.
	if not os.path.exists(fdir):
	    os.makedirs(fdir)

	# Loop through extracting the files.
	xdir = []
	for bfname, offset in files:

		# Decode the name buffer into a string and strip the nulls.
		fname = bfname.decode("cp1252").rstrip("\0")
		# Save a directory list.
		xdir.append((offset, fname))
		
		# Jump to the offset, read the size, and grab the archived file.
		f.seek(offset)
		data = f.read(4)
		fields = struct.unpack("<I", data)
		fsize = fields[0]
		data = f.read(fsize)
		
		# Write the file to the output folder.
		print("writing", os.path.join(fdir, fname), fsize, "*{}".format(offset))
		with open(os.path.join(fdir, fname), "wb") as ff:
			ff.write(data)

# Save the directory list in a file for later use.
# Specifically, for repacking in the same order to minimize game patch size.
dirfile = fdir + ".dir.pickle"
print("Saving archive directory to restore original packing order (if found):", dirfile)
with open(dirfile, "wb") as ff:
	pickle.dump(xdir, ff, pickle.HIGHEST_PROTOCOL)

print("fin")
