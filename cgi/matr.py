#!/usr/bin/env python3

import cgi, os
import cgitb; cgitb.enable()
from sys import argv
import hashlib

def main():
   print('Content-type: text/html\n\n')
   hash = None
   try:
      form = cgi.FieldStorage()
      hash = form.getvalue('hash')
   except:
      pass
   if hash is None:
      try:
         student = argv[1].strip() # debug mode
         hash = hashlib.md5(student.encode("utf-8")).hexdigest()
      except:
         return
   else:
      hash = hash.strip()
   with open('/var/www/html/elisa/data/reg.txt', 'r') as reg:
      for line in reg:
         line = line.strip()
         if len(line) == 0:
            continue
         else:
            tokens = line.split()
            if len(tokens) == 2:
               h = tokens[0]
               m = tokens[1]
               if hash == h:
                  with open('/var/www/html/elisa/data/inscritos.lst', 'r') as incr:
                     for line in incr:
                        line = line.strip()
                        if len(line) == 0:
                           continue
                        else:
                           tokens = line.split()
                           if len(tokens) == 2:
                              mat = tokens[0]
                              gr = tokens[1]
                              if mat == m:
                                 print(m, gr)
                                 return

if __name__ == "__main__":
    main()
