#!/usr/bin/env python3
import cgi, os
import cgitb; cgitb.enable()
from xml.dom import minidom
import datetime
import glob
from sys import argv, stderr

DLOC = '/var/www/html/elisa/data/'

def main():
   print("Content-type: text/html\n\n<html><body>")
   form = cgi.FieldStorage()
   try:
      helper = form.getvalue('helper').strip().lower()
      helped = form.getvalue('helped').strip().lower()
      topic = form.getvalue('topic').strip().lower()
      prof = form.getvalue('prof').strip().lower()
      if '\n' in topic or len(topic) > 80:
         print('<p><span style="color:red">Manten sencilla la descripci&oacute;n de la ayuda.</span></p>')
      elif len(helper) == 7 and len(helped) == 7 and helper.isdigit() and helped.isdigit() and len(topic) > 0:
         with open(DLOC + 'ayudas_' + prof + '.txt', 'a') as target:
            print(helper, helped, datetime.datetime.now(), topic, file = target)
            print('<p><span style="color:green">Registro exitoso.</span></p>')
      else:
         print('<p><span style="color:red">Revisa que las matr&iacute;culas sean v&aacute;lidas e intenta nuevamente.</span></p>')
   except:
      pass
   print('</body></html>')

if __name__ == "__main__":
    main()

