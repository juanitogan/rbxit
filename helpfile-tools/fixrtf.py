#! /usr/bin/python3
###############################################################################
# fixrtf.py
# Fix RTF files
# by mj.Jernigan, Nov 2018
#
# Usage: python3 fixrtf.py <old.rtf> <new.rtf>
#
# Meant to fix RTF files that are unpacked from MVB (MediaViewer Book)
# help files.  "Fix" as in fix for running through Microsofts' HTML Help
# Workshop (HHW) with better success and more support for styling.
#
# Will be expanded to include RTF files from HLP files eventually.
#
# The RTF paragraph tag \par would most literally be converted to <br\>
# (as a terminator and not a wrapper)
# instead of <p></p>, but HHW understandably (I guess) didn't do this
# because it is messier for editing down the road with proper styling.
# But lots of whitespace formatting is lost by doing this.  Thus, working
# around this by forcing blank lines to come in as <p></p> as well.
# For better or for worse.
#
# Far from optimized.  While complex regexs that can slow the process down
# to several seconds or several minutes, have been eliminated, other
# performance possibilities were not engaged in if they would make the code
# even harder to read (such as reversing strings to do reverse lookups,
# or eliminating regexs in favor of loops with waaay more IF statements).
#
# Don't expect DRY code either.
# Don't expect DRY code either.
#
# Lots of contengency cases not handled.
# Written for only one RTF at this point, which has been pretty predictable.
#
# No fore-color changes checked for yet because the two fore colors found in
# this RTF represent the default color and the link color, which are best
# handled by elemental CSS.
# When handling more color, a list of colors to be ignored should be defined
# and only changes to and from the other colors tagged.  This list should
# include the default color, link color, and anything else easily handled by
# non-class CSS such as bullet color, etc.
# For example: ignore=1,2,4 >> ["cf1","cf2","cf4"]
#
# more later as this will be a never ending project with multiple tools
#
###############################################################################
# RBXIT - Really Basic sIerra Tools (the X is x'd out)
# Copyright (C) 2018  mj.Jernigan
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
import re

if len(sys.argv) <= 2:
	sys.exit("Usage: fixrtf <old.rtf> <new.rtf>")

# Get the filenames from the command line.
rtf = sys.argv[1]
out = sys.argv[2]

print("fixrtf: Pseudo-tagging '{}' into '{}'.".format(rtf, out))

# Regexs with ^ and $ tend to not run correctly in Windows Linux Ubuntu (WSL).

# If HHW tells you the DLLs aren't installed for RTF conversion,
# it really means you broke the RTF and not the install.

imagetag	= re.compile(r"\\\{ew[lcr] .*!")
zeroparent	= re.compile(r"\} 0:")
popup		= re.compile(r"!PopupID\(.*`(.*)>pop'\)")
#blankline	= re.compile(r"^(\\(par|trowd) *(\\[^ ]+ *)*)$")
#blankcell	= re.compile(r"^(\\(par|trowd) *(\\[^ ]+ *)*?)\\cell\\") # *? to make it non-greedy (lazy)
#pagefix	= re.compile(r"\\page *\xA0")
#rowfix		= re.compile(r"\\row *\xA0")

paragraph	= re.compile(r"\\(par|trowd)[\\\{ \n]")
cellEnd		= re.compile(r"\\(cell|par|trowd)[\\\{ \n]") # and other mid-line dividers
rowStart	= re.compile(r"\\trowd[\\\{ \n]")
rowEnd		= re.compile(r"\\row[\\\{ \n]")
pageEnd		= re.compile(r"\\page[\\\{ \n]")
content		= re.compile(r"( [^\\\{\}\n]| \\\{| \\\\)")

#alignment	= re.compile(r"\\(q[lcrj]|pard)[\\\{ \n]")
alignment	= re.compile(r"\\(q[lcrj]|pard)")
LEFT		= " .class.left."
CENTER		= " .class.center."
RIGHT		= " .class.right."
JUSTIFY		= " .class.justify."
DEFAULT		= ""
alignState	= DEFAULT
alignDefault= "ql" #TODO make a setting for this

#fontsize	= re.compile(r"\\(fs[0-9]+|plain)[\\\{ \n]") # misses "\plain\fs16"
fontsize	= re.compile(r"\\(fs[0-9]+|plain)")
FS			= " .class.fs{}." # kept changing my mind
fsState		= DEFAULT
fsDefault	= "fs20" #TODO make a setting for this

firstline	= re.compile(r"\\(fi[0-9-]+|pard)")
INDENT		= " .class.indent."
NOINDENT	= " .class.noindent."
HANGING		= " .class.hanging."
indentState	= DEFAULT
indentDefault = "fi0" #TODO make a setting for this

# Returns a different state if a new one is found in the given string.
def findAlignState(line):
	# Default to previous state.
	newState = alignState
	# Find the last alignment tag in a string, if there is one.
	allthat = alignment.findall(line)
	if allthat:
		if allthat[-1] in ["pard", alignDefault]:
			newState = DEFAULT
		elif allthat[-1] == "qc":
			newState = CENTER
		elif allthat[-1] == "qr":
			newState = RIGHT
		elif allthat[-1] == "qj":
			newState = JUSTIFY
		else:
			newState = LEFT
	return newState

# Returns a different state if a new one is found in the given string.
def findFontsizeState(line):
	# Default to previous state.
	newState = fsState
	# Find the last fs tag in a string, if there is one.
	allthat = fontsize.findall(line)
	if allthat:
		if allthat[-1] in ["plain", fsDefault]:
			newState = DEFAULT
		else:
			newState = FS.format(allthat[-1][2:])
	return newState

# Returns a different state if a new one is found in the given string.
# Just checks for type of indent and not size (should be good enough).
def findIndentState(line):
	# Default to previous state.
	newState = indentState
	# Find the last first-line indent tag in a string, if there is one.
	allthat = firstline.findall(line)
	if allthat:
		if allthat[-1] in ["pard", indentDefault]:
			newState = DEFAULT
		elif allthat[-1][2:3] == "-":
			newState = HANGING
		elif allthat[-1] == "fs0":
			newState = NOINDENT
		else:
			newState = INDENT
	return newState

def findAllStates(line):
	global alignState, fsState, indentState
	alignState = findAlignState(line)
	fsState = findFontsizeState(line)
	indentState = findIndentState(line)
	return alignState + fsState + indentState


with open(rtf, "rt", encoding="cp1252", newline=None) as f:
	with open(out, "wt", encoding="cp1252", newline="\r\n") as o:

		for line in f:
			
			# Convert MVB image tags {eml...} to HLP image tags {bmc...}.
			# Note: eml != bml (bml means left align AND wrap text around image).
			#       bmc seams to mean left align but no wrap (as in Clear?).
			line = imagetag.sub("\\{bmc ", line)
			#TODO only seen ewl so ew[lcr] is a guess and [cr] may need own logic

			# Replace the strange "0" parent keyword with nothing.
			line = zeroparent.sub("} ", line)

			# Convert popup links to regular links because these
			# don't convert to HTML without Active X controls and JS.
			line = popup.sub(r"\1", line)
			# NOTE: Popups can be auto-setup by HHPMod which post-processes an HHW import,
			# but it's a finicky tool keying on things like single underlines and
			# topics with an ID but no title.
			# Ignoring it for now until I can see a WORKING example in action.
			# Abandoning HHPMod because HHW doesn't preserve blank lines.
			# Update: NOT!  HHPMod is back in!
			# HHW wins the contest by converting many more link types and
			# consequently writing a more complete index file.
			#
			# NOTE: HTML attribute title="Tooltip text." is supported in CHM.
			# Line breaks can be done with actual breaks in the file (not "\n")
			# but no other styling.

			# Well, let's workaround those blank lines to force keeping them.
			# nbsp = \xA0 = \u00A0
			# NOTE: Python can't grok this: "\u00A0".encode("cp1252").decode()
			#       so you can't do this either: b"\xA0".decode()
			# Some regexs are REALLY SLOW in Python, so instead of doing all this in
			# complex re.sub() calls, break it up into more readable and faster pieces.
			parObj = paragraph.match(line)
			if parObj:

				# Also, parse alignment tags here.
				# The way this works, basically, as I recall, is:
				# Look for the last alignment tag among all lines
				# and store it as the latest alignment state for content
				# that has no immediate preceding tag.  (This is actually
				# done last on one line in prep for the next line.)
				# When content is found, however, first look backwards
				# to the beginning of the paragraph or cell for the last
				# alignment tag and, if one found, use it; else, default
				# that content to the latest stored state.
				# Finally, when content is found to have alignment other
				# than the default, insert a custom dot-tag for post-processing.
				#
				# And now, parse font size tags here.
				# And now, parse first-line indentation tags here.
				#
				#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
				# This might be easier if rewritten to just process all RTF \tags
				# and track state and content flags as they come in.
				# So goes the evolution of unplanned features in one-off tools.

				# Keep blank lines in cells too (and pars in cells).
				cellObj = cellEnd.search(line, parObj.end() - 1)
				# If there are table objects, it gets more complicated quickly.
				if cellObj:

					# If the last line in a cell is blank
					# (RTF line begins with \par followed by \cell
					# with no content between the two),
					# fill it.
					newTextShift = 0
					# Except that "\par \trowd" should not have a filler.
					if cellObj.group(1) != "trowd":
						# If there is no content between line start
						# and first cell divider, fill it.
						if not content.search(line, parObj.end() - 1, cellObj.start()):
							line = line[: cellObj.start()] + "\xA0" + line[cellObj.start() :]
							newTextShift += 1

					# Process all the cells in the line for alignment tags.
					prevCellObj = parObj #None
					#modPrevCellObjEnd = 0 if not prevCellObj else prevCellObj.end() - 1
					modPrevCellObjEnd = prevCellObj.end() - 1
					while cellObj:
						cellInnards = line[modPrevCellObjEnd : cellObj.start()]
						contentObj = content.search(cellInnards)
						if contentObj:
							# Tag alignment changes for later parsing in HTML
							# (to class tags for CSS).
							#TODO: Ignoring {bracketed {text}} for now due to abundant
							#      use of \pard.  But, really, it should be sliced out
							#      with an open-bracket-counting loop.
							# NOTE: Not sure setting global state is the best thing
							#       here since cells may have their own state???????
							states = findAllStates(cellInnards[: contentObj.start() + 1])
							if states:
								line = line[: modPrevCellObjEnd] + states + line[modPrevCellObjEnd :]
								newTextShift += len(states)
						# Don't forget to adjust start point according to text just added:
						modPrevCellObjEnd = cellObj.end() - 1 + newTextShift
						newTextShift = 0
						prevCellObj = cellObj
						cellObj = cellEnd.search(line, modPrevCellObjEnd)
					# Continue with having found the last cell terminator on the line.

					# If the first line in a cell breaks due to a \par
					# (which forces a new line in the RTF),
					# but that first line is not filled, fill it.
					# (Cell's don't need a \par unless they break for another line.)
					if not content.search(line, modPrevCellObjEnd):
						if not rowEnd.search(line, modPrevCellObjEnd):
							line = line[:-1] + "\xA0\n"
					else:
						# Look for final alignment tags if there is any trailing content.
						cellInnards = line[modPrevCellObjEnd :]
						contentObj = content.search(cellInnards)
						if contentObj:
							states = findAllStates(cellInnards[: contentObj.start() + 1])
							if states:
								line = line[: modPrevCellObjEnd] + states + line[modPrevCellObjEnd :]

				# Keep regular (non-table) blank lines.
				else:
					contentObj = content.search(line, parObj.end() - 1)
					if contentObj:
						states = findAllStates(line[parObj.end() - 1 : contentObj.start() + 1])
						if states:
							line = line[: parObj.end() - 1] + states + line[parObj.end() - 1 :]
					else:
						if not pageEnd.search(line, parObj.end() - 1):
							line = line[:-1] + "\xA0\n"

				# NOTE: Can't find cause of underlining in some tables cells
				#       in CyberStorm's Bioderm Biographies page.
				#       It's not in the RTF so something else must be triggering it.
				#       And, it only underlines the lowest line in the cell. Weird.

			# Handle outliers (like images or text after a mid-page {link}).
			else:
				if line[0] == "\\":
					contentObj = content.search(line, 2)
					if contentObj:
						states = findAllStates(line[0 : contentObj.start() + 1])
						if states:
							line = line[: contentObj.start() + 1] + states + line[contentObj.start() + 1 :]


			# Store final align state from lines not otherwise processed,
			# (due to CRs from "\row", "}", etc.)...
			# that maybe should be processed.
			# Maybe I should process page-to-page instead of by line.
			findAllStates(line)


			# stdout
			#print(line, end="", flush=True)

			o.write(line)


			####################################################################
			# Old sed script stuff for working around the many faults
			# in HelpScribble.
			# Not all of which can be overcome without a stupid level of effort.

			# Preserve the extended characters for later restoration ($ to &).
			# Because HelpScribble is stupid with these.
			##s/\\'85/\$hellip;/g
			#s/\\'91/\$lsquo;/g
			#s/\\'92/\$rsquo;/g
			#s/\\'93/\$ldquo;/g
			#s/\\'94/\$rdquo;/g
			#s/\\'96/\$ndash;/g
			#s/\\'97/\$mdash;/g
			##s/\\'[aA]9/\$copy;/g
			##s/\\'[eE]9/ ... accented e makes it through (as does copyright and ellipis)

			# Convert the mid-page targets to simpler HPJ form.
			# First, convert the double-line targets with a keyword def
			# (which can't be done in HelpScribble):
			##s/\\par \{\\up #\}.*\n.*\{\\up K\} (.*)}/\\par \{\\footnote \1\}/g
			# Then, convert the single-line targets:
			##s/\\par \{\\up #\}.*\{\\up #\} (.*)\}/\\par \{\\footnote \1\}/g
			#s/\\par(.*) \{\\up #\}.*\{\\up #\} (.*)\}/\\par\1 \{\\footnote \2\}/g
			# Kill the keywork def on these
			# (mid-page targets can't be keywords in HelpScribble):
			#s/^\{\\up K\}.*\{\\up K\} .*\}//

print("fixrtf: fin")
