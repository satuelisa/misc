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

class Nodo:
 
    def __init__(self):
        self.contenido = None
        self.izquierdo = None
        self.derecho = None
        self.padre = None
        self.altura = None
        self.profundidad = None

    def alt(self):
        opt = [0]
        if self.izquierdo is not None:
            opt.append(self.izquierdo.alt())
        if self.derecho is not None:
            opt.append(self.derecho.alt())
        self.altura = max(opt) + 1
        return self.altura

    def ubicar(self, buscado, cual):
        if self.contenido == buscado:
            if cual == 'padre':
                return self.padre
            elif cual == 'izquierdo':
                return self.izquierdo
            elif cual == 'derecho':
                return self.derecho
            elif cual == 'altura':
                return self.altura
            elif cual == 'profundidad':
                return self.profundidad
        if buscado < self.contenido and self.izquierdo is not None:
            return self.izquierdo.ubicar(buscado, cual)
        if buscado > self.contenido and self.derecho is not None:
            return self.derecho.ubicar(buscado, cual)
        return None
        
    def prof(self, p):
        self.profundidad = p
        if self.izquierdo is not None:
            self.izquierdo.prof(p + 1)
        if self.derecho is not None:
            self.derecho.prof(p + 1)

    def hojas(self):
        conteo = 0
        if self.izquierdo is not None:
            conteo += self.izquierdo.hojas()
        if self.derecho is not None:
            conteo += self.derecho.hojas()
        if conteo == 0:
            return 1 # es hoja
        else:
            return conteo # es interno
    
    def agrega(self, elemento, padre = None):
        self.padre = padre
        if self.contenido is None:
            self.contenido = elemento
        else:
            if elemento < self.contenido:
                if self.izquierdo is None:
                    self.izquierdo = Nodo()
                self.izquierdo.agrega(elemento, self)
            if elemento > self.contenido:
                if self.derecho is None:
                    self.derecho = Nodo()
                self.derecho.agrega(elemento, self)
 
class Arbol:
 
    def __init__(self):
        self.raiz = None
 
    def __str__(self):
        return str(self.raiz)
 
    def __repr__(self):
        return str(self.raiz)
 
    def agrega(self, elemento):
        if self.raiz is None:
            self.raiz = Nodo()
        self.raiz.agrega(elemento)

    def calcula(self):
        self.raiz.alt()
        self.raiz.prof(0)

    def hojas(self):
        return self.raiz.hojas()

    def ubicar(self, valor, cual):
        obtenido = self.raiz.ubicar(valor, cual)
        if obtenido is not None:
            if cual in ['padre', 'izquierdo', 'derecho']:
                return obtenido.contenido
            else:
                return obtenido
        else:
            return 'no tiene'

def mst(E):
    cand = deepcopy(E)
    cost = 0
    comp = dict()
    t = set()
    while len(cand) > 0:
        e = min(cand.keys(), key = (lambda k: cand[k]))
        del cand[e] 
        (u, v) = e
        c = comp.get(v, {v})
        if u not in c:
            t.add(e)
            cost += E[e]
            new = c.union(comp.get(u, {u}))
            for w in new:
                comp[w] = new    
    return cost, t

def rw(A, limit, p = 0.5, rep = False):
    walk = [sample(A.keys(), 1)[0]]
    while random() < p and len(walk) < limit:
        curr = walk[-1]
        opt = A[curr]
        if len(opt) == 0:
            break
        cont = choice(list(opt))
        if rep or cont not in walk:
            walk.append(cont)
    return walk

def floyd_warshall(A, E): 
    d = {}
    for v in A:
        d[(v, v)] = 0 # distancia reflexiva es cero
        for u in A[v]: # para vecinos, la distancia es el peso
            if (v, u) in E:
                d[(v, u)] = E[(v, u)]
            elif (u, v) in E:
                d[(v, u)] = E[(u, v)]                
    for intermedio in A:
        for desde in A:
            for hasta in A:
                di = None
                if (desde, intermedio) in d:
                    di = d[(desde, intermedio)]
                ih = None
                if (intermedio, hasta) in d:
                    ih = d[(intermedio, hasta)]
                if di is not None and ih is not None:
                    c = di + ih # largo del camino via 'i'
                    if (desde, hasta) not in d or c < d[(desde, hasta)]:
                        d[(desde, hasta)] = c # mejora al camino actual
    return d

def dfs(seed, A):
    queue = [ seed ]
    comp = set()
    while len(queue) > 0:
        curr = queue.pop(0)
        comp.add(curr)
        for v in A[curr]:
            if v not in comp:
                if v not in queue:
                    queue.append(v)
    return comp
    
def comps(A):
    placement = dict()
    C = []
    for v in A.keys():
        if v not in placement:
            C.append(dfs(v, A))
            for u in C[-1]:
                placement[u] = v
    return C

from local import algs, probs

def binom(n, k): # a lo pendejo por hueva
    div = factorial(k) * factorial(n - k)
    return round(factorial(n) / div)

def primo(n):
    if n < 1:
        return False
    if n == 1 or n == 2:
        return True
    for div in range(2, ceil(sqrt(n)) + 1):
        if n % div == 0:
            return False
    return True

def digito(valor):
    if valor < 10:
        return str(valor)
    else: # letras a = 10, b = 11, c = 12, etc.
        return string.ascii_lowercase[valor - 10]
    
def convertir(decimal, base): # convertir un valor decimal a otra base
    potencia = 0
    while base**potencia <= decimal:
        potencia += 1
    digitos = ''
    pendiente = decimal
    while potencia > 0:
        potencia -= 1
        cuanto = base**potencia
        digitos += digito(pendiente // cuanto) # las veces que cabe indica el digito
        pendiente %= cuanto # lo que sobra se cubre con las potencias menores
    # verificamos que coincida con lo que dice la libreria estandar        
    assert decimal == int(digitos, base)
    return digitos

def gcd(a, b):
    if b == 0:
        return a
    else:
        mayor = max(a, b)
        menor = min(a, b)
        return gcd(menor, mayor % menor)

def fibo(n): # from F_0 up to F_n
    f = [0, 1] 
    while len(f) <= n:
        f.append(f[-1] + f[-2])
    return f

# https://www.tutorialspoint.com/data_structures_algorithms/expression_parsing_using_statck.htm
def postfix(expr, prec):
    resultado = []
    pila = []
    for pedazo in expr:
        if pedazo not in prec: # no es operador
            resultado.append(pedazo)
        else:
            if pedazo == '(': # abre subexpresion
                pila.append(pedazo)
            else:
                if pedazo == ')': # cierra subexpresion
                    while True:
                        siguiente = pila.pop(-1)
                        if siguiente == '(':
                            break
                        else:
                            resultado.append(siguiente)
                        if len(pila) == 0:
                            print('Hay una parentesis que no se cierra, no es posible evaluar.')
                            return None
                else:
                    if len(pila) == 0 or prec.index(pedazo) > prec.index(pila[-1]):
                        pila.append(pedazo)
                    else:
                        while len(pila) > 0 and prec.index(pedazo) <= prec.index(pila[-1]): 
                            resultado.append(pila.pop(-1))
                        pila.append(pedazo)
    return resultado + pila[::-1]

def valor(a, b, op):
    if op in 'AOXIE': # operador booleano binario
        if DEBUG:
            print(op)
        assert(a in '01' and b in '01') # acepta solamente bits
        if op == 'A': # and
            if a == '1' and b == '1': # ambos unos para que sea verdadero
                return '1'
            else:
                return '0'
        elif op == 'X': # xor
            if a != b: # con que sean diferentes
                return '1'
            else:
                return '0'
        elif op == 'E': # equivalencia
            if a == b: # con que sean iguales
                return '1'
            else:
                return '0'
        elif op == 'O': # or
            if a == '1' or b == '1': # con que hay por lo menos un uno
                return '1'
            else:
                return '0'
        else: # nada mas queda la implicacion como opcion
            assert op == 'I'
            if a == '0' or b == '1': # o no a o b
                return '1'
            else:
                return '0'
    elif op in '+-*/%': # aritmetica regular (de enteros en este caso)
        va = None
        vb = None
        try:
            va = int(a)
            vb = int(b)
        except:
            print('Se permite solamente enteros; no se puede evaluar de otra forma.')
            quit()
        if op == '+':
            return str(va + vb)
        elif op == '-':
            return str(va - vb)
        elif op == '*':
            return str(va * vb)
        if op in '/%':
            if vb == 0:
                print('No se puede realizar divisiones entre cero.')
                quit()
        if op == '/':
            return str(va // vb)
        if op == '%':
            return str(va % vb)
    else:
        print('Unexpected operator', op)

def boolean(expr, prec='EIXOA'): # toma como entrada la expresion en forma postfix
    prec = '()' + prec + 'N' # add defaults
    pfe = postfix(expr, prec)
    pila = []
    while len(pfe) > 0:
        if DEBUG:
            print(pila, pfe)
        if pfe[0] not in prec: # no es un operador
            pila.append(pfe.pop(0))
        else: # es un operador
            operador = pfe.pop(0)
            if operador == 'N': # unario
                v = pila.pop(-1)
                assert v in '01' # solamente para bits
                if v == '1': # voltear el valor
                    pila.append('0')
                else:
                    pila.append('1')                
            else: # los demas son binarios
                ladoDer = pila.pop(-1)
                ladoIzq = pila.pop(-1)
                v = valor(ladoIzq, ladoDer, operador)
                if DEBUG:
                    print(v)
                pila.append(v)
    return pila[0]

from simplejson import load

tipo = {'mc': 'Medio curso',
        'ord': 'Ordinario',
        'xord': 'Extraordinario'}
prefix = {'mc': 'mc', 'ord': 'eo', 'xord': 'xo'}

def grade(filename, response, trial):
    results = []
    exam = None
    with open(filename, encoding='utf-8') as data:
        exam = load(data)
    expires = datetime.strptime(exam['expires'], '%Y-%m-%d %H:%M:%S.%f')
    if not trial and expires < datetime.now():
        print('<html><body>Este examen ya expir&oacute; ({:s}). Entregas posteriores no se califican. Cuenta como NP.</body></html>'.format(str(expires)))
        return None
    lan = 0 if exam['language'] == 'spa' else 1 # eng
    questions = exam['questions']
    responses = [int(r) - 1 for r in response]
    if not exam['kind'] == 'ord':
        q = questions.pop(0)
        x1, x2, y1, y2 = q['data'][1:-1].split(',')
        x = floor(int(x1)/int(x2))
        y = ceil(int(y1)/int(y2))
        op = ' '.join(q['options'])
        order = [(op.index('geq'), x >= y),
                 (op.index('leq'), x <= y),
                 (op.index('>'), x > y),
                 (op.index('<'), x < y),
                 (op.index('='), x == y)]
        order.sort(key = lambda k: k[0])
        results.append(order[responses.pop(0)][1]) # q1
        q = questions.pop(0)
        o, n, b = q['data'][1:-1].split(',')
        c = log(int(n), int(b))
        if 'ceil' in o:
            c = ceil(c)
        else:
            c = floor(c)
        results.append(q['options'].index(str(int(c))) == responses.pop(0)) # q2
        q = questions.pop(0)
        a, b = q['data'][1:-1].split(',')
        c = int(a) % int(b)
        results.append(q['options'].index(str(int(c))) == responses.pop(0)) # q3
        q = questions.pop(0)
        n, b = q['data'][1:-1].split(',')
        c = int(n[1:-1], int(b))
        results.append(q['options'].index(str(int(c))) == responses.pop(0)) # q4
        q = questions.pop(0)
        n, b = q['data'][1:-1].split(',')
        c = int(n[1:-1], int(b))
        results.append(q['options'].index(str(int(c))) == responses.pop(0)) # q5
        q = questions.pop(0)
        b = int(q['data'], 2)
        c = oct(b)[2:]
        results.append(q['options'].index(c) == responses.pop(0)) # q6
        q = questions.pop(0)
        b = int(q['data'], 8)
        c = hex(b)[2:]
        results.append(q['options'].index(c) == responses.pop(0)) # q7
        q = questions.pop(0)
        n, b = q['data'][1:-1].split(',')
        c = str(convertir(int(n), int(b)))
        results.append(q['options'].index(c) == responses.pop(0)) # q8
        q = questions.pop(0)
        a, b = q['data'][1:-1].split(',')
        c = str(gcd(int(a), int(b)))
        results.append(q['options'].index(c) == responses.pop(0)) # q9
        q = questions.pop(0)
        e = q['data'].replace(' ', '')
        sat = []
        for op in q['options']:
            if 'ninguna' in op or 'none' in op:
                sat.append(None)
            else:
                a, b, c, d = 'a = \\top' in op, 'b = \\top' in op, 'c = \\top' in op, 'd = \\top' in op
                ex = e.replace('a', '1' if a else '0')
                ex = ex.replace('b', '1' if b else '0')
                ex = ex.replace('c', '1' if c else '0')
                ex = ex.replace('d', '1' if d else '0')
                sat.append(boolean(ex))
        sat[sat.index(None)] = '1' if not any([s == '1' for s in sat]) else '0'
        sat = [s == '1' for s in sat]
        results.append(sat[responses.pop(0)]) # q10    
        q = questions.pop(0)
        d  = q['data'].split(',')
        pr = d[0][2:-1].replace(' ', '')[::-1]
        e = d[1][2:-2].replace(' ', '')
        sat = []
        for op in q['options']:
            if 'ninguna' in op or 'none' in op:
                sat.append(None)
            else:
                a, b, c, d = 'a = \\top' in op, 'b = \\top' in op, 'c = \\top' in op, 'd = \\top' in op
                ex = e.replace('a', '1' if a else '0')
                ex = ex.replace('b', '1' if b else '0')
                ex = ex.replace('c', '1' if c else '0')
                ex = ex.replace('d', '1' if d else '0')
                sat.append(boolean(ex, pr))
        sat[sat.index(None)] = '1' if not any([s == '1' for s in sat]) else '0'
        sat = [s == '1' for s in sat]
        results.append(sat[responses.pop(0)]) # q11  
        q = questions.pop(0)
        a, b, c, d, e, f, d0, d1, o1, o2, o3 = q['data'][1:-1].split(',')
        dire = (d0[3:-1], d1[2:-2])
        iop = (o1[3:-1], o2[2:-1], o3[2:-2])
        bc = int(b) << int(c) if dire[0] == '<<' else int(b) >> int(c)
        ef = int(e) << int(f) if dire[1] == '<<' else int(e) >> int(f)
        left = int(a) & bc if '&' in iop[0] else int(a) | bc if '|' in iop[0] else int(a) ^ bc
        right = int(d) & ef if '&' in iop[2] else int(d) | ef if '|' in iop[2] else int(d) ^ ef
        corr = left & right if '&' in iop[1] else left | right if '|' in iop[1] else left ^ right
        results.append(q['options'].index(str(corr)) == responses.pop(0)) # q12 
        q = questions.pop(0)
        A = q['data'][1:-1].split(',')
        results.append(q['options'].index(str(len(A))) == responses.pop(0)) # q13
        q = questions.pop(0)
        a, s, l, c = q['data'][1:-1].split(',')
        desde = int(s)
        hasta = desde + int(l)
        if a[1] == '(':
            desde += 1
        if c[2] == ')':
            hasta -= 1
        incluidos = []
        for x in range(desde, hasta + 1):
            if primo(x):
                incluidos.append(x)
        r = int(q['options'][int(responses.pop(0))])
        results.append(r in incluidos) # q14
        q = questions.pop(0)
        a, s, l, c = q['data'][1:-1].split(',')
        hasta = int(s) + int(l)
        desde = int(s)
        if a[1] == '(':
            desde += 1
        if c[2] == ')':
            hasta -= 1
        f = fibo(hasta)
        incluidos = set(f[desde:])
        r = int(q['options'][int(responses.pop(0))])
        results.append(r in incluidos) # q15
        q = questions.pop(0)
        d = q['data'].replace("'", '')
        d = d.replace('\\', '')
        d = d.replace(' ', '')        
        s = d.index('{') + 1
        e = d.index('}')
        A = set(d[s:e].split(','))
        s = d.index('{', e + 1) + 1
        e = d.index('}', s + 1)
        B = set(d[s:e].split(','))
        C = set()
        if not 'set' in d:
            s = d.index('{', e + 1) + 1
            e = d.index('}', s + 1)
            C = set(d[s:e].split(','))
        op = q['options']
        s = ['cup', 'cap', 'minus A', 'minus B', 'ninguna']
        if lan == 1:
            s[-1] = 'none'
        for i in range(5):
            for r in s:
                op[i] = r if r in op[i] else op[i]
        order = [(op.index('cup'), A | B == C),
                 (op.index('cap'), A & B == C),
                 (op.index('minus B'), A - B == C),
                 (op.index('minus A'), B - A == C)]
        if lan == 0:
            order.append((op.index('ninguna'), True if not any([o[1] for o in order]) else False))
        else:
            order.append((op.index('none'), True if not any([o[1] for o in order]) else False))            
        order.sort(key = lambda k: k[0])
        results.append(order[responses.pop(0)][1]) # q16
        q = questions.pop(0)
        d = q['data'].replace("'", '')
        d = d.replace('\\', '')        
        d = d.replace(' ', '')        
        s = d.index('[') + 1
        e = d.index(']')
        A = set(d[s:e].split(','))
        s = d.index('[', e + 1) + 1
        e = d.index(']', s + 1)
        B = set(d[s:e].split(','))
        op = q['options']
        s = ['subseteq', 'supseteq', 'subset B', 'supset B', 'ninguna']
        if lan == 1:
            s[-1] = 'none'
        for i in range(5):
            for r in s:
                op[i] = r if r in op[i] else op[i]
        order = [(op.index('subseteq'), A.issubset(B) or A == B), 
                 (op.index('supseteq'), A.issuperset(B) or A == B),
                 (op.index('subset B'), A.issubset(B) and A != B),
                 (op.index('supset B'), A.issuperset(B) and A != B)]
        if lan == 0:
            order.append((op.index('ninguna'), True if not any([o[1] for o in order]) else False))
        else:
            order.append((op.index('none'), True if not any([o[1] for o in order]) else False))
        order.sort(key = lambda k: k[0])
        pos = int(responses.pop(0))
        results.append(order[pos][1]) # q17
        q = questions.pop(0)
        c = factorial(len(q['data'][1:-1].split(',')))
        results.append(q['options'].index(str(c)) == responses.pop(0)) # q18
        q = questions.pop(0)
        c = 2**(len(q['data'][1:-1].split(',')))
        results.append(q['options'].index(str(c)) == responses.pop(0)) # q19
        q = questions.pop(0)
        n, k = q['data'][1:-1].split(',')
        c = str(binom(int(n), int(k)))
        results.append(q['options'].index(c) == responses.pop(0)) # q20
    if 'ord' in exam['kind']:
        q = questions.pop(0)
        V = set(q['data'][1:-1].replace("'", '').replace(' ', '').split(','))
        n = len(V)
        results.append(q['options'].index(str(n)) == responses.pop(0)) # q1
        q = questions.pop(0)
        raw = q['data'][1:-1].replace("'", '').replace(' ', '').split('(')
        raw.pop(0)
        A = defaultdict(set)        
        E = dict()
        for d in raw:
            u = d[:d.index(',')]
            v = d[(d.index(',') + 1):d.index(')')]
            w = int(d[(d.index(':') + 1):].replace(',', ''))
            u, v = min(u, v), max(u, v)
            E[(u, v)] = w
            A[u].add(v)
            A[v].add(u)            
        m = len(E)
        results.append(q['options'].index(str(m)) == responses.pop(0)) # q2  
        q = questions.pop(0)
        d = str(Fraction(2*m, n * (n - 1)))
        results.append(q['options'].index(d) == responses.pop(0)) # q3           
        q = questions.pop(0)
        deg = {v: len(A[v]) for v in V}
        d = q['data']
        c = None
        if 'nimo' in d or 'min' in d:
            c = str(min(deg.values()))
        elif 'ximo' in d or 'max' in d:
            c = str(max(deg.values()))
        elif 'promedio' in d or 'average' in d:
            c = str(Fraction(2 * m, n))
        else:
            v = d.split()[-1].replace('$', '')
            c = str(deg[v])
        results.append(q['options'].index(c) == responses.pop(0)) # q4
        q = questions.pop(0)
        S = set(q['data'][1:-1].replace("'", '').replace(' ', '').split(','))
        k = 0
        for u in S:
            for v in S:
                if u < v:
                    if v in A[u]:
                        k += 1
        correct = q['options'].index(str(k))
        results.append(correct == responses.pop(0)) # q5
        q = questions.pop(0)
        c = []
        for cand in q['options']:
            if 'ninguna' in cand or 'none' in cand:
                c.append(-2)
            else:
                seq = cand.replace('$', '')
                if len(seq) < 3:
                    c.append(-1)
                else:
                    cycle = [char for char in seq]  
                    cycle.append(cycle[0]) # add first at the end
                    ok = True # is a cycle
                    while len(cycle) > 1:
                        u = cycle[0]
                        v = cycle[1]
                        u, v = min(u, v), max(u, v)
                        if (u, v) not in E:
                            ok = False
                            break
                        cycle.pop(0)
                    c.append(ok)
        c[c.index(-2)] = True if True not in c else False
        while -1 in c:
            c[c.index(-1)] = False
        results.append(c[responses.pop(0)]) # q6
        q = questions.pop(0)
        c = []
        for cand in q['options']:
            if 'ninguna' in cand or 'none' in cand:
                c.append(-2)
            else:
                for e in '${}, $\\':
                    cand = cand.replace(e, '')
                ok = True 
                for u in cand: # is it a clique
                    for v in cand:
                        if u != v and u not in A[v]:
                            ok = False # not a clique
                            break
                for v in V: # is it also maximal
                    if v not in cand:
                        if all(w in A[v] for w in cand):
                            ok = False # not maximal
                            break
                if ok:
                    c.append(len(cand))
                else:
                    c.append(-1)
        longest = max(max(c), 0)
        resp = [l == longest for l in c]
        resp[c.index(-2)] = True if not any([l > 0 for l in c]) else False
        results.append(resp[int(responses.pop(0))]) # q7
        q = questions.pop(0)
        c = []
        for cand in q['options']:
            if 'ninguna' in cand or 'none' in cand:
                c.append(-2)
            else:
                for e in '${}, $\\':
                    cand = cand.replace(e, '')                
                ok = True # idset
                for u in cand:
                    for v in cand:
                        if u in A[v]:
                            ok = False
                            break
                if ok:
                    c.append(len(seq))
                else:
                    c.append(-1)
        longest = max(max(c), 0)
        resp = [l == longest for l in c]
        resp[c.index(-2)] = True if not any([l > 0 for l in c]) else False
        results.append(resp[responses.pop(0)]) # q8
        q = questions.pop(0)
        GC = comps(A)
        mcc = set()
        for cc in GC:
            k = len(cc)
            if k > len(mcc):
                mcc = cc
        results.append(q['options'][responses.pop(0)] == str(len(mcc))) # q9
        q = questions.pop(0)
        Ec = dict()
        Ac = defaultdict(list)
        for (u, v) in E:
            if u in mcc and v in mcc:
                Ec[(u, v)] = E[(u, v)]
        for v in V:
            if v in mcc:
                for u in A[v]:
                    if u in mcc:
                        Ac[v].append(u)
        D = floyd_warshall(Ac, Ec)
        u, v = q['data'][1:-1].replace("'", '').replace(' ', '').split(',')
        dist = D[(u, v)]
        results.append(q['options'][responses.pop(0)] == str(dist)) # q10
        q = questions.pop(0)
        diam = max(D.values())
        results.append(q['options'][responses.pop(0)] == str(diam)) # q11
        q = questions.pop(0)
        cost, tree = mst(Ec)
        results.append(q['options'][responses.pop(0)] == str(cost)) # q12
        q = questions.pop(0)        
        A = Arbol()
        N = [int(cl) for cl in q['data'][1:-1].replace("'", '').replace(' ', '').split(',')]
        for cl in N:
            A.agrega(cl)
        A.calcula()
        results.append(q['options'][responses.pop(0)] == str(N[0])) # q13
        q = questions.pop(0)        
        hc = A.hojas()
        results.append(q['options'][responses.pop(0)] == str(hc)) # q14
        q = questions.pop(0)
        cl = int(q['data'])
        p = A.ubicar(cl, 'padre')
        results.append(q['options'][responses.pop(0)] == str(p)) # q15
        q = questions.pop(0)
        d = q['data'].split(',')
        chosen = d.pop(0)
        cual = 'derecho' if ('echo' in chosen or 'right' in chosen) else 'izquierdo'
        cl = int(d.pop(0)[1:-1])
        h = A.ubicar(cl, cual)
        ok = [ str(h) ]
        if 'no tiene' in ok:
            ok.append('none')
        results.append(q['options'][responses.pop(0)] in ok) # q16
        q = questions.pop(0)
        results.append(q['options'][responses.pop(0)] == str(A.ubicar(int(q['data']), 'altura'))) # q17
        q = questions.pop(0)
        results.append(q['options'][responses.pop(0)] == str(A.ubicar(int(q['data']), 'profundidad'))) # q18
        q = questions.pop(0)
        d = q['data']
        for e in "[]()'":
            d = d.replace(e, '')
        d = d.split(',')
        r = d.pop(0) # problem in question
        i = int(d.pop(0)) # aspect in question
        d = [int(v) for v in d] # options presented to the student
        correct = probs[r][i]
        pos = d.index(correct) if correct in d else None
        if pos is None:
            print('probs', d, correct, responses[0])
        results.append(pos == responses.pop(0)) # q19
        q = questions.pop(0)
        d = q['data']
        for e in "[]()'":
            d = d.replace(e, '')
        d = d.split(',')
        r = d.pop(0)
        i = int(d.pop(0))
        d = [int(v) for v in d]
        correct = algs[r][i]
        pos =  d.index(correct) if correct in d else None
        if pos is None:
            print('algs', d, correct, responses[0])
        results.append(pos == responses.pop(0)) # q20
    return results

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
        response = form.getvalue('resp').strip().lower()
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
            access = '/var/www/html/elisa/teaching/mat/discretas/data/exam/access/{:s}{:s}.lst'.format(kind, today)
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
                            m = tokens[0][:-1] # quitar lo de :
                            submit = tokens[2] # segunda clave
                            if m == matr:
                                if pin != submit:
                                    print('<html><body>Clave incorrecta. La profesora tiene las claves de entrega. Consulte con ella.</body></html>')
                                    return
                                else:
                                    ok = True
                                break
                if not ok:
                    print('<html><body>Clave faltante, avisa a la profesora que no existe tu clave.</body></html>')
                    return                    
    except:
        print('<html><body>Datos incorrectos, favor de revisar.</body></html>')
        return
    if '-' in response:
        print('<html><body>Preguntas sin responder, no se procesa. Favor de revisar.</body></html>')
        return
    filename = '/var/www/html/elisa/teaching/mat/discretas/data/exam/{:s}{:s}_{:s}.json'.format('trial/' if trial else '', h, kind)
    if os.path.isfile(filename):
        store = filename.replace('.json', '_graded.json')
        if not trial and os.path.isfile(store):
            print('<html><body>Este examen ya ha sido calificado. No se permite reintentar cuando no es un examen de pr&aacute;ctica.</body></html>')
            return
        correct = grade(filename, response, trial)
        if correct is None:
            return            
        else:
            output = '{{"graded":"{:s}",\n'.format(str(datetime.now()))
            output += '"response":"{:s}",\n'.format(response)
            pts = ''.join(['1' if r else '0' for r in correct])
            output += '"correct":"{:s}"}}'.format(pts)
            with codecs.open(store, "w", "utf-8-sig") as target:
                target.write(output)
            n = len(correct)
            assert len(response) == len(correct)
            if not trial:
                with open('/home/elisa/html/data/exams_md.txt', 'a') as record:
                    corr = ''.join(['1' if c else '0' for c in correct])
                    print('{:s} {:s}{:s}'.format(matr, prefix[kind], corr), file = record)
            print('''<html><head>
<LINK rel="stylesheet" type="text/css" href="https://elisa.dyndns-web.com/teaching/result.css">
</head>
<body>
            <h1>Resultado de examen</h1>''')
            print('<h2>Matr&iacute;cula: {:s}</h2>'.format(matr))
            print('<h2>Tipo de examen: {:s}</h2>'.format(tipo[kind]))
            if trial:
                print('<p><em><span style="color:red">Examen de pr&aacute;ctica sin validez para la calificaci&oacute;n final</span></em></p>')
            print('<h3><span style="color:blue">Se otorgaron {:d} puntos de un total de 20 por las preguntas 1&ndash;20</span></h3>'.format(sum(correct[:20])))
            if n == 40:
                print('<h3><span style="color:blue">Se otorgaron {:d} puntos de un total de 20 por las preguntas 21&ndash;40</span></h3>'.format(sum(correct[20:])))
            print('<ol>')
            exam = None
            with open(filename, encoding='utf-8') as data:
                exam = load(data)
            for i in range(n):
                result = '<span style="color:green">correcta</span>' if correct[i] else '<span style="color:red">incorrecta</span>'
                q = exam['questions'][i]
                d = q['description'].encode('ascii', 'xmlcharrefreplace').decode('ascii')
                print('<li><strong>{:s}</strong>\n<ul>'.format(d))
                r = int(response[i]) - 1
                for a in range(5):
                    s, c = '', ''
                    if a == r:
                        s = '<span style="color:blue"> &mdash; la opci&oacute;n seleccionada fue</span>'
                        c = result
                    o = q['options'][a].encode('ascii', 'xmlcharrefreplace').decode('ascii')
                    print('<li>{:s} {:s} {:s}</li>'.format(o, s, c))
                print('</ul></li>')
            print('''</ol>
<p>El resultado <strong>ha sido guardado</strong> en el servidor. Se puede cerrar esta p&aacute;gina sin p&eacute;rdida de datos.</p>
<script>
  MathJax = {
      tex: {
	  inlineMath: [['$', '$']]
      }
  };
</script>
<script id="MathJax-script" async
	src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js">
</script>
</body></html>''')
            if trial:
                print('''<p>Siendo un examen de pr&aacute;ctica, se permite intentar nuevamente con el mismo examen, 
tomando en cuenta que se borran las selecciones previamente hechas al regresar a la p&aacute;gina anterior.</p>''')
    else:
        print('<html><body>Datos incorrectos, favor de revisar.</body></html>')
        return                            
    return
      
if __name__ == "__main__":
    main()
