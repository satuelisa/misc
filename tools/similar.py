import pandas as pd
comp = pd.read_csv('competencies.csv', sep=';', encoding = 'latin_1',
                 header = None, skiprows = 1, engine = 'python')

devis = dict()
descr = dict()

for i, r in comp.iterrows():
    d = r[0]
    c = r[1]
    t = bytes(r[2], 'iso-8859-1').decode('utf8')
    devis[c] = d
    descr[c] = t

stopwords = set( [ 'les', 'la', 'le', 'en', 'de', 'des', 'un', 'une', 'pour',
                   'et', 'ses', 'avec', 'dans', 'au', 'sans', 'sur', 'à',
                   'du', 'd’un', 'aux', 'ou' ] )
generic = set( [ 'analyser', 'contribuer', 'perfectionner', 'explorer',
                 'exploiter', 'utiliser', 'assurer', 'effectuer', 'réaliser',
                 'traiter', 'créer', 'effectuer', 'projet' ] )
prefix = [ 'd’', 'l’' ]

remove = stopwords | generic

def strip(word):
    for p in prefix:
        l = len(prefix)
        if word[:l] == prefix:
            return word[l:]
    return word

def prune(words):
    return words - remove

debug = False

def textsimilarity(t1, t2):
    # bags of words
    b1 = prune(set([ strip(t.lower()) for t in t1.split() ]))
    b2 = prune(set([ strip(t.lower()) for t in t2.split() ]))
    shared = b1 & b2
    joint = b1 | b2
    if len(shared) > 1:
        if debug:
            print(shared)
        return len(shared) / len(joint)
    else:
        return 0 # just one shared word is not enough
    
import networkx as nx    

G = nx.Graph()

for c1 in descr:
    for c2 in descr:
        if c1 > c2:
            sim = textsimilarity(descr[c1], descr[c2])
            if sim > 0:
                G.add_edge(c1, c2, sim = sim)

# from https://python-louvain.readthedocs.io/en/latest/api.html

import matplotlib.cm as cm
import matplotlib.pyplot as plt
import community as community_louvain

parts = community_louvain.best_partition(G, weight = 'sim')

vis = False

count = max(parts.values()) + 1

if vis:
    pos = nx.spring_layout(G)
    cmap = cm.get_cmap('viridis', count)
    nx.draw_networkx_nodes(G, pos, parts.keys(), node_size = 40,cmap = cmap, node_color = list(parts.values()))
    nx.draw_networkx_edges(G, pos, alpha = 0.5)
    plt.show()

from collections import defaultdict
groups = defaultdict(set)
for (c, g) in parts.items():
    groups[g].add(c)

for g in range(count):
    d = set()
    for c in groups[g]:
        d.add(devis[c])
    if len(d) > 1: # more than one
        for c in groups[g]:
            print(descr[c], c, devis[c])
        print('\n') # gap
