# -*- coding: latin-1 -*-
OSX = False

absoluteWidthFactor = 1.0 / 3930
absoluteHeightFactor = 1.0 / 5343
absoluteCharacterWidth = 70
absoluleCharacterHeight = 90
absoluteLineLength = 70
absoluteThousandsSep = 25
absoluteWhitespaceSep = 30

thousandsSep = absoluteThousandsSep * absoluteWidthFactor
whitespaceSep = absoluteWhitespaceSep * absoluteWidthFactor
characterWidth = absoluteCharacterWidth * absoluteWidthFactor
tolerance = absoluteCharacterHeight * absoluteHeightFactor

if OSX:
    from Foundation import NSData
    from AppKit import NSPDFImageRep

import Image
import numpy
from math import fabs
from sys import stderr, argv
import operator
import itertools
from subprocess import check_call, check_output
from time import time
import os.path
import codecs
import multiprocessing
import re

CPUs = multiprocessing.cpu_count()
semaphore = multiprocessing.Semaphore(CPUs)
head = None
foot = None
title = None
body = None


def within(wb, r, both=False):
    (start, end) = r
    x1 = wb.xul
    x2 = wb.xlr
    if both:
        return (x1 >= start and x2 <= end) or (start <= x1 and x2 >= end)
    else:
        return (x1 >= start and x2 <= end) 

def detectColumns(rows, kind, type):
    cols = dict()
    ranges = dict()
    words = list()
    for key in rows:
        row = rows[key]
        if kind[key] == type:
            words += row

    for word in sorted(words, key = operator.attrgetter('n'), reverse = True):
        placed = False
        for other in cols:
            if other.sameCol(word) or within(word, ranges[other], type == "header"):
                cols[other].append(word) # add to existing column
                (start, end) = ranges[other]
                ranges[other] = (min(start, word.xul), max(end, word.xlr))
                placed = True
                break
        if not placed:
            cols[word] = [word] # a new column
            ranges[word] = (word.xul, word.xlr) # its horizontal range
    return cols

freeAddition = {' '}
freeElimination = {' '}
confusingPairs = ['oc', 'o0', 'l1']
accented2ASCII = {'\xe1': 'a', '\xe1': 'e','\xed': 'i', '\xf3': 'o', '\xfa': 'u', '\xf1': 'n'}

freeReplacement = set()
for pair in confusingPairs:
    f = pair[0]
    s = pair[1]
    freeReplacement.add((f, s))
    freeReplacement.add((s, f))

def editdist(firstWord, secondWord, lower=False):
    if lower:
        first = firstWord.lower()
        second = secondWord.lower()
    else:
        first = firstWord
        second = secondWord
    first = first.replace(' ', '')
    second = second.replace(' ', '')
    lf = len(first) + 1
    ls = len(second) + 1
    previous = range(lf)
    for s in range(ls - 1):
        ss = second[s]
        current = [0] * lf
        current[0] = s + 1
        for f in range(lf - 1):
            ff = first[f]
            a = previous[f + 1] + (1 - (ss in freeAddition))
            b = current[f] + (1 - (ss in freeElimination))
            c = previous[f] + (1 - (ff == ss or (ff, ss) in freeReplacement or (ss, ff) in freeReplacement))
            current[f + 1] = min([a, b, c])
        previous = current
    return current[-1] / (1.0 * max(ls, lf))

statenames = {'Aguascalientes': 'AGU', 'Baja California': 'BCN', 'Baja California Sur': 'BCS', 'Campeche': 'CAM', \
          'Chiapas': 'CHP', 'Chihuahua': 'CHH', 'Coahuila': 'COA', 'Colima': 'COL', 'Distrito Federal': 'DIF', \
          'Durango': 'DUR', 'Guanajuato': 'GUA', 'Guerrero': 'GRO', 'Hidalgo': 'HID', 'Jalisco': 'JAL', \
          'Mexico': 'MEX', 'Michoacan': 'MIC', 'Morelos': 'MOR', 'Nayarit': 'NAY', 'Nuevo Leon': 'NLE', \
          'Oaxaca': 'OAX', 'Puebla': 'PUE', 'Queretaro': 'QUE', 'Quintana Roo': 'ROO', 'San Luis Potosi': 'SLP', \
          'Sinaloa': 'SIN', 'Sonora': 'SON', 'Tabasco': 'TAB', 'Tamaulipas': 'TAM', 'Tlaxcala': 'TLA', \
          'Veracruz': 'VER', 'Yucatan': 'YUC', 'Zacatecas': 'ZAC' }
known = {'ENTIDAD', 'FEDERATIVA', 'CUADRO', 'TOTAL'}

staterow = dict()
states = statenames.copy()
expected = len(states)

commonErrors = {"SJr": "Sur"}
shortWords = ["a", "y", "o", "la", "el", "del", "de", "por", \
              "Sur", "sur", "Roo", "roo", "CIE", "REV", "San", "Por", "A"]

class wordbox:

    def checkState(self):
        global states, expected, staterow, body
        remove = None
        for state in states:
            d = editdist(state, self.content, lower=True)
            if d < 0.5:
#                print 'Found', state
                expected -= 1
#                print 'Expecting', expected, 'more states, still'
#                print self.content
                self.content = states[state]
                remove = state
                staterow[state] = self
                break
        if remove is not None:
            del states[remove]
            if remove == 'Aguascalientes':
#                print 'Table body starts at', self
                body = self
                return True
        return False
            
    def __init__(self, coordstr, content):

        tokens = None
        try:
            tokens = coordstr.split()
        except: 
            print 'ERROR', coordstr
            return

        self.xul = None
        self.yul = None
        self.xlr = None
        self.ylr = None

        try:
            self.xul = int(tokens[0])
        except:
            print 'ERROR', tokens
            return
            
        try:
            self.yul = int(tokens[1])
        except:
            print 'ERROR', tokens
            return

        try:
            self.xlr = int(tokens[2])
        except:
            print 'ERROR', tokens
            return
            
        try:
            self.ylr = int(tokens[3])
        except:
            print 'ERROR', tokens
            return

        self.x = (self.xul + self.xlr) / 2
        self.y = (self.yul + self.ylr) / 2

        content = content.strip()
        ascii = content
        for c in content:
            if c in accented2ASCII:
                ascii = ascii.replace(c, accented2ASCII[c])
        content = ''
        for pos in xrange(len(ascii) - 1):
            content += ascii[pos]
            if ascii[pos].islower() and ascii[pos+1].isupper():
                content += ' '
        content += ascii[-1]
        self.content = content
        self.n = len(self.content)
        self.r = None
        self.c = None

    def row(self, row):
        self.r = row
        
    def col(self, col):
        self.c = col

    def debug(self):
        return '%s @ (%d, %d) -> (%d, %d)' % (self.content, self.xul, self.yul, self.xlr, self.ylr)

    def __str__(self):
        return '%s' % self.content

    def __repr__(self):
        return str(self)

    def sep(self, following):
        separation = (following.xul - self.xlr) / absoluteWidth
        if self.content[-1].isdigit() and following.content[0].isdigit():
            if separation <= thousandsSep:
                return '' # join the digits upon merge
            elif separation <= whitespaceSep:
                return ' ' # join with a whitespace
            else:
                return None # separate figures, do not merge
        if separation <= characterWidth:
            if len(self.content) < 4 and self.content not in shortWords:
                return '' # glue it together
            else:
                return ' '
        return None

    def sameRow(self, other):
        if self.content is None or other.content is None:
            return False
        t = 80
        below = fabs(other.ylr - self.ylr)
        above = fabs(self.yul - other.yul)        
        return (below < t and above < t)

    def sameCol(self, other):
        if self.content is None or other.content is None:
            return False
        return min(self.xlr, other.xlr) > max(self.xul, other.xul)

    def merge(self, other, separator):
        self.content = '%s%s%s' % (self.content.strip(), separator, other.content.strip())
        self.xlr = max(self.xlr, other.xlr)
        self.xul = min(self.xul, other.xul)
        self.ylr = max(self.ylr, other.ylr)
        self.yul = min(self.yul, other.yul)
        self.n = len(self.content) 

    def special(self):
        global body, head, foot, title
        if self.checkState():
            return
        if 'CUADRO' in self.content:
            title = self
            return
        if 'FUENTE' in self.content:
            foot = self
            return
        if editdist(self.content, 'FEDERATIVA') < 0.1:
            head = self
            return

tags = ['div', 'p', 'html', 'title', 'meta', 'head', 'body', 'doctype', '?xml']

def parse(inputfile, outputfile):
    starts = ['TOTAL']
    for state in states:
        starts.append(states[state])
    try:
        input = open(inputfile, 'r')
    except:
        print >>stderr, 'No input file to parse', inputfile
        return False

    skip = list()
    for tag in tags:
        skip.append(tag + '>')
        skip.append('<' + tag)

    words = list()
    for line in input.readlines():
        omit = False
        for token in skip:
            if token in line.lower():
                omit = True
                break
        if omit:
            continue
        if 'span' in line:
            tokens = line.split('span')
            for token in tokens:
                if 'ocrx_word' in token:
                    content = token[token.index('>') + 1 : -2].strip()
                    content = content.replace('<em>', ' ')
                    content = content.replace('</em>', ' ')
                    content = content.replace('<strong>', ' ')
                    content = content.replace('</strong>', ' ')
                    content = content.strip()
                    if len(content) > 0:
                        if 'bbox' in token:
                            start = token.index('bbox')
                            end = token.index(';')
                            bbox = token[start + 5 : end]
                            words.append(wordbox(bbox, content))
    input.close()
    rows = dict()
    for word in words:
        placed = False
        for other in rows:
            if other.sameRow(word):
                rows[other].append(word) # add to existing row
                placed = True
                break
        if not placed:
            rows[word] = [word] # a new row

    for key in rows:
        row = sorted(rows[key], key = operator.attrgetter('x'))
        pos = 0
        clean = list()
        incr = 1
        if len(row) < 2:
            continue
        prev = row[0]
        pending = False
        for foll in row[1:]:
            s = prev.sep(foll)
            if s is not None:
                prev.merge(foll, s)
                pending = True
            else: 
                clean.append(prev)
                prev = foll
                pending = False
        if pending:
            clean.append(prev)
        rows[key] = clean
    for key in rows:
        for word in rows[key]:
            word.special()
    if head is None:
        print 'Header not identified'
        return
    if foot is None:
        print 'Footer not identified'
        return
    if body is None:
        print 'Table body not identified'
        return
    if title is None:
        print 'Title not identified'
        return
    kind = dict()
    r = dict()
    for key in rows:
        row = rows[key]
        if len(row) == 0:
            continue 
        y = list()
        for word in row:
            y.append((word.yul + word.ylr) / 2.0) # center y coordinate
        m = sum(y) / (1.0 * len(y))
        r[m] = row
        if title.ylr < m and head.ylr > m:
            kind[m] = 'label'
        elif m < head.ylr - tolerance:
            kind[m] = 'header'
        elif m > foot.yul + tolerance:
            kind[m] = 'footer'
        elif m > head.ylr and m < body.yul:
            kind[m] = 'legend'
        else: # main data
            kind[m] = 'data'
            
    # print 'Grouping into columns'
    rows = None # no longer needed
    data = detectColumns(r, kind, 'data')
    label = detectColumns(r, kind, 'label')
    header = list()
    footer = '#'
    header = '#'
    legend = list()
    number = 0
    keys = sorted(r.keys())

    for key in keys:
        row = r[key]
        k = kind[key]
        if k == 'data':
            for word in row:
                word.row(number)
            number += 1
        elif k == 'header':
            for word in row:
                if 'CUADRO' in word.content :
                    header += '\n#'
                header += ' ' + word.content
        elif k == 'footer':
            for word in row:
                footer += ' ' + word.content
        elif k == 'legend':
            legend += row
        elif k == 'label':
            x = 0
            found = False
            for word in row:
                if 'excepto' in word.content:
                    found = True
                    break
                x += 1
            if found:
                for p in xrange(x + 1, len(row)):
                    w = row[p]
                    w.content = 'excepto ' + w.content
    years = set()
    weekly = None
    for word in legend:
        if word.n == 4 and '20' in word.content or '19' in word.content:
            years.add(word.content)
        elif word.content == 'Sem.':
            weekly = word
    nr = number
    weeklyCol = -1
    c = dict()
    for key in data:
        col = sorted(data[key], key = operator.attrgetter('y'))
        x = list()
        for word in col:
            x.append((word.xul + word.xlr) / 2.0) # center
        m = sum(x) / (1.0 * len(x))
        c[m] = col
    keys = sorted(c.keys())
    number = 0
    for key in keys:
        col = c[key]
        if len(col) > 0:
            for word in col:
                if weekly is not None and weeklyCol == -1 and word.sameCol(weekly):
                    weeklyCol = number
                word.col(number)
            number += 1
    c = None
    nc = number    
    l = dict()
    for key in label:
        col = sorted(label[key], key = operator.attrgetter('y'))
        x = list()
        for word in col:
            x.append((word.xul + word.xlr) / 2.0) # center
            if '.D' in word.content:
                word.content = word.content.replace('.D', 'J0')
        m = sum(x) / (1.0 * len(x))
        l[m] = col
    keys = sorted(l.keys())
    number = 0
    ds = dict()
    for key in keys:
        col = l[key]
        if len(col) > 0:
            for word in col:
                word.col(number)
            ds[number] = col
            number += 1
    nl = number

    if expected == 0: # found all the states, prepare a CSV
        rownumber = dict()
        for state in staterow:
            rownumber[staterow[state].r] = state
        output = open(outputfile, 'w')
        print >>output, header
        print >>output, '#', ' '.join(years)
        for d in xrange(0, nl):
            descr = '# %d:' % (d + 1)
            for word in sorted(ds[d], key = operator.attrgetter('y')):
                descr = '%s %s' % (descr, word.content)
            print >>output, descr
        cells = list()
        for row in xrange(0, nr):
            cells.append(list())
            for col in xrange(0, nc):
                cells[row].append(None)
        for word in words:
            if word.r is not None and word.c is not None:
                cells[word.r][word.c] = word.content
        colHdr = 'ENTIDAD FEDERATIVA, '
        turns = ['M', 'F', 'Acum.']
        turn = 0
        d = 1
        for col in xrange(1, nc):
            if col == weeklyCol:
                colHdr += '%d: Sem., ' % d
            else:
                colHdr += '%d: %s, ' % (d, turns[turn])
                turn = (turn + 1) % len(turns)
                if turn == 0:
                    d += 1
        print >>output, (colHdr.strip())[:-1]
        sums = dict()
        errors = list()
        sumline = list()
        for row in xrange(0, nr):
            if row == nr - 1:
                name = 'TOTAL'
            else:
                name = ''
            if row in rownumber:
                name = statenames[rownumber[row]]
            line = '%s,' % name
            content = False
            for col in xrange(0, nc):
                cell = cells[row][col]
                s = '-,'
                if cell is not None:
                    number = None
                    text = cell
                    try:
                        number = int(text)
                    except:
                        continue
                    if number is not None:
                        s = '%d,' % number
                        content = True
                        if row < nr - 1:
                            if col not in sums:
                                sums[col] = 0
                            sums[col] += number
                        else: # last row
                            if col in sums:
                                error = number - sums[col]
                                sumline.append('%d' % sums[col])
                            else:
                                error = 0
                                sumline.append('')
                            if error > 0:
                                errors.append('%d' % error)
                            else:
                                errors.append('')
                line = '%s%s' % (line, s)
            if content:
                print >>output, line[:-1]
        print >>output, 'SUMA,%s' % ','.join(sumline)
        print >>output, 'ERROR,%s' % ','.join(errors)
        print >>output, footer
        output.close()
        return True
    else:
        print >>stderr, '%d states missing; this page does not contain a proper table' % expected
        if expected < len(statenames):
            print >>stderr, states
        return False

def process(filename):
    global semaphore
    with semaphore:
        print 'Processing', filename
        if parse(filename, '%s.csv' % filename):
            return True
        else:
            print 'Failure with %s.' % filename
    return

def main():
    global CPUs
    pool = multiprocessing.Pool(CPUs)
    for filename in check_output(['ls', '-1']).split('\n'):
        if filename[-4:] == '.xml':
            pool.apply_async(process, [filename])
    pool.close()
    pool.join()
    return

if __name__ == '__main__':
    main()
