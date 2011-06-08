# -*- coding: utf-8 -*-
import os, sys, glob
#from PyQt4 import QtWebKit, QtGui
import logging
import os, sys, getopt
import glob
import subprocess
import logging
#import dicom

import Image, ImageChops

##
# Crop borders off an image.
#
# @param im Source image.
# @param bgcolor Background color, using either a color tuple or
# a color name (1.1.4 only).
# @return An image without borders, or None if there's no actual
# content in the image.


def autocrop(im, bgcolor):
    if im.mode != "RGB":
        im = im.convert("RGB")
    bg = Image.new("RGB", im.size, bgcolor)
    diff = ImageChops.difference(im, bg)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)
    print "kkkk"
    return None # no contents
    
img = Image.open("DLIA_TEST_CROPA.jpeg")
zz=autocrop(img,"#000")
zz.save("ggg.jpg")
    