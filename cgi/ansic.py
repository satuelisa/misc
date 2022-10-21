#!/usr/bin/env python3

import cgi, os
import cgitb; cgitb.enable()
from time import localtime, strftime
import datetime
from os import path, chmod
import random
from sys import argv
import hashlib
import string

def char(count, params):
    generated = list()
    alph = None
    try:
        alph = params[-1]
        print("Using alphabet", alph, file = stderr)
    except:
        alph = string.ascii_letters
    for x in range(count):
        cand = random.choice(alph)
        generated.append(cand)
    return generated

# discrete uniform distribution (integers)
def unid(count, params):
    start = int(params[0])
    end = int(params[1])
    generated = list()
    rep = True
    if params[-1] == "no":
        rep = False
    while len(generated) < count:
        cand = random.randint(start, end)
        if rep or cand not in generated:
            generated.append(cand)
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
    elif kind == 'char':
        for element in data:
            enforced.append('%s' % element)
    else: # float
        for element in data:
            enforced.append('%.3f' % float(element))
    return enforced

distributions = {"unid": unid, "unic": unic, 
                 "geom": geom, "norm": norm, 
                 "pois": pois, "bino": bino, 
                 "expo": expo, "char": char}
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
    student = student.strip()
    hashstr = hashlib.md5(student.encode("utf-8")).hexdigest()
    print(hashstr)
    expires =  (datetime.datetime.now() + datetime.timedelta(weeks=30)).strftime('%a, %d %b %Y %H:%M:%S GMT') 
    filename = f'/var/www/html/elisa/teaching/prog/ansic/data/{hashstr}.generated.xml'
    if not path.isfile(filename):
        with open(filename, 'w') as data:
            print("<xml>", file = data)
            with open('/var/www/html/elisa/data/ansic.txt') as template:
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
                        value = ' '.join(enforce(distributions[distrib](count, params), kind))
                        print(f'<field><id>{label}</id><value>{value}</value></field>', file = data)
            print("</xml>", file = data)
            with open(f'/var/www/html/elisa/teaching/prog/ansic/data/{hashstr}.awarded.xml', 'w') as tmp:
                print('<xml>\n</xml>', file = tmp)
            with open(f'/var/www/html/elisa/teaching/prog/ansic/data/{hashstr}.accepted.xml', 'w') as tmp:
                print('<xml>\n</xml>', file = tmp)
            with open(f'/var/www/html/elisa/teaching/prog/ansic/data/{hashstr}.rejected.xml', 'w') as tmp:
                print('<xml>\n</xml>', file = tmp)
            with open(f'/var/www/html/elisa/teaching/prog/ansic/data/{hashstr}.attempts.xml', 'w') as tmp:
                print('<xml>\n</xml>', file = tmp)
    return

if __name__ == "__main__":
    main()
