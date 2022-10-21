#!/usr/bin/python3
import cgi, os
import cgitb; cgitb.enable()
import hashlib
from time import localtime, strftime

hash = None
sourceip = None
timestamp = None

def getHash():
   global hash, sourceip, timestamp
   if hash is not None:
      return hash
   else:
      if timestamp is None:
         timestamp = strftime("%a, %d %b %Y %H:%M:%S +0000", localtime())
      if sourceip is None:
         try:
            sourceip = cgi.escape(os.environ["REMOTE_ADDR"])
         except:
            sourceip = "localhost"
      t = timestamp + sourceip
      hash = hashlib.md5(t.encode("utf-8")).hexdigest()            
      return hash

def identify():
   global sourceip
   global timestamp
   s = '<hash>%s</hash>\n' % getHash()
   s += '<author>%s</author>\n' % sourceip
   s += '<time>%s</time>\n' % timestamp
   return s

def multipleChoice(form):
   correct = form.getfirst('correct', '').strip()
   if len(correct) == 0:
      return None
   distractors = list()
   count = 1
   label = 'distract.%d' % count
   while label in form:
      d = form.getfirst(label, '').strip()
      if len(d) == 0:
         return None
      distractors.append(d)
      count += 1
      label = 'distract.%d' % count
   output = '<multiple>\n'
   output += '<correct>![CDATA[%s]]</correct>\n' % correct
   for d in distractors:
      output += '<distractor>![CDATA[%s]]</distractor>\n' % d
   output += '</multiple>\n'
   return output

def material(form, mandatory=False):
   sourceFile = None
   try:
      sourceFile = form['material']
   except:
      return False
   filename = None
   try:
      filename = sourceFile.filename
   except:
      return False
   if len(filename) == 0:
      return False
   ext = filename.split('.')[-1].lower()
   if ext != 'pdf':
      return False
   filename = getHash() + '.' + ext
   try:
      target = open('/var/www/html/elisa/data/nano/%s' % filename, 'wb')
      target.write(sourceFile.file.read())
      target.close()
   except:
      return False
   return True

def main():
   print('Content-Type: text/html\n')
   error = False
   form = cgi.FieldStorage()
   style = form.getfirst('type', '')
   content = form.getfirst('content', '').strip()
   area = form.getfirst('area', '') 
   if style == '':
      error = True
   else:
      output = '<question>\n'
      output += identify()
      material(form, style == 'mat')
      if style == 'mul':
         proc = multipleChoice(form)
         if proc is not None:
            output += proc
         else:
            error = True
   if not (error or len(content) == 0 or len(area) == 0):
      output += '<content>![CDATA[%s]]</content>\n' % content
      output += '<area>%s</area>\n' % area
      with open('/var/www/html/elisa/data/nano/preguntas.xml', 'a') as storage:
         print(output, '</question>', file = storage)
   else:
      with open('/var/www/html/elisa/data/nano/log.txt', 'a') as log:
         print(identify(), file = log)

   with open("/var/www/html/elisa/nano/static.html") as data:
      for line in data:
         if '#AREAS#' in line:
            with open("/var/www/html/elisa/nano/areas.lst") as ia:
               for line in ia:
                  t = line.split()
                  label = t.pop(0)
                  descr = ' '.join(t)
                  print('<option value="%s">%s</option>' % (label, descr))
      else:
         print(line)

main()
