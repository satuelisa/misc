#!/usr/bin/env python3

LOC = '/var/www/html/elisa/'

import cgi, os
import cgitb; cgitb.enable()
import datetime
from os import path, chmod
import random
from sys import argv
import hashlib

# discrete uniform distribution (integers)
def unid(count, params):
    start = int(params[0])
    end = int(params[1])
    generated = list()
    for x in range(count):
        generated.append(random.randint(start, end))
    return generated

# continuous uniform distribution
def unic(count, params):
    start = float(params[0])
    end = float(params[1])
    generated = list()
    for x in range(count):
        generated.append(random.uniform(start, end))
    return generated

# geometric distribution
def geom(count, params):
    success = float(params[0])
    generated = list()
    for x in range(count):
        counter = 0
        while True:
            if random.random() < success:
                break
            counter += 1
        generated.append(counter)
    return generated

def norm(count, params):
    mu = float(params[0])
    sigma = float(params[1])
    generated = list()
    for x in range(count):
        generated.append(random.gauss(mu, sigma))
    return generated

def expo(count, params):
    lambd = float(params[0])
    generated = list()
    for x in range(count):
        generated.append(random.expovariate(lambd))
    return generated

def pois(count, params):
    lambd = float(params[0])
    generated = list()
    for x in range(count):
        sum = 0.0
        counter = 0
        while sum < 1.0:
            sum += random.expovariate(lambd)
            counter += 1
        generated.append(counter)
    return generated

def bino(count, params):
    attempts = int(params[0])
    success = float(params[1])
    generated = list()
    for x in range(count):
        counter = 0
        for trial in range(attempts):
            if random.random() < success:
                counter += 1
        generated.append(counter)
    return generated

def enforce(data, kind):
    enforced = list()
    if kind == 'int':
        for element in data:
            enforced.append('%d' % int(round(element)))
    else: # float
        for element in data:
            enforced.append('%.3f' % float(element))
    return enforced

distributions = {"unid": unid, "unic": unic, 
                 "geom": geom, "norm": norm, 
                 "pois": pois, "bino": bino, 
                 "expo": expo}
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
    hashstr = hashlib.md5(student.encode("utf-8")).hexdigest()
    print(hashstr)
    expires =  (datetime.datetime.now() + datetime.timedelta(weeks=30)).strftime('%a, %d %b %Y %H:%M:%S GMT') 
    filename = LOC + 'teaching/prob/data/%s.generated.xml' % hashstr
    if not path.isfile(filename):
        with open(LOC + 'teaching/prob/data/%s.awarded.xml' % hashstr, 'w') as tmp:
            print('<xml>\n</xml>', file = tmp)
        with open(LOC + 'teaching/prob/data/%s.accepted.xml' % hashstr, 'w') as tmp:
            print('<xml>\n</xml>', file = tmp)
        with open(LOC + 'teaching/prob/data/%s.rejected.xml' % hashstr, 'w') as tmp:
            print('<xml>\n</xml>', file = tmp)
        with open(LOC + 'teaching/prob/data/%s.attempts.xml' % hashstr, 'w') as tmp:
            print('<xml>\n</xml>', file = tmp)
        with open(filename, 'w') as data:
            print("<xml>", file = data)
            with open(LOC + 'data/template.txt') as template:
                for line in template:
                    line = line.strip()
                    if len(line) == 0:
                        continue
                    tokens = line.split()
                    if tokens[0] == "#":
                        continue
                    else:
                        label = tokens[0]
                        count = int(tokens[1])
                        distrib = tokens[2]
                        kind = tokens[3]
                        params = tokens[4:]
                        v = ' '.join(enforce(distributions[distrib](count, params), kind))
                        print("<field><id>%s</id><value>%s</value></field>" % (label, v), file = data)
            print("</xml>", file = data)
    return

if __name__ == "__main__":
    main()
