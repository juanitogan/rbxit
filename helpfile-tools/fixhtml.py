#! /usr/bin/python3
###############################################################################
# fixhtml.py
# Fix HTML files from HWW via MVB RTF or HLP RTF
# by mj.Jernigan, Nov 2018
#
# Usage: python3 fixhtml.py <filename or glob like *.htm>
#
#        Must be run from same folder as *.htm files (for now).
#
# Output: Edits files in place (because they are just automated output from
#         from HHW) so back them up first if you really want.
#
# Requirements: lxml Python package from lxml.de
#               (built-in xml works only with well-formed xml [and html is not])
#
# Meant to post-process the HTML files that come out of Microsofts' HTML Help
# Workshop (HHW) to implement the hidden class tags that were embedded by
# fixrtf.py.
#
# Will also bring in image <map> elements from one of two sources:
#   (1) Look for a map along side the image file:  ../images/<image.img>.map
#     These are easiest made from scratch with GIMP (Filters > Web > Image Map).
#     image-map.net is also useful as an online tool for one-off work.
#     X-Map works okay but mostly through text editing (and not clicking the
#       map preview) but can also be useful for checking maps from others.
#     A plugin for paint.NET was started but only got as far as doing rectangles.
#     Those are the free tools - you can find the paid tools on your own.
#     (Note: I then had to re-edit for each language since filenames can change.
#       Thus, I had to search for GIF filenames or other identifiers in the HTML.
#       Files also appear to be in the same order in the HHP files regardless of name.)
#   Else, (2) look for a map along side the html file:  <htmlfile.htm>.map
#     This is for scraping maps using the free version of HelpScribble (HS):
#       Import an HPJ project, "Make" a CHM (with GIFs, unless your images are
#       >256 color--but this requires editing HHW or HS html to the final image type),
#       decompile that CHM with HHW, rename the files with maps in them to *.htm.map,
#       then copy those to the HHPMod output html folder.
#
# Maybe clean out other unneeded stuff as well
# (like the <object> thing I don't need).
#
# Works before or after HHPMod (update: sort of).
# Now, works best after HHPMod (esp, in the case of <htmlfile.htm>.map files).
#
# More later as this will be a never-ending project with multiple tools.
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
#import xml.etree.ElementTree as ET
import lxml.html

if len(sys.argv) <= 1:
	sys.exit("Usage: fixhtml <filename or glob like *.htm>")

# Get the filename(s) from the command line.
# Globs on the command line get expanded on the command line.
htmlfiles = sys.argv[1:]

print("fixhtml: Converting pseudo-tags to html tags in '{}' ...".format(sys.argv[1]))

# Regexs with ^ and $ tend to not run correctly in Windows Linux Ubuntu (WSL).

classtag	= re.compile(r"\.class\.([^\.]+)\.")
nbspfix		= re.compile(r"\xA0")


for htmlfile in htmlfiles:
	#tree = ET.parse(htmlfile)
	#tree = lxml.html.parse(htmlfile) #doesn't handle newline correctly
	#with open(htmlfile, "rt", encoding="cp1252", newline=None) as f:
	with open(htmlfile, "rb", newline=None) as f:

		tree = lxml.html.parse(f)
		root = tree.getroot()
		body = root.find("body")

		lastViableParent = None
		maps = []
		for e in body.iter("*"):

			# Is this an element that can hold the classes we want to set?
			if e.tag in ["p", "td"]:
				lastViableParent = e

			# Center align all tables.
			#TODO include personal notes on this
			#TODO make this optional
			elif e.tag == "table":
				e.set("align", "center")

			# Check images for image map elements to import.
			elif e.tag == "img":
				mapfile = None
				src = e.get("src")
				# Get the base filename.
				imgbasename = src.rsplit(".", maxsplit=1)[0].rsplit("/", maxsplit=1)[1]
				# First, look for an ../images/<image.img>.map file.
				if os.path.isfile(src + ".map"):
					mapfile = src + ".map"
				# If not found, look for an <htmlfile.htm>.map file.
				elif os.path.isfile(htmlfile + ".map"):
					mapfile = htmlfile + ".map"
				# If .map file found, look for a matching map element.
				#   <map name="imgbasename" ...>
				if mapfile:
					print("Map file found:", mapfile)
					with open(mapfile, "rb", newline=None) as m:
						# Cleanout GIMP (or other tool) comments.
						#mparser = lxml.html.HTMLParser(remove_blank_text=True, remove_comments=True)
						mparser = lxml.html.HTMLParser(remove_comments=True)
						mroot = lxml.html.parse(m, mparser).getroot()
						mapelement = mroot.find(".//map[@name='{}']".format(imgbasename))
						# If matching map el found, store it for later insertion.
						if mapelement is not None:
							mapelement.tail = "\n\n" # Format it.
							maps.append(mapelement)
							# Tag the image to use the found map.
							e.set("usemap", "#{}".format(imgbasename))
							print("Added map to image:", imgbasename)

			# Look for the custom class tag text.
			if e.text:
				newClasses = classtag.findall(e.text)
				if newClasses:
					# Tags found so set the class(es) and remove the tags.
					#lastViableParent.set("class", " ".join(newClasses)) #should get() first
					# Add to current classes (using new method from lxml).
					lastViableParent.classes |= newClasses
					e.text = classtag.sub("", e.text)
				# Replace all \x0A (cp1252 nbsp) with "&#8203;" (zero-width space)
				# to eliminate the aberration of underlined nbsp.
				# ZWSP requires IE7 and later (which is Win Vista era).
				e.text = nbspfix.sub("\u200b", e.text)
			# Check the tails of all the children as well.
			for child in e.findall("*"):
				if child.tail:
					newClasses = classtag.findall(child.tail)
					if newClasses:
						lastViableParent.classes |= newClasses
						child.tail = classtag.sub("", child.tail)
					child.tail = nbspfix.sub("\u200b", child.tail)

		# Clean up the HHW junk.
		for e in body.findall("object"):
			#TODO make this optional in case it is related to the optional JS popup stuff
			# NOTE: You can't modify the tree structure in an .iter().
			e.drop_tree()
		# Avoid map collisions.
		for e in body.findall("map"):
			# NOTE: You can't modify the tree structure in an .iter().
			e.drop_tree()

		# Insert any found map elements.
		for m in maps:
			body.insert(0, m)

		tree.write(htmlfile, encoding="cp1252", method="html")

print("fixhtml: fin")
