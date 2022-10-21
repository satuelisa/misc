#!/usr/bin/env python3

import cgi, os
import cgitb; cgitb.enable()
from sys import argv

def main():
   print('Content-type: text/plain\n\n')
   with open('/var/www/html/elisa/data/interact.txt', 'a') as votes:
      print('reset', file = votes)

if __name__ == "__main__":
    main()
