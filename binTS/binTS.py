from random import random, choices
from PIL import Image, ImageDraw
from math import floor
from sys import argv

def canvas(n, r):
    w = r * n
    h = r
    return Image.new('RGBA', (w, h))

def stage(x, low, high):
    span = high - low
    return '{:02x}'.format(round(x * span + low))

def color(value, start, end):
    rLow = int(start[1:3], 16)
    gLow = int(start[3:5], 16)
    bLow = int(start[5:], 16)
    rHigh = int(end[1:3], 16)
    gHigh = int(end[3:5], 16)
    bHigh = int(end[5:], 16)
    r = stage(value, rLow, rHigh)
    g = stage(value, gLow, gHigh)
    b = stage(value, bLow, bHigh)
    return f'#{r}{g}{b}'
    
def gradient(data, r, a, start = '#00ffff', end = '#00cc00', curve = '#ff0000'): # cumulative series
    n = len(data)
    h = r * a
    c = canvas(n, h)
    d = ImageDraw.Draw(c)
    x = 0
    maximum = sum(data)
    level = 0
    yp = h
    xp = 0
    for bit in data:
        level += bit
        pos = level / maximum
        f = color(pos, start, end)
        d.rectangle([(x, 0), (x + r, h)], fill = f, outline = None, width = 0)
        p = h - round(pos * h)
        m = (2 * x + r) / 2
        if curve is not None:
            d.line([(xp, yp), (m, p)], fill = curve, width = 1)
        xp, yp = m, p
        x += r
    return c
        
def barcode(data, r, a, on = '#ff8000', off = '#6600cc'): # raw series
    n = len(data)
    h = r * a
    c = canvas(n, h)
    d = ImageDraw.Draw(c)
    x = 0
    for bit in data:
        f = on if bit else off
        d.rectangle([(x, 0), (x + r, h)], fill = f, outline = None, width = 0)
        x += r
    return c

def combo(data, r, a):
    n = len(data)
    m = int(floor(r / 2))    
    w = r * n + 2 * m
    h = 2 * (a * r) + 3 * m
    c = Image.new('RGBA', (w, h))
    c.paste(barcode(data, r, a) , (m, m))
    c.paste(gradient(data, r, a) , (m, (a * r)  + 2 * m))
    c.save('binTS.png')

def demo():
    n = 0 # data length in bits
    r = 0 # resolution unit: pixels per data point 
    a = 0 # aspect ratio: height-unit
    try:
        n = int(argv[1])
    except:
        n = int(input('Bit count: '))
    if n < 1:
        n = 128 # default length
    try:
        r = int(argv[2])
    except:
        r = int(input('Resolution unit: '))
    if r < 1:
        r = 32 # default resolution
    try:
        a = int(argv[3])
    except:
        a = int(input('Aspect ratio: '))
    if a < 1:
        a = 3 # default height ratio
    # use True/False to keep this didactive
    p = [0.1, 0.5, 0.9]
    w = [8, 2, 1]
    combo([random() < choices(p, weights = w, k = 1)[0] for i in range(n)], r, a) 
    
if __name__ == "__main__":
    demo()
    
