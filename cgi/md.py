#!/usr/bin/env python3

LOC = '/var/www/html/elisa/'

import cgi, os
import cgitb; cgitb.enable()
from time import localtime, strftime
import datetime
import string
from os import path, chmod
import random
from sys import argv
import hashlib

def latexletter(params):
    first = params[0][0]
    last = params[1][0]
    while True:
        cand = random.choice(string.ascii_letters)
        if cand >= first and cand <= last:
            return cand

def number(params):
    start = int(params[0])
    end = int(params[1])
    res = random.randint(start, end)
    if params[-1] == 'odd':
        if res % 2 == 0:
            if res == start:
                res += 1
            else:
                res -= 1
    return '%s' % res

def binary(params):
    minimum = 2**int(params[0])
    maximum = 2**int(params[1])
    return bin(random.randint(minimum, maximum))[2:]

def latexbool(params):
    if random.random() > 0.5:
        return '0'
    return '1'

def array(params, sort = False):
    count = int(params[0])
    start = int(params[1])
    end = int(params[2])
    generated = set()
    while len(generated) < count:
        generated.add(random.randint(start, end))
    l = list(generated)    
    if sort:
        l.sort()
    s = ''
    for v in l:
        s += '%d ' % v
    return s[:-2]

def latexset(params):
    return array(params, True)

def polynomial(params):
    minimum = int(params[0])
    maximum = int(params[1])    
    degree = random.randint(minimum, maximum)
    p = ''
    for d in range(degree)[::-1]:
        term = '%d' % random.randint(2, 8)
        if d > 0:
            term += '<em>x</em>'
        if d > 1:
            term += '<sup>%d</sup>' % d
        if len(p) == 0:
            p = term
        else:
            p = '%s+%s' % (p, term)
    return p 

def function(params):
    return 'sqrt(<em>n</em><sup>%d</sup>)<em>n</em><sup>%d</sup>log%d<em>n</em><sup>%d</sup>' % \
        (random.randint(2, 5), random.randint(2, 5), \
        random.randint(2, 5), random.randint(2, 5))

def generator(name):
    possibles = globals().copy()
    possibles.update(locals())
    method = possibles.get(name)
    return method

def main():
    print('Content-type: text/html\n\n')
    student = None
    try:
        form = cgi.FieldStorage()
        student = form.getvalue('student')
    except:
        pass
    if student is None:
        try:
            student = argv[1] # debug mode
        except:
            return
    if student is None:
        return
    if '@' not in student or '.' not in student or ' ' in student:
        return
    student = student.strip()
    shash = hashlib.md5(student.encode("utf-8")).hexdigest()
    expires = \
        (datetime.datetime.now() + \
             datetime.timedelta(weeks=30)).strftime('%a, %d %b %Y %H:%M:%S GMT') 
    testfile = LOC + 'teaching/mat/discretas/data/%s.awarded.xml' % shash
    filename = LOC + 'teaching/mat/discretas/data/%s.generated.xml' % shash
    if path.isfile(testfile):
        print(shash, "old")
        return
    else: # new account
        with open(filename, 'w') as data:
            print("<xml>", file = data)
            with open(LOC + "/data/md.txt", 'r') as template:
                for line in template:
                    line = line.strip()
                    if len(line) == 0:
                        continue
                    tokens = line.split()
                    if tokens[0] == "#":
                        continue
                    else:
                        label = tokens[0]
                        gen = generator(tokens[1])
                        value = gen(tokens[2:])
                        print("<field><id>%s</id><value><![CDATA[%s]]></value></field>" % \
                              (label, value), file = data)
            print("</xml>", file = data)
            with open(LOC + 'teaching/mat/discretas/data/%s.awarded.xml' % shash, 'w') as tmp:
                print('<xml>\n</xml>', file = tmp)
            with open(LOC + 'teaching/mat/discretas/data/%s.accepted.xml' % shash, 'w') as tmp:
                print('<xml>\n</xml>', file = tmp)
            with open(LOC + 'teaching/mat/discretas/data/%s.rejected.xml' % shash, 'w') as tmp:
                print('<xml>\n</xml>', file = tmp)
            with open(LOC + 'teaching/mat/discretas/data/%s.attempts.xml' % shash, 'w') as tmp:
                print('<xml>\n</xml>', file = tmp)
            print(shash, "new")
    return

if __name__ == "__main__":
    main()
