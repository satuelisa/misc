#!/usr/bin/env python3

import cgi, os
import cgitb; cgitb.enable()

def main():
   print('Content-type: text/html\n\n')
   try:
      form = cgi.FieldStorage()
      matr = (form.getvalue('matr')).strip()
      print(f'<html><head><title>Descarga</title></head><body><p><a href="https://elisa.dyndns-web.com/download/{matr}.pdf" download="{matr}.pdf">Descargue su documento <code>{matr}.pdf</code></a></p></body></html>')
   except:
      print('<html><head><title>Descarga</title></head><body><p>Se ocupa contar con la matr&iacute;cula.</p></body></html>')
   return

if __name__ == "__main__":
    main()
