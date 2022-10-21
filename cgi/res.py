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
OPT = '&#9733;' # spacer
fundamentals = {'A1': 'r1.', 'A2': 'r2.', 'A3': 'mc', 'A4': 'r3.', 'A5': 'r4.', 'A6': 'r5.', 'A7': 'pr', 'A8': 'eo'}
awarded = {v: k for k, v in fundamentals.items()}
nombres = [('A1', 1), ('A2', 1), ('A4', 1), ('A5', 1), ('A6', 1), ('A7', 1), ('A3', 1), ('A8', 1)]
tareas = {'A1', 'A2', 'A4', 'A5', 'A6'}
tc = len(tareas)
maximos = {'A1': 10, 'A2': 10, 'A3': 20, 'A4': 10, 'A5': 10, 'A6': 10, 'A7': 10, 'A8': 20}
limit = 0.3 * len(maximos)
especiales = {'mc': 'A3', 'pr': 'A7', 'eo': 'A8'}
cumpl = dict()
for i in fundamentals:
   cumpl[i] = dict()
header = '<tr><th rowspan="2">Mat.</th><th rowspan="2">PE</th><th rowspan="2">Hora</h2><th colspan="{:d}">Tareas</th>'.format(tc + 1)
header += '<th rowspan="2">PI</th><th colspan="2">Ex&aacute;menes</th><th rowspan="2">X</th><th colspan="2">CF</th><th rowspan="2"><small>NP</small></th></tr><tr>'
for x in range(tc):
   header += '<th>{:d}</th>'.format(x + 1)
header += '<th>&Sigma;</th><th><small>Medio curso</small></th><th><small>Ordinario</small></th><th>CA</th><th><small>2da</small></th></tr>'
nopart = ('<td colspan="5" align="center"><small>(sin tareas)</small></td><th>0</th>', 5, 0.0)
decrep = {'25': (1, 4), '50': (1, 2), '75': (3, 4), '67': (2, 3), '58': (7, 12), '17': (1, 6), '92': (11, 12), \
          '42': (5, 12), '83': (5, 6), '33': (1, 3), '08': (1, 12), '36': (9, 25)}

def tidy(number):
   if '.' not in number:
      return number
   pieces = number.split('.')
   whole = int(pieces.pop(0))
   dec = ''
   if whole == 0:
      whole = ''
   else:
      whole = str(whole) + ' '
      dp = pieces.pop(0)
      if dp != '00':
         (up, down) = decrep[dp]
         dec = '<span style="font-size:9px"><sup>' + str(up) + '</sup>&frasl;<sub>' + str(down) + '</sub></span>'
   return whole + dec

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
      target[label] = 2 * float(value) # 2 pts per question
   return target
   
def identity(label, insc):
   tagopen = ''
   tagclose = ''
   if insc:
      tagopen = '<strong>'
      tagclose = '</strong>'
   return '<td>{:s}{:s}{:s}</td>'.format(tagopen, label, tagclose)

def evaluate(result):
   desc = ''
   points = 0
   if '_' in result: # a fraction
      parts = result.split('_')
      if len(parts) == 2:
         up = int(parts.pop(0))
         down = int(parts.pop(0))
         value = up / (1.0 * down)
         desc += '<span style="font-size:9px"><sup>' + str(up) + '</sup>&frasl;<sub>' + str(down) + '</sub></span>'
         points = float(value)
      else:
         assert len(parts) == 3
         whole = int(parts.pop(0))         
         up = int(parts.pop(0))
         down = int(parts.pop(0))
         value = whole + up / (1.0 * down)
         desc += ('' + str(whole) + '<span style="font-size:9px"><sup>' + str(up) + '</sup>&frasl;<sub>' + str(down) + '</sub></span>')
         points = float(value)
   elif len(result) >= 20: # exam
      desc += '['
      for c in result:
         if c == '0':
            desc += ' 0'
            continue
         elif c == '1':
            points += 1
            desc += ' 1'
      desc += ' ]'
   else: # an integer
      points = int(result)
      desc = str(result)
   return (desc, points)

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
no present&oacute</li> <li><strong>X</strong>: puntos por registros de ayuda</li> <li><strong>PI</strong>: proyecto integrador</li>
<li><strong>SR</strong>: sin respuesta (igual como un &mdash;)</li>
<li><strong>% Calif. Prom.</strong>: calif. promedio entre
 inscritos como porcentaje de M&aacute;x.</li>
<li><strong>% de Particip.</strong>: porcentaje de inscritos que han participado
en una AF</li> <li><strong>&Sigma;</strong>: suma</li>
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
   with open(DLOC + 'inscritos.lst') as insc:
      for line in insc:
         line = line.strip()
         if len(line) > 0: 
            tokens = line.split()
            m = tokens.pop(0)
            matriculas.add(m)
            grupo[m] = tokens.pop(0)
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
            if t.pop(0) == 'md':
               m = t.pop(0)
               nocumple.add(m)
   with open(DLOC + 'aprobados.txt') as data:
      for line in data:
         t = line.split()
         if len(t) == 5:
            if t.pop(0) == 'md':
               m = t.pop(0)
               aprobados.add(m)
   if matr is None or mailhash is None:
      print("""<h2>Registro</h2>
<p>
Es necesario proporcionar tus datos para contabilizar tus
puntos ya que es la &uacute;nica manera de asociar el correo electr&oacute;nico utilizado en las tareas a la matr&iacute;cula correspondiente.
</p>
<form action="https://elisa.dyndns-web.com/cgi-bin/res.py" method="post">
<p>Correo utilizado para responder las tareas: <input type="email" autocomplete="on"  name="student" id="student" size="30" value="" /></p>
<p>Matr&iacute;cula <strong>completa</strong> de siete d&iacute;gitos: <input type="text" name="matr" id="matr" size="10" value="" />
</p>
<p>PE: <select name="pe">
<option value="IAS">Ingeniero Administrador de Sistemas</option>
<option value="IMC">Ingeniero en Mecatr&oacute;nica</option>
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
   tareas = dict()
   for filename in glob.glob(XLOC + '/mat/discretas/data/*.awarded.xml'):
      h = filename.split('.')[0].split('/')[-1]
      if h in known:
         line = ''
         m = known[h]
         something = False
         part = set()
         results = parseExerciseResults(filename)
         total = 0
         for ex in range(5):
            effect = 0.0
            label = 'r{:d}.'.format(ex + 1)
            for question in results:
               if label in question: # belongs to this homework
                  effect += results[question]
            if effect > 0:
               part.add(label)
               value = '{:f}'.format(effect)
               line += '<td>{:s}</td>'.format(clean(value))
               something = True
               total += effect
               if m in inscripciones:
                  cumpl[awarded[label]][m] = effect
            else:
               line += '<td>&mdash;</td>'
         if something:
            line += '<th>{:s}</th>'.format(clean('{:f}'.format(total)))
         else:
            line += '<th>&mdash;</th>'
         tareas[m] = (line, tc - len(part), total)
   exams = defaultdict(dict)
   xord = set()
   with open(DLOC + 'exams_md.txt', 'r') as ex:
      for line in ex:
         l = line.strip()
         if len(l) > 0:
            tokens = l.split()
            m = tokens.pop(0)
            if m in inscripciones:
               for problem in tokens:
                  problem = problem.strip().lstrip()
                  if problem[:2] == 'xo': # segundas
                     exams[m]['xmc'] = evaluate(problem[2:22])
                     exams[m]['xeo'] = evaluate(problem[22:])
                     xord.add(m)
                  else:
                     exams[m][problem[:2]] = evaluate(problem[2:])
   participants = list()
   for m in matriculas:
      if m in aprobados:
         continue # already passed the class
      if m in nocumple:
         continue # lost the right to present 
      part = False
      init = None
      if m in revknown:
         init = tareas.get(m, nopart)
      if init is None:
         init = nopart
      (line, NP, total) = init
      cells = {'mc': None, 'eo': None, 'pr': None, 'pf': None}
      part = total > 0 # has some assignments
      for activity in ['mc', 'eo', 'pr', 'pf', 'xo']:
         if m in exams and activity in exams[m]:
            part = True
            if activity in exams[m]:
               (descr, res) = exams[m][activity]
               total += res
               if m in inscripciones and activity != 'pf':
                  cumpl[awarded[activity]][m] = res
            if activity in ['mc', 'eo', 'pr']: # fundamentals
               mp = None
               try:
                  mp = maximos[especiales[activity]]
               except:
                  pass
               perc = ''
               if mp is not None:
                  perc = ' <small>({:d} %)</small>'.format(min(round(100.0 * res / mp), 100))
               if '+' in descr or '[' in descr:
                  dr = clean('{:s} = {:s}'.format(descr, tidy('{:.2f}'.format(res))))
                  cells[activity] = '<td><small>{:s} {:s}</small></td>'.format(dr, perc)
               else:
                  if '.' in descr:
                     descr = clean(descr)
                  cells[activity] = '<td><small>{:s} {:s}</small></td>'.format(descr, perc)
            else: # extras
               cells[activity] = '<td>{:s}</td>'.format(descr)
         else:
            if activity == 'pf': 
               cells[activity] = '<td>&mdash;</td>' # no registred extras
            elif activity in ['mc', 'eo', 'pr']:
               cells[activity] = '<td><small>NP</small></td>' 
               NP += 1
      if m in xord:
         for xa in ['xmc', 'xeo']:
            (descr, res) = exams[m][xa]
            total += res
            orig = xa[1:]
            if orig in exams[m]: # check if is an improvment
               (temp, old) = exams[m][orig]
               if res > old: # substitute
                  total -= old
               else:
                  total -= res # the old was better
                  continue # leave it be
            mp = None
            try:
               mp = maximos[especiales[orig]]
            except:
               pass
            perc = ''
            if mp is not None:
               perc = ' <small>({:d} %)</small>'.format(min(round(100.0 * res / mp), 100))
            if '+' in descr or '[' in descr:
               dr = clean('{:s} = {:s}'.format(descr, tidy('{:.2f}'.format(res))))
               cells[orig] = '<td><small>{:s} {:s}</small></td>'.format(dr, perc)
            else:
               if '.' in descr:
                  descr = clean(descr)
               cells[orig] = '<td><small>{:s} {:s}</small></td>'.format(descr, perc)
      gr = grupo.get(m, 'NA')
      pe = program.get(m, None)
      grade = ''
      if pe is None:
         pe = "???"
      identif = '{:s}<td>{:s}</td><td align="center">{:s}</td>'.format(identity(abbrv.get(m, '???'), m in inscripciones), pe, gr)
      extraord = '<td>&nbsp;</td>'
      if gr != 'NA' or part and (m in revknown and revknown[m] in tareas):
         gradecolor = 'orange'
         if gr == 'NA':
            gradecolor = 'gray'
            grade = 'NA'
            extraord = '<td>NA</td>'
            NP = 0
      if not part:
         grade = '<span style="color:gray"><strong>NP</strong></span>'
      if part and total <= 100:
         grade = clean('{:f}'.format(round(total)))
      else:
         grade = '100'
      if m in xord:
         extraord = '<td>&#10003;</td>'
      gradecolor = 'orange'
      if round(total) >= 70:
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
         if total > 0 or part:
            line += cells['pr'] + cells['mc'] +cells['eo'] +cells['pf']
            participants.append('<tr>{:s}{:s}<th><span style="color:{:s}">{:s}</span></th>{:s}<td>{:s}</td></tr>'.format(identif, line, gradecolor, grade, extraord, str(NP)))
         else:
            participants.append('<tr>{:s}<td colspan="{:d}" align="center"><span style="color:gray"><em><small>alumno inscrito en la unidad de aprendizaje sin registro y/o participaci&oacute;n (NP 1ra, NC 2da)</small></em></span></td></tr>'.format(identif, tc + 8))
   print('<h2>Matem&aacute;ticas discretas</h2>\n<table border="1">\n' + header)
   for p in sorted(participants):
      print(p)
   nline = '<tr><th colspan="3" bgcolor="#bbbbbb"><small>Actividad Fund.</small></th>'
   pline = '<tr><th colspan="3" bgcolor="#bbbbbb"><small>M&aacute;ximo</small></th>'
   pos = 0
   total = 0
   for (etiq, w) in nombres:
      pos += 1
      if pos == tc + 1:
         pline += '<th bgcolor="#bbbbbb">{:d}</th>'.format(total)
         nline += '<th bgcolor="#bbbbbb">&Sigma;</th>'
      if etiq != OPT:
         if w == 0:
            pline = pline[:-5] + " &amp; "
            nline = nline[:-13] + " &amp; "
         else:
            pline += '<td colspan="{:d}" bgcolor="#bbbbbb">'.format(w)
            nline += '<th colspan="{:d}" bgcolor="#bbbbbb"><small>'.format(w)
         pts = maximos[etiq]
         pline += '{:d}</td>'.format(pts)
         if etiq == 'A3':
            etiq = 'A3 (medio curso)'
         elif etiq == 'A8':
            etiq = 'A8 (ordinario)'
         nline += '{:s}</small></th>'.format(etiq)
         total += pts
      else:
         nline += '<td rowspan="2" align="center" valign="center" bgcolor="#333333"><span style="color:white">{:s}</span></td>'.format(OPT)
   nline += '<td rowspan="2" align="center" valign="center" bgcolor="#333333"><span style="color:white">{:s}</span></td>'.format(OPT) # PFE
   print('{:s}<th colspan="4" rowspan="3" bgcolor="#000000"><span style="color:white"></span></th></tr>'.format(nline))
   print('{:s}</tr>'.format(pline))
   print('<tr><th colspan="{:d}" bgcolor="#eeeeee">Estad&iacute;sticas de cumplimiento de AF por <em>programa educativo</em></th></tr>'.format(tc + 7))
   for pe in set(program.values()): # for each study program
      pos = 0
      porc = ''
      prom = ''
      tot = 0      
      for m in program:
         if program[m] == pe and m in inscripciones:
            tot += 1
      if tot > 0: # there are some
         for (fund, w) in nombres: # for each activity
            pos += 1
            if pos == tc + 1: # last activity
               porc += '<th bgcolor="#000000"><span style="color:white">#P</span></th>' 
               prom += '<td bgcolor="#bbbbbb">{:d}</td>'.format(tot)
            if fund != OPT:
               if fund in cumpl:
                  c = 0
                  suma = 0.0
                  for m in cumpl[fund]:
                     if m in program and program[m] == pe:                        
                        c += 1
                        suma += cumpl[fund][m]
                  if w == 0:
                     porc = porc[:-5] + " &amp; "
                     prom = prom[:-5] + " &amp; "
                  else:
                     porc += '<td colspan="{:d}" bgcolor="#cccccc">'.format(w)
                     prom += '<td colspan="{:d}" bgcolor="#dddddd">'.format(w)
                  porc += '{:.0f}</td>'.format(100.0 * c / tot)
                  if c > 0:
                     prom += '{:.0f}</td>'.format((100.0 * suma / c) / maximos[fund])
                  else:
                     prom += 'NA</td>'
               else:
                  if w == 0:
                     porc = porc[:-5] + " &amp; 0.00</td>"
                     prom = prom[:-5] + " &amp; NA</td>"
                  else:
                     porc += '<td align="center" colspan="{:d}" bgcolor="#cccccc">0.00</td>'.format(w)
                     prom += '<td align="center" colspan="{:d}" bgcolor="#dddddd">NA</td>'.format(w)
            else:
               porc += '<td rowspan="2" align="center" valign="center" bgcolor="#333333"><span style="color:white">{:s}</span></td>'.format(OPT)
         porc += '<td rowspan="2" align="center" valign="center" bgcolor="#333333"><span style="color:white">{:s}</span></td>'.format(OPT)               
         print('<tr><th colspan="3" bgcolor="#000000"><small><span style="color:white">% de Particip.</span></small></th>{:s}<th rowspan="2" colspan="3" bgcolor="#bbbbbb">{:s}</th></tr>'.format(porc, pe))
         print('<tr><th colspan="3" bgcolor="#000000"><small><span style="color:white">% Calif. Prom.</span></small></th>{:s}</tr>'.format(prom))
   print('<tr><th colspan="{:d}" bgcolor="#eeeeee">Estad&iacute;sticas de cumplimiento de AF por <em>grupo</em></th></tr>'.format(tc + 7))
   for gr in ['M4', 'V1', 'V4']: # for each group
      pos = 0
      porc = ''
      prom = ''
      tot = list(grupo.values()).count(gr)
      if tot > 0:
         for (fund, w) in nombres:
            pos += 1
            if pos == tc + 1:
               porc += '<th bgcolor="#000000"><span style="color:white">#P</span></th>' 
               prom += '<td bgcolor="#bbbbbb">{:d}</td>'.format(tot)
            if fund != OPT:
               if fund in cumpl:
                  particip = cumpl[fund]
                  c = 0
                  suma = 0.0
                  for m in particip:
                     if m in inscripciones and m in grupo:
                        if gr in grupo[m]:
                           c += 1
                           suma += particip[m]
                  if w == 0:
                     porc = porc[:-5] + " &amp; "
                     prom = prom[:-5] + " &amp; "
                  else:
                     porc += '<td colspan="{:d}" bgcolor="#cccccc">'.format(w)
                     prom += '<td colspan="{:d}" bgcolor="#dddddd">'.format(w)
                  porc += '{:.0f}</td>'.format(100.0 * c / tot)
                  if c > 0:
                     prom += '{:.0f}</td>'.format((100.0 * suma / c) / maximos[fund])
                  else:
                     prom += 'NA</td>'
               else:
                  if w == 0:
                     porc = porc[:-5] + " &amp; 0.00</td>"
                     prom = prom[:-5] + " &amp; NA</td>"
                  else:
                     porc += '<td align="center" colspan="{:d}" bgcolor="#cccccc">0.00</td>'.format(w)
                     prom += '<td align="center" colspan="{:d}" bgcolor="#dddddd">NA</td>'.format(w)
            else:
               porc += '<td rowspan="2" align="center" valign="center" bgcolor="#333333"><span style="color:white">{:s}</span></td>'.format(OPT)
         porc += '<td rowspan="2" align="center" valign="center" bgcolor="#333333"><span style="color:white">{:s}</span></td>'.format(OPT)
         print('<tr><th colspan="3" bgcolor="#000000"><small><span style="color:white">% de Particip.</span></small></th>{:s}<th rowspan="2" colspan="3" bgcolor="#bbbbbb">{:s}</th></tr>'.format(porc, gr))
         print('<tr><th colspan="3" bgcolor="#000000"><small><span style="color:white">% Calif. Prom.</span></small></th>{:s}</tr>'.format(prom))
   print('</table>')
   print('</div>')
   print('<div id="pie">Lista de resultados generada {:s}.<br />'.format(str(datetime.datetime.now()).split('.')[0])[:-3])
   print('URL: https://elisa.dyndns-web.com/cgi-bin/res.py</div></div>\n</body></html>')
   return


if __name__ == "__main__":
    main()
