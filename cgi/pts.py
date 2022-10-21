#!/usr/bin/env python3
import cgi, os
import cgitb; cgitb.enable()
from xml.dom import minidom
import hashlib
import datetime
import glob
from collections import defaultdict

VERBOSE = True
XLOC = '/var/www/html/elisa/teaching/'
DLOC = '/var/www/html/elisa/data/'
activities = ['E1', 'E2', 'E3', 'E4', 'E5', 'E6', 'E7', 'A7', 'A3', 'A6']
fundamentals = ['A1', 'A2', 'A4', 'A5', 'A7', 'A3', 'A6']
homework = {'E1': 'A1', 'E2': 'A2', 'E3': 'A2', 'E4': 'A4', 'E5': 'A4', 'E6': 'A5', 'E7': 'A5'}
corr = defaultdict(set)
for (e, a) in homework.items():
   corr[a].add(e)
nonhw = ['A3', 'A6', 'A7'] 
tareas = ['A1', 'A2', 'A4', 'A5']
awarded = {'r1.': 'E1', 'r2.': 'E2', 'r3.': 'E3', 'r4.': 'E4', \
           'mc': 'A3', \
           'r5.': 'E5', 'r6.': 'E6', 'r7.': 'E7', \
           'pr': 'A7', \
           'eo' : 'A6', \
           't1': 'A1', 't2': 'A2', 't3': 'A3', 't4': 'A4', \
           't5': 'A6', 't6': 'A7', 't7': 'A8'}
cumpl = dict()
for i in activities:
   cumpl[i] = dict()
tc = len(homework)
maximos = {'A1': 5, 'A2': 10, 'A3': 20, 'A4': 15, 'A5': 15, 'A6': 20, 'A7': 15}
limit = 0.3 * len(maximos)
especiales = {'mc': 'A3', 'pr': 'A7', 'eo': 'A6'}
header = '<tr><th rowspan="2">Mat.</th><th rowspan="2">PE</th><th rowspan="2">Hora</h2><th colspan="{:d}">Tareas</th>'.format(tc)
header += '<th rowspan="2">PI</th><th colspan="2">Ex&aacute;menes</th><th colspan="2">CF</th><th rowspan="2"><small>NP</small></th></tr><tr>'
for x in range(tc):
   header += '<th>E{:d}</th>'.format(x + 1)
header += '<th><small>Medio curso</small></th><th><small>Ordinario</small></th><th>CA</th><th><small>2da</small></th></tr>'


def clean(s):
   s = s.replace('[ ', '[')
   s = s.replace(' ]', ']')
   s = s.rstrip('0').rstrip('.')
   return s

def parseExerciseResults(filename):
   source = minidom.parse(filename)
   target = dict()
   fields = source.getElementsByTagName('field')
   for field in fields:
      label = field.childNodes[0].firstChild.data
      value = field.childNodes[1].firstChild.data
      label = label.encode('ascii', 'ignore').decode('ascii')
      value = value.encode('ascii', 'ignore').decode('ascii')
      target[label] = float(value) # 1 pt per question
   return target
   
def identity(label, insc):
   tagopen = ''
   tagclose = ''
   if insc:
      tagopen = '<strong>'
      tagclose = '</strong>'
   return '<td>{:s}{:s}{:s}</td>'.format(tagopen, label, tagclose)

def evaluate(result):
   k = len(result)
   if k == 20 or k == 40: # exam
      return sum([int(d) for d in result])
   if '-' in result:
      return None
   else: 
      return int(result)

def abbreviate(keys, subset):
   data = dict()
   for key in keys:
      if key in subset:
         data[key] = key
   k = len(data)
   next = data
   while len(next) == k:
      data = next
      next = dict()
      for key in data:
         if len(key) == 1:
            break
         next[key[1:]] = data[key]
   result = dict()
   for key in data:
      result[data[key]] = key
   return result

def main():
   print("""Content-type: text/html\n\n <html> <head>
<meta http-equiv="refresh" content="300">
<title>Resultados &mdash;
Docencia &mdash; Schaeffer</title> <LINK rel="stylesheet"
type="text/css"
href="https://elisa.dyndns-web.com/teaching/elisa.teaching.css">
</head> <body> <div id="elementos"> <div id="navibar"> <p> <a
href="https://elisa.dyndns-web.com/">Schaeffer</a> / <a
href="https://elisa.dyndns-web.com/teaching/espanol.html">Docencia</a>
/ Resultados de cursos de licenciatura </p> </div> <div
ID="contenido"> <h1>Resultados de cursos <em>activos</em> de
licenciatura</h1>
<h3>Notaci&oacute;n y abreviaciones</h3> 
<p> Para preguntas de m&uacute;ltiples partes y ex&aacute;menes de
m&uacute;ltiples preguntas breves, los puntajes est&aacute;n juntadas
dentro de "[...]".</p>
<ul> <li><strong>2da</strong>: segunda oportunidad
(extraordinario)</li> <li><strong>Actividad Fund.</strong>: actividad
fundamental (AF)</li> <li><strong>CA</strong>: la calificaci&oacute;n total
acumulada hasta la fecha</li> <li><strong>CF</strong>:
calificaci&oacute;n final</li> <li><strong>Mat.</strong>: los
&uacute;ltimos d&iacute;gitos del n&uacute;mero de matr&iacute;cula
del participante</li> <li><strong>M&aacute;x.</strong>: puntaje
m&aacute;ximo posible por actividad fundamental</li>
<li><strong>NA</strong>: no aplica</li> <li><strong>NC</strong>: no
cumple (sin derecho a 2da oportunidad)</li> <li><strong>NP</strong>:
no present&oacute</li> <li><strong>PI</strong>: proyecto integrador</li>
<li><strong>SR</strong>: sin respuesta (igual como un &mdash;)</li>
<li><strong>% Calif. Prom.</strong>: calif. promedio entre
 inscritos como porcentaje de M&aacute;x.</li>
<li><strong>% de Particip.</strong>: porcentaje de inscritos que han participado
en una AF</li> 
<li><strong>#P</strong>: n&uacute;mero de participantes inscritos por
grupo</li></ul> 
<h3>Derecho a segunda oportunidad</h3> <p>
Aquellos ejercicios para los cuales no se ha recibido respuesta
cuentan como NP <em>los ex&aacute;menes que a&uacute;n no se han
aplicado o que el alumno no present&oacute; y proyectos (si hay) que
no se han entregado tambi&eacute;n cuentan como NP.</em> El momento
que el alumno haga un primer intento a un ejercicio, el NP se
reemplaza por la calificaci&oacute;n obtenida. No hay l&iacute;mite a
la cantidad de intentos. Los ejercicios contestados a m&aacute;s
tardar el d&iacute;a del examen ordinario cuentan para la primera
oportunidad y los que se contesten a m&aacute;s tardar el d&iacute;a
del extraordinario cuentan tambi&eacute;n para la segunda, con que se
hayan contestado antes del inicio del examen en los dos casos.</p>
</p> <p>El reglamento de <span style="color:red">la UANL requiere que
el alumno haya participado en el 70 por ciento o m&aacute;s de las
actividades fundamentales para tener derecho a segunda
oportunidad</span>, por lo cual no se puede tener m&aacute;s de dos NP
sin perder ese derecho.</p> <h3>Fechas l&iacute;mite</h3> <p> La
minuta de <em>primera oportunidad se cierra el d&iacute;a del examen
ordinario</em>. Despu&eacute;s de que haya iniciado el examen
ordinario, los puntos de tareas posteriores ya no afectar&aacute;n la
calificaci&oacute;n capturada para primera oportunidad ni al derecho
de presentar el extraordinario</strong>. De forma similar, los puntos
de tareas que se cuentan para la segunda oportunidad son aquellos
registrados antes del inicio del examen extraordinario. </p>""")
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
   pe = None
   try:
      pe = form.getvalue('pe').strip()
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
   grupo = defaultdict()
   inscripciones = set()
   with open(DLOC + 'inscPE.lst') as insc:
      for line in insc:
         line = line.strip()
         if len(line) > 0: 
            tokens = line.split()
            tokens.pop(0) # skip sequence number
            m = tokens.pop(0) # quedan nombre, email, y oportunidad
            matriculas.add(m)
            grupo[m] = 'V4' # solamente uno
            inscripciones.add(m)
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
            with open(DLOC + 'pe.txt', 'a') as PEs:
               print(matr, pe, file=PEs)
            print('<p><span style="color:green">Registro realizado para el correo {:s} con la matr&iacute;cula {:s} para el PE {:s}.</span></p>'.format(student, matr, pe))
   program = dict()
   with open(DLOC + 'pe.txt') as PEs:
      for line in PEs:
         line = line.strip()
         if len(line) > 0: 
            tokens = line.split()
            m = tokens.pop(0)
            pe = tokens.pop(0)
            program[m] = pe
   nocumple = set()
   aprobados = set()
   with open(DLOC + 'nocumple.txt') as data:
      for line in data:
         t = line.split()
         if len(t) >= 2:
            if t.pop(0) == 'pr':
               m = t.pop(0)
               nocumple.add(m)
   with open(DLOC + 'aprobados.txt') as data:
      for line in data:
         t = line.split()
         if len(t) == 5:
            if t.pop(0) == 'pr':
               m = t.pop(0)
               aprobados.add(m)
   if matr is None or mailhash is None:
      print("""<h2>Registro</h2>
<p>
Es necesario proporcionar tus datos para contabilizar tus
puntos ya que es la &uacute;nica manera de asociar el correo electr&oacute;nico utilizado en las tareas a la matr&iacute;cula correspondiente.
</p>
<form action="https://elisa.dyndns-web.com/cgi-bin/pts.py" method="post">
<p>Correo utilizado para responder las tareas: <input type="email" autocomplete="on" name="student" id="student" size="30" value="" /></p>
<p>Matr&iacute;cula <strong>completa</strong> de siete d&iacute;gitos: <input type="text" name="matr" id="matr" size="10" value="" />
</p>
<p>PE: <select name="pe">
<option value="IAS">Ingeniero Administrador de Sistemas</option>
<option value="IEA">Ingeniero en Electr&oacute;nica y Automatizaci&oacute;n</option>
<option value="IEC">Ingeniero en Electr&oacute;nica y Comunicaciones</option>
<option value="IMA">Ingeniero Mec&aacute;nico Administrador</option>
<option value="IMC">Ingeniero en Mecatr&oacute;nica</option>
<option value="IME">Ingeniero Mec&aacute;nico Electricista</option>
<option value="IMF">Ingeniero en Manufactura</option>
<option value="IMT">Ingeniero en Materiales</option>
<option value="ITS">Ingeniero en Tecnolog&iacute;a de Software</option>
<option value="BIO">Ingeniero Biom&eacute;dico</option>
<option value="otro">Otro</option>
</select>
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
   if len(matriculas) > 0:
      abbrv = abbreviate(matriculas, inscripciones)
   recover = {v: k for k, v in abbrv.items()}
   for filename in glob.glob(XLOC + '/prog/ansic/data/*.awarded.xml'):
      h = filename.split('.')[0].split('/')[-1]
      if h in known:
         line = ''
         m = known[h]
         part = set()
         results = parseExerciseResults(filename)
         for ex in range(7):
            effect = 0.0
            label = 'r{:d}.'.format(ex + 1)
            for question in results:
               if label in question: # belongs to this homework
                  effect += results[question]
            if effect > 0:
               target = awarded[label]
               if target not in cumpl:
                  target = homework[target]
               cumpl[target][m] = effect
   xord = set()
   with open(DLOC + 'exams_pe.txt', 'r') as ex:
      for line in ex:
         l = line.strip()
         if len(l) > 0:
            tokens = l.split()
            m = tokens.pop(0)
            if m in inscripciones:
               for problem in tokens:
                  problem = problem.strip().lstrip()
                  if problem[0] == 't': # tareas de programacion calificadas en clase
                     tid = 'E' + problem[1:2]
                     pts = evaluate(problem[3:]) # add to the mini exercises unless NP
                     if pts is not None:
                        cumpl[tid][m] = cumpl[tid].get(m, 0) + pts
                  elif problem[:2] == 'xo': # segundas
                     xmc = evaluate(problem[2:22])
                     xeo = evaluate(problem[22:])
                     cumpl[awarded['mc']][m] = max(xmc,  cumpl[awarded['mc']].get(m, 0))
                     cumpl[awarded['eo']][m] = max(xeo,  cumpl[awarded['eo']].get(m, 0))
                     xord.add(m)
                  else:
                    cumpl[awarded[problem[:2]]][m] = evaluate(problem[2:])
   participants = list()
   for m in matriculas:
      if m in aprobados:
         continue # already passed the class
      if m in nocumple:
         continue # lost the right to present
      line = ''
      part = False
      total = 0
      NP = 0
      for activity in activities:
         ok = False
         if m in cumpl[activity]:
            pts = cumpl[activity][m]
            if pts is not None:
               part = True
               perc = ''
               if activity in especiales.values():
                  perc = ' <small>({:d} %)</small>'.format(min(round(100.0 * pts / maximos[activity]), 100))
               line += '<td><small>{:d}{:s}</small></td>'.format(int(pts), perc)
               total += pts
               ok = True
         if not ok:
            line += '<td><small>NP</small></td>'
            NP += 1
      gr = grupo.get(m, 'NA')
      pe = program.get(m, None)
      grade = ''
      if pe is None:
         pe = "???"
      identif = '{:s}<td>{:s}</td><td align="center">{:s}</td>'.format(identity(abbrv. get(m, '???'), m in inscripciones), pe, gr)
      extraord = '<td>&nbsp;</td>'
      if gr != 'NA' or part:
         gradecolor = 'orange'
         if gr == 'NA':
            gradecolor = 'gray'
            grade = 'NA'
            extraord = '<td>NA</td>'
            NP = 0
      if not part:
         grade = '<span style="color:gray"><strong>NP</strong></span>'
      if part and total <= 100:
         grade = str(int(round(total)))
      else:
         grade = '100'
      if m in xord:
         extraord = '<td>&#10003;</td>'
      gradecolor = 'orange'
      if total >= 70:
         gradecolor = 'green'
         if m not in xord:
            extraord = '<td><span style="color:gray">NA</span></td>'
      else: # failed
         if NP > limit:
            extraord = '<td><span style="color:red"><strong>NC</strong></span></td>'
            gradecolor = 'red'
         elif m not in xord:
            extraord = '<td>NP</td>'                  
            gradecolor = 'orange'
      if m in inscripciones: # muestra solamente inscritos
         if total > 0:
            participants.append('<tr>{:s}{:s}<th><span style="color:{:s}">{:s}</span></th>{:s}<td>{:s}</td></tr>'.format(identif, line, gradecolor, grade, extraord, str(NP)))
         else:
            participants.append('<tr>{:s}<td colspan="{:d}" align="center"><span style="color:gray"><em><small>alumno inscrito en la unidad de aprendizaje sin registro y/o participaci&oacute;n (NP 1ra, NC 2da)</small></em></span></td></tr>'.format(identif, tc + 6))
   print('<h2>Programaci&oacute;n Estructurada</h2>\n<table border="1">\n' + header)
   for p in sorted(participants):
      print(p)
   nline = '<tr><th colspan="3" bgcolor="#bbbbbb"><small>Actividad Fund.</small></th>'
   pline = '<tr><th colspan="3" bgcolor="#bbbbbb"><small>M&aacute;ximo</small></th>'
   pos = 0
   total = 0
   for etiq in fundamentals:
      l = 1 if etiq in nonhw else sum([v == etiq for v in homework.values()])
      pos += 1
      pline += f'<td colspan="{l}" bgcolor="#bbbbbb">'
      nline += f'<th colspan="{l}" bgcolor="#bbbbbb"><small>'
      pts = maximos[etiq]
      pline += '{:d}</td>'.format(pts)
      if etiq == 'A3':
         etiq = 'A3 (medio curso)'
      elif etiq == 'A6':
         etiq = 'A6 (ordinario)'
      nline += '{:s}</small></th>'.format(etiq)
      total += pts
   print('{:s}<th colspan="4" rowspan="2" bgcolor="#000000"><span style="color:white"></span></th></tr>'.format(nline))
   print('{:s}</tr>'.format(pline))
   print('<tr><th colspan="{:d}" bgcolor="#eeeeee">Estad&iacute;sticas de cumplimiento de AF por <em>programa educativo</em></th></tr>'.format(tc + 9))
   order = list(set(program.values())) # for each study program
   sorted(order)
   for pe in order: # for each study program
      pos = 0
      porc = ''
      prom = ''
      tot = 0      
      for m in program:
         if program.get(m, None) == pe and m in inscripciones:
            tot += 1
      if tot > 0: # there are some
         for fund in fundamentals:
            part = set()
            suma = 0.0
            l = 1 if fund in nonhw else sum([v == fund for v in homework.values()])
            for label in [fund] if fund in cumpl else corr[fund]:
               if label in cumpl:
                  for m in cumpl[label]:
                     if program.get(m, None) == pe and m in inscripciones:
                        contrib = cumpl[label][m]
                        if contrib is not None:
                           part.add(m)
                           suma += contrib
            porc += f'<td colspan="{l}" bgcolor="#cccccc">'
            prom += f'<td colspan="{l}" bgcolor="#dddddd">'
            c = len(part)
            porc += '{:.0f}</td>'.format(100.0 * c / tot)
            if c > 0:
               prom += '{:.0f}</td>'.format((100.0 * suma / c) / maximos[fund])
            else:
               prom += 'NA</td>'
         porc += '<th bgcolor="#000000"><span style="color:white">#P</span></th>' 
         prom += '<td bgcolor="#bbbbbb">{:d}</td>'.format(tot)
         print('<tr><th colspan="3" bgcolor="#000000"><small><span style="color:white">% de Particip.</span></small></th>{:s}<th rowspan="2" colspan="3" bgcolor="#bbbbbb">{:s}</th></tr>'.format(porc, pe))
         print('<tr><th colspan="3" bgcolor="#000000"><small><span style="color:white">% Calif. Prom.</span></small></th>{:s}</tr>'.format(prom))
   print('<tr><th colspan="{:d}" bgcolor="#eeeeee">Estad&iacute;sticas de cumplimiento de AF por <em>grupo</em></th></tr>'.format(tc + 9))
   for gr in ['V4']: # for each group
      porc = ''
      prom = ''
      tot = list(grupo.values()).count(gr)
      if tot > 0:
         for fund in fundamentals:
            part = set()
            suma = 0.0
            l = 1 if fund in nonhw else sum([v == fund for v in homework.values()])
            for label in [fund] if fund in cumpl else corr[fund]:
               if label in cumpl:
                  for m in cumpl[label]:
                     if grupo.get(m, None) == gr and m in inscripciones:            
                        contrib = cumpl[label][m]
                        if contrib is not None:
                           part.add(m)
                           suma += contrib
            porc += f'<td colspan="{l}" bgcolor="#cccccc">'
            prom += f'<td colspan="{l}" bgcolor="#dddddd">'
            c = len(part)
            porc += '{:.0f}</td>'.format(100.0 * c / tot)
            if c > 0:
               prom += '{:.0f}</td>'.format((100.0 * suma / c) / maximos[fund])
            else:
               prom += 'NA</td>'
         porc += '<th bgcolor="#000000"><span style="color:white">#P</span></th>' 
         prom += '<td bgcolor="#bbbbbb">{:d}</td>'.format(tot)
         print('<tr><th colspan="3" bgcolor="#000000"><small><span style="color:white">% de Particip.</span></small></th>{:s}<th rowspan="2" colspan="3" bgcolor="#bbbbbb">{:s}</th></tr>'.format(porc, gr))
         print('<tr><th colspan="3" bgcolor="#000000"><small><span style="color:white">% Calif. Prom.</span></small></th>{:s}</tr>'.format(prom))
   print('</table>')
   print('</div>')
   
   print('<div id="pie">Lista de resultados generada {:s}.<br />'.format(str(datetime.datetime.now()).split('.')[0])[:-3])
   print('URL: https://elisa.dyndns-web.com/cgi-bin/pts.py</div></div>\n</body></html>')
   return


if __name__ == "__main__":
    main()
