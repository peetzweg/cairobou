#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import math
import cairo
import optparse
import logging


# globale variables
g_options = False # command line options
g_images = False # images to process

# constants
INCH = 72 # 72 pixels (p) = 1 inch (in)
MM = INCH / 25.4 # 25.4 milimeters (mm) = 1 in
CM = INCH / 2.54 # 2.54 centimetes (cm) = 1 in
A4_WIDTH, A4_HEIGHT = INCH * 8.3, INCH * 11.7 # DIN A4 Paper is 297mm heigh and 210mm wide

def circle():
	image = cairo.ImageSurface.create_from_png(g_images[0])
	width = cairo.ImageSurface.get_width(image)
	height = cairo.ImageSurface.get_height(image)
	
	size = max(width, height)
	surface = cairo.PDFSurface(g_options.out, size, size)
	cr = cairo.Context(surface)

	imageCount = len(g_images)
	radius = min(width, height)/2
	d = 30
	loop = 0
	while radius > 50:
		image = cairo.ImageSurface.create_from_png(g_images[loop % imageCount])
		cr.arc(size/2, size/2, radius, 0, 2*math.pi)
		cr.clip()
		cr.set_source_surface(image, 0, height/4)
		cr.paint()

		radius -= d
		loop+=1

def main():
	# SetUp OptionParser
	usage = "usage: %prog [options] images*"
	parser = optparse.OptionParser(usage = usage)
	parser.add_option("-o", "--out", dest="out", type="string",
					help="specify output file", default="cairobou.pdf")

	parser.add_option("-v", "--verbose", action="store_true",
					help="print status messages to stdout", default=False)
	parser.add_option("-d", "--debug", action="store_true",
					help="print status and debug messages to stdout", default=False)
	global g_options
	global g_images
	(g_options, g_images) = parser.parse_args()

	# checking if enough images are specified
	if(len(g_images)<1):
		parser.error("At least one image has to be specified!")
		return 1

	# defining output
	if(g_options.debug):
		logging.basicConfig(format='%(message)s', level="DEBUG")
		# Printing Options for Debugging
		for option in parser.option_list:
			if(option.dest != None):
				logging.debug("%s = %s", option, getattr(g_options, option.dest))
		logging.debug("Processing %d image(s):", len(g_images))
		for image in g_images:
			logging.debug("\t%s",str(image))
	elif(g_options.verbose):
		logging.basicConfig(format='%(message)s', level="INFO")

	circle()

	return 0

if __name__ == "__main__":
    sys.exit(main())
