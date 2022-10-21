#!/usr/bin/env python3

import cgi, os
import cgitb; cgitb.enable()
from collections import defaultdict

options = [ "green", "yellow", "red", "gray", "black" ]
symbols = { "green": "&#128578;",
            "yellow": "&#128533;",
            "red": "&#9995;",
            "gray": "&#128164;" ,
            "black": "&#128721;" }
classes = { "green": "agree",
            "yellow": "confused",
            "red": "question",
            "gray": "absent",
            "black": "problem" }

def main():
   print('Content-type: text/html\n\n')
   print('''<!DOCTYPE html>
<html lang="en">
  <head>
    <META HTTP-EQUIV="Content-Type" content="text/html; charset=UTF-8">
    <meta http-equiv="refresh" content="5">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">    
    <LINK rel="stylesheet" type="text/css" href="https://elisa.dyndns-web.com/teaching/join.css"> 
    <title>Votes</title>
  </head>
  <body>
    <div>''')
   
   vote = dict()
   with open('/var/www/html/elisa/data/interact.txt', 'r') as votes:
      for line in votes:
         if 'reset' in line:
            vote = dict() # reset
         else:
            fields = line.strip().split()
            person = fields.pop(0)
            value = fields.pop(0)
            vote[person] = value
   for o in options:
      n = sum([v == o for v in vote.values()])
      s = symbols[o]
      c = classes[o]
      if n > 0:
         print(f'<button class="{c}">{n} {s}</button><br>')
      else:
         print(f'<button class="inactive{c}">&ndash; {s}</button><br>')
      
   print('</div></body></html>')
      
      
if __name__ == "__main__":
    main()

    
