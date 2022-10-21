#!/usr/bin/env python3
import cgi, os
import cgitb; cgitb.enable()
from os import chmod
import random
from sys import argv, stdout, stderr
from xml.dom import minidom
from subprocess import check_call, Popen, CalledProcessError
import hashlib
import datetime

LOC = '/var/www/html/elisa/'

store = ["r8.1", "r8.2", "r8.3", "r8.5", "r8.7", "r8.9"]

def output(filename, fields):
   with open(filename, 'w') as target:
      print('<xml>', file = target)
      for label in fields:
         print("<field><id>{:s}</id><value>{:s}</value></field>".format(str(label), str(fields[label])), file = target)
      print('</xml>', file = target)
   return

def fill(target, filename):
   print(filename)
   source = minidom.parse(filename)
   fields = source.getElementsByTagName('field')
   for field in fields:
      label = field.childNodes[0].firstChild.data
      value = field.childNodes[1].firstChild.data
      label = label.encode('ascii', 'ignore')
      value = value.encode('ascii', 'ignore')
      target[label.decode('utf-8')] = value.decode('utf-8') 
   return

def cleantext(string):
   string = string.replace("->", '')
   string = string.replace("<-", '')
   string = string.replace(">", '')
   string = string.replace("<", '')
   string = string.replace("/", '')
   string = string.replace("(", '')
   string = string.replace(")", '')
   string = string.replace("[", '')
   string = string.replace("]", '')
   string = string.replace("{", '')
   string = string.replace("}", '')
   string = string.replace("--", '')
   return string

def clean(string):
   string = cleantext(string)
   cleaned = ''
   permitted = '.-0123456789'
   for char in string:
      place = ' '
      if char in permitted:
         place = char
      cleaned = '{:s}{:s}'.format(cleaned, place)
   return cleaned

def str2ints(string):
   values = list()
   for token in string.split():
      if '.' in token:
         token = (token.split('.'))[0]
      values.append(int(token))
   return values

def str2floats(string):
   values = list()
   for token in string.split():
      values.append(float(token))
   return values

def list2ivect(elements):
   if elements is None or len(elements) == 0:
      return 'c()'
   vector = 'c('
   for value in elements:
      vector += '{:d}, '.format(value)
   return vector[:-2] + ')'

def list2fvect(elements):
   if elements is None or len(elements) == 0:
      return 'c()'
   vector = 'c('
   for value in elements:
      vector += '{:f}, '.format(value)
   return vector[:-2] + ')'

def parse(hashstr):
   results = dict()
   with open(LOC + 'data/prob/{:s}.out'.format(hashstr)) as source:
      for line in source:
         print('Parsing result line _{:s}_<br />'.format(line.strip()))
         line = line.strip()
         tokens = line.split()
         if len(tokens) == 3: # R output
            label = tokens[1][1:-1]
            result = ("TRUE" in tokens[2])
            results[label] = result
   return results

def s2vi(label, storage, secondary=None):
   value = None
   try:
      value = str2ints(clean(storage[label]))
   except:
      if secondary is not None:
         try:
            value = str2ints(clean(secondary[label]))
         except:
            pass
      pass
   return value

def s2vf(label, storage, secondary=None):
   value = None
   try:
      value = str2floats(clean(storage[label]))
   except:
      if secondary is not None:
         try:
            value = str2floats(clean(secondary[label]))
         except:
            pass
      pass
   return value

def s2i(label, storage, secondary=None):
   value = None
   try:
      value = int(storage[label])
   except:
      if secondary is not None:
         try:
            value = int(secondary[label])
         except:
            pass
      pass
   return value

def s2f(label, storage, secondary=None):
   value = None
   try:
      value = float(storage[label])
   except:
      if secondary is not None:
         try:
            value = float(storage[label])
         except:
            pass
      pass
   return value

def exercise1(R, generated, submitted, accepted):
   print('len1 = {:s}'.format(generated["1.len"]), file = R)
   print('min1 = {:s}'.format(generated["1.min"]), file = R)
   print('max1 = {:s}'.format(generated["1.max"]), file = R)
   v1 = s2vi("r1.1", submitted, accepted)
   if v1 is not None:
      print('v1 = {:s}'.format(list2ivect(v1)), file = R)
      print('c1 = length(v1) >= len1 & min(v1) >= min1 & max(v1) <= max1', file = R)
      print('print(c("r1.1", c1 & mean(v1) > median(v1)))', file = R)
   v2 = s2vi("r1.2", submitted, accepted)
   if v2 is not None:
      print('v2 = {:s}'.format(list2ivect(v2)), file = R)
      print('c2 = length(v2) >= len1 & min(v2) >= min1 & max(v2) <= max1', file = R)
      print('print(c("r1.2", c2 & mean(v2) < median(v2)))', file = R)
   v3 = s2i("r1.3", submitted, accepted)
   if v1 is not None and v3 is not None:
      print('print(c("r1.3", min(v1) == {:d}))'.format(v3), file = R)
   v4 = s2i("r1.4", submitted, accepted)
   if v2 is not None and v4 is not None:
      print('print(c("r1.4", max(v2) == {:d}))'.format(v4), file = R)
   v5 = s2f("r1.5", submitted)
   if v1 is not None and v5 is not None:
      print('print(c("r1.5", {:f} == unname(quantile(v1, 0.25))))'.format(v5), file = R)
   v6 = s2f("r1.6", submitted, accepted)
   if v2 is not None and v6 is not None:
      print('print(c("r1.6", {:f} == unname(quantile(v2, 0.75))))'.format(v6), file = R)
   v7 = s2i("r1.7", submitted, accepted)
   if v7 is not None:
      if v1 is not None and v2 is not None:
         print('a1 = quantile(v1, 0.75) - quantile(v1, 0.25)', file = R)
         print('a2 = quantile(v2, 0.75) - quantile(v2, 0.25)', file = R)
         print('r1 = 0', file = R)
         print('if (a1 > a2) { r1 = 1 }', file = R)
         print('if (a1 == a2) { r1 = 2 }', file = R)
         print('if (a1 < a2) { r1 = 3 }', file = R)
         print('print(c("r1.7", r1 == {:d}))'.format(v7), file = R)
      else:
         print('print(c("r1.7", 3 == 4))', file = R)
   return 

def exercise2(R, generated, submitted, accepted):
   v = s2vi("2.data", generated)
   print('v = {:s}'.format(list2ivect(v)), file = R)
   print('t = table(v)', file = R)
   v1 = s2i("r2.1", submitted, accepted)
   if v1 is not None:
      print('mode = as.numeric(names(t))[which.max(t)]', file = R)
      print('mf = as.numeric(t[names(t) == mode])', file = R)
      print('rf = as.numeric(t[names(t) == {:d}])'.format(v1), file = R)
      print('print(c("r2.1", mf == rf))', file = R)
   v2 = s2f("r2.2", submitted, accepted) 
   if v2 is not None:
      print('print(c("r2.2", round(sd(v), 3) == {:.3f}))'.format(v2), file = R)
   v3 = s2i("r2.3", submitted, accepted)
   if v3 is not None:
      print('h = hist(v, 3, plot=FALSE)', file = R)
      print('least = which.min(h$counts)', file = R)
      print('howmany = sum(h$counts == least)', file = R)
      print('option = least', file = R)
      print('if (howmany > 1) { option = 4 }', file = R)
      print('print(c("r2.3", (option == {:d})))'.format(v3), file = R)
   v4 = s2i("r2.4", submitted, accepted)
   if v4 is not None:
      print('cumrel = cumsum(t) / length(v)', file = R)
      print('upper = cumrel[cumrel >= 0.5]', file = R)
      print('first = names(upper)[1]', file = R)
      print('print(c("r2.4", first == {:d}))'.format(v4), file = R)
   return

def exercise3(R, generated, submitted, accepted):
   print('len3 = 20', file = R)
   print('min3 = {:s}'.format(generated["3.min"]), file = R)
   print('max3 = {:s}'.format(generated["3.max"]), file = R)
   print('library("moments")', file = R)
   v1 = s2vi("r3.1", submitted, accepted)
   if v1 is not None:
      print('v1 = {:s}'.format(list2ivect(v1)), file = R)
      print('c1 = length(v1) >= len3 & min(v1) >= min3 & max(v1) <= max3', file = R)
      print('print(c("r3.1", c1 & (kurtosis(v1) > 4)))', file = R)
   v2 = s2vi("r3.2", submitted, accepted)
   if v2 is not None:
      print('v2 = {:s}'.format(list2ivect(v2)), file = R)
      print('c2 = length(v2) >= len3 & min(v2) >= min3 & max(v2) <= max3', file = R)
      print('print(c("r3.2", c2 & (kurtosis(v2) < 2)))', file = R)
   v3 = s2vi("r3.3", submitted, accepted)
   if v3 is not None:
      print('v3 = {:s}'.format(list2ivect(v3)), file = R)
      print('c3 = length(v3) >= len3 & min(v3) >= min3 & max(v3) <= max3', file = R)
      print('print(c("r3.3", c3 & (skewness(v3) > 0.7)))', file = R)
   v4 = s2vi("r3.4", submitted, accepted)
   if v4 is not None:
      print('v4 = {:s}'.format(list2ivect(v4)), file = R)
      print('c4 = length(v4) >= len3 & min(v4) >= min3 & max(v4) <= max3', file = R)
      print('print(c("r3.4", c4 & (skewness(v4) < -0.7)))', file = R)
   return

def exercise4(R, generated, submitted, accepted):
   print('x1 = {:d}'.format(s2i("4.x1", generated)), file = R)
   print('x2 = {:d}'.format(s2i("4.x2", generated)), file = R)
   print('x3 = {:d}'.format(s2i("4.x3", generated)), file = R)
   print('x4 = {:d}'.format(s2i("4.x4", generated)), file = R)
   print('t = x1 + x2 + x3 + x4', file = R)
   print('p1 = x1 / t', file = R)
   print('p2 = x2 / t', file = R)
   print('p3 = x3 / t', file = R)
   print('p4 = x4 / t', file = R)
   print('singletons = c(p1, p2, p3, p4)', file = R)
   print('pairs = c(p1 + p2, p1 + p3, p1 + p4, p2 + p3, p2 + p4, p3 + p4)', file = R)
   v1 = s2f("r4.1", submitted, accepted)
   if v1 is not None:
      print('print(c("r4.1", round(max(1 - singletons), 3) == {:.3f}))'.format(v1), file = R)
   v2 = s2f("r4.2", submitted, accepted)
   if v2 is not None:
      print('print(c("r4.2", round(min(pairs), 3) == {:.3f}))'.format(v2), file = R)
   v3 = s2f("r4.3", submitted, accepted)
   if v3 is not None:
      print('print(c("r4.3", round(max(pairs), 3) == {:.3f}))'.format(v3), file = R)
   v4 = s2f("r4.4", submitted, accepted)
   if v4 is not None:
      print('print(c("r4.4", round(max(singletons), 3) == {:.3f}))'.format(v4), file = R)
   return

def exercise5(R, generated, submitted, accepted):
   print('l <- 6', file = R)
   print('p = 1 / l', file = R)
   print('q = 1 - p', file = R)
   print('n <- l**3', file = R)
   v1 = s2f("r5.1", submitted, accepted)
   if v1 is not None:
      print('allsame =  1 * p * p', file = R)
      print('print(c("r5.1", round(allsame, 3) == {:.3f}))'.format(v1), file = R)
   v2 = s2f("r5.2", submitted, accepted)
   if v2 is not None:
      print('ninguno = q * q * q', file = R)
      print('porlomenosuno =  1 - ninguno', file = R)
      print('print(c("r5.2", round(porlomenosuno, 3) == {:.3f}))'.format(v2), file = R)
   v3 = s2f("r5.3", submitted, accepted)
   if v3 is not None:
      suma = s2i('5.sum', generated)
      print('v <- {:d}'.format(suma), file = R)
      print('k <- 0', file = R)
      print('r <- seq(1, l, 1)', file = R)
      print('for (x in r) { for (y in r) { for (z in r) { if (x + y + z > v) { k <- k + 1 }}}}', file = R)
      print('sumamayor <- k / n', file = R)
      print('print(c("r5.3", round(sumamayor, 3) == {:.3f}))'.format(v3), file = R)
   v4 = s2f("r5.4", submitted, accepted)
   if v4 is not None:
      menor = s2i('5.less', generated)
      print('m <- {:d}'.format(menor), file = R)
      print('pm <- (m  - 1)/ l', file = R)
      print('todosmenos <- pm * pm * pm', file = R)
      print('print(c("r5.4", round(todosmenos, 3) == {:.3f}))'.format(v4), file = R)
   return

def exercise6(R, generated, submitted, accepted):
   v = s2f("r6.1", submitted, accepted)
   if v is not None:
      n = s2i("6.len", generated)
      F = s2i("6.cheat", generated)
      print('PT = {:d} / {:d}'.format(F, n), file = R)
      HH = s2i("6.HH", generated)
      print('PhH = {:d} / 100'.format(HH), file = R)
      TT = s2i("6.TT", generated)
      print('PtT = {:d} / 100'.format(TT), file = R)
      print('PH <- 1 - PT', file = R)
      print('PhT <- 1 - PtT', file = R)
      print('PtH <- 1 - PhH', file = R)
      print('a <- PT * PtT', file = R)
      print('b <- PH * PtH', file = R)
      print('PTt <- a / (a + b)', file = R)
      print('print(c("r6.1", round(PTt, 3) == {:.3f}))'.format(v), file = R)
   return

def exercise7(R, generated, submitted, accepted):
   vu = s2f("r7.1", submitted, accepted)
   if vu is not None:
      umin = s2i('7.umin', generated)
      umax = s2i('7.umax', generated)
      ux = s2i('7.ux', generated)
      print('a = {:d}'.format(umin), file = R)
      print('b = {:d}'.format(umax), file = R)
      print('cuantos = b - a + 1', file = R)
      print('corte = {:d}'.format(ux), file = R)
      print('encima = b - corte', file = R)
      print('pu = 1 - encima / cuantos', file = R)
      print('print(c("r7.1", round(pu, 3) == {:.3f}))'.format(vu), file = R)

   vg = s2f("r7.2", submitted, accepted)
   if vg is not None:
      gp = s2f('7.gp', generated)
      gx = s2i('7.gx', generated)
      print('p = {:f}'.format(gp), file = R)
      print('gx = {:d}'.format(gx), file = R)
      print('q <- 1 - p', file = R)
      print('probs <- numeric()', file = R)
      print('for (x in seq(0, gx, 1)) { probs <- c(probs, q**x * p) }', file = R)
      print('cumulat <- cumsum(probs)', file = R)
      print('pg = cumulat[gx + 1]', file = R)
      print('print(c("r7.2", round(pg, 3) == {:.3f}))'.format(vg), file = R)

   vh = s2f("r7.3", submitted, accepted)
   if vh is not None:
      hm = s2i('7.hm', generated)
      hn = s2i('7.hn', generated)
      hk = s2i('7.hk', generated)
      hx = s2i('7.hx', generated)
      if hx is None:
         print('Using the default value for 7.hx')
         hx = 5
      print('hm <- {:d}'.format(hm), file = R)
      print('hn <- {:d}'.format(hn), file = R)
      print('hk <- {:d}'.format(hk), file = R)
      print('hx <- {:d}'.format(hx), file = R)
      print('ho <- seq(0, hx, 1)', file = R)
      print('b <- choose(hn, ho)', file = R)
      print('c <- choose(hm, hk - ho)', file = R)
      print('hr <- (b * c) / choose(hn + hm, hk)', file = R)
      print('print(c("r7.3", round(sum(hr), 3) == {:.3f}))'.format(vh))

   vb = s2f("r7.4", submitted, accepted)
   if vb is not None:
      bp = s2f('7.bp', generated)
      bmax = s2i('7.bmax', generated)
      bx = s2i('7.bx', generated)
      print('p = {:f}'.format(bp), file = R)
      print('q <- 1 - p', file = R)
      print('n = {:d}'.format(bmax), file = R)
      print('bx = {:d}'.format(bx), file = R)
      print('pr <- numeric()', file = R)
      print('for (x in seq(0, bx, 1)) { pr <- c(pr, choose(n, x) * p**x * q**(n-x)) }', file = R)
      print('cumulat <- cumsum(pr)', file = R)
      print('pb = cumulat[bx + 1]', file = R)
      print('print(c("r7.4", round(pb, 3) == {:.3f}))'.format(vb), file = R)

   vp = s2f("r7.5", submitted, accepted)
   if vp is not None:
      pl = s2f('7.pl', generated)
      px = s2i('7.px', generated)
      print('px <- {:d}'.format(px), file = R)
      print('lambda <- {:f}'.format(pl), file = R)
      print('probs <- numeric()', file = R)
      print('for (x in seq(0, px, 1)) { probs <- c(probs, (exp(-lambda) * lambda**x) / factorial(x)) }', file = R)
      print('cumulat <- cumsum(probs)', file = R)
      print('pp = cumulat[px + 1]', file = R)
      print('print(c("r7.5", round(pp, 3) == {:.3f}))'.format(vp), file = R)

   ve = s2f("r7.6", submitted, accepted)
   if ve is not None:
      el = s2f('7.el', generated)
      efrom = s2f('7.efrom', generated)
      eto = s2f('7.eto', generated)
      print('el <- {:f}'.format(el), file = R)
      print('efrom <- {:f}'.format(efrom), file = R)
      print('eto <- {:f}'.format(eto), file = R)
      print('elow <- pexp(efrom, rate=el)', file = R)
      print('ehi <- pexp(eto, rate=el)', file = R)
      print('print(c("r7.6", round(ehi - elow, 3) == {:.3f}))'.format(ve), file = R)

   vn = s2f("r7.7", submitted, accepted)
   if vn is not None:
      nm = s2f('7.nm', generated)
      nd = s2f('7.nd', generated)
      nfrom = s2f('7.nfrom', generated)
      nto = s2f('7.nto', generated)
      print('nm <- {:f}'.format(nm), file = R)
      print('nd <- {:f}'.format(nd), file = R)
      print('nfrom <- {:f}'.format(nfrom), file = R)
      print('nto <- {:f}'.format(nto), file = R)
      print('nlow <- pnorm(nfrom, mean=nm, sd=nd)', file = R)
      print('nhi <- pnorm(nto, mean=nm, sd=nd)', file = R)
      print('print(c("r7.7", round(nhi - nlow, 3) == {:.3f}))'.format(vn), file = R)
   return

def exercise8(R, generated, submitted, accepted):
   print('req = 15', file = R) # largo minimo requerido
   i1 = s2vf("r8.4", submitted, accepted)
   if i1 is not None:
      print('i1 = {:s}'.format(list2fvect(i1)), file = R)
      print('n1 = length(i1)', file = R)
      print('print(c("r8.4", n1 >= req))', file = R)
      print 
   i2 = s2vf("r8.6", submitted, accepted)
   if i2 is not None:
      print('i2 = {:s}'.format(list2fvect(i2)), file = R)
      print('n2 = length(i2)', file = R)
      print('print(c("r8.6", n2 >= req))', file = R)
   i3 = s2vf("r8.8", submitted, accepted)
   if i3 is not None:
      print('i3 = {:s}'.format(list2fvect(i3)), file = R)
      print('n3 = length(i3)', file = R)
      print('print(c("r8.8", n3 >= req))', file = R)
   i4 = s2vf("r8.10", submitted, accepted)
   if i4 is not None:
      print('i4 = {:s}'.format(list2fvect(i4)), file = R)
      print('n4 = length(i4)', file = R)
      print('print(c("r8.10", n4 >= req))', file = R)
   pob = s2vi("r8.11", submitted, accepted)
   if pob is not None:
      print('pob = {:s}'.format(list2ivect(pob)), file = R)
      print('np = length(pob)', file = R)
      print('print(c("r8.11", np >= req & min(pob) >= 0))', file = R)
   norm = s2vi("r8.12", submitted, accepted)
   if norm is not None:
      if pob is None or i1 is None:
         print('print(c("r8.12", FALSE))' , file = R)
      else:
         print('norm = round({:s}, 3)'.format(list2fvect(norm)), file = R)
         print('correct = round(i1 / pob, 3)', file = R)
         print('print(c("r8.12", sum((norm == correct) == length(norm)) == 0))', file = R)
   c12 = s2f("r8.13", submitted, accepted)
   if c12 is not None:
      if i1 is None or i2 is None:
         print('print(c("r8.13", FALSE))', file = R)
      else:
         print('if (n1 != n2 | n1 != np | n2 != np | np < 15) { print(c("r8.13", FALSE)) } else {', file = R)
         print('cor12 = round(cor(i1 / pob, i2 / pob), 3)', file = R)
         print('print(c("r8.13", cor12 == {:.3f})) }'.format(c12), file = R)
   c13 = s2f("r8.14", submitted, accepted)
   if c13 is not None:
      if i1 is None or i3 is None or pob is None:
         print('print(c("r8.14", FALSE))', file = R)
      else:
         print('if (n1 != n3 | n1 != np | n3 != np | np < 15) { print(c("r8.14", FALSE)) } else {', file = R)
         print('cor13 = round(cor(i1 / pob, i3 / pob), 3)', file = R)
         print('print(c("r8.14", cor13 == {:.3f})) }'.format(c13), file = R)
   c24 = s2f("r8.15", submitted, accepted)
   if c24 is not None:
      if  i2 is None or i4 is None or pob is None:
         print('print(c("r8.15", FALSE))', file = R)
      else:
         print('if (n2 != n4 | n2 != np | n4 != np | np < 15) { print(c("r8.15", FALSE)) } else {', file = R)
         print('cor24 = round(cor(i2 / pob, i4 / pob), 3)', file = R)
         print('print(c("r8.15", cor24 == {:.3f})) }'.format(c24), file = R)
   c34 = s2f("r8.16", submitted, accepted)
   if c34 is not None:
      if i3 is None or i4 is None or pob is None:
         print('print(c("r8.16", FALSE))', file = R)
      else:
         print('if (n3 != n4 | n3 != np | n4 != np | np < 15) { print(c("r8.16", FALSE)) } else {', file = R)
         print('cor34 = round(cor(i3 / pob, i4 / pob), 3)', file = R)
         print('print(c("r8.16", cor34 == {:.3f})) }'.format(c34), file = R)
   opt = s2i("r8.17", submitted, accepted)
   if opt is not None:
      print('print(c("r8.17", {:d} == 1))'.format(opt), file = R)
   return

def exercise9(R, generated, submitted, accepted):
   print('ns = 20', file = R)
   print('nl = 100', file = R)
   print('m = {:f}'.format(s2f('9.mean', generated)), file = R)
   print('s = {:f}'.format(s2f('9.sd', generated)), file = R)
   print('a = 1 - {:d} / 100'.format(s2i('9.conf', generated)), file = R)
   print('cola <- a / 2', file = R)
   print('quartil <- 1 - cola', file = R)
   small = s2vf("r9.1", submitted, accepted) 
   if small is not None:
      print('small = {:s}'.format(list2fvect(small)), file = R)
      print('ms = mean(small)', file = R)
      print('mok = ms > m - s & ms < m + s', file = R)
      print('ss = sd(small)', file = R)
      print('sok = ss > s / 2 & ss < 2 * s', file = R)
      print('print(c("r9.1", length(small) == ns & mok & sok))', file = R)
   inferior = s2f("r9.2", submitted, accepted)
   if inferior is not None:
      if small is None:
         print('print(c("r9.2", FALSE))', file = R)
      else:
         print('infc <- ms - qt(quartil, ns - 1) * (ss / sqrt(ns))', file = R)
         print('print(c("r9.2", round(infc, 3) == {:.3f}))'.format(inferior), file = R)
   large = s2vf("r9.3", submitted, accepted)
   if large is not None:
      print('large = {:s}'.format(list2fvect(large)), file = R)
      print('ml = mean(large)', file = R)
      print('mok = ml > m - s & ml < m + s', file = R)
      print('sl = sd(large)', file = R)
      print('sok = sl > s / 2 & sl < 2 * s', file = R)
      print('print(c("r9.3", length(large) == nl & mok & sok))', file = R)
   superior = s2f("r9.4", submitted, accepted)
   if superior is not None:
      if large is None:
         print('print(c"9.3", FALSE))', file = R)
      else:
         print('supc <- ml + qt(quartil, nl - 1) * (sl / sqrt(nl))', file = R)
         print('print(c("r9.4", round(supc, 3) == {:.3f}))'.format(superior), file = R)
   return

def exercise10(R, generated, submitted, accepted):
   p = s2f("r10.1", submitted, accepted)
   if p is not None:
      print('rawagua <- c(16, 15, 11, 20, 19, 14, 13, 15, 14, 16)', file = R)
      print('rawalcohol <- c(13, 13, 10, 18, 17, 11, 10, 15, 11, 16)', file = R)
      excl = s2i("10.excl", generated)
      print('excl = {:d}'.format(excl), file = R)
      print('agua = rawagua[-excl]', file = R)
      print('alcohol = rawalcohol[-excl]', file = R)
      print('n <- length(agua)', file = R)
      print('diferencia <- agua - alcohol', file = R)
      print('mediaObservada <- mean(diferencia)', file = R)
      print('desviacion <- sd(diferencia)', file = R)
      print('error <- desviacion / sqrt(n)', file = R)
      print('t <- mediaObservada / error', file = R)
      print('gdl <- n - 1', file = R)
      print('colaIzquierda <- pt(-t, gdl)', file = R)
      print('colaDerecha <- 1 - pt(t, gdl)', file = R)
      print('valorP <- colaIzquierda + colaDerecha', file = R)
      print('print(c("r10.1", round(valorP, 3) == {:.3f}))'.format(p), file = R)
   a = s2f("r10.2", submitted, accepted)
   if a is not None:
      print('alfa = {:f}'.format(a), file = R)
      print('print(c("r10.2", alfa > 0.01 & alfa < 0.5))', file = R)
   hipo = s2i("r10.3", submitted, accepted)
   if hipo is not None:
      if p is None or a is None:
         print('print(c("r10.3",FALSE))', file = R)
      else:
         print('opt = 0', file = R)
         print('if (valorP < alfa) { opt = 1 } else { opt = 2 }', file = R)
         print('print(c("r10.3", opt == {:d}))'.format(hipo), file = R)
   conc = s2i("r10.4", submitted, accepted)
   if conc is not None:
      if p is None or a is None or hipo is None:
         print('print(c("r10.4",FALSE))', file = R)
      else:
         print('print(c("r10.4", opt == {:d}))'.format(conc), file = R)
   return

def exercise11(R, generated, submitted, accepted):
   x1 = s2i("11.x1", generated)
   x2 = s2i("11.x2", generated)
   x3 = s2i("11.x3", generated)
   x4 = s2i("11.x4", generated)
   x5 = s2i("11.x5", generated)
   x6 = s2i("11.x6", generated)
   y1 = s2i("11.y1", generated)
   y2 = s2i("11.y2", generated)
   y3 = s2i("11.y3", generated)
   y4 = s2i("11.y4", generated)
   y5 = s2i("11.y5", generated)
   y6 = s2i("11.y6", generated)
   print('X = c({:d}, {:d}, {:d}, {:d}, {:d}, {:d})'.format(x1, x2, x3, x4, x5, x6), file = R)
   print('Y = c({:d}, {:d}, {:d}, {:d}, {:d}, {:d})'.format(y1, y2, y3, y4, y5, y6), file = R)
   print('r <- cor(X, Y)', file = R)
   print('b <- r * sd(Y) / sd(X)', file = R)
   print('a <- mean(Y) - b * mean(X)', file = R)
   print('Yp <- b * X + a', file = R)
   b = s2f("r11.1", submitted, accepted)
   if b is not None:
      print('print(c("r11.1", round(b, 3) == {:.3f}))'.format(b), file = R)
   a = s2f("r11.2", submitted, accepted)
   if a is not None:
      print('print(c("r11.2", round(a, 3) == {:.3f}))'.format(a), file = R)
   conf = s2i("11.conf", generated)
   print('SSY <- sum((Y - mean(Y))**2)', file = R)
   print('SSYp <- sum((Yp - mean(Yp))**2)', file = R)
   print('SSE <- sum((Y - Yp)**2)', file = R)
   print('n <- length(X)', file = R)
   print('se <- sqrt(((1 - r**2)*SSY)/(n - 2))', file = R)
   print('SSX <- sum((X - mean(X))**2)', file = R)
   print('sb <- se / sqrt(SSX)', file = R)
   print('DoF <- n - 2', file = R)
   mitad = (100.0 - conf) / 2
   quartil = 1.0 - mitad / 100.0
   print('paso <- sb * qt({:f}, DoF)'.format(quartil), file = R)
   print('bInf <- b - paso', file = R)
   print('bSup <- b + paso', file = R)
   linf = s2f("r11.3", submitted, accepted)
   if linf is not None:
      print('print(c("r11.3", round(bInf, 3) == {:.3f}))'.format(linf), file = R)
   lsup = s2f("r11.4", submitted, accepted)
   if lsup is not None:
      print('print(c("r11.4", round(bSup, 3) == {:.3f{))'.format(lsup), file = R)
   p = s2f("r11.5", submitted, accepted)
   if p is not None:
      print('m = lm(Y ~ X)', file = R)
      print('s = summary(m)', file = R)
      print('p = s$coefficients[2, 4]', file = R)
      print('print(c("r11.5", round(p, 3) == {:.3f}))'.format(p), file = R)
   opt = s2i("r11.6", submitted, accepted)
   if opt is not None:
      print('optP = 2', file = R)
      print('optInt = 1', file = R)
      if p is not None:
         print('if (p < 0.05) { optP = 1 }', file = R)
      if linf is not None and lsup is not None:
         print('if (bInf <= 0 & bSup >= 0) { optInt = 2 }', file = R)
      print('if (optP != optInt) { opt = 3 } else { opt = optP }', file = R)
      print('print(c("r11.6", opt == {:d}))'.format(opt), file = R)
   return

def exercise12(R, generated, submitted, accepted):
   inc = s2i("12.inc", generated)
   ismoke = s2i("12.ismoke", generated)
   iprev = s2i("12.iprev", generated)
   cont = s2i("12.cont", generated)
   csmoke = s2i("12.csmoke", generated)
   cprev = s2i("12.cprev", generated)
   inever = inc - ismoke - iprev
   cnever = cont - csmoke - cprev
   print('saludables <- c({:d}, {:d}, {:d})'.format(csmoke, cprev, cnever), file = R)
   print('enfermos <- c({:d}, {:d}, {:d})'.format(ismoke, iprev, inever), file = R)
   print('total <- saludables + enfermos', file = R)
   print('te <- sum(enfermos)', file = R)
   print('ts <- sum(saludables)', file = R)
   print('tt <- sum(total)', file = R)
   print('ee <- (te * total) / tt', file = R)
   print('es <- (ts * total) / tt', file = R)
   ein = s2f('r12.1', submitted, accepted)
   if ein is not None:
      print('ein = ee[3]', file = R)
      print('print(c("r12.1", round(ein, 3) == {:.3f}))'.format(ein), file = R)
   ecs = s2f('r12.2', submitted, accepted)
   if ecs is not None:
      print('ecs = es[1]', file = R)
      print('print(c("r12.2", round(ecs, 3) == {:.3f}))'.format(ecs), file = R)
   p = s2f('r12.3', submitted, accepted)
   if p is not None:
      print('consultar <- sum(((enfermos - ee)**2 / ee)) + sum(((saludables - es)**2 / es))', file = R)
      print('gdl <- (2 - 1) * (3 - 1)', file = R)
      print('p <- 1 - pchisq(consultar, gdl)', file = R)
      print('print(c("r12.3", round(p, 3) == {:.3f}))'.format(p), file = R)
   opt = s2i('r12.4', submitted, accepted)
   if opt is not None:
      if p is None:
         print('print(c("r12.4", FALSE))', file = R)
      else:
         print('opt = {:d}'.format(opt), file = R)
         print('a = 0.01', file = R)
         print('if (p < a & opt == 1) { print(c("r12.4", TRUE)) }' , file = R)
         print('if (p < a & opt == 2) { print(c("r12.4", FALSE)) }' , file = R)
         print('if (p >= a & opt == 1) { print(c("r12.4", FALSE)) }', file = R)
         print('if (p >= a & opt == 2) { print(c("r12.4", TRUE)) }', file = R)
   return


specific = { "r1": exercise1, "r2": exercise2, "r3": exercise3, "r4": exercise4, \
             "r5": exercise5, "r6": exercise6, "r7": exercise7, "r8": exercise8, \
             "r9": exercise9, "r10": exercise10, "r11": exercise11, "r12": exercise12 }

def grade(label, generated, submitted, accepted, hashstr):
   if label not in specific:
      print('ERROR: Unknown exercise label _{:s}_<br />.'.format(label))
      return 
   resultname = LOC + 'data/prob/{:s}.out'.format(hashstr)
   with open(resultname, 'w') as R:
      print('(erased)', file = R) # erase previous execution
   scriptname = LOC + 'data/prob/{:s}.R'.format(hashstr)
   with open(scriptname, 'w') as R:
      print('sink("{:s}")'.format(resultname), file = R)
      specific[label](R, generated, submitted, accepted)
      print('sink()', file = R)
      print('quit(save = "no", status = 0)', file = R)
   try:
      check_call(['/usr/bin/Rscript --vanilla {:s}'.format(scriptname)], stderr=stdout, stdout=stdout, shell=True)
   except CalledProcessError as e:
      print('<p>Error al ejecutar R: {:s} </p>'.format(str(e)))
      pass
   return 
            
def main():
   print('Content-type: text/html\n\n')
   print('<html>')
   print('<head><title>Grading completed</title></head>')
   print('<body>')
   print('<p>No-one actually needs to see this.</p>')
   hashstr = None
   form = None
   timestamp = str(datetime.datetime.now()).split('.')[0]
   print('<h1>Debug output</h1><p>')
   print('Activated', timestamp, '<br />')
   form = cgi.FieldStorage()
   hashstr = form.getvalue('hash')
   if hashstr is None:
      try:
         student = argv[1] # debug mode
      except:
         print('No hashstr nor student info <br />')
         return
   if hashstr is None: # debug mode
      hashstr = hashlib.md5(student.encode("utf-8")).hexdigest()
   print('Hashstr', hashstr, '<br />')
   filename = LOC + 'teaching/prob/data/{:s}'.format(hashstr)
   logged = list()
   with open(LOC + 'data/logged.txt') as record:
      for line in record.readlines():
         line = line.strip()
         if len(line) == 0:
            continue
         elif line[0] == "#":
            continue # comment
      else:
         if line[0] == "r":
            logged.append(line)
   record.close()

   award = dict()
   with open(LOC + 'data/awarded.txt', 'r') as pts:
      for line in pts:
         line = line.strip()
         if len(line) == 0:
            continue
         elif line[0] == "#":
            continue # comment
         else:
            tokens = line.split()
            if len(tokens) == 2:
               label = tokens[0]
               value = float(tokens[1])
               award[label] = value
            else:
               print('ERROR parsing awarded points: <{:s}>.'.format(line , '<br />'))
   print('Point values parsed', '<br />')
   status = dict()
   fill(status, '{:s}.awarded.xml'.format(filename))
   accepted = dict()
   fill(accepted, '{:s}.accepted.xml'.format(filename))
   rejected = dict()
   fill(rejected, '{:s}.rejected.xml'.format(filename))
   attempts = dict()
   fill(attempts, '{:s}.attempts.xml'.format(filename))
   generated = dict()
   fill(generated, '{:s}.generated.xml'.format(filename))
   print('Participant data storage parsed from', filename, '<br />')
   with open(LOC + 'data/prob/{:s}.log'.format(hashstr), 'a') as logfile:
      print('Logfile open; will log ', logged, '<br />')
      print('<session>\nSubmission of {:s} at {:s}'.format(hashstr, timestamp), file = logfile)
      submitted = dict()
      exercise = None
      for label in award:
         response = form.getvalue(label)
         if response is not None:
            response = response.strip()
            if len(response) == 0:
               continue
            submitted[label] = response
            if exercise is None:
               exercise = (label.split('.'))[0]
      for label in logged:
         response = form.getvalue(label)
         if response is not None:
            response = response.strip()
            if len(response) == 0:
               continue
            print(label, response)
            print("<p>Logging {:s} for {:s}.</p>".format(response, label))
            print('Contents of field {:s}: {:s}'.format(label, response), file = logfile)
            accepted[label] = response # these are automatically accepted and remembered
      if len(submitted) == 0:
         try:
            for value in argv[2:]:
               tokens = value.split('=')
               label = tokens[0]
               response = tokens[1]
               submitted[label] = response
               if exercise is None:
                  exercise = (label.split('.'))[0]
                  print('Exercise: {:s}\n</session>'.format(exercise), file = logfile)
                  print('Identified exercise as {:s}.<br>'.format(exercise))
         except:
            pass
   print(submitted)
   if exercise is not None:
      print('Grading exercise', exercise, 'using ', submitted, '<br />')
      print('Computing the expected results', '<br />')
      grade(exercise, generated, submitted, accepted, hashstr)
      print('Parsing the results', '<br />')
      responses = parse(hashstr)
      c = len(responses)
      print(c, 'results graded', '<br />')
      if c > 0:
         if exercise not in attempts:
            attempts[exercise] = 1
         else:
            attempts[exercise] = int(attempts[exercise]) + 1
      for label in responses:
         if label in store:
            print('Stored answer for', label, '<br>')
            accepted[label] = cleantext(submitted[label])
            if label not in attempts:
               attempts[label] = 1
            else:
               attempts[label] = int(attempts[label]) + 1
         if label in submitted:
            if responses[label]: # correct
               print('Correct answer for', label, '<br>')
               status[label] = award[label]
               accepted[label] = submitted[label]
            else:
               print('Incorrect answer for', label, '<br>')
               if label not in status: 
                  status[label] = "0" 
               if status[label] == "0":
                  rejected[label] = submitted[label]
      print('Done grading, ready to store the results', '<br />')
      output('{:s}.awarded.xml'.format(filename), status)
      output('{:s}.accepted.xml'.format(filename), accepted)
      output('{:s}.rejected.xml'.format(filename), rejected)
      output('{:s}.attempts.xml'.format(filename), attempts)
   print('</p>')
   print('</body>')
   print('</html>')
   return


if __name__ == "__main__":
    main()

