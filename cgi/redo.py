#!/usr/bin/env python3

import cgi, os
import cgitb; cgitb.enable()
from shutil import copyfile

def main():
   print('Content-type: text/plain\n\n')
   form = cgi.FieldStorage()
   pw = form.getvalue('pw')
   if pw is None or pw != 'cat':
      print('lol, no')
      return
   with open('/var/www/html/elisa/data/wordcloud.txt', 'w') as target:
      print('', file = target)
   # it has nothing now
   target = '/var/www/html/elisa/pics/wordcloud.png'
   source = '/var/www/html/elisa/pics/none.png'
   copyfile(source, target)
   print('done')   
   
if __name__ == "__main__":
    main()
