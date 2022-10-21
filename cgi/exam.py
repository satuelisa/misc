#!/usr/bin/env python3

import cgi, os
import cgitb; cgitb.enable()
from time import localtime, strftime
import datetime
from os import path, chmod
import random
from sys import argv

LOC = '/var/www/html/elisa/data/'

def space(cont):
   cont = cont.strip()
   if ' ' in cont:
      return cont
   else:
      spaced = ''
      for c in cont:
         spaced = '%s %c' % (spaced, c)
      return spaced

def points(cont, unidad):
   total = 0
   problems = cont.split()
   for problem in problems:
      if '-' not in problem:
         try:
            total += float(problem)
         except:
            pass
   return total

def main():
   print('Content-type: text/html\n\n')
   hash = None
   try:
      form = cgi.FieldStorage()
      matr = form.getvalue('matr')
      unidad = form.getvalue('ua')
   except:
      return
   if matr is None:
      return
   matr = matr.strip()
   filename = "exams_" + unidad.strip() + ".txt"
   data = None
   try:
      data = open(LOC + filename, 'r')
   except:
      return
   for line in data:
      line = line.strip()
      if len(line) == 0:
         continue
      if matr in line:
         mc = ''
         ord = ''
         pf = ''
         pr = ''
         for token in line.split():
            if 'mc' in token:
               mc = '%s%s ' % (mc, token[2:])
            if 'eo' in token:
               ord = '%s%s ' % (ord, token[2:])
            if 'pf' in token:
               pf = '%s%s ' % (pf, token[2:])
            if 'pr' in token:
               pr = '%s%s ' % (pr, token[2:])
         if len(mc) > 0:
            print('mc', mc.strip())
         if len(ord) > 0:
            print('eo', ord.strip())
         if len(pf) > 0:
            print('pf', pf.strip())
         if len(pr) > 0:
            print('pr', pr.strip())
   data.close()

if __name__ == "__main__":
    main()
