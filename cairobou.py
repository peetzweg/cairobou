#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os.path
import math
import cairo
import optparse
import logging

# constants
INCH = 72 # 72 pixels (p) = 1 inch (in)
MM = INCH / 25.4 # 25.4 milimeters (mm) = 1 in
CM = INCH / 2.54 # 2.54 centimetes (cm) = 1 in
A4_WIDTH, A4_HEIGHT = INCH * 8.3, INCH * 11.7 # DIN A4 Paper is 297mm heigh and 210mm wide

def clipCircle(context, cx, cy, r):
	context.arc(cx, cy, r, 0, 2*math.pi)
	context.clip()

def clipCube(context, cx, cy, a):
	context.rectangle(cx-(a/2), cy-(a/2), a, a)
	context.clip()

def clipSineWave(context, cx, cy , amplitude, width):
	start = cx - width/2
	end = cx + width/2

	context.move_to(start, cy)
	context.curve_to(cx-width/4,cy+amplitude, cx, cy, cx+width/4, cy-amplitude)
	context.set_line_width(30)
	context.stroke()
	context.clip()

def doIt(output, images):
	image = cairo.ImageSurface.create_from_png(images[0])
	width = cairo.ImageSurface.get_width(image)
	height = cairo.ImageSurface.get_height(image)
	
	size = max(width, height)
	extension = os.path.splitext(output)[1]
	surface = False
	if(extension == ".pdf"):
		surface = cairo.PDFSurface(output, size, size)
	elif(extension == ".svg"):
		surface = cairo.SVGSurface(output, size, size)

	cr = cairo.Context(surface)

	imageCount = len(images)
	radius = min(width, height)/2
	d = 30
	loop = 0

	while radius > 50:
		image = cairo.ImageSurface.create_from_png(images[loop % imageCount])
	
		#clipSineWave(cr, size/2, size/2,height/2,width)
		clipCircle(cr, size/2, size/2, radius)

		cr.set_source_surface(image, 0, height/4)
		cr.paint()

		radius -= d
		loop+=1

def main():
	# SetUp OptionParser
	usage = "usage: %prog [options] images*"
	parser = optparse.OptionParser(usage = usage)
	parser.add_option("-o", "--out", dest="out", type="string",
					help="specify output file", default="output.svg")
	parser.add_option("-v", "--verbose", action="store_true",
					help="print status messages to stdout", default=False)
	parser.add_option("-d", "--debug", action="store_true",
					help="print status and debug messages to stdout", default=False)

	(options, images) = parser.parse_args()

	# checking if enough images are specified
	if(len(images)<1):
		parser.error("At least one image has to be specified!")
		return 1

	# checking if output format is supported
	extension = os.path.splitext(options.out)[1]
	supported = [".pdf",".svg"]
	if(extension not in [".pdf",".svg"]):
		parser.error("Unsupported output format. Currently supported: "+", ".join(supported))
		return 1

	# defining output
	if(options.debug):
		logging.basicConfig(format='%(message)s', level="DEBUG")
		# Printing Options for Debugging
		for option in parser.option_list:
			if(option.dest != None):
				logging.debug("%s = %s", option, getattr(options, option.dest))
		logging.debug("Processing %d image(s):", len(images))
		for image in images:
			logging.debug("\t%s",str(image))
	elif(options.verbose):
		logging.basicConfig(format='%(message)s', level="INFO")
	
	doIt(options.out, images)

	return 0

if __name__ == "__main__":
    sys.exit(main())
