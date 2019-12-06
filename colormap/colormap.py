# -*- coding: latin-1 -*-
import Image
import numpy
from random import randint
from subprocess import check_call
from math import ceil, log

def bucket(queue, data):
    chosen = list()
    while len(queue) > 0:
        pos = queue.pop(0)
        chosen.append(pos)
        (x, y) = pos
        for n in [(x - 1, y), (x + 1, y), (x, y + 1), (x, y - 1)]:
            if n in chosen:
                continue
            (c, r) = n
            try:
                if data[x, y] == (255, 255, 255): # white
                    if n not in queue:
                        queue.append(n)
            except:
                pass
    return chosen

def process(data, positions, map):
    read = open(data, 'r')
    dat = dict()
    minimum = float('Inf')
    maximum = float('-Inf')
    steps = None
    for line in read:
        line = line.strip()
        if len(line) > 0:
            tokens = line.split()
            label = tokens.pop(0)
            dat[label] = list() 
            if steps is None:
                steps = len(tokens)
            else:
                assert(steps == len(tokens))
            for token in tokens:
                value = int(token)
                if value < minimum:
                    minimum = value
                if value > maximum:
                    maximum = value
                dat[label].append(value)
    read.close()    
    read = open(positions, 'r')
    pos = dict()
    for line in read:
        line = line.strip()
        if len(line) > 0:
            tokens = line.split()
            pos[tokens[0]] = (int(tokens[1]), int(tokens[2]))
    read.close()

    i = Image.open(map)
    rgb = i.convert('RGB')
    pix = rgb.load()
    zone = dict()
    width = maximum - minimum
    for state in pos:
        print 'Locating state %s' % state
        (x, y) = pos[state]
        zone[state] = bucket([(x, y)], pix)
        
    digitos = int(ceil(log(steps, 10)))
    for t in xrange(steps):
        print 'Drawing step %d' % (t + 1)
        for state in dat:
            value = dat[state].pop(0)
            color = int(255.0 * (value - minimum) / width)
            for (x, y) in zone[state]:
                pix[x, y] = (color, 255 - color, 0)
        num = str(t)
        while len(num) < digitos:
            num = '0%s' % num
        rgb.save('t%s.png' % num)

def main():
    process("demo.txt", "states.txt", "colormap.png")
    check_call(['/usr/local/bin/convert', '-delay',  '35', '-loop', '1', 't*.png', 'colormap.gif'])
    return

if __name__ == '__main__':
    main()
