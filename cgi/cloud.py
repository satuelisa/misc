#!/usr/bin/env python3

import cgi
import os
import cgitb; cgitb.enable()
from collections import defaultdict
import wordcloud
from random import randint

source = '/var/www/html/elisa/data/wordcloud.txt'
target = '/var/www/html/elisa/pics/wordcloud.png'

def bright(word, font_size, position, orientation, random_state = None, **kwargs):
    return f'hsl({randint(0, 360)}, 100%, 50%)'

def main():
    print('Content-type: text/plain\n\n')
    form = cgi.FieldStorage()
    pw = form.getvalue('pw')
    if pw is None or pw != 'cat':
        print('lol, no')
        return
    s = os.path.getmtime(source)
    t = os.path.getmtime(target)
    if t > s: # the image is newer
        print('up to date')
        return
    response = dict()
    with open(source) as text:
        for line in text:
            line = line.strip()
            if len(line) > 0:
                fields = line.strip().split()
                person = fields.pop(0)
                value = fields.pop(0)
                response[person] = value
    lines = [ text for text in response.values() if '###BLANK###' not in text ]
    if len(lines) > 0:
        freq = dict()
        for line in lines:
            for w in line.split(','):
                if w not in freq:
                    freq[w] = 1
                else:
                    freq[w] += 1
        img = wordcloud.WordCloud(max_font_size = 256,
                                  min_font_size = 32,
                                  max_words = 50,
                                  width = 800,
                                  height = 800,
                                  mode = 'RGBA',
                                  background_color = None)        
        img.generate_from_frequencies(freq)
        img.recolor(color_func = bright, random_state = None)
        img.to_file(target)
        print('rebuilt')            
    print('no content')    

if __name__ == "__main__":
    main()
