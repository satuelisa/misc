#!/usr/bin/env python3
import cgi, os
import cgitb; cgitb.enable()
from xml.dom import minidom
import hashlib
import datetime
import glob

DLOC = '/var/www/html/elisa/data/'

def main():
   print("""Content-type: text/html\n\n <html> <head>
<title>Registro &mdash;
Docencia &mdash; Schaeffer</title> <LINK rel="stylesheet"
type="text/css"
href="https://elisa.dyndns-web.com/teaching/elisa.teaching.css">
</head> <body> <div id="elementos"> <div id="navibar"> <p> <a
href="https://elisa.dyndns-web.com/">Schaeffer</a> / <a
href="https://elisa.dyndns-web.com/teaching/espanol.html">Docencia</a>
/ Registro para interactuar en clase por Discord</p> </div> <div
ID="contenido"> <h1>Registro para interactuar en clase por Discord</h1>""")
   form = cgi.FieldStorage()
   mailhash = None
   try:
      mailhash = form.getvalue('mailhash').strip()
   except:
      pass
   if mailhash is not None and len(mailhash) == 0:
      mailhash = None
   student = None
   try:
      student = form.getvalue('student').strip().lower()
   except:
      pass
   if student is not None:
      if '.' not in student or '@' not in student:
         student = None
      if student is not None and len(student) > 40:
         student = None
      if student is not None:
         for c in student:
            if not (c.isalpha() or c.isdigit() or c in "-_@."):
               student = None
               break
   if student is not None:
      mailhash = hashlib.md5(student.encode("utf-8")).hexdigest()
   matr = None
   try:
      matr = form.getvalue('matr').strip()
   except:
      pass
   if mailhash is not None:
      mailhash = mailhash.replace("\"", "")
   matriculas = set()
   known = dict()
   revknown = dict()
   with open(DLOC + 'reg.txt') as reg:
      for line in reg:
         line = line.strip()
         if len(line) == 0:
            continue
         else:
            tokens = line.split()
            if len(tokens) == 2:
               h = tokens[0]
               m = tokens[1]
               known[h]  = m
               revknown[m] = h
               matriculas.add(m)
   if matr is not None and mailhash is not None:
      temp = ""
      for c in matr:
         if c.isdigit():
            temp += c
      matr = temp
      if len(matr) < 6 or len(matr) > 8:
         print('<p><span style="color:red">No es una matr&iacute;cula v&aacute;lida. Revisa los datos e intenta nuevamente.</span></p>')
         matr = None
      if matr is not None:
         if matr in known.values():
            if mailhash in known and known[mailhash] == matr:
               print('<p><span style="color:grey">Ya te has registrado anteriormente.</span></p>')
            else:
               print('<p><span style="color:red">Ya existe un correo asociado con la matr&iacute;cula {:s}.'.format(matr))
               print(' Contacta la profesora si no eres t&uacute;.</span></p>')
         else:
            known[mailhash] = matr
            revknown[matr] = mailhash
            matriculas.add(matr)
            with open(DLOC + 'reg.txt', 'a') as reg:
               print(mailhash, matr, file=reg)
            print('<p><span style="color:green">Registro realizado para el correo {:s} con la matr&iacute;cula {:s}.</span></p>'.format(student, matr))
   if matr is None or mailhash is None:
      print("""<p>
Es necesario proporcionar tus datos para contabilizar tus respuestas y 
votos para que se asocien al correo electr&oacute;nico correspondiente.
</p>
<form action="https://elisa.dyndns-web.com/cgi-bin/register.py" method="post">
<p>Correo por registrar: <input type="email" autocomplete="on" name="student" id="student" size="30" value="" /></p>
<p>Matr&iacute;cula <strong>completa</strong> de siete d&iacute;gitos: <input type="text" name="matr" id="matr" size="10" value="" />
</p>
</p>
<input type="hidden" id="mailhash" name="mailhash" value="">
<input type="submit" name="submit" value="Registrar">
</form>
</p>
<script>
  function getCookieByName(name) {
    var cookiestring=RegExp(""+name+"[^;]+").exec(document.cookie);
   return unescape(!!cookiestring ? cookiestring.toString().replace(/^[^=]+./,"") : "");
 }
 student = "";
 mailhash = "";
 if (document.cookie.indexOf("mailhash") >= 0 ) {
    mailhash = getCookieByName("mailhash").trim();
  }
  if (mailhash != "") {
     document.getElementById("mailhash").value = mailhash;
  }
  if (document.cookie.indexOf("student") >= 0 ) {
     student = getCookieByName("student").trim();
  }
  if (student != "") {
     document.getElementById("student").value = student;
  }
</script>""")
   
   print('<p>Actualizado el 19 de enero del 2022.</p><p>URL: https://elisa.dyndns-web.com/cgi-bin/register.py</p></div>\n</body></html>')
   return


if __name__ == "__main__":
    main()
