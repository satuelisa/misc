#!/usr/bin/env python3
import cgi, os
import cgitb; cgitb.enable()
from xml.dom import minidom
import hashlib
import datetime
import glob
from collections import defaultdict

GRUPO = 'V1'
maximos = {'A1': 5, 'A2': 15, 'A3': 10, 'A4': 20, 'A5': 10, 'A6': 30, 'A7': 10}
VERBOSE = True
DLOC = '/var/www/html/elisa/data/'
OPT = '&#9733;' # spacer
tc = 7 # eight fundamental activities
limit = 0.7 * tc
correspondence = [('A1', 'r1.'),
                  ('A1', 'r2.'),
                  ('A2', 'r4.'),
                  ('A2', 'r5.'),
                  ('A2', 'r6.'),
                  ('A3', 'mc'),
                  ('A4', 'r7.'),
                  ('A5', 'r8.'),
                  ('A5', 'r9.'),
                  ('A5', 'r10.'),
                  ('A5', 'r11.'),
                  ('A6', 'pi'),
                  ('A7', 'eo')]
awarded = {v: k for (k, v) in correspondence}
cumpl = dict()
for a in maximos.keys():
   cumpl[a] = dict()

nopart = (dict(), '<td colspan="5" align="center"><small>(sin tareas)</small></td><th>0</th>', 0, 8)
nombres = [('A1', 2), ('A2', 3), ('A4', 1), ('A5', 4), (OPT, 1), ('A6', 1), ('A3', 1), ('A7', 1)]
anchos = {v: k for (v, k) in nombres}
homework = ['A1', 'A2', 'A4', 'A5']
hwc = 10 # divided into ten exercises
extras = 2
count = hwc + extras

   
header = f'<tr><th colspan="3">Participante</th><th colspan="{hwc}">Puntos obtenidos por tarea</th><th rowspan="2">Total</th><th rowspan="2">PI</th><th rowspan="2" colspan="2">Ex&aacute;menes</th><th rowspan="2">Extra</th><th rowspan="2">CF</th><th rowspan="2">2da</th><th rowspan="2"><small>NP</small></th></tr>'
header += '<tr><th>Mat</th><th>PE</th><th>Hr</th>'
for x in range(10):
   header += f'<th>HW{x + 1}</td>'
header += '</tr>'

def match(label):
   for key in awarded:
      if key in label:
         return key
   return None

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


def identity(label, insc):
   tagopen = ''
   tagclose = ''
   if insc:
      tagopen = '<strong>'
      tagclose = '</strong>'
   return '<td>{:s}{:s}{:s}</td>'.format(tagopen, label, tagclose)

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
      target[label] = float(value) 
   return target
   
def abbreviate(keys):
   data = dict()
   for key in keys:
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
</head> <body> <div id="elementos"> <div id="navibar"></div> <div
ID="contenido"> <h1>Probabilidad y Estad&iacute;stica</h1>
<h3>Notaci&oacute;n y abreviaciones</h3> 
<p> Para preguntas de m&uacute;ltiples partes y ex&aacute;menes de
m&uacute;ltiples preguntas breves, los puntajes est&aacute;n juntadas
dentro de "[...]".</p>
<ul> <li><strong>Actividad Fund.</strong>: actividad
fundamental (AF)</li>
<li><strong>PI</strong>: proyecto integrador</li>
 <li><strong>CF</strong>: la calificaci&oacute;n total
acumulada hasta la fecha</li> <li><strong>Mat.</strong>: los
&uacute;ltimos d&iacute;gitos del n&uacute;mero de matr&iacute;cula
del participante</li> <li><strong>M&aacute;x.</strong>: puntaje
m&aacute;ximo posible por actividad fundamental</li>
<li><strong>NA</strong>: no aplica</li> <li><strong>NC</strong>: no
cumple (sin derecho a 2da oportunidad)</li> <li><strong>NP</strong>:
no present&oacute</li>
<li>&mdash;: sin respuesta</li>
<li><strong>% Calif. Prom.</strong>: calif. promedio entre
 inscritos como porcentaje de M&aacute;x.</li>
<li><strong>% de Particip.</strong>: porcentaje de inscritos que han participado
en una AF</li> <li><strong>&Sigma;</strong>: suma</li>
<li><strong>#P</strong>: n&uacute;mero de participantes inscritos</li></ul> 
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
   pe = None
   try:
      pe = form.getvalue('pe').strip()
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
   grupo = defaultdict()
   inscripciones = set()
   with open(DLOC + 'prob.lst') as insc:
      for line in insc:
         line = line.strip()
         if len(line) > 0: 
            tokens = line.split()
            m = tokens.pop(0) 
            matriculas.add(m)
            grupo[m] = GRUPO # solamente uno (tentativo)
            inscripciones.add(m)
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
               print(' Contacta a tu maestro si no eres t&uacute;.</span></p>')
         else:
            known[mailhash] = matr
            revknown[matr] = mailhash
            matriculas.add(matr)
            with open(DLOC + 'proba.txt', 'a') as reg:
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
            if t.pop(0) == 'pe':
               m = t.pop(0)
               nocumple.add(m)
   with open(DLOC + 'aprobados.txt') as data:
      for line in data:
         t = line.split()
         if len(t) == 5:
            if t.pop(0) == 'pe':
               m = t.pop(0)
               aprobados.add(m)
            
   if matr is None or mailhash is None:
      print("""<h2>Registro</h2> <p> Es necesario proporcionar tus datos para
contabilizar tus puntos ya que es la &uacute;nica manera de asociar el
correo electr&oacute;nico utilizado en las tareas a la
matr&iacute;cula correspondiente.  </p> <form
action="https://elisa.dyndns-web.com/cgi-bin/pe.py" method="post">
<p>Correo utilizado para responder las tareas: <input type="text"
name="student" id="student" size="30" value="" /></p>
<p>Matr&iacute;cula <em>completa</em> de siete d&iacute;gitos:
<input type="text" name="matr" id="matr" size="10" value="" /> </p>
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
<input type="submit" name="submit" value="Registrar"> </form> </p>
<script> function getCookieByName(name) { var
cookiestring=RegExp(""+name+"[^;]+").exec(document.cookie); return
unescape(!!cookiestring ?
cookiestring.toString().replace(/^[^=]+./,"") : ""); } student = "";
mailhash = ""; if (document.cookie.indexOf("mailhash") >= 0 ) {
mailhash = getCookieByName("mailhash").trim(); } if (mailhash != "") {
document.getElementById("mailhash").value = mailhash; } if
(document.cookie.indexOf("student") >= 0 ) { student =
getCookieByName("student").trim(); } if (student != "") {
document.getElementById("student").value = student; } </script>""")
   if len(matriculas) > 0:
      abbrv = abbreviate(matriculas)
   recover = {v: k for k, v in abbrv.items()}      
   tareas = dict()
   for filename in glob.glob('/home/elisa/html/teaching/prob/data/*.awarded.xml'):
      h = filename.split('.')[0].split('/')[-1]
      if h in known:
         m = known[h]
         something = False
         part = set()
         results = parseExerciseResults(filename)
         total = 0
         NP = 0
         for ex in range(count):
            effect = 0.0
            label = 'r{:d}.'.format(ex + 1)
            for question in results:
               if label in question: # belongs to this homework
                  effect += results[question]
            if effect > 0:
               total += effect
            else:
               NP += 1
         tareas[m] = (results, total, NP)

   xord = set()
   exams = defaultdict(dict)
   xord = set()
   with open(DLOC + 'exams_pr.txt', 'r') as ex:
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
      init = None
      if m in revknown:
         init = tareas.get(m, nopart)
      if init is None:
         init = nopart
      (pts, total, NP) = init
      cells = {'mc': None, 'eo': None, 'pi': None}
      part = total > 0 # has some assignments
      for activity in ['pi', 'mc', 'eo', 'xo']:
         if m in exams and activity in exams.get(m, []):
            part = True
            if activity in exams[m]:
               (descr, res) = exams[m][activity]
               total += res
               if m in inscripciones:
                  if activity in awarded:
                     cumpl[awarded[activity]][m] = res
            if activity in ['mc', 'eo', 'pi']: # fundamentals
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
            if activity in ['mc', 'eo', 'pi']:
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
      identif = '{:s}<td>{:s}</td><td align="center">{:s}</td>'.format(identity(abbrv[m], m in inscripciones), pe, gr)
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
      if m in inscripciones: # muestra solamente inscritos
         if total > 0:
            line = ''
            hw = dict()
            extra = 0
            for label in pts:
               corr = awarded.get(match(label), None)
               if corr is None:
                  extra += pts[label]
               else:
                  if pts[label] > 0:
                     if corr not in hw:
                        hw[corr] = 0
                     hw[corr] += pts[label]
            for h in hw:
               if hw[h] > 0:
                  cumpl[h][m] = hw[h]                   
            for h in homework:
               w = '' if anchos[h] == 1 else f' colspan="{anchos[h]}"'
               if h in hw:
                  line += f'<td{w} align="right"> {hw[h]:.2f}</td>'
               else:
                  line += f'<td {w} align="center"> &mdash; </td>'                  
            line += f'<td>{total:.2f}</td>' + cells['pi'] + cells['mc'] + cells['eo'] + f'<td>{extra:.2f}</td>'
            participants.append('<tr>{:s}{:s}<th><span style="color:{:s}">{:s}</span></th>{:s}<td>{:s}</td></tr>'.format(identif, line, gradecolor, grade, extraord, str(NP)))
         else:
            participants.append('<tr>{:s}<td colspan="{:d}" align="center"><span style="color:gray"><em><small>alumno inscrito en la unidad de aprendizaje sin registro y/o participaci&oacute;n (NP 1ra, NC 2da)</small></em></span></td></tr>'.format(identif, tc + 8))
   print('<h2>Probabilidad y estad&iacute;stica</h2>\n<table border="1">\n' + header)
   for p in sorted(participants):
      print(p)
   nline = '<tr><th colspan="3" bgcolor="#bbbbbb"><small>Actividad Fund.</small></th>'
   pline = '<tr><th colspan="3" bgcolor="#bbbbbb"><small>M&aacute;ximo</small></th>'
   pos = 0
   total = 0
   for (etiq, w) in nombres:
      pos += 1
      if etiq != OPT:
         pline += '<td colspan="{:d}" bgcolor="#bbbbbb">'.format(w)
         nline += '<th colspan="{:d}" bgcolor="#bbbbbb"><small>'.format(w)
         pts = maximos[etiq]
         pline += '{:d}</td>'.format(pts)
         if etiq == 'A3':
            etiq = 'A3 (medio curso)'
         elif etiq == 'A7':
            etiq = 'A7 (ordinario)'
         nline += '{:s}</small></th>'.format(etiq)
         total += pts
      else:
         pline += '<th bgcolor="#bbbbbb">{:d}</th>'.format(total)
         nline += '<th bgcolor="#bbbbbb">&Sigma;</th>'
   nline += '<td rowspan="2" align="center" valign="center" bgcolor="#333333"><span style="color:white">{:s}</span></td>'.format(OPT) # PFE
   print('{:s}<th colspan="4" rowspan="3" bgcolor="#000000"><span style="color:white"></span></th></tr>'.format(nline))
   print('{:s}</tr>'.format(pline))
   print('<tr><th colspan="{:d}" bgcolor="#eeeeee">Estad&iacute;sticas de cumplimiento de AF por <em>programa educativo</em></th></tr>'.format(tc + 10))
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
   print('<tr><th colspan="{:d}" bgcolor="#eeeeee">Estad&iacute;sticas de cumplimiento de AF por <em>grupo</em></th></tr>'.format(tc + 10))

   for gr in [GRUPO]: # one group
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
   print('URL: https://elisa.dyndns-web.com/cgi-bin/pe.py</div></div>\n</body></html>')
   return


if __name__ == "__main__":
    main()
