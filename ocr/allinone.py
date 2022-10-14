# -*- coding: latin-1 -*-
OSX = True

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

def pageCount(pdfPath):
    count = None
    if OSX:
        data = NSData.dataWithContentsOfFile_(pdfPath)
        img = NSPDFImageRep.imageRepWithData_(data)
        count = img.pageCount()
    else:
        regexp = re.compile(r"/Type\s*/Page([^s]|$)", re.MULTILINE|re.DOTALL)
        data = file(pdfPath, "rb").read()
        count = len(regexp.findall(data))
    return count

def bucket(seed, data, chosen, replacement):
    queue = [seed]
    while len(queue) > 0:
        if len(queue) > 500:
            return False 
        pos = queue.pop(0)
        (c, r) = pos
        data[c, r] = replacement
        for n in [(c - 1, r), (c + 1, r), (c, r + 1), (c, r - 1)]:
            if n in queue:
                continue
            else:
                value = None
                (c, r) = n
                try:
                    value = data[c, r]
                except:
                    pass
                if value is not None and value == chosen:
                    queue.append(n)
    return True

def extractTableImage(inputfile, outputfile):
    pixels = numpy.array(Image.open(inputfile))
    (width, height, channels) = numpy.shape(pixels)
    black = 0
    white = 255
    cut = 255 / 2
    colorful = 10
    gray = 192
    result = numpy.zeros((width,height), numpy.uint8)

    for column in xrange(width):
        for row in xrange(height):
            raw = pixels[column, row]
            r = int(raw[0])
            g = int(raw[1])
            b = int(raw[2])
            avg = (r + b + g) / 3
            d = [ int(fabs(r - g)), int(fabs(r - b)), int(fabs(g - b))]
            if max(d) > colorful or raw[3] == 0: # colorful and transparent ones go to while
                result[column, row] = white
            elif max(d) == 0: # a true gray
                if r > 0.9 * gray and r < 1.1 * gray: # neither very bright nor very dark
                    result[column, row] = white # erase                
            else: # for all other pixels, we binarize by the average
                if avg < cut: 
                    result[column, row] = 0 # black
                else:
                    result[column, row] = white
    maskHeight = 50
    maskWidth = 3
    for column in xrange(3 * width / 4, width - maskWidth):
        for row in xrange(3 * height / 4, height - maskHeight):
            zone = result[column : column + maskWidth, row : row + maskHeight]
            total = numpy.sum(zone)
            if total == black: 
                if bucket((column, row), result, black, white): # make all lines white
                    data = Image.fromarray(result)
                    data.save(outputfile)
                    return True
                else:
                    # too much black for this page to contain a table
                    return False
    # no line grid start position was found; hence no table was detected
    return False

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
# accented2ASCII = {'á': 'a', 'é': 'e','í': 'i', 'ó': 'o', 'ú': 'u', 'ñ': 'n'}
accented2ASCII = {'\xe1': 'a', '\xe1': 'e','\xed': 'i', '\xf3': 'o', '\xfa': 'u', '\xf1': 'n'}
accented2HTML = {'\xe1': '&aacute;', '\xe1': '&eacute;','\xed': '&iacute;', '\xf3': '&oacute;', '\xfa': '&uacute;', '\xf1': '&ntilde;'}
# accented2HTML =  {'á': '&aacute;', 'é': '&eacute;','í': '&iacute;', 'ó': '&oacute;', 'ú': '&uacute', 'ñ': '&ntilde', \
#                  'Á': '&Aacute;', 'É': '&Eacute;','Í': '&Iacute;', 'Ó': '&Oacute;', 'Ú': '&Uacute;', 'Ñ': '&Ntilde;'}

def text2HTML(text):
    for symbol in accented2HTML:
        replacement = accented2HTML[symbol]
        text = text.replace(replacement)
    return text

freeReplacement = set()
for pair in confusingPairs:
    f = pair[0]
    s = pair[1]
    freeReplacement.add((f, s))
    freeReplacement.add((s, f))
for f in accented2ASCII:
    s = accented2ASCII[f]
    freeReplacement.add((f, s))
    freeReplacement.add((s, f))

omissions = ['ENTIDAD', 'FEDERATIVA', 'REV.', 'CIE 10']

def ignore(text):
    global omissions
    n = len(text)
    for word in omissions:
        umbral = min(len(word), n)
        d = editdist(text, word)
        if d < 3:
            return True
    return False

def editdist(firstWord, secondWord, lower=False):
    global freeAddition, freeElimination, freeReplacement, accented2ASCII
    if lower:
        first = firstWord.lower()
        second = secondWord.lower()
    else:
        first = firstWord
        second = secondWord
    lf = len(first) + 1
    ls = len(second) + 1
    previous = range(lf)
    for s in range(ls - 1):
        ss = second[s].encode('utf-8')
        if ss in accented2ASCII:
            ss = accented2ASCII[ss]
        current = [0] * lf
        current[0] = s + 1
        for f in range(lf - 1):
            ff = first[f].encode('utf-8')
            if ff in accented2ASCII:
                ff = accented2ASCII[ff]
            a = previous[f + 1] + (1 - (ss in freeAddition))
            b = current[f] + (1 - (ss in freeElimination))
            c = previous[f] + (1 - (ff == ss or (ff, ss) in freeReplacement or (ss, ff) in freeReplacement))
            current[f + 1] = min([a, b, c])
        previous = current
    return current[-1]

statenames = {'Aguascalientes': 'AGU', 'Baja California': 'BCN', 'Baja California Sur': 'BCS', 'Campeche': 'CAM', \
          'Chiapas': 'CHP', 'Chihuahua': 'CHH', 'Coahuila': 'COA', 'Colima': 'COL', 'Distrito Federal': 'DIF', \
          'Durango': 'DUR', 'Guanajuato': 'GUA', 'Guerrero': 'GRO', 'Hidalgo': 'HID', 'Jalisco': 'JAL', \
          'Mexico': 'MEX', 'Michoacan': 'MIC', 'Morelos': 'MOR', 'Nayarit': 'NAY', 'Nuevo Leon': 'NLE', \
          'Oaxaca': 'OAX', 'Puebla': 'PUE', 'Queretaro': 'QUE', 'Quintana Roo': 'ROO', 'San Luis Potosi': 'SLP', \
          'Sinaloa': 'SIN', 'Sonora': 'SON', 'Tabasco': 'TAB', 'Tamaulipas': 'TAM', 'Tlaxcala': 'TLA', \
          'Veracruz': 'VER', 'Yucatan': 'YUC', 'Zacatecas': 'ZAC' }
known = {'ENTIDAD', 'FEDERATIVA', 'CUADRO', 'TOTAL'}
threshold = 20

commonErrors = {"SJr": "Sur"}
shortWords = ["a", "y", "o", "la", "el", "del", "de", "por", "Sur", "sur", "Roo", "roo", "CIE", "REV", "San", "Por", "A"]

class wordbox:

    def checkState(self, staterow, states):
        for state in states:
            d = editdist(state, self.content, lower=True)
            if d < 3:
                self.content = states[state]
                del states[state]
                staterow[state] = self
#                print "Matched", state, self.content.encode('utf-8')
                return 1
        return 0
            
    def __init__(self, coordstr, content):
        tokens = coordstr.split()
        self.xul = int(tokens[0])
        self.yul = int(tokens[1])
        self.xlr = int(tokens[2])
        self.ylr = int(tokens[3])
        self.x = (self.xul + self.xlr) / 2
        self.y = (self.yul + self.ylr) / 2
        self.content = content.strip()
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
        return '%s' % self.content.encode('utf-8')

    def __repr__(self):
        return str(self)

    def same(self, following):
        global threshold
        if self.content is None or following.content is None:
            return False
        if self.content[-1].isdigit() != following.content[0].isdigit():
            return False
        sep = following.xul - self.xlr
        return sep < threshold

    def sameRow(self, other):
        if self.content is None or other.content is None:
            return False
        global threshold
        below = fabs(other.ylr - self.ylr)
        above = fabs(self.yul - other.yul)        
        return (below < threshold and above < threshold)

    def sameCol(self, other):
        if self.content is None or other.content is None:
            return False
        global threshold
        inside = (self.xul <= other.xul and self.xlr >= other.xlr) \
             or (other.xul <= self.xul and other.xlr >= self.xlr)
        left = fabs(other.xlr - self.xlr)
        right = fabs(self.xul - other.xul)
        return (inside or left < threshold or right < threshold)

    def merge(self, other, staterow, space = False):
        for state in staterow:
            if staterow[state] == other:
                staterow[state] = self
        if not space and self.content[-1].isdigit() and other.content[0].isdigit():
            self.content = '%s%s' % (self.content, other.content) # numbers are joined
        else:
            self.content = '%s %s' % (self.content, other.content) # words are spaced               
        self.xlr = max(self.xlr, other.xlr)
        self.xul = min(self.xul, other.xul)
        self.ylr = max(self.ylr, other.ylr)
        self.yul = min(self.yul, other.yul)
        self.n = len(self.content) # update

    def compress(self):
        if self.content.find(' ') > 0:
            global shortWords, commonErrors
            replacement = ''
            for piece in self.content.split():
                separator = ' '
                if piece in commonErrors:
                    piece = commonErrors[piece]
                if len(piece) < 4 and (not piece[0].isdigit()) and piece not in shortWords:
                    separator = ''
                replacement = '%s%s%s' % (replacement, separator, piece)
            self.content = replacement.strip().lstrip()
        return

tags = ['div', 'p', 'html', 'title', 'meta', 'head', 'body', 'doctype', '?xml']

def parse(inputfile, outputfile):
    global statenames, known, tags
    staterow = dict()
    states = statenames.copy()
    starts = ['TOTAL']
    for state in states:
        starts.append(states[state])
    expected = len(states)
    try:
        # input = open(inputfile, 'r')
        input = codecs.open(inputfile, 'r', 'utf-8')
    except:
        print >>stderr, 'No input file to parse', inputfile
        return False

    skip = list()
    for tag in tags:
        skip.append(tag + '>')
        skip.append('<' + tag)

    upper = None
    lower = None
    title = None
    body = None

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
                    content = token[token.index('">') + 2 : -2].strip()
                    content = content.replace('-', ' ')
                    content = content.replace(',', ' ')
                    content = content.replace('<em>', ' ')
                    content = content.replace('</em>', ' ')
                    content = content.replace('<strong>', ' ')
                    content = content.replace('</strong>', ' ')
                    content = content.strip()
                    if len(content) > 0:
                        if 'bbox' in token:
                            start = token.index('bbox')
                            end = token[start : ].index('"')
                            bbox = token[start + 5: start + end]
                            word = wordbox(bbox, content)
                            if editdist(content, 'Aguascalientes') < 3:
                                body = word
                            if editdist(content, 'FEDERATIVA') < 3:
                                upper = word
                            elif editdist(content, 'TOTAL') < 2:
                                lower = word
                            if not ignore(content):
                                words.append(word)
    input.close()
    rows = dict()
    for word in words: # assign each word to a row
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
        word = row.pop(0)
        while len(row) > 0:
            other = row.pop(0)
            if word.same(other):
                word.merge(other, staterow)
            else:
                word.compress()
                clean.append(word)
                if 'hasta la semana epidem' in word.content:
                    title = word
                word = other
        rows[key] = clean

    if title is None: # wrong type of table
        return 

    kind = dict()
    r = dict()
    for key in rows:
        row = rows[key]
        if len(row) == 0:
            continue # skip empty ones, if any
        y = list()
        for word in row:
            expected -= word.checkState(staterow, states)
            y.append((word.yul + word.ylr) / 2.0) # center y coordinate

        m = sum(y) / (1.0 * len(y))
        r[m] = row

        if title.ylr < m and  upper.ylr > m:
            kind[m] = 'label'
        elif m < upper.ylr - threshold:
            kind[m] = 'header'
        elif m > lower.yul + threshold:
            kind[m] = 'footer'
        elif m > upper.ylr and m < body.yul:
            kind[m] = 'legend'
        else: # main data
            kind[m] = 'data'

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
        print >>output, text2HTML(header.encode('utf-8'))
        print >>output, '#', ' '.join(years)

        for d in xrange(0, nl):
            descr = '# %d:' % (d + 1)
            for word in sorted(ds[d], key = operator.attrgetter('y')):
                descr = '%s %s' % (descr, word.content)
            print >>output, text2HTML(descr.encode('utf-8'))

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
                    text = text2HTML(str(cell.encode('utf-8')))
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
        print >>output, text2HTML(footer.encode('utf-8'))
        output.close()
        return True
    else:
        print >>stderr, '%d states missing; this page does not contain a proper table' % expected
        if expected < len(statenames):
            print >>stderr, states
        return False

def processPage(filename, basename, page):
    global semaphore
    with semaphore:
        inputfile = '%s[%d]' % (filename, page)
        outputfile = '%s.%d.pre.png' % (basename, page)
        if not os.path.isfile(outputfile) and not os.path.isfile(outputfile + '.fail'): 
            try:
                check_call(['/usr/local/bin/convert', \
                            '-quality', '100', '-density', '300', '-sharpen', '0x1.0', '-trim', inputfile, outputfile])
            except:
                print >>stderr, 'Image extraction failed for page %d.' % (page + 1)
                check_call(['touch', outputfile + '.fail'])
                return False
        inputfile = outputfile
        outputfile = '%s.%d.png' % (basename, page)
        if not os.path.isfile(outputfile) and not os.path.isfile(outputfile + '.fail'): 
            if extractTableImage(inputfile, outputfile):
                print >>stderr, 'Identified a potential table on page %d.' % (page + 1)
            else:
                print >>stderr, 'No table detected on page %d.' % (page + 1)
                check_call(['touch', outputfile + '.fail'])
                return False
        inputfile = outputfile
        outputfile = '%s.%d' % (basename, page)
        if not os.path.isfile(outputfile + '.html') and not os.path.isfile(outputfile + '.fail'): 
            try:
                check_call(['/usr/local/bin/tesseract', inputfile, outputfile, '-l',  'spa', 'hocr'])
            except:
                print >>stderr, 'Unable to complete OCR on page %d.' % (page + 1)
                check_call(['touch', outputfile + '.fail'])
                return False
        inputfile = outputfile + '.html'
        outputfile = '%s.%d.csv' % (basename, page)
        if not os.path.isfile(outputfile) and not os.path.isfile(outputfile + '.fail'): 
            if parse(inputfile, outputfile):
                return True
            print >>stderr, 'The table on page %s is not the desired kind.' % (page + 1)
            check_call(['touch', outputfile + '.fail'])
    return

def processFile(filename, prefix=''):
    (result, goodToGo) = checkFor(filename, 'pdf', prefix)
    if not goodToGo:
        if result is not None:
            return result
        return None
    filename = result
    count = pageCount(filename)
    print >>stderr, 'Extracting tables from a %d-page %s' % (count, filename)
    basename = filename[:-4]
    filestart = time()
    pages = list()
    global CPUs
    pool = multiprocessing.Pool(CPUs)
    for page in xrange(0, count):
        pool.apply_async(processPage, [filename, basename, page])
    pool.close()
    pool.join()
    print >>stderr, "Completed the processing of %s." % filename
    return ''

def checkFor(filename, extension, prefix=''):
    filename = filename.strip()
    if len(filename) == 0: # empty line
        return ('', False)
    if filename[-1] == ':':
        prefix = filename[2:-1] + '/'
        if len(prefix) != 5: # the proper directories are named by years
            return (None, False)
        return (prefix, False)
    elif filename[-len(extension):] != extension:
        return (None, False)
    return ('%s%s' % (prefix, filename), True)

def listing():
    opentag = {True: '<th>', False: '<td>'}
    closetag = {True: '</th>', False: '</td>'}
    print '<html><head><title>Cuadros de boletines epidemiol&oacute;gicos</title></head><body>'
    prefix = ''
    for filename in check_output(['ls', '-1R']).split('\n'):
        (result, goodToGo) = checkFor(filename, 'pdf', prefix)
        if not goodToGo:
            if result is not None:
                prefix = result
            continue
        if len(prefix) != 5:
            continue
        filename = result
        basename = filename[:-4]
        cut = basename.find('/')
        if not cut >= 0:
            continue
        a = None
        try:
            a = int(basename[:cut])
        except:
            continue
        d = basename.find('.')
        s = None
        try:
            s = int(basename[cut + 4:d])
        except:
            continue
        count = pageCount('%s.pdf' % basename)
        for page in xrange(count):
            try: 
                data = open('%s.%d.csv' % (basename, page))
                print '<h1>Boletin Epidemiol&oacute;gico &mdash; <em>A&ntilde;o %d, semana %d</em></h1>' % (a, s)
                print '<h2>P&aacute;gina %d</h2>' % (page + 1)
                for line in data.readlines():
                    if line[0] == '#':
                        if line.find("FUENTE") >= 0:
                            print '</table>'
                        print '<p>%s</p>' % line.strip()
                    else:
                        print '<tr>'
                        tokens = line.split(',')
                        header = False
                        if tokens[0] == "ENTIDAD FEDERATIVA":
                            header = True
                            print '<table>'
                        for token in tokens:
                            print '%s%s%s' % (opentag[header], token, closetag[header])
                        print '</tr>'
            except:
                pass
    print '</body></html>'
    return

def main():
    prefix = ''
    for filename in check_output(['ls', '-1R']).split('\n'):
        result = processFile(filename, prefix)
        if result is not None:
            if len(result) > 0:
                prefix = result
    listing()
    return

if __name__ == '__main__':
    main()
