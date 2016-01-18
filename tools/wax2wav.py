#! /usr/bin/python3
###############################################################################
# wax2wav.py
# Sierra WAX to WAV transcoder
# by mj.Jernigan, Jan 2016
#
# Usage: python3 wax2wav.py <filename or glob like *.WAX>
#
# Requirements: SoX (Sound eXchange) tool from sox.sourceforge.net
#
# It is not unusual to see 1 or 2 ADPCM state errors from a WAX file like:
#   sox WARN adpcms: -: ADPCM state errors: 1
#
# See wax421.py for notes on the WAX file format.
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
#import os
import struct
import subprocess

WAX_ID    = b"WAX:"
WAX_PCM   = 1
WAX_ADPCM = 4

if len(sys.argv) <= 1:
	sys.exit("Usage: wax2wav <filename or glob like *.WAX>")

# Load up the files list to process.
#waxfiles = glob.glob(sys.argv[1])
# Globs on the command line get expanded on the command line.
waxfiles = sys.argv[1:]

print("Beginning Sierra WAX to MS WAV transcodings:")

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

	wavname = waxfile.rsplit(".", maxsplit=1)[0] + ".wav"

	# Pass the raw audio data to SoX for all the hard work.
	if waxType == WAX_PCM:
		print(waxfile, "transcoding WAX PCM to WAV PCM", wavname)
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
	elif waxType == WAX_ADPCM:
		print(waxfile, "transcoding WAX Sierra ADPCM to WAV IMA ADPCM", wavname)
		foo = subprocess.check_output(
			["sox",
			 "-t", "ima", "-N", "-r", str(nSamplesPerSec), "-c", str(nChannels), "-",
			 "-t", "wav", wavname ],
			input=audiodata )
	else:
		print(waxfile, "is not a recognizable WAX type.  Skipping.  !WARNING!")

print("fin")
