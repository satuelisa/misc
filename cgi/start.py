#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from random import shuffle, randint, choice, sample, random
from math import log, ceil, floor, sqrt, factorial
from collections import defaultdict
from fractions import Fraction
import cgitb; cgitb.enable()
from datetime import datetime, timedelta, date
from copy import deepcopy
from hashlib import md5
import codecs
import string
import cgi, os
import glob
import os

mark = '$'
separator = '@@@'
count = dict()
options = dict()
kinds = ['mc', 'ord']
for exam in kinds:
    count[exam] = 0
    with open(f't{exam}.c') as data:
        for line in data:
            count[exam] += line.count(mark)
    options[exam] = [x for x in range(count[exam])] 

def generate(kind):
    if not kind in kinds:
        print('Not available yet')
        return None
    n = 20 if kind != 'xo' else 40
    sel = sample(options[kind], n)
    sel.sort()
    output = ''
    p = 0
    i = 0
    with open(f't{kind}.c') as data:
        for line in data:
            if line[-1] == '\n':
                line = line[:-1]
            line = line.replace('\\', '\\\\') # escape \ for json
            line = line.replace('/', '\\/') # escape / for json
            line = line.replace('"', '\\"') # escape " for json
            replacement = ''
            parts = line.split(separator)
            fields = [s.strip() for s in parts[-1].split()]
            line = parts[0]
            while mark in line:
                pos = line.index(mark)
                replacement += line[:pos]
                if i < n and p == sel[i]:
                    i += 1
                    replacement += '...'
                    fields.pop(0) # value not needed
                else:
                    replacement += fields.pop(0) # put the value instead
                line = line[(pos + 1):]
                p += 1
            replacement += line
            output += replacement + 'NEWLINE'
    assert output.count('...') == n  
    return (sel, output.replace(' ', 'WHITESPACE'))
    
def main():
    trial = True
    print("Content-type: text/html\n\n")
    matr = None
    correo = None
    kind = None
    pin = None
    try:
        form = cgi.FieldStorage()
        matr = form.getvalue('matr')
        if matr is not None:
            matr = matr.strip().lower()
        if matr is None or len(matr) != 7:
            print('<html><body>La matr&iacute;cula debe ser de siete d&iacute;gitos.</body></html>')
            return
        correo = form.getvalue('correo').strip().lower()
        if '@' not in correo:
            print('<html><body>Correo inv&aacute;lido. Favor de revisar</body></html>')
            return
        kind = form.getvalue('kind').strip().lower()
        mod = form.getvalue('mod').strip().lower()
        if 'r' in mod:
            trial = False
            pin = form.getvalue('pin').strip().lower()
            today = datetime.now().strftime('%d%m%Y')
            access = '/var/www/html/elisa/teaching/prog/ansic/data/exam/access/{:s}{:s}.lst'.format(kind, today)
            if not os.path.isfile(access):
                print('<html><body>En esta fecha no se presentan ex&aacute;menes de ese tipo. Se permite practicar, pero no presentar.</body></html>')
                return
            with open(access) as acc:
                ok = False
                for line in acc:
                    line = line.strip()
                    if len(line) == 0:
                        continue
                    else:
                        tokens = line.split()
                        if len(tokens) == 3:
                            m = tokens[0][:-1]
                            entry = tokens[1]
                            if m == matr:
                                if pin != entry:
                                    print('<html><body>Clave incorrecta. La profesora tiene las claves de acceso. Consulte con ella.</body></html>')
                                    return
                                else:
                                    ok = True
                                break
                if not ok:
                    print('<html><body>No existe clave con tus datos. Consulta con la profesora.</body></html>')
                    return                    
    except Exception as e:
        print('<html><body>Datos incorrectos, favor de revisar.', str(e) ,'</body></html>')
        return
    with open('/var/www/html/elisa/data/reg.txt') as reg:
        for line in reg:
            line = line.strip()
            if len(line) == 0:
                continue
            else:
                tokens = line.split()
                if len(tokens) == 2:
                    h = tokens[0]
                    m = tokens[1]
                    if m == matr:
                        if h != md5(correo.encode('utf-8')).hexdigest():
                            print('<html><body>Correo incorrecto para la matr&iacute;cula proporcionada. No se permite acceso.</body></html>')
                            return
                        else:
                            print('<html><title>Redireccionando al examen...</title>')
                            print('<meta http-equiv="refresh" content="3; https://elisa.dyndns-web.com/teaching/prog/ansic/exam.html?hash={:s}&kind={:s}&mod={:s}&time={:s}">'.format(h, kind, mod, str(datetime.now())))
                            print('</head><body>')
                            filename = '/var/www/html/elisa/teaching/prog/ansic/data/exam/{:s}{:s}_{:s}.json'.format('trial/' if trial else '', h, kind)
                            if trial or not os.path.isfile(filename):
                                print('Se est&aacute; generando un nuevo examen.')
                                output = '{{\n"kind":"{:s}",\n"created":"{:s}",\n'.format(kind, str(datetime.now()))
                                (opt, text) = generate(kind)
                                output += f'"content":"{text}",\n'
                                opt = '_'.join([str(s) for s in opt])
                                output += f'"selection":"{opt}",\n'
                                output += '"expires":"{:s}"\n}}'.format(str(datetime.now() + timedelta(minutes = 60))) # una hora
                                with codecs.open(filename, "w", "utf-8-sig") as target:
                                    target.write(output)
                                print('Se guardan las preguntas en el servidor.')                                                                    
                            else:
                                print('Un examen de este tipo ya ha sido generado.')                                
                            print('Est&aacute;s siendo redirigido para poder contestarlo.</body></html>')
                            return
        print('<html><body>La matr&iacute;cula proporcionada no cuenta con registro. No se permite acceso.</body></html>')
        return
    return
      
if __name__ == "__main__":
    main()
