#! /usr/bin/python3
###############################################################################
# fixnames.py
# Fix output from HHPMod where topic names are lost and mangled in the RTF.
# by mj.Jernigan, May 2019
#
# Usage: python3 fixnames.py
#
# Run from the folder above the html folder.
#
# Expects a file, fixnames.csv, in the form of: badname,goodname
# This CSV should be in the current directory.
#
# Sometimes topic names in the RTF source are mangled and don't translate
# through the HHW and HHPMod processes.  This is most likely due to a bug in
# HELPDECO as far as I can tell, since I can't find any hint of the mangling
# in the MVB file.
#
# This script helps automate the renaming work but you must still find and
# supply the bad and good names.  The HHP and CNT files help, but not fully.
# You will likely need to find the actual context-sensitive topic names in
# the game source somewhere, and/or view the command line of calls to
# MVIEWER2.EXE with a tool like Sysinternals Process Explorer.
#
###############################################################################
# RBXIT - Really Basic sIerra Tools (the X is x'd out)
# Copyright (C) 2019  mj.Jernigan
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
from pathlib import Path
import csv

# Make fixnames.csv manually by column editing two HHP files.
# Should be in the form of: oldname,newname
# Or, in other words: badname,goodname
# No filename suffixes.
fixnames = []
with open("fixnames.csv", encoding="cp1252", newline="") as f:
	csvReader = csv.reader(f)
	for row in csvReader:
		if row[0]:
			fixnames.append(row)


# Rename files that match a filename to be corrected.
for p in Path("./html").glob("*.htm"):

	for row in fixnames:
		checkme = Path("./html/{}.htm".format(row[0]))
		if checkme.exists() and p.samefile(checkme):
			print("Renaming {}.htm to {}.htm".format(row[0], row[1]))
			p.rename("./html/{}.htm".format(row[1]))
			break


# Replace any text that matches filenames to be corrected.
for suffix in ["hhp", "hhk", "htm*", "map"]:

	for p in Path(".").glob("**/*.{}".format(suffix)):

		with p.open("r+", encoding="cp1252", newline="") as f:

			text = f.read()
			textnew = text
			for row in fixnames:
				textnew = textnew.replace(row[0], row[1])
			if text != textnew:
				print("Modified", p)
				f.seek(0)
				f.write(textnew)
				f.truncate()
