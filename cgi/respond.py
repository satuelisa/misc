#!/usr/bin/env python3
import cgi, os
import cgitb; cgitb.enable()
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from better_profanity import profanity
import wordcloud
from random import randint

nltk.data.path.append('/var/www/html/elisa/data/nltk')
filename = '/var/www/html/elisa/pics/wordcloud.png'

en = stopwords.words('english')
sp = stopwords.words('spanish')
fr = stopwords.words('french') 

custom = []
with open('filter.txt') as source:
    for line in source:
        w = line.strip()
        custom.append(w)
        if w[-1] == 'o':
            custom.append(w[:-1] + 'a')
            custom.append(w[:-1] + 'as')
        if w[-1] != 's':
            custom.append(w + 's')
            custom.append(w + 'es')            

profanity.load_censor_words(custom)

def clean(text):
    raw = word_tokenize(text)
    # all lower case
    low = { w.lower() for w in raw }
    # no puntuaction
    words = [ w for w in low if w.isalpha() ]
    # filter out stop words
    words = [ w for w in words if w not in sp ]
    words = [ w for w in words if w not in fr ]
    words = [ w for w in words if w not in en ]
    # filter out profanity
    ok = [ w for w in words if not profanity.contains_profanity(w) ]
    return ','.join(ok)

def bright(word, font_size, position, orientation, random_state = None, **kwargs):
    return f'hsl({randint(0, 360)}, 100%, 50%)'

def main():
    print('Content-type: text/plain\n\n')
    form = cgi.FieldStorage()
    text = form.getvalue('value')
    label = form.getvalue('hash')
    matr = form.getvalue('matr')   
    if label is None:
        with open('/var/www/html/elisa/data/reg.txt', 'r') as reg:
            for line in reg:
                f = line.strip().split()
                h = f[0]
                m = f[1]
                if matr == m:
                    label = h
                    break
    if label is None: # unknown
        print('unknown')
        return
    t = clean(text)
    if len(t) > 0:
        # store the response
        with open('/var/www/html/elisa/data/wordcloud.txt', 'a') as target:
            print(label, t, file = target)
        print('thanks')

if __name__ == "__main__":
    main()

