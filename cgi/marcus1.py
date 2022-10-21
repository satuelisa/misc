#!/usr/bin/env python3
import cgi, os
import cgitb; cgitb.enable()

def main():
   form = cgi.FieldStorage()
   uno, dos, tres = '', '', ''
   try:
      uno = form.getvalue('uno').strip().lower() + "_v1"
      dos = form.getvalue('dos').strip().lower() + "_v1"
      tres = form.getvalue('tres').strip().lower() + "_v1"
   except:
      pass
   json = '{"uno": "' + uno + '", "dos": "' + dos + '", "tres": "'    + tres + '"}'   
   print("Content-type: text/plain\nAccess-Control-Allow-Origin: *\n")
   print(json)

if __name__ == "__main__":
    main()

