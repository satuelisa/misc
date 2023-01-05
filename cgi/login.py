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
            if cual == 'padre' or cual == 'parent':
                return self.padre
            elif cual == 'izquierdo' or cual == 'left':
                return self.izquierdo
            elif cual == 'derecho' or cual == 'right':
                return self.derecho
            elif cual == 'altura' or cual == 'height':
                return self.altura
            elif cual == 'profundidad' or cual == 'depth':
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
            if cual in ['padre', 'izquierdo', 'derecho', 'parent', 'left', 'right']:
                return obtenido.contenido
            else:
                return obtenido
        else:
            return None

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

def rw(A, limit, rep = False, stall = 20):
    walk = [sample(A.keys(), 1)[0]]
    s = 0
    while len(walk) < limit:
        curr = walk[-1]
        opt = A[curr]
        if len(opt) == 0:
            break
        cont = choice(list(opt))
        if rep or cont not in walk:
            walk.append(cont)
        s += 1
        if s > stall:
            break
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

algsIdx = {
    0: ['¿Qué se obtiene con el algoritmo',
        '¿Cuál es la complejidad asintótica de peor caso del algoritmo',
        '¿Qué se le da como entrada al algoritmo',
        '¿Qué produce como salida el algoritmo'],
    1: ['The goal of',
        'The worst-case asymptotic complexity of',
        'The input for',
        'The output of']
}

algsOp = {
    0: {1: 'todas las distancias',
        2: '$\mathcal{O}(n^3)$',
        3: 'un grafo simple (ponderado)',
        4: 'una matriz de distancia',
        5: 'flujo máximo',
        6: 'un grafo ponderado y los vértices fuente y sumidero', 
        7: 'valor total de flujo y el flujo por arista',
        8: 'árbol de expansión mínima',
        9: '$\mathcal{O}(m + n \log n)$',
        10: 'un grafo necesariamente ponderado',
        11: 'el costo total y las aristas incluidas', 
        12: '$\mathcal{O}(m \log n)$',
        13: 'componente conexo de un vértice',
        14: '$\mathcal{O}(n + m)$',
        16: 'un recorrido de los vértices alcanzables', 
        17: 'los vértices alcanzables agrupados por su distancia',
        18: 'ordenar un arreglo',
        19: '$\mathcal{O}(n \log n)$',
        20: 'un arreglo en orden arbitrario', 
        21: 'un arreglo ordenado',
        22: '$\mathcal{O}(n^2)$',
        23: 'si un elemento está en un arreglo',
        24: '$\mathcal{O}(\log n)$', 
        26: 'verdad o falso',
        27: 'el mayor divisor común',
        28: '$\mathcal{O}(a + b)$',
        29: 'dos números enteros',
        30: '$\mathcal{O}(\log(a + b))$'},
    1: {1: 'all the distances',
        2: '$\mathcal{O}(n^3)$',
        3: 'a simple (weighted) graph',
        4: 'a distance matrix',
        5: 'maximum flow',
        6: 'a weighted graph with source and target vertices', 
        7: 'the total flow and the flow per edge',
        8: 'minimum spanning tree',
        9: '$\mathcal{O}(m + n \log n)$',
        10: 'a weighted graph',
        11: 'the total cost and the included edges', 
        12: '$\mathcal{O}(m \log n)$',
        13: 'the connected component of a vertex',
        14: '$\mathcal{O}(n + m)$',
        16: 'a traversal of researchable vertices', 
        17: 'the reachable vertices group by distance',
        18: 'sorting of an array',
        19: '$\mathcal{O}(n \log n)$',
        20: 'an array in abritrary order', 
        21: 'a sorted array',
        22: '$\mathcal{O}(n^2)$',
        23: 'whether an element is included in an array',
        24: '$\mathcal{O}(\log n)$', 
        26: 'true or false',
        27: 'the greatest common divisor',
        28: '$\mathcal{O}(a + b)$',
        29: 'two integers',
        30: '$\mathcal{O}(\log(a + b))$'}
}

algNames = {
    0: {
        'FW': 'Floyd-Warshall',
        'FF': 'Ford-Fulkerson',
        'of': 'ordenamiento por fusión',
        'os': 'ordenamiento por selección',
        'bb': 'búsqueda binaria',
        'es': 'Euclidiano por resta',
        'er': 'Euclidiano por residuo'
    },
    1: {
        'FW': 'Floyd-Warshall algorithm',
        'FF': 'Ford-Fulkerson algorithm',
        'of': 'merge sort algorithm',
        'os': 'selection sort algorithm',
        'bb': 'binary search',
        'es': 'Euclidian algorithm by subtraction',
        'er': 'Euclidian algorithm by residue'
    }
}

probIdx = {
    0: ['¿Cuál es la complejidad computacional del problema de',
        '¿Qué busca determinar el problema de',
        '¿Cuál es la función objetivo del problema de',
        '¿Qué restricciones tiene el problema de'],
    1: ['What is the computational complexity of the',
        'What is the goal of the',
        'What is the objective function of the',
        'What are the restrictions of the']
}

probOp = {
    0: {1: 'pseudopolinomial',
        2: 'cuál combinación de objetos incluir',
        3: 'maximizar valor total',
        4: 'no superar el peso permitido',
        5: 'polinomial',
        6: 'cómo cambiar una cadena a otra',
        7: 'minimizar costo total',
        8: 'no tiene',
        9: 'cuánto vale (cómo número)',
        10: 'no es un problema de optimización',
        11: 'minimizar capacidad total',
        12: 'separar el fuente del sumidero, respetar capacidades',          
        13: 'maximizar flujo total',
        14: 'que ambas divisiones sean exactas',
        15: 'maximizar cobertura',
        16: 'no repetir vértices',
        17: 'cúales aristas incluir',
        18: 'expandir sin crear ciclos',
        19: 'NP-completo',
        20: 'en qué orden visitar',
        21: 'visitar cada vértice exactamente una vez',
        22: 'cuáles vértices incluir',
        23: 'maximizar cardinalidad',
        24: 'que todos los incluidos sean vecinos entre ellos',
        25: 'que ningunos de los incluidos sean vecinos entre ellos',
        26: 'minimizar cardinalidad', 
        27: 'que cada arista sea cubierto por lo menos una vez',
        28: 'que sea el divisor más grande',
        29: 'que cada vértice sea cubierto por lo menos una vez',
        30: 'asignar colores a los vértices',
        31: 'que ningunos vecinos compartan color',
        32: 'desconocido',
        33: 'PSPACE-completo'},
    1: {1: 'pseudopolynomial',
        2: 'the selection of objects to include',
        3: 'maximize total value',
        4: 'not to exceed the weight limit',
        5: 'polynomial',
        6: 'how to transform a string into another',
        7: 'minimize total cost',
        8: 'none',
        9: 'its numeric value',
        10: 'it is not an optimization problem',
        11: 'minimize total capacity',
        12: 'separate the source from the target, respecting the capacities',          
        13: 'maximize total flow',
        14: 'that both divisions be exact',
        15: 'maximize the coverage',
        16: 'not to repeat vertices',
        17: 'which edges to include',
        18: 'expand without introducing cycles',
        19: 'NP-complete',
        20: 'in which order to make the visits',
        21: 'visit each vertex exactly once',
        22: 'which vertices to include',
        23: 'maximize cardinality',
        24: 'that all included vertices be neighbors',
        25: 'that none of the included vertices be neighbors',
        26: 'minimize the cardinality', 
        27: 'that each edge be covered at least once',
        28: 'that the divisor be the largest possible',
        29: 'that each vertex be covered at least once',
        30: 'to assign a color to each vertex',
        31: 'that no pair of neighbors share a color',
        32: 'unknown',
        33: 'PSPACE-complete'}
}
         
probNames = {
    0: {'editdist': 'distancia de edición',
        'gcd': 'mayor divisor común',
        'mincut': 'corte mínimo',
        'maxflow': 'flujo máximo',
        'matching': 'acoplamiento máximo',
        'mst': 'árbol de expansión mínima',
        'tsp': 'problema del viajante',
        'clique': 'camarilla máxima', 
        'idset': 'conjunto independiente máximo',
        'vertexcover': 'cubierta mínima con vértices',
        'edgecover': 'cubierta mínima con aristas',
        '2color': '2-coloreo',
        'kcolor': '$k$-coloreo'},
    1: {'editdist': 'edit distance problem',
        'gcd': 'greatest common divisor problem',
        'mincut': 'minimum cut problem',
        'maxflow': 'maximum flow problem',
        'matching': 'matching problem',
        'mst': 'minimum spanning tree',
        'tsp': 'travelling salesman problem',
        'clique': 'clique problem', 
        'idset': 'independent set problem',
        'vertexcover': 'vertex cover problem',
        'edgecover': 'edge cover problem',
        '2color': '2-coloring problem',
        'kcolor': '$k$-coloring problem'}
}

def binom(n, k): 
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

def fibo(n):
    f = [0, 1]
    while len(f) < n:
        f.append(f[-1] + f[-2])
    return f

def generate(kind, lan):
    questions = []
    if not kind == 'ord':
        x1 = randint(20, 80)
        y1 = randint(30, 70)
        x2 = randint(3, 10)
        y2 = randint(4, 12)
        options = ['$x \\leq y$', '$x \\geq y$', '$x < y$', '$x > y$', '$x = y$']
        # 1 comparisons and rounding
        shuffle(options)
        if lan == 0:
            questions.append(('Con $x = \\lfloor\\frac{{{:d}}}{{{:d}}}\\rfloor$ y $y = \\lceil\\frac{{{:d}}}{{{:d}}}\\rceil$, ¿cúal de las siguientes es la descripción más precisa de su relación?'.format(x1, x2, y1, y2), options, (x1,  x2, y1, y2)))
        else:
            questions.append(('With $x = \\lfloor\\frac{{{:d}}}{{{:d}}}\\rfloor$ and $y = \\lceil\\frac{{{:d}}}{{{:d}}}\\rceil$, which of the following is the most precise description of their relationship?'.format(x1, x2, y1, y2), options, (x1,  x2, y1, y2)))
            
        o = choice(['ceil', 'floor'])
        n = randint(20, 80)
        b = randint(2, 5)
        corr = log(n, b)
        options = { int(ceil(corr)), int(floor(corr)), 1 }        
        while len(options) < 5:
            options.add(randint(2, 3 + b * round(corr)))
        options = list(options)
        # 2 logarithms of arbitrary bases
        shuffle(options)
        if lan == 0:
            questions.append(('¿Cuánto vale $\\l{:s}\\log_{:d} {:d}\\r{:s}$?'.format(o, b, n, o), options, (o, n, b)))
        else:
            questions.append(('What is the value of $\\l{:s}\\log_{:d} {:d}\\r{:s}$?'.format(o, b, n, o), options, (o, n, b)))
        a = randint(20, 50)
        b = randint(7, 15)
        corr = a % b
        options = { corr }
        while len(options) < 5:
            options.add(randint(0, b))
        options = list(options)
        # 3 modular arithmetic                        
        shuffle(options)
        if lan == 0:
            questions.append(('¿Cuánto vale ${:d} \\bmod {:d}$?'.format(a, b), options, (a, b)))
        else:
            questions.append(('What is the value of ${:d} \\bmod {:d}$?'.format(a, b), options, (a, b)))
        b = choice([i for i in range(3, 8)] + [9])
        n = ''.join([str(randint(0, b - 1)) for x in range(4)])
        corr = int(n, b)
        options = { corr }
        while len(options) < 5:
            options.add(randint(0, 2 * corr + 10))
        options = list(options)       
        # 4 interpretation of small bases in decimal
        shuffle(options)
        if lan == 0:
            questions.append(('¿Cuánto vale ${:s}_{:d}$ en decimal?'.format(n, b), options, (n, b)))
        else:
            questions.append(('What is the decimal representation for ${:s}_{:d}$?'.format(n, b), options, (n, b)))
        b = choice([i for i in range(11, 16)] + [i for i in range(17, 25)])
        n = ''.join([digito(randint(0, b - 1)) for x in range(3)])
        corr = int(n, b)
        options = { corr }
        while len(options) < 5:
            options.add(randint(corr // 2, 2 * corr))
        options = list(options)       
        # 5 interpretation of large bases in decimal
        shuffle(options)
        if lan == 0:
            questions.append(('¿Cuánto vale ${:s}_{{ {:d} }}$ en decimal?'.format(n, b), options, (n, b)))
        else:
            questions.append(('What is the decimal representation for ${:s}_{{ {:d} }}$?'.format(n, b), options, (n, b)))
        b = '1{:s}'.format(''.join([str(randint(0, 1)) for x in range(5)]))
        options = { oct(int(b, 2))[2:] }
        while len(options) < 5:
            br = '1{:s}'.format(''.join([str(randint(0, 1)) for x in range(randint(4, 6))]))
            options.add(oct(int(br, 2))[2:])
        options = list(options)
        # 6 octal from binary
        shuffle(options)
        if lan == 0:
            questions.append(('¿Cuánto vale ${:s}_2$ en octal?'.format(b), options, b))
        else:
            questions.append(('What is the octal representation for ${:s}_2$?'.format(b), options, b))
        n = ''.join([str(randint(0, 7)) for i in range(3)]).lstrip('0')
        d = int(n, 8)
        options = { hex(d)[2:] }
        while len(options) < 5:
            options.add(hex(randint(d // 2, 2 * d))[2:])
        options = list(options)
        # 7 hexadecimal from octal
        shuffle(options)
        if lan == 0:
            questions.append(('¿Cuánto vale ${:s}_8$ en hexadecimal?'.format(n), options, n))
        else:
            questions.append(('What is the hexadecimal representation of ${:s}_8$?'.format(n), options, n))
        num = randint(90, 180)
        base = randint(17, 25)
        corr = convertir(num, base)
        options = { corr } 
        while len(options) < 5:
            options.add(convertir(randint(90, 180), randint(17, 25)))
        options = list(options)
        # 8 bases above hexadecimal        
        shuffle(options)
        if lan == 0:
            questions.append(('¿Cuánto vale ${:d}_{{10}}$ en base ${:d}$?'.format(num, base), options, (num, base)))
        else:
            questions.append(('What is the representation for ${:d}_{{10}}$ in base ${:d}$?'.format(num, base), options, (num, base)))        
        x = randint(100, 150)
        y = randint(20, 50)
        corr = gcd(x, y)
        smaller = min(x, y)
        options = {1, smaller}
        while len(options) < 9:
            cand = randint(2, smaller)
            if cand != corr:
                options.add(cand)
        options = sample(options, 5)
        if corr not in options:
            options.remove(sample(options, 1)[0])
            options.append(corr)
        # 9 gcd
        shuffle(options)
        if lan == 0:
            questions.append(('¿Cuánto vale $\\text{{gcd}}({:d}, {:d})?$'.format(x, y), options, (x, y)))
        else:
            questions.append(('What is the value of $\\text{{gcd}}({:d}, {:d})?$'.format(x, y), options, (x, y)))
        bop = {'X': '\\oplus', 'A': '\\wedge', 'O': '\\vee', 'I': '\\rightarrow', 'E': '\\leftrightarrow', 'N': '\\neg'}
        cand = bop.keys() -  {'0', '1', 'N'}
        bor = sample(cand, 3)
        negs = ['N' if random() < 0.5 else '' for i in range(3)]
        expr = '{:s} ( {:s} (a {:s} b) {:s} c) {:s} {:s} d'.format(negs[0], negs[1], bor.pop(0), bor.pop(0), bor.pop(0), negs[2])
        q = expr
        for op in bop:
            q = q.replace(op, bop[op]) # prepare as LaTeX
        options = set()
        while len(options) < 4:
            options.add('$a = \{:s}, b = \{:s}, c = \{:s}, d = \{:s}$'.format('top' if random() < 0.5 else 'bot', 'top' if random() < 0.5 else 'bot', 'top' if random() < 0.5 else 'bot', 'top' if random() < 0.5 else 'bot'))
        if lan == 0:
            options.add('ninguna')
        else:
            options.add('none')            
        options = list(options)
        # 10 evaluating boolean expressions
        shuffle(options)
        if lan == 0:
            questions.append(('¿Cuál de las siguientes asignaciones satisface a ${:s}$?'.format(q), options, expr))
        else:
            questions.append(('Which of the following assignments satisfies ${:s}$?'.format(q), options, expr))        
        bor = sample(cand, 3)
        expr = 'a {:s} b {:s} c {:s} d'.format(bor[0], bor[1], bor[2])
        shuffle(bor)
        sp = ' '.join(bor) 
        q = expr
        lp = sp[::-1] # reverse
        prec = lp
        for op in bop: # prepare as LaTeX
            q = q.replace(op, bop[op]) 
            lp = lp.replace(op, bop[op])
        options = set()
        while len(options) < 4:
            options.add('$a = \{:s}, b = \{:s}, c = \{:s}, d = \{:s}$'.format('top' if random() < 0.5 else 'bot', 'top' if random() < 0.5 else 'bot', 'top' if random() < 0.5 else 'bot', 'top' if random() < 0.5 else 'bot'))
        if lan == 0:
            options.add('ninguna')
        else:
            options.add('none')            
        options = list(options)
        # 11 precedence
        shuffle(options)
        if lan == 0:
            questions.append(('Teniendo la precendencia, de mayor a menor, $ {:s} $, ¿cuál de las siguientes asignaciones satisface a ${:s}$?'.format(lp, q), options, (prec, expr)))
        else:
            questions.append(('With precedence, from highest to lowest, $ {:s} $, which of the following assignments satisfies ${:s}$?'.format(lp, q), options, (prec, expr)))
        iop = ['|', '&', '^']
        shuffle(iop)
        dire = ['<<', '>>']
        shuffle(dire)
        a = randint(20, 40)
        b = randint(10, 19)
        c = randint(1, 3)
        d = randint(30, 50)
        e = randint(20, 40)
        f = randint(1, 3)
        bc = b << c if dire[0] == '<<' else b >> c
        ef = e << f if dire[1] == '<<' else e >> f
        left = a & bc if '&' in iop[0] else a | bc if '|' in iop[0] else a ^ bc
        right = d & ef if '&' in iop[2] else d | ef if '|' in iop[2] else d ^ ef
        corr = left & right if '&' in iop[1] else left | right if '|' in iop[1] else left ^ right
        options = set()
        while len(options) < 4:
            cand = randint(0, 2 * (corr + 10))
            if cand != corr:
                options.add(cand)
        options.add(corr)
        options = list(options)
        expr = '({:d} {:s} ({:d} {:s} {:d})) {:s} ({:d} {:s} ({:d} {:s} {:d}))'.format(a, iop[0], b, dire[0], c, iop[1], d, iop[2], e, dire[1], f)
        # 12 binary arithmetic
        shuffle(options)
        if lan == 0:
            questions.append(('¿Cuánto vale {:s}?'.format(expr), options, (a, b, c, d, e, f, dire, iop)))
        else:
            questions.append(('What is the value of {:s}?'.format(expr), options, (a, b, c, d, e, f, dire, iop)))
        A = {randint(1, 99) for p in range(6, 15)}
        A = list(A)
        sA = '\\{{ {:s} \}}'.format(', '.join([str(a) for a in A]))
        options = { len(A), min(A), max(A), choice(A), randint(1, len(A) - 1)}
        while len(options) < 5:
            options.add(randint(0, 10))
        options = list(options)
        # 13 cardinality                       
        shuffle(options)
        if lan == 0:
            questions.append(('¿Cuál es la cardinalidad de $A = {:s}$?'.format(sA), options, A))
        else:
            questions.append(('What is the cardinality of $A = {:s}$?'.format(sA), options, A))
        pstart = randint(1, 7)
        plen = 12
        abre = ['(', '[']
        cierre = [')', ']']
        shuffle(abre)
        shuffle(cierre)
        hasta = pstart + plen
        desde = pstart
        if abre[0] == '(':
            desde += 1
        if cierre[0] == ')':
            hasta -= 1
        incluidos = []
        for x in range(desde, hasta + 1):
            if primo(x):
                incluidos.append(x)
        options = set()
        while len(options) < 4:
            cand = randint(0, 3 * hasta)
            if cand not in incluidos: # not a correct option
                options.add(cand)
        options.add(choice(incluidos))
        options = list(options)
        incl = '$\\{{ x \\mid x \\text{{ es primo }} \wedge x \\in {:s}{:d}, {:d} {:s}\\}}$'.format(abre[0], pstart, pstart + plen, cierre[0])
        # 14 prime numbers
        shuffle(options)
        if lan == 0:
            questions.append(('¿Cuál de los siguientes números pertenece a {:s}?'.format(incl), options, (abre[0], pstart, pstart + plen, cierre[0])))
        else:
            questions.append(('Which of the following numbers belongs to {:s}?'.format(incl), options, (abre[0], pstart, pstart + plen, cierre[0])))
        fstart = randint(0, 5)
        flen = randint(3, 5)
        extras = randint(2, 4)
        hasta = fstart + flen
        desde = fstart
        if abre[1] == '(':
            desde += 1
        if cierre[1] == ')':
            hasta -= 1
        f = fibo(hasta + extras)
        incluidos = f[desde:(hasta + 1)]
        options = set()
        while len(options) < 4:
            cand = randint(0, 2 * hasta)
            if cand not in incluidos:
                options.add(cand)
        options.add(choice(incluidos))
        options = list(options)
        incl = '$\\{{ F_i \\mid i \\in {:s}{:d}, {:d}{:s}\\}}$'.format(abre[1], fstart, fstart + flen, cierre[1])
        # 15 Fibonacci numbers
        shuffle(options)
        if lan == 0:
            questions.append(('¿Cuál de los siguientes números pertenece a {:s}'.format(incl), options, (abre[1], fstart, fstart + flen, cierre[1])))
        else:
            questions.append(('Which of the following numbers belongs to {:s}'.format(incl), options, (abre[1], fstart, fstart + flen, cierre[1])))
        A = set([string.ascii_lowercase[randint(2, 18)] for p in range(3, 6)])
        sA = '\\{{ {:s} \}}'.format(', '.join(A))
        B = set([string.ascii_lowercase[randint(0, 20)] for p in range(5, 9)])
        sB = '\\{{ {:s} \}}'.format(', '.join(B))
        op = randint(0, 3)
        if op == 0:
            C = A | B
        elif op == 1:
            C = A & B
        elif op == 2:
            C = A - B
        elif op == 3:
            C = B - A
        if random() < 0.2 and len(C) > 1:
            C.remove(sample(C, 1)[0])
        elif random() < 0.2:
            C.add(string.ascii_lowercase[randint(2, 18)])
        sC = '\\{{ {:s} \}}'.format(', '.join(C))
        sA.replace('\\{  \\}', '\\emptyset')
        sB.replace('\\{  \\}', '\\emptyset')
        sC.replace('\\{  \\}', '\\emptyset')
        options = ['$C = A \cup B$', '$C = A \cap B$', '$C = A \setminus B$', '$C = B \setminus A$']
        if lan == 0:
            options.append('ninguna')
        else:
            options.append('none')
        # 16 set operations
        shuffle(options)
        if lan == 0:
            questions.append(('Teniendo $A = {:s}$, $B = {:s}$ y $C = {:s}$, ¿cuál de las siguientes es la descripción más precisa de su relación?'.format(sA, sB, sC), options, (A, B, C)))
        else:
            questions.append(('With $A = {:s}$, $B = {:s}$ and $C = {:s}$, which of the following is the most precise description of their relationship?'.format(sA, sB, sC), options, (A, B, C)))  
        superset = sample(string.ascii_lowercase, randint(5, 8))
        k = len(superset)
        A, B = superset, sample(superset, k - randint(0, k // 2))
        if random() < 0.5:
            A, B = B, A
        sA = '\\{{ {:s} \}}'.format(', '.join(A))
        sB = '\\{{ {:s} \}}'.format(', '.join(B))
        sA.replace('\\{  \\}', '\\emptyset')
        sB.replace('\\{  \\}', '\\emptyset')
        sC.replace('\\{  \\}', '\\emptyset')        
        options = ['$A \subset B$', '$A \supset B$', '$A \subseteq B$', '$A \supseteq B$']
        if lan == 0:
            options.append('ninguna')
        else:
            options.append('none')
        # 17 subsets and supersets
        shuffle(options)
        if lan == 0:
            questions.append(('Teniendo $A = {:s}$ y $B = {:s}$, ¿cuál de las siguientes es la descripción más precisa de su relación?'.format(sA, sB), options, (A, B)))
        else:
            questions.append(('With $A = {:s}$ and $B = {:s}$, which of the following is the most precise description of their relationship?'.format(sA, sB), options, (A, B)))
        A = sample([c for c in string.ascii_lowercase], randint(4, 7))
        sA = '\\{{ {:s} \}}'.format(', '.join(A))
        corr = factorial(len(A))
        options = set()
        while len(options) < 5:
            options.add(randint(2, 7 * corr))
        if corr not in options:
            options.remove(sample(options, 1)[0])
            options.add(corr)
        options = list(options)
        shuffle(options)
        # 18 factorial
        if lan == 0:
            questions.append(('¿Cuánto vale $|{:s}|!$?'.format(sA), options, A))
        else:
            questions.append(('What is the value of $|{:s}|!$?'.format(sA), options, A))
        A = set([string.ascii_lowercase[randint(0, 20)] for p in range(4, 8)])
        sA = '\\{{ {:s} \}}'.format(', '.join(A))
        ck = len(A)
        corr = 2**ck
        options = set()
        while len(options) < 5:
            if random() < 0.5:
                options.add(2**randint(0, ck + 2))
            else:
                options.add(randint(0, 2 * corr))                
        options = sample(options, 5)        
        if corr not in options:
            options.remove(sample(options, 1)[0])
            options.append(corr)        
        # 19 conjunto potencia 
        shuffle(options)
        if lan == 0:
            questions.append(('¿Cuánto vale $|2^{{ {:s} }}|?$'.format(sA), options, A))
        else:
            questions.append(('What is the value of $|2^{{ {:s} }}|?$'.format(sA), options, A))
        n = randint(10, 15)
        k = randint(2 , n - 2)        
        options = {binom(n, h) for h in range(k - 2, k + 2)}
        while len(options) < 5:
            options.add(randint(0, 2**n))
        options = sample(options, 5)
        corr = binom(n, k)
        if corr not in options:
            options.remove(sample(options, 1)[0])
            options.append(corr)
        # 20 binomioal coefficient
        shuffle(options)
        if lan == 0:
            questions.append(('¿Cuánto vale $\\binom{{ {:d} }}{{ {:d} }}?$'.format(n, k), options, (n, k)))
        else:
            questions.append(('What is the value of $\\binom{{ {:d} }}{{ {:d} }}?$'.format(n, k), options, (n, k)))
    if 'ord' in kind:
        n = randint(5, 8)
        V = set([string.ascii_lowercase[i] for i in range(0, n)])
        m = n + randint(2, 5)
        E = dict()
        A = defaultdict(set)
        while len(E) < m:
            e = sample(V, 2)
            u = min(e)
            v = max(e)
            A[u].add(v)
            A[v].add(u)
            w = randint(1, 9)
            E[(u, v)] = w
        possibles = [str(n + i) for i in range(-3, 3)]
        possibles += [str(m + i) for i in range(-3, 3)]
        possibles = set(possibles)
        options = sample(possibles, 5)
        if str(n) not in options:
            options.remove(sample(options, 1)[0])
            options.append(str(n))
        # 1: order
        shuffle(options)
        if lan == 0:
            questions.append(('¿Cuál es el orden del grafo $G = (V, E)$ donde $V = \{' +
                              ', '.join([v for v in sorted(list(V))]) + '\}$ y $E = \{' +
                              ', '.join(['({:s}, {:s}): {:d}'.format(e[0], e[1], w) for (e, w) in E.items()]) + ' \}$', options, V))
        else:
            questions.append(('What is the order of the graph $G = (V, E)$ where $V = \{' +
                              ', '.join([v for v in sorted(list(V))]) + '\}$ and $E = \{' +
                              ', '.join(['({:s}, {:s}): {:d}'.format(e[0], e[1], w) for (e, w) in E.items()]) + ' \}$', options, V))        
        options = sample(possibles, 5)
        if str(m) not in options:
            options.remove(sample(options, 1)[0])
            options.append(str(m))
        # 2: size
        shuffle(options)
        if lan == 0:
            questions.append(('¿Cuál es el tamaño del grafo $G$?', options, E))
        else:
            questions.append(('What is the size of the graph $G$?', options, E))
        options = set([str(Fraction(2*m, n * (n - 1))), str(Fraction(2*m, n)), str(Fraction(m, n**2)), str(Fraction(m, 2 * n)), str(Fraction(2*m, (n - 1)**2))])
        while len(options) < 5:
            options.add(str(Fraction(randint(2 * m + 1, 3 * m), n * (n-1))))
        options = list(options)
        # 3: density
        shuffle(options)
        if lan == 0:
            questions.append(('¿Cuál es la densidad de $G$?', options, ''))
        else:
            questions.append(('What is the density of $G$?', options, ''))
        deg = {v: len(A[v]) for v in V}
        options = set([i for i in range(0, max(deg.values()) + 2)] + [str(Fraction(m + randint(0, m), n + randint(-n, n) // 2)) for i in range(4)])
        options = sample(list(options), 5)
        v = sample(V, 1)[0]
        grado = { 0: {'mínimo': min(deg.values()), 
                      'máximo': max(deg.values()), 
                      'promedio': Fraction(2 * m, n), 
                      'del vértice ${:s}$'.format(v): deg[v]},
                  1: {'minimum degree': min(deg.values()), 
                      'maximum degree': max(deg.values()), 
                      'average degree': Fraction(2 * m, n), 
                      'degree of vertex ${:s}$'.format(v): deg[v]}
        }
        chosen = sample(grado[lan].keys(), 1)[0]
        if grado[lan][chosen] not in options:
            options.remove(sample(options, 1)[0])
            options.append(grado[lan][chosen])
        # 4: degree
        shuffle(options)
        if lan == 0:
            questions.append(('¿Cuál es el grado ' + chosen + ' en $G$?', options, chosen))
        else:
            questions.append(('What is the ' + chosen + ' in $G$?', options, chosen))
        S = sample(V, randint(3, max(n - 3, 5)))
        k = 0
        for u in S:
            for v in S:
                if u < v:
                    if v in A[u]:
                        k += 1
        options = [i for i in range(0, m)]
        options = sample(options, 5)
        if k not in options:
            options.remove(sample(options, 1)[0])
            options.append(k)
        # 5: subgrafo
        shuffle(options)
        if lan == 0:
            questions.append(('¿Cuántas aristas tiene el subgrafo inducido en $G$ por $\{' +
                              ', '.join([v for v in S]) + '\}$?', options, S))
        else:
            questions.append(('How many edges does the subgraph induced in $G$ by $\{' +
                              ', '.join([v for v in S]) + '\}$ have?', options, S))

        options = set()
        while len(options) < 4:
            options.add('$' + ''.join([x for x in rw(A, randint(3, 5))]) + '$')
        options = list(options)
        if lan == 0:
            options.append('ninguna')
        else:
            options.append('none')
        # 6: cycle
        shuffle(options)
        if lan == 0:
            questions.append(('Elija un ciclo en $G$.', options, ''))
        else:
            questions.append(('Pick a cycle in $G$.', options, ''))
        options = set()
        allowed = min(5, len(V) - 1)
        while len(options) < 4:
            options.add('$\{' + ', '.join([x for x in set(rw(A, randint(2, allowed), rep = True))]) + '\}$')
        options = list(options)
        shuffle(options)
        if lan == 0:
            options.append('ninguna')
        else:
            options.append('none')            
            # 7: clique
        shuffle(options)
        if lan == 0:
            questions.append(('¿Cuál de las siguientes es la camarilla maximal más grande en $G$?', options, ''))
        else:
            questions.append(('Which of the following is the largest maximal clique in $G$?', options, ''))
        options = set()
        allowed = min(6, len(V))
        while len(options) < 4:
            options.add('$\{' + ', '.join([x for x in sample(V, randint(2, allowed))]) + '\}$')
        options = list(options)
        shuffle(options)
        if lan == 0:
            options.append('ninguna')
        else:
            options.append('none')
        # 8: idset
        shuffle(options)
        if lan == 0:
            questions.append(('¿Cuál de los siguientes es el conjunto independiente más grande en $G$?', options, ''))
        else:
            questions.append(('Which of the following is the largest independent set in $G$?', options, ''))
        GC = comps(A)
        mcc = set()
        options = { n }
        for cc in GC:
            k = len(cc)
            options.add(k)
            if k > len(mcc):
                mcc = cc
        while len(options) < 5:
            options.add(randint(0, m))
        # 9: connected component
        options = list(options)
        shuffle(options)
        if lan == 0:
            questions.append(('Denotando el mayor componente conexo de $G$ por $C$, ¿cuál es el orden de $C$?', options, ''))
        else:
            questions.append(('Denoting the greatest connected component of $G$ by $C$, what is order of $C$?', options, ''))
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
        dist = 0
        diam = 0
        temp = list(mcc)
        u = temp[0]
        v = temp[0]
        if len(mcc) > 1:
            D = floyd_warshall(Ac, Ec)
            selection = sample(mcc, 2)
            u = selection[0]
            for i in range(6):
                v = selection[1]
                if v not in A[u]:
                    break
            dist = D[(u, v)]
            diam = max(D.values())
        options = sample(set(D.values()), 5)
        if dist not in options:
            options.remove(sample(options, 1)[0])
            options.append(dist)
        # 10: distance        
        shuffle(options)
        if lan == 0:
            questions.append(('¿Cuál es la distancia ponderada del vértice ${:s}$ al vértice ${:s}$ en $C$?'.format(u, v), options, (u, v)))
        else:
            questions.append(('What is the weighted distance from vertex ${:s}$ to vertex ${:s}$ in $C$?'.format(u, v), options, (u, v)))
        options = sample(set(D.values()), 5)        
        if diam not in options:
            options.remove(sample(options, 1)[0])
            options.append(diam)
        # 11: diameter
        shuffle(options)
        if lan == 0:
            questions.append(('¿Cuál es el diámetro ponderado de $C$?', options, ''))
        else:
            questions.append(('What is the weighted diameter of $C$?', options, ''))
        cost, tree = mst(Ec)
        options = sample([i for i in range(max(cost - 10, 1), cost + 10)], 5)
        if cost not in options:
            options.remove(sample(options, 1)[0])
            options.append(cost)
        # 12: MST
        shuffle(options)
        if lan == 0:
            questions.append(('¿Cuánto cuesta un árbol de expansión mínima de $C$?', options, ''))
        else:
            questions.append(('What is the cost of a minimum spanning tree for $C$?', options, ''))
        A = Arbol()
        N = sample([i for i in range(1, 100)], randint(12, 18))
        for cl in N:
            A.agrega(cl)
        A.calcula()
        options = sample(N, 5)
        if N[0] not in options:
            options.remove(sample(options, 1)[0])
            options.append(N[0])
        # 13: raiz
        shuffle(options)
        if lan == 0:
            questions.append(('Sea $A$ el árbol binario que resulta agregando la secuencia de llaves $' +
                              ','.join([str(cl) for cl in N]) + '$, ¿cúal es la raíz de $A$?', options, N))
        else:
            questions.append(('Let $A$ be the binary tree that results from inserting the key sequence $' +
                              ','.join([str(cl) for cl in N]) + '$, what is the root of $A$?', options, N))        
        hc = A.hojas()
        options = sample([i for i in range(0, len(N) + 1)], 5)
        if hc not in options:
            options.remove(sample(options, 1)[0])
            options.append(hc)
        # 14: leaves
        shuffle(options)
        if lan == 0:
            questions.append(('¿Cuántas hojas tiene a $A$?', options, ''))
        else:
            questions.append(('How many leaves does $A$ have?', options, ''))
        cl = choice(N)
        nope = {0: 'no tiene', 1: 'none'}        
        p = A.ubicar(cl, 'padre')
        options = sample(N, 5)        
        if p not in options:
            options.remove(sample(options, 1)[0])
            options.append(p if p is not None else nope[lan])
        # 15: parent
        shuffle(options)
        if lan == 0:
            questions.append(('¿Cuál es el padre del nodo ${:d}$ en $A$?'.format(cl), options, cl))
        else:
            questions.append(('What is the parent of node ${:d}$ in $A$?'.format(cl), options, cl))
        cl = choice(N)
        cual = choice(['derecho', 'izquierdo']) if lan == 0 else choice(['right', 'left'])
        h = A.ubicar(cl, cual)
        options = sample(N, 5)
        if h not in options:
            options.remove(choice(options))
            options.append(h if h is not None else nope[lan])            
        # 16: child
        shuffle(options)
        if lan == 0:
            questions.append(('¿Cuál es el hijo {:s} del nodo ${:d}$ en $A$?'.format(cual, cl), options, (cual, cl)))
        else:
            questions.append(('What the is {:s} child of node ${:d}$ in $A$?'.format(cual, cl), options, (cual, cl)))
        cl = choice(N)
        a = A.ubicar(cl, 'altura')
        ma = floor(log(len(N), 2)) + 1
        options = sample([x for x in range(0, ma + 1)], 5)
        if a not in options:
            options.remove(choice(options))
            options.append(a)
        # 17: height
        shuffle(options)
        if lan == 0:
            questions.append(('¿Cuál es la altura del nodo ${:d}$ en $A$?'.format(cl), options, cl))
        else:
            questions.append(('What is the height of node ${:d}$ in $A$?'.format(cl), options, cl))
        cl = choice(N)
        p = A.ubicar(cl, 'profundidad')
        options = sample([x for x in range(0, ma + 1)], 5)
        if p not in options:
            options.remove(sample(options, 1)[0])
            options.append(p)
        # 18: depth
        shuffle(options)
        if lan == 0:
            questions.append(('¿Cuál es la profundidad del nodo ${:d}$ en $A$?'.format(cl), options, cl))
        else:
            questions.append(('What is the depth of node ${:d}$ in $A$?'.format(cl), options, cl))
        pr = sample(probs.keys(), 1)[0]
        pi = randint(0, len(probIdx[lan]) - 1)
        existentes = {v[pi] for v in probs.values()}
        if pi == 0:
            existentes |= {32, 33}
        options = sample(existentes, 5)
        corr = probs[pr][pi]        
        if corr not in options:
            options.remove(sample(options, 1)[0])
            options.append(corr)
        shuffle(options) # 19: problems
        questions.append(('{:s} {:s}?'.format(probIdx[lan][pi],
                                              probNames[lan].get(pr, pr)),
                          [probOp[lan][o] for o in options], (pr, pi, options)))
        al = sample(algs.keys(), 1)[0] 
        ai = randint(0, len(algsIdx[lan]) - 1)
        options = sample({v[ai] for v in algs.values()}, 5)
        corr = algs[al][ai]        
        if corr not in options:
            options.remove(sample(options, 1)[0])
            options.append(corr)
        shuffle(options) # 20: algorithms
        questions.append(('{:s} {:s}?'.format(algsIdx[lan][ai],
                                              algNames[lan].get(al, al)),
                          [algsOp[lan][o] for o in options], (al, ai, options)))
    return questions

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
        swap = False
        try:
            swap = form.getvalue('swap').strip().lower() == 'on'
        except:
            swap = False
        if 'r' in mod:
            trial = False # presentar de verdad
            swap = False # no se permite cambiar idioma
            pin = form.getvalue('pin').strip().lower()
            today = datetime.now().strftime('%d%m%Y')
            access = '/var/www/html/elisa/teaching/mat/discretas/data/exam/access/{:s}{:s}.lst'.format(kind, today)
            if not os.path.isfile(access):
                print('''<html>
<body>
En esta fecha no se presentan ex&aacute;menes de ese tipo. Se permite practicar, pero no presentar.
</body>
</html>''')
                return
            ok = False
            with open(access) as acc:
                for line in acc:
                    line = line.strip()
                    if len(line) == 0:
                        continue
                    else:
                        tokens = line.split()
                        if len(tokens) == 3:
                            m = tokens[0][:-1] # quitar :
                            entry = tokens[1]
                            if m == matr:
                                if pin != entry:
                                    print('<html><body>Clave incorrecta. La profesora tiene las claves de acceso. Consulte con ella.</body></html>')
                                    return
                                else:
                                    ok = True
                                break
            if not ok:
                print('<html><body>Clave inexistente. Avisa a la profesora; solamente los inscritos tienen claves.</body></html>')
                return
    except Exception as e:
        print('<html><body>Datos incorrectos, favor de revisar.', str(e) ,'</body></html>')
        return
    language = 1 * swap # Spanish if no switch, English if switch as default for those with no signup
    lan = 'spa' if language == 0 else 'eng'
    with open('/var/www/html/elisa/data/inscritos.lst') as insc:
        for line in insc:
            line = line.strip()
            if len(line) == 0:
                continue
            else:
                tokens = line.split()
                if len(tokens) == 2:
                    m = tokens[0]
                    gr = tokens[1]
                    if m == matr:
                        if swap: # switch requested
                            if tokens[1] == 'V1':
                                language = 1 # english
                            elif tokens[1] == 'M4':
                                language = 0 # spanish
                        break
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
                            print('''<html>
<body>
Correo incorrecto para la matr&iacute;cula proporcionada. No se permite el acceso.
</body>
</html>''')
                            return
                        else:
                            print('<html><title>Redireccionando al examen...</title>')
                            print('<meta http-equiv="refresh" content="2; https://elisa.dyndns-web.com/teaching/mat/discretas/exam.html?hash={:s}&kind={:s}&mod={:s}&lan={:s}&time={:s}">'.format(h, kind, mod, lan, str(datetime.now())))
                            print('</head><body>')
                            filename = '/var/www/html/elisa/teaching/mat/discretas/data/exam/{:s}{:s}_{:s}.json'.format('trial/' if trial else '', h, kind)
                            if trial or not os.path.isfile(filename):
                                print('Se est&aacute; generando un nuevo examen.')
                                output = '{{\n"kind":"{:s}",\n"language":"{:s}",\n"created":"{:s}",\n'.format(kind, lan, str(datetime.now()))
                                output += '"questions":[\n'
                                for q in generate(kind, language):
                                    output += '{{"description":"{:s}",\n'.format(q[0])
                                    output += '"data":"{:s}",\n'.format(str(q[2]))
                                    output += '"options":[{:s}]}},\n'.format(','.join(['"{:s}"'.format(str(alt)) for alt in q[1]]))
                                output = output[:-2]
                                output += '\n],\n"expires":"{:s}"\n}}'.format(str(datetime.now() + timedelta(minutes = 90)))
                                with codecs.open(filename, "w", "utf-8-sig") as target:
                                    target.write(output.replace('\\', '\\\\'))
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
