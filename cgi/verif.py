#!/usr/bin/env python3
import cgi, os
import cgitb; cgitb.enable()
from os import chmod
from random import randint
from sys import argv, stdout, stderr
from xml.dom import minidom
from subprocess import check_call, Popen, CalledProcessError, check_output
import hashlib
import datetime

LOC = '/var/www/html/elisa/'

def generator(name):
    possibles = globals().copy()
    possibles.update(locals())
    method = possibles.get(name)
    return method

def cleantext(string):
   string = string.replace("->", '')
   string = string.replace("<-", '')
   string = string.replace(">", '')
   string = string.replace("<", '')
   string = string.replace("/", '')
   string = string.replace("[", '')
   string = string.replace("]", '')
   string = string.replace("{", '')
   string = string.replace("}", '')
   string = string.replace("--", '')
   return string

def clean(string):
    string = cleantext(string)
    cleaned = ''
    permitted = '^(),.-'
    for char in string:
        place = ' '
        if char.isdigit() or char.isalpha() or char in permitted:
            place = char
        cleaned = f'{cleaned}{place}'
    return cleaned

class Nodo:
    def __init__(self):
        self.contenido = None
        self.izquierdo = None
        self.derecho = None
 
    def __str__(self):
        if self.contenido is None:
            return ''
        else:
            return '%s [%s | %s]' % \
                (self.contenido, self.izquierdo, self.derecho)
 
    def agrega(self, elemento):
        if self.contenido is None:
            self.contenido = elemento
        else:
            if elemento < self.contenido:
                if self.izquierdo is None:
                    self.izquierdo = Nodo()
                self.izquierdo.agrega(elemento)
            if elemento > self.contenido:
                if self.derecho is None:
                    self.derecho = Nodo()
                self.derecho.agrega(elemento)
 
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

u_contador = 0

def ubicar(nodo, buscado):
    global u_contador
    u_contador += 1
    if nodo.contenido == buscado:
        return True
    if buscado < nodo.contenido and nodo.izquierdo is not None:
        return ubicar(nodo.izquierdo, buscado)
    if buscado > nodo.contenido and nodo.derecho is not None:
        return ubicar(nodo.derecho, buscado)
    return False

def camino(s, t, c, f):
    cola = [s]
    usados = set()
    camino = dict()
    while len(cola) > 0:
        u = cola.pop(0)
        usados.add(u)
        for (w, v) in c:
            if w == u and v not in cola and v not in usados:
                actual = f.get((u, v), 0)
                dif = c[(u, v)] - actual
                if dif > 0:
                    cola.append(v)
                    camino[v] = (u, dif)
    if t in usados:
        return camino
    else: 
        return None
 
def ford_fulkerson(c, s, t): # algoritmo de Ford y Fulkerson
    if s == t:
        return 0
    maximo = 0
    f = dict()
    while True:
        aum = camino(s, t, c, f)
        if aum is None:
            break # ya no hay
        incr = min(aum.values(), key = (lambda k: k[1]))[1]
        u = t
        while u in aum:
            v = aum[u][0]
            actual = f.get((v, u), 0) # cero si no hay
            inverso = f.get((u, v), 0)
            f[(v, u)] = actual + incr
            f[(u, v)] = inverso - incr
            u = v
        maximo += incr
    return maximo

def binom(n, k):
    from math import factorial
    value = 1
    for factor in range(max(k, n - k) + 1, n + 1):
        value *= factor
    return value / factorial(min(k, n - k))

def fibo(cuantos):
    listado = [0, 1]
    for pos in range(cuantos - 2):
        listado.append(listado[-1] + listado[-2])
    return listado

class Grafo:
    def __init__(self):
        self.V = set() # un conjunto
        self.E = dict() # un mapeo de pesos de aristas
        self.vecinos = dict() # un mapeo
 
    def agrega(self, v):
        self.V.add(v)
        if not v in self.vecinos: # vecindad de v
            self.vecinos[v] = set() # inicialmente no tiene nada
 
    def conecta(self, v, u, peso=1):
        self.agrega(v)
        self.agrega(u)
        self.E[(v, u)] = self.E[(u, v)] = peso # no dirigido
        self.vecinos[v].add(u)
        self.vecinos[u].add(v)

def floyd_warshall(G):
    d = {}
    for v in G.V:
        d[(v, v)] = 0 # distancia reflexiva es cero
        for u in G.vecinos[v]: # para vecinos, la distancia es el peso
           d[(v, u)] = G.E[(v, u)]
    for intermedio in G.V:
        for desde in G.V:
            for hasta in G.V:
                di = None
                if (desde, intermedio) in d:
                    di = d[(desde, intermedio)]
                ih = None
                if (intermedio, hasta) in d:
                    ih = d[(intermedio, hasta)]
                if di is not None and ih is not None:
                    c = di + ih # largo del camino de "d" a "h" via "i"
                    if (desde, hasta) not in d or c < d[(desde, hasta)]:
                        d[(desde, hasta)] = c # mejora al camino actual
    return d

def tarea_1_1(gen, sub):
    A = set([int(t) for t in gen['1.A'].split()])
    B = set([int(t) for t in gen['1.B'].split()])
    C = set([int(t) for t in gen['1.C'].split()])
    D = set([int(t) for t in gen['1.D'].split()])
    R = A.union(B.difference(C.intersection(D)))
    S = set()
    s = sub['r1.1'].replace(',', ' ')
    s = s.replace('{', '')
    s = s.replace('}', '')
    for element in s.split():
        received = None
        try:
            received = int(element)
        except:
            return False
        if received is not None:
            S.add(received)
    return R == S

def tarea_1_2(gen, sub):
    received = None
    try:
        received = int(sub['r1.2'])
    except:
        return False
    return int(gen['1.bin'], 2) == received

def tarea_1_3(gen, sub):
    from math import log, ceil
    n = int(gen['1.dec'])
    b = int(gen['1.base'])
    try: 
        return int(sub['r1.3'], b) == n
    except:
        return False

def tarea_1_4(gen, sub):
    received = None
    try:
        received = int(sub['r1.4'])
    except:
        return False
    correct = int(gen['1.a']) & (int(gen['1.b']) << int(gen['1.c']))
    return received == correct
               
def tarea_1_5(gen, sub):
    response = sub['r1.5'].strip()
    if len(response) != 1: 
        return False
    if not response[0] in '01':
        return False
    x = (int(gen['1.x']) == 1)
    y = (int(gen['1.y']) == 1)
    z = (int(gen['1.z']) == 1)
    return ((x or z) and not(not y or not z)) == int(response)

def tarea_2_1(gen, sub):
    from math import factorial
    received = None
    try:
        received = int(sub['r2.1'])
    except:
        return False
    return received == factorial(5)

def tarea_2_2(gen, sub):
    k = int(gen['2.k'])
    n = 8 - len(gen['2.sub'].split())
    received = None
    try:
        received = int(sub['r2.2'])
    except:
        return False
    return received == binom(n, k)
    
def tarea_2_3(gen, sub):
    received = None
    try:
        received = int(sub['r2.3'])
    except:
        return False
    return fibo(int(gen['2.fibo']))[-1] == received

def tarea_2_4(gen, sub):
    return gen['2.turing'][:-1] == sub['r2.4']

def tarea_2_5(gen, sub):
    received = None
    try:
        received = int(sub['r2.5'])
    except:
        return False
    return len(gen['2.turing']) + 4 == received

E = None

def aristas(gen):
    global E
    u = int(gen['3.u'])
    v = int(gen['3.v'])
    E = set()
    for (x, y) in [(1, 2), (1, 3), (2, 4), (u, v), (3, 5), \
                   (3, 6), (4, 6), (4, 7), (5, 8), (6, 9), (7, 9)]:
        E.add((min(x, y), max(x, y)))
    return 

def tarea_3_1(gen, sub):
    if E is None:
        aristas(gen)
    maxdeg = 0
    for v in range(1, 10):
        deg = 0
        for e in E:
            if v in e:
                deg += 1
        if deg > maxdeg:
            maxdeg = deg
    received = None
    try:
        received = int(sub['r3.1'])
    except:
        return False
    return received == maxdeg

def tarea_3_2(gen, sub):
    if E is None:
        aristas(gen)
    return abs(float(sub['r3.2']) - \
               (1.0 * len(set(E))) / binom(9, 2)) < 0.01
            
D = None

def distancias(gen):
    global D
    if E is None:
        aristas(gen)
    G = Grafo()
    for (s, t) in E:
        G.conecta(s, t, 1)
    D = floyd_warshall(G)
    return
   
def tarea_3_3(gen, sub):
    if D is None:
        distancias(gen)
    v = int(gen['3.v'])
    received = None
    try:
        received = int(sub['r3.3'])
    except:
        return False
    return D[(1, v)] == received

def tarea_3_4(gen, sub):
    if D is None:    
        distancias(gen)
    received = None
    try:
        received = int(sub['r3.4'])
    except:
        return False
    return max(D.values()) == received

def tarea_3_5(gen, sub):
    if E is None:
        aristas(gen)
    u = int(gen['3.u'])
    v = int(gen['3.v'])
    contador = 0
    for e in E:
        if u not in e and v not in e:
            contador += 1
    received = None
    try:
        received = int(sub['r3.5'])
    except:
        return False
    return contador == received

def tarea_4_1(gen, sub):
    t = gen['4.pol']
    desde = t.index('<sup>')
    hasta = t.index('</sup>')
    pot = int(t[desde + 5 : hasta])
    return ('O(x^%d)' % pot) == sub['r4.1']

def parse(f, value):
    from math import sqrt, log
    desde = f.index('<sup>', 0)
    hasta = f.index('</sup>', desde)
    a = int(f[desde + 5 : hasta])
    desde = f.index('<sup>', hasta)
    hasta = f.index('</sup>', desde)
    b = int(f[desde + 5 : hasta])
    desde = f.index('log', hasta)
    hasta = f.index('<em>', desde)
    c = int(f[desde + 3 : hasta])
    desde = f.index('<sup>', hasta)
    hasta = f.index('</sup>', desde)
    d = int(f[desde + 5 : hasta])

    return sqrt(value ** a) * (value ** b) * log(c * (value ** d))

def tarea_4_2(gen, sub):
    excess = float('inf')
    while True:
        n = 5000.0
        f = parse(gen['4.f'], n)
        g = parse(gen['4.g'], n)
        h = parse(gen['4.h'], n)
        if f == excess and g == excess and h == excess:
            n /= 2
        else:
            break
    least = min(f, g, h)
    if least == f:
        return 'f(n)' == sub['r4.2']
    elif least == g:
        return 'g(n)' == sub['r4.2']
    return 'h(n)' == sub['r4.2']

def tarea_4_3(gen, sub):
    peso_permitido = int(gen['4.limite'])
    p = int(gen['4.peso'])
    v = int(gen['4.valor'])
    objetos = ((5, 10), (8, 12), (4, 24), (12, 30), (5, 7), \
               (2, 8), (1, 3), (p, v))
    peso_total = sum([objeto[0] for objeto in objetos])
    valor_total = sum([objeto[1] for objeto in objetos])
    opt = None
    if peso_total < peso_permitido:
        opt = valor_total
    else:
        cantidad = len(objetos)
        V = dict()
        for w in range(peso_permitido + 1):
            V[(w, 0)] = 0
        for i in range(cantidad):
            (peso, valor) = objetos[i]
            for w in range(peso_permitido + 1):
                V[(w, i + 1)] = \
                    max(V[(w, i)], \
                            V.get((w - peso, i), -float('inf')) \
                            + valor)
        opt = max(V.values())
    received = None
    try:
        received = int(sub['r4.3'])
    except:
        return False
    return opt == received

C = None

def flujo(gen):
    global C
    C = {(0, 1): 16, (0, 2): 13, (1, 2): 10, (2, 1): 4, (3, 2): 9, \
         (1, 3): 12, (2, 4): 14, (4, 3): 7, (3, 5): 20, (4, 5): 4}
    u = int(gen['4.desde'])
    v = int(gen['4.hasta'])
    cap = int(gen['4.cap'])
    C[(u, v)] = cap

def tarea_4_4(gen, sub):
    if C is None:
        flujo(gen)
    received = None
    try:
        received = int(sub['r4.4'])
    except:
        return False
    return ford_fulkerson(C, 1, 4) == received

def tarea_4_5(gen, sub):
    if C is None:
        flujo(gen)
    mayor = None
    for s in range(6):
        for t in range(6):
            if s != t:
                f = ford_fulkerson(C, s, t)
                if mayor is None or f > mayor:
                    mayor = f
    received = None
    try:
        received = int(sub['r4.5'])
    except:
        return False
    return mayor == received

bb_llamadas = 0

def bbinaria(ordenados, buscado):
    global bb_llamadas 
    bb_llamadas += 1
    n = len(ordenados)
    if n == 0: # no hay nada
        return False
    pos = n // 2 # div. entera
    pivote = ordenados[pos]
    if pivote == buscado:
        return True # encontrado
    elif buscado < pivote: # viene antes del pivote
        return bbinaria(ordenados[: pos], buscado)
    else: 
        return bbinaria(ordenados[pos + 1 :], buscado)

def tarea_5_1(gen, sub):
    desde = int(gen['5.desde'])
    hasta = int(gen['5.hasta'])
    paso = int(gen['5.pasos'])
    valor = int(gen['5.valor'])
    global bb_llamadas
    bb_llamadas = 0
    bbinaria(range(desde, hasta + 1)[::paso], valor)
    received = None
    try:
        received = int(sub['r5.1'])
    except:
        return False
    return bb_llamadas == received

def tarea_5_2(gen, sub):
    from math import log, ceil 
    received = None
    try:
        received = int(sub['r5.2'])
    except:
        return False
    return int(ceil(log(int(gen['5.nodos']) + 1, 2))) == received

def tarea_5_3(gen, sub):
    a = Arbol()
    for value in [int(t) for t in gen['5.arbol'].split()]:
        a.agrega(value)
    global u_contador
    u_contador = 0
    ubicar(a.raiz, int(gen['5.elemento']))
    received = None
    try:
        received = int(sub['r5.3'])
    except:
        return False
    return u_contador == received

def tarea_5_4(gen, sub):
    p = "sabado"
    q = "domingo"
    ic = int(gen['5.ins'])
    ec = int(gen['5.eli'])
    rc = int(gen['5.ree'])
    d = dict()
    np = len(p) + 1
    nq = len(q) + 1
    for i in range(np):
        d[(i, 0)] = ic * i
    for j in range(nq):
        d[(0, j)] = ec * j
    for i in range(1, np):
        for j in range(1, nq):
            eli = d[(i - 1, j)] + ec
            ins = d[(i, j - 1)] + ic
            ree = d[(i - 1, j - 1)] + rc * (p[i - 1] != q[j - 1])
            d[(i, j)] = min(eli, ins, ree)
    received = None
    try:
        received = int(sub['r5.4'])
    except:
        return False
    return d[(np -1, nq - 1)] == received

def tarea_5_5(gen, sub):
    grafo = {(1, 3): 4, (2, 3): 2, (2, 4): 1, (3, 4): 2, (4, 6): 1, (5, 6): 2}
    u = int(gen['5.inicio'])
    v = int(gen['5.final'])
    p = int(gen['5.peso'])
    grafo[(u, v)] = p
    from copy import deepcopy
    cand = deepcopy(grafo)
    arbol = set()
    peso = 0
    comp = dict()
    while len(cand) > 0:
        arista = min(cand.keys(), key = (lambda k: cand[k]))
        del cand[arista]
        (u, v) = arista
        c = comp.get(v, {v})
        if u not in c:
            arbol.add(arista)
            peso += grafo[arista]
            nuevo = c.union(comp.get(u, {u}))
            for w in nuevo:
                comp[w] = nuevo    
    received = None
    try:
        received = int(sub['r5.5'])
    except:
        return False
    return peso == received

def output(filename, fields):
    with open(filename, 'w') as target:
        print ('<xml>', file = target)
        for label in fields:
            print ("<field><id>%s</id><value><![CDATA[%s]]></value></field>" \
                   % (label, fields[label]), file = target)
        print ('</xml>', file = target)

def fill(target, filename):
    source = minidom.parse(filename)
    fields = source.getElementsByTagName('field')
    for field in fields:
        try:
            label = field.childNodes[0].firstChild.data
            value = field.childNodes[1].firstChild.data
            label = label.encode('ascii', 'ignore')
            value = value.encode('ascii', 'ignore')
            target[label.decode('utf-8')] = value.decode('utf-8')
        except:
            pass
       
def main():
    print('Content-type: text/html\n\n')
    print('<html>')
    print('<head><title>Grading completed</title></head>')
    print('<body><span style="color:red">')
    h = None
    form = None
    timestamp = str(datetime.datetime.now()).split('.')[0]
    print('<h2>Script reply</h2><p>')
    print('Activated at', timestamp, '<br />')
    try:
        form = cgi.FieldStorage()
        h = form.getvalue('hash')
    except:
        pass
    if h is None:
        try:
            student = argv[1] # debug mode
            print(student)
            print("Parsing a hash")
            h = hashlib.md5(student.encode("utf-8")).hexdigest()
            print('Hash', h, '<br />')
        except:
            print('No hash nor student info <br />')
            return
    filename = LOC + ('teaching/mat/discretas/data/%s' % h)
    try:
        status = dict()
        fill(status, '%s.awarded.xml' % filename)
        accepted = dict()
        fill(accepted, '%s.accepted.xml' % filename)
        rejected = dict()
        fill(rejected, '%s.rejected.xml' % filename)
        attempts = dict()
        fill(attempts, '%s.attempts.xml' % filename)
        generated = dict()
        fill(generated, '%s.generated.xml' % filename)
    except Exception as e:
        print('No such student')
        print('</p>')
        print('</span></body>')
        print('</html>')
        return
    print('Updating student log<br>')
    logfile = LOC + 'data/md/%s.log' % h
    try:
        with open(logfile, 'a') as log:
            print('<session>\nSubmission of %s at %s' % (h, timestamp), file = log)
            submitted = dict()
            for label in form.keys():
                if 'r' in label:
                    response = form.getvalue(label)
                    if response is not None and len(response) > 0:
                        print("Received '%s' for %s." % (response, label), file = log)
                        submitted[label] = clean(response)
                        print('Processing', submitted[label], 'for', label, '<br>')
            for exercise in submitted:
                if exercise not in attempts:
                    attempts[exercise] = "1"
                else:
                    attempts[exercise] = int(attempts[exercise]) + 1
                    print('Choosing the evaluator<br>')
                    evaluator = generator(exercise.replace('r', 'tarea_').replace('.', '_'))
                    print("Grading %s with %s." % (exercise, evaluator), file = log)
                    print('Grading<br>')
                    if evaluator(generated, submitted):
                        print("Correct solution for %s." % exercise, file = log)
                        print(exercise, 'correct<br>')
                        status[exercise] = "1"
                        accepted[exercise] = submitted[exercise]
                        if exercise in rejected:
                            del rejected[exercise]
                    else:
                        print(exercise, 'incorrect<br>')
                        print("Incorrect solution for %s." % exercise, file = log)
                        if exercise not in status: 
                            status[exercise] = "0"
                        rejected[exercise] = submitted[exercise]
            output('%s.awarded.xml' % filename, status)
            output('%s.accepted.xml' % filename, accepted)
            output('%s.rejected.xml' % filename, rejected)
            output('%s.attempts.xml' % filename, attempts)
            print('</session>', file = log)
    except Exception as e:
        print(str(e))
        pass
    print('</p>')
    print('</span></body>')
    print('</html>')
    return

if __name__ == "__main__":
    main()

