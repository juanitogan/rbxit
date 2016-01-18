#! /usr/bin/python3
###############################################################################
# wax421.py
# Sierra WAX ADPCM (type 4) to PCM (type 1) encoder
# by mj.Jernigan, Jan 2016
#
# Usage: python3 wax421.py <filename or glob like *.WAX>
# Secret Usage: python3 [-nw] wax421.py <filename or glob like *.WAX>
#
# Do the whole wad if you like (assuming you made a "wax421" shell script):
#   wax421 */*.???
#
# Requirements: SoX (Sound eXchange) tool from sox.sourceforge.net
#
# It is not unusual to see 1 or 2 ADPCM state errors from a WAX file like:
#   sox WARN adpcms: -: ADPCM state errors: 1
#
# WAX File Format (similar to WAV but not WAV):
#
#   M  = bytes per sample
#   Ns = number of samples
#   Nc = number of channels
#   F  = frequency
#
#   Type            Length          Contents
#   =============== =============== ================
#   String          4               File type ID: "WAX:"
#   Int             4               Sierra audio type: 1=PCM, 4=ADPCM
#   Int             4               Data size: M*Nc*Ns
#   Int 		    2               WAV wFormatTag: always 1 (PCM) in WAX
#   Int             2               WAV nChannels: Nc
#   Int             4               WAV nSamplesPerSec: F
#   Int             4               WAV nAvgBytesPerSec: F*M*Nc
#   Int             2               WAV nBlockAlign: M*Nc
#   Int             2               WAV wBitsPerSample: 8*M (float) or 16 (log-PCM)
#   String          2  (total: 30)  WAV ckID: "data" chopped to "da"
#   (0x001E) Data   n               PCM: M*Nc*Ns; ADPCM 0.5*Nc*Ns
#   no pad byte
#
#   Note: ADPCM data is specified in its uncompressed form in the above
#   fields (ADPCM: M = 2).  Sierra ADPCM is stored in 4 bits but decompresses
#   to 16 bits.  Therefore, in all the above calculations for ADPCM data,
#   the number of bytes per sample (M) should be 2 and not 0.5.
#   Thus, it seems apparent that Sierra decodes their ADPCM data to PCM data
#   themselves before sending it to DirectSound and this header should
#   reflect that.
#
#   Sierra ADPCM appears to be the same as IMA ADPCM but with reversed
#   high and low nibbles (reversed nibbles produces a bit more fry).
#   Even the decoding tables (index table and step table) are exactly the
#   same as IMA, as found in at least two games.
#
#   IMA ADPCM index table found in Sierra's MINIGOLF.EXE:
#   FF FF FF FF FF FF FF FF 02 00 04 00 06 00 08 00
#   FF FF FF FF FF FF FF FF 02 00 04 00 06 00 08 00
#
#   IMA ADPCM step table found in Sierra's MINIGOLF.EXE:
#   07 00 08 00 09 00 0A 00 0B 00 0C 00 0D 00 0E 00 10 00 11 00 13 00 15 00 
#   17 00 19 00 1C 00 1F 00 22 00 25 00 29 00 2D 00 32 00 37 00 3C 00 42 00 
#   49 00 50 00 58 00 61 00 6B 00 76 00 82 00 8F 00 9D 00 AD 00 BE 00 D1 00 
#   E6 00 FD 00 17 01 33 01 51 01 73 01 98 01 C1 01 EE 01 20 02 56 02 92 02 
#   D4 02 1C 03 6C 03 C3 03 24 04 8E 04 02 05 83 05 10 06 AB 06 56 07 12 08 
#   E0 08 C3 09 BD 0A D0 0B FF 0C 4C 0E BA 0F 4C 11 07 13 EE 14 06 17 54 19 
#   DC 1B A5 1E B6 21 15 25 CA 28 DF 2C 5B 31 4B 36 B9 3B B2 41 44 48 7E 4F 
#   71 57 2F 60 CE 69 62 74 FF 7F 
#
#   Caution: This is all by my own deductions and may change as more info
#   is found in more games.
#
# The following Linux and SoX commands will strip the WAX header and decode
# the Sierra ADPCM data into signed 16-bit PCM data:
#
#   tail -c +31 digi_001.wax | sox -t ima -r 22050 -c 1 -N - digi_001.s16
#
# You can find a tail.exe for DOS (to run with SoX for DOS) here:
#   http://sourceforge.net/projects/unxutils/files/unxutils/current/
# Look in /usr/local/wbin/
#
# To decode to WAV (or something else) just replace the .s16 extention with
# .wav (or another supported extension).
#
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
#import glob
import os
import struct
import subprocess

WAX_ID    = b"WAX:"
WAX_PCM   = 1
WAX_ADPCM = 4

if len(sys.argv) <= 1:
	sys.exit("Usage: wax421 <filename or glob like *.WAX>")

# Load up the files list to process.
#waxfiles = glob.glob(sys.argv[1])
# Globs on the command line get expanded on the command line.
if sys.argv[1] == "-nw":
	makeWaves = False
	waxfiles = sys.argv[2:]
else:
	makeWaves = True
	waxfiles = sys.argv[1:]

print("Beginning Sierra WAX ADPCM (type 4) to PCM (type 1) conversions:")

for waxfile in waxfiles:
	with open(waxfile, 'rb') as f:

		# Read the header.
		headdata = f.read(30)
		fields = struct.unpack("<4sIIHHIIHH2s", headdata)
		waxID,               \
			waxType,         \
			datasize,        \
			wFormatTag,      \
			nChannels,       \
			nSamplesPerSec,  \
			nAvgBytesPerSec, \
			nBlockAlign,     \
			wBitsPerSample,  \
			ckID             = fields

		if waxID != WAX_ID:
			print(waxfile, "is not WAX audio.  Skipping.")
			continue

		# Read the rest of the file, then close it to rename it.
		audiodata = f.read()

	wavname = waxfile + ".wav"
	#wavname = waxfile.rsplit(".", maxsplit=1)[0] + ".wav"

	# For quick testing, make WAVs out of files to check original quality.
	if waxType == WAX_PCM:
		if makeWaves:
			print(waxfile, "transcoding WAX type 1 to test WAV", wavname)
			if wBitsPerSample <= 8:
				foo = subprocess.check_output(
					["sox",
					 "-t", "raw", "-e", "unsigned-integer",
					     "-r", str(nSamplesPerSec), "-c", str(nChannels), "-b", str(wBitsPerSample), "-",
					 "-t", "wav", wavname ],
					input=audiodata )
			else:
				foo = subprocess.check_output(
					["sox",
					 "-t", "raw", "-e", "signed-integer",
					     "-r", str(nSamplesPerSec), "-c", str(nChannels), "-b", str(wBitsPerSample), "-",
					 "-t", "wav", wavname ],
					input=audiodata )
			continue
	elif waxType == WAX_ADPCM:
		#if makeWaves: #We have to do a test conversion to WAV to check nChannels.
			foo = subprocess.check_output(
				["sox",
				 "-t", "ima", "-N", "-r", str(nSamplesPerSec), "-c", str(nChannels), "-",
				 "-t", "wav", "-e", "signed", wavname ],
				input=audiodata )
	else:
		print(waxfile, "is not a recognizable WAX type.  Skipping.  !WARNING!")
		continue

	# Grab the actual number of channels SoX found in the WAV conversion.
	with open(wavname, "rb") as ff:
		ff.seek(22)
		data = ff.read(2)
		wavChannels, = struct.unpack("<H", data)
		if wavChannels != nChannels:
			print(waxfile,
				"header indicates {} channels, {} found.  Fixing.  CAUTION".format(nChannels, wavChannels))

	# Now that we have the info we need, delete the WAV if we don't want it.
	# We went to a file instead of a stdout buffer because SoX writes some
	# header data (such as length) after it writes and gives a warning
	# regarding this when using stdout.
	if makeWaves:
		print(waxfile, "encoding WAX type 4 to PCM test WAV", wavname)
	else:
		os.remove(wavname)

	# Backup the original WAX file before writing a new one.
	bakname = waxfile + ".4"
	os.rename(waxfile, bakname)
	print(waxfile, "renamed to", bakname, "for processing")

	# Call SoX to decode the raw ADPCM into raw, signed, 16-bit PCM.
	# Args must be separate elements in a list.  Py docs not helpful here.
	pcmdata = subprocess.check_output(
		["sox",
		 "-t", "ima", "-N", "-r", str(nSamplesPerSec), "-c", str(wavChannels), "-",
		 "-t", "s16", "-" ],
		input=audiodata )

	# Write the decoded data from SoX to a new WAX file.
	print(" `--> writing new", waxfile)
	with open(waxfile, "wb") as ff:
		# Build the new header and recalc the values
		# because some files have 8-bit values in their header.
		# Worse, some files claim 2 channels when they have 1.
		# WAV doesn't like odd number of samples so PCM Ns may grow by 1 (2B).
		headdata = struct.pack("<4sIIHHIIHH2s",
								waxID,
								WAX_PCM,
								len(pcmdata),                 #datasize,
								1,                            #wFormatTag,
								wavChannels,                  #nChannels,
								nSamplesPerSec,
								nSamplesPerSec*2*wavChannels, #nAvgBytesPerSec,
								2*wavChannels,                #nBlockAlign,
								16,                           #wBitsPerSample,
								ckID )
		ff.write(headdata)
		ff.write(pcmdata)

print("fin")
