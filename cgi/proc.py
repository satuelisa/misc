#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cgitb; cgitb.enable()
from hashlib import md5
import codecs
import cgi, os
import glob
import os
from datetime import datetime
from random import shuffle, randint, choice, sample, random
from math import log, ceil, floor, sqrt, factorial
from collections import defaultdict
from fractions import Fraction
from copy import deepcopy
import string
import sys

DEBUG = False

from simplejson import load

tipo = {'mc': 'Medio curso',
        'ord': 'Ordinario',
        'xord': 'Extraordinario'}
prefix = {'mc': 'mc', 'ord': 'eo', 'xord': 'xo'}
separator = '@@@'
mark = '$'

def grade(filename, response, trial, kind):
    exam = None
    with open(filename, encoding='utf-8') as data:
        exam = load(data)
    expires = datetime.strptime(exam['expires'], '%Y-%m-%d %H:%M:%S.%f')
    if not trial and expires < datetime.now():
        print('<html><body>Este examen ya expir&oacute; ({:s}). Entregas posteriores no se califican. Cuenta como NP.</body></html>'.format(str(expires)))
        return None, None, None
    sel = [int(s) for s in exam['selection'].split('_')]
    n = len(sel)
    responses = [s for s in response.split(separator)]
    results = []
    correct = []
    i = 0
    with open(f't{kind}.c') as data:
        p = 0
        for line in data:
            parts = line.split(separator)
            fields = [s.strip() for s in parts[-1].split()]
            line = parts[0]
            while mark in line:
                pos = line.index(mark)
                f = fields.pop(0)
                if i < n and p == sel[i]:
                    correct.append(f)
                    left = ''.join(responses[i].split())
                    right = ''.join(correct[-1].split()) # whitespace insensitive
                    results.append(left == right)
                    i += 1
                line = line[(pos + 1):]
                p += 1
    return results, correct, responses

def main():
    print("Content-type: text/html\n\n")
    kind = None
    mod = None
    trial = True
    response = None
    h = None
    pin = None
    matr = None
    try:
        form = cgi.FieldStorage()
        kind = form.getvalue('kind').strip().lower()
        mod = form.getvalue('mod').strip().lower()
        trial = 't' in mod
        response = form.getvalue('resp').strip()
        h = form.getvalue('hash').strip().lower()
        with open('/var/www/html/elisa/data/reg.txt') as reg:
            for line in reg:
                line = line.strip()
                if len(line) == 0:
                    continue
                else:
                    tokens = line.split()
                    if len(tokens) == 2:
                        if h == tokens[0]:
                            matr = tokens[1]
                            break
            if matr is None:
                print('<html><body>La informaci&oacute;n enviada no corresponde a una matr&iacute;cula registrada.</body></html>')
                return
        if not trial:
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
                            submit = tokens[2]
                            if m == matr:
                                if pin == submit:
                                    ok = True
                                    break
                                else:
                                    print('<html><body>Clave incorrecta. La profesora tiene las claves de entrega. Consulte con ella.</body></html>')
                                    return
                if not ok:
                    print('<html><body>Clave inexistente. Consulta con la profesora.</body></html>')
                    return                    
    except:
        print('<html><body>Datos incorrectos, favor de revisar.</body></html>')
        return
    filename = '/var/www/html/elisa/teaching/prog/ansic/data/exam/{:s}{:s}_{:s}.json'.format('trial/' if trial else '', h, kind)
    if os.path.isfile(filename):
        store = filename.replace('.json', '_graded.json')
        if not trial and os.path.isfile(store):
            print('<html><body>Este examen ya ha sido calificado. No se permite reintentar cuando no es un examen de pr&aacute;ctica.</body></html>')
            return
        results, correct, responses = grade(filename, response, trial, kind)
        if correct is None:
            return            
        else:
            output = '{{"graded":"{:s}",\n'.format(str(datetime.now()))
            output += '"response":"{:s}",\n'.format(separator.join(responses))
            pts = ''.join(['1' if r else '0' for r in results])
            output += '"points":"{:s}"}}'.format(pts)
            with codecs.open(store, "w", "utf-8-sig") as target:
                target.write(output)
            n = len(results)
            if not trial:
                with open('/home/elisa/html/data/exams_pe.txt', 'a') as record:
                    print('{:s} {:s}{:s}'.format(matr, prefix[kind], pts), file = record)
            print('''<html><head><LINK rel="stylesheet" type="text/css" href="https://elisa.dyndns-web.com/teaching/result.css"></head><body><h1>Resultado de examen</h1>''')
            print('<h2>Matr&iacute;cula: {:s}</h2>'.format(matr))
            print('<h2>Tipo de examen: {:s}</h2>'.format(tipo[kind]))
            if trial:
                print('<p><em><span style="color:red">Examen de pr&aacute;ctica sin validez para la calificaci&oacute;n final</span></em></p>')
            print('<h3><span style="color:blue">Se otorgaron {:d} puntos de un total de 20 por las preguntas 1&ndash;20</span></h3>'.format(sum(results[:20])))
            if n == 40:
                print('<h3><span style="color:blue">Se otorgaron {:d} puntos de un total de 20 por las preguntas 21&ndash;40</span></h3>'.format(sum(results[20:])))
            print('<ol>')
            exam = None
            with open(filename, encoding='utf-8') as data:
                exam = load(data)
            for i in range(n):
                result = f'<li>Pusiste <code>{responses[i]}</code> y se esperaba <code>{correct[i]}</code>. La respuesta es '
                result += '<span style="color:green">correcta</span>' if results[i] else '<span style="color:red">incorrecta</span>' + '.</li>'
                print(result)
            print('''</ol>
<p>El resultado <strong>ha sido guardado</strong> en el servidor. Se puede cerrar esta p&aacute;gina sin p&eacute;rdida de datos.</p>
</body></html>''')
            if trial:
                print('''<p>Siendo un examen de pr&aacute;ctica, se permite intentar nuevamente con el mismo examen, 
tomando en cuenta que se borran las selecciones previamente hechas al regresar a la p&aacute;gina anterior.</p>''')
    else:
        print('<html><body>Imposible de calificar; avisar a la profesora.</body></html>')
        return                            
    return
      
if __name__ == "__main__":
    main()
