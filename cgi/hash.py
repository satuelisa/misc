#!/usr/bin/env python3

import cgi, os
import cgitb; cgitb.enable()
from sys import argv
import hashlib

def main():
   print('Content-type: text/html\n\n')
   student = None
   try:
      form = cgi.FieldStorage()
      student = form.getvalue('student')
   except:
      pass
   if  student is None:
      try:
         student = argv[1] # debug mode
      except:
         return
   if student is None:
      return
   student = student.strip().lower()
   h = hashlib.md5(student.encode("utf-8")).hexdigest()
   print(h)
   return

if __name__ == "__main__":
    main()
