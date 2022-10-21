#!/usr/bin/env python3

import cgi, os
import cgitb; cgitb.enable()
from sys import argv

def main():
   print('Content-type: text/plain\n\n')
   form = cgi.FieldStorage()
   vote = form.getvalue('value')
   label = form.getvalue('hash')
   matr = form.getvalue('matr')   
   if label is None:
      with open('/var/www/html/elisa/data/reg.txt', 'r') as reg:
         for line in reg:
            f = line.strip().split()
            h = f[0]
            m = f[1]
            if matr == m:
               label = h
               break
   if label is None: # unknown
         print('unknown')
         return
   with open('/var/www/html/elisa/data/interact.txt', 'a') as votes:
      print(label, vote, file = votes)
      print(vote)

if __name__ == "__main__":
    main()
