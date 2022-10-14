#!/usr/local/bin/python2.7
import Image
import numpy
from math import fabs
from sys import argv

input = None
try: 
    input = argv[1]
except:
    print 'No input file is defined; therefore no output.'
    quit()

print 'Reading', input
png = Image.open(input).convert('RGBA')
png.load()
pixels = numpy.array(png)
(width, height, channels) = numpy.shape(pixels)

# colorful background fills must go to white and the enclosed text inverted
color = None
rgb = None
for column in xrange(width):
    for row in xrange(height):
        raw = pixels[column, row]
        r = int(raw[0])
        g = int(raw[1])
        b = int(raw[2])
        t = int(raw[3])
        if t != 0: # not transparent
            s = r + g + b
            d = [ int(fabs(r - g)), int(fabs(r - b)), int(fabs(g - b))]
            if color is None or max(d) > color:
                color = max(d)
                rgb = (r, g, b)
                break

black = 0
white = 255

xMin = None
xMax = None
yMin = None
yMax = None

if color < 10:
    print 'No colorful background present'
    rgb = None # no color detected
else:
    print 'Eliminating color fill', rgb

result = numpy.zeros((width,height), numpy.uint8)
for column in xrange(width):
    for row in xrange(height):
        raw = pixels[column, row]
        r = int(raw[0])
        g = int(raw[1])
        b = int(raw[2])
        t = int(raw[3])
        gray = (r + g + b) / 3
        if (r, g, b) == rgb:
            if xMin is None or column < xMin:
                xMin = column
            if xMax is None or column > xMax:
                xMax = column
            if yMin is None or row < yMin:
                yMin = row
            if yMax is None or row > yMax:
                yMax = row
        else: # other pixels go to grayscale
            if t == 0: # transparent tp white
                result[column, row] = white 
            else: # others to grayscale
                result[column, row] = gray

print 'Processing the colorful bounding box'
if rgb is not None:
    for column in xrange(xMin, xMax + 1):
        for row in xrange(yMin, yMax + 1):
            raw = pixels[column, row]
            r = int(raw[0])
            g = int(raw[1])
            b = int(raw[2])
            t = int(raw[3])
            if (r, g, b) == rgb: 
                result[column, row] = white # that color will become white
            else:
                result[column, row] = white - result[column, row] # invert grays inside the box

line = 100
remaining = list()
print 'Erasing vertical grid lines'
for column in xrange(width):
    for row in xrange(height):
        color = result[column, row]
        if color == black:
            ccount = 0
            pos = column
            while pos < width and result[pos, row] == black:
                pos += 1
                ccount += 1
            if ccount > line: # erase vertical lines
                for d in xrange(ccount):
                    result[column + d, row] = white
            else:
                remaining.append((column, row)) # still black
        elif color != white:
            if color > 128:
                result[column, row] = white
            else:
                result[column, row] = black


print 'Erasing horizontal grid lines'
for pixel in remaining:
    if len(remaining) % 100 == 0:
        print len(remaining), 'remaining'
    (column, row) = pixel
    if result[column, row] == black:
        rcount = 0
        pos = row
        while pos < height and result[column, pos] == black:
            pos += 1
            rcount += 1
        if rcount > line: # erase horizontal lines
            for d in xrange(rcount):
                result[column, row + d] = white

print 'Storing result'
data = Image.fromarray(result)
outfile = argv[2]
data.save(outfile)
print 'Result saved as', outfile
quit()
