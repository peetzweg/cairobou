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


# global attributes
GAP = False
BIGGEST_SIDE = False
SMALLEST_SIDE = False

#####################
# Clipping Function #
#####################
def clipCircle(context, cx, cy, r):
	context.arc(cx, cy, r, 0, 2*math.pi)
	context.clip()

def clipCube(context, cx, cy, a):
	context.rectangle(cx - (a / 2), cy - (a / 2), a, a)
	context.clip()

def clipEquiTriangle(context, cx, cy, height):
	side = height / (math.sqrt(3.0) / 2)
	startX = cx - (side / 2)
	startY = cy + (height / 3.0)
	context.move_to(startX, startY)
	context.rel_line_to(side, 0)
	context.rel_line_to(-side/2, -height)
	context.line_to(startX, startY)
	context.clip()

#####################
# Creating Function #
#####################
def doTriangles(context, images):
	imageCount = len(images)

	triangleHeight = SMALLEST_SIDE
	cx = BIGGEST_SIDE/2.0
	cy = BIGGEST_SIDE/2.0 + (triangleHeight/6)

	loop = 0
	while triangleHeight > 50:
		image = images[loop % imageCount]

		clipEquiTriangle(context, cx, cy, triangleHeight)

		context.set_source_surface(image, 0, (BIGGEST_SIDE - cairo.ImageSurface.get_height(image))/2)
	
		context.paint()

		triangleHeight -= GAP
		loop += 1

def doCircles(context, images):
	imageCount = len(images)
	size = BIGGEST_SIDE
	radius = SMALLEST_SIDE / 2
	d = GAP
	loop = 0

	while radius > GAP:
		image = images[loop % imageCount]
	
		clipCircle(context, size/2, size/2, radius)

		context.set_source_surface(image, 0, (BIGGEST_SIDE-cairo.ImageSurface.get_height(image))/2)
		context.paint()

		radius -= d
		loop += 1

#########################
# Preparation Functions #
#########################
def createImageSurfaces(imagePaths):
	images = []
	for path in imagePaths:
		images.append(cairo.ImageSurface.create_from_png(path))
	return images

def determineImageSurface(imageSurfaces):
	logging.debug("Searching for the smallest and biggest side among given images")
	overallSmallest = sys.maxint
	overallBiggest = 0
	
	for image in imageSurfaces:
		width = cairo.ImageSurface.get_width(image)
		height = cairo.ImageSurface.get_height(image)

		imageSmallest = min(width, height)
		overallSmallest = min(overallSmallest, imageSmallest)

		imageBiggest = max(width, height)
		overallBiggest = max(overallBiggest, imageBiggest)

	logging.debug("Smallest: %d Biggest: %d", overallSmallest, overallBiggest)
	global SMALLEST_SIDE, BIGGEST_SIDE
	SMALLEST_SIDE = overallSmallest
	BIGGEST_SIDE = overallBiggest

def createContext(output, images):
	# determine the smallest side of all images and making the drawing surface slightly bigger
	global BIGGEST_SIDE
	size = BIGGEST_SIDE
	
	extension = os.path.splitext(output)[1]
	logging.debug("Creating %sSurface with the size of %d, %d", extension.upper(), size,size)
	
	surface = False
	if(extension == ".pdf"):
		surface = cairo.PDFSurface(output, size, size)
	elif(extension == ".svg"):
		surface = cairo.SVGSurface(output, size, size)

	context = cairo.Context(surface)
	return context

def main():
	# SetUp OptionParser
	usage = "usage: %prog [options] images*"
	parser = optparse.OptionParser(usage = usage)
	parser.add_option("-o", "--out", dest="out", type="string",
					help="specify output file", default="output.svg")
	parser.add_option("-g", "--gap", dest="gap", type="int",
					help="difference between the images", default=50)
	parser.add_option("-v", "--verbose", action="store_true",
					help="print status messages to stdout", default=False)
	parser.add_option("-d", "--debug", action="store_true",
					help="print status and debug messages to stdout", default=False)

	(options, imagePaths) = parser.parse_args()

	# checking if enough images are specified
	if(len(imagePaths)<1):
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
		logging.debug("Processing %d image(s):", len(imagePaths))
		for path in imagePaths:
			logging.debug("\t%s",str(path))
	elif(options.verbose):
		logging.basicConfig(format='%(message)s', level="INFO")

	# Storing global attributs
	global GAP
	GAP = options.gap

	images = createImageSurfaces(imagePaths)
	determineImageSurface(images)
	context = createContext(options.out, images)

	doCircles(context, images)
	#doTriangles(context, images)

	return 0

if __name__ == "__main__":
    sys.exit(main())
