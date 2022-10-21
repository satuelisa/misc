#!/usr/bin/env python3
import cgi, os, sys
import cgitb; cgitb.enable()

def main(): # this one uses POST
   d = ''
   for l in sys.stdin.readline():
      d += l
   f =  d[1:].split('&')
   uno, dos, tres = '', '', ''
   try:
      uno = f[0].split('=')[1].strip().lower() + "_v2"
      dos = f[1].split('=')[1].strip().lower() + "_v2"
      tres = f[2].split('=')[1].strip().lower() + "_v2"
   except:
      pass
   print("Content-type: text/plain\nAccess-Control-Allow-Origin: *\n")
   print('{"uno": "' + uno + '", "dos": "' + dos + '", "tres": "'    + tres + '"}')

if __name__ == "__main__":
   main()
    
    
