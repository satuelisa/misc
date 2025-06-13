
import pandas as pd
obs = pd.read_csv('obsolete.csv', sep=';')
flag = set()
for i, r in obs.iterrows():
    s = [ str(v) for v in r ]
    if 'JAMAIS' in s[-1]: # last
        flag.add(s[0]) # first


flag.add('OTHERS') # skip also this

from collections import defaultdict
disciplines = defaultdict(set)
people = dict()
adj = defaultdict(int)
freq = defaultdict(int)

c = 0
with open('disc.txt') as input:
    for line in input:
        profile = line.split(',')
        c += 1
        label = f'Person {c}'
        held = set([ s.strip().upper() for s in profile ])
        people[label] = held
        for d1 in held:
            freq[d1] += 1
            if d1 in flag:
                continue
            disciplines[d1].add(label)
            for d2 in held:
                if d2 in flag:
                    continue
                if d1 != d2: # count co-occurrences of discipline pairs
                    adj[f'{d1},{d2}'] += 1
                    adj[f'{d2},{d1}'] += 1


excl = defaultdict(int)
for pair in adj: # check if the co-occuring pairs sometimes appear without one another
    parts = pair.split(',')
    d1,d2 = parts[0], parts[-1]
    for combo in people.values():
        if (d1 in combo and d2 not in combo): # one without the other
            excl[f'{d1},{d2}'] += 1
        if (d2 in combo and d1 not in combo): # vice versa
            excl[f'{d2},{d1}'] += 1            

safe = set()
mixed = set()
            
for pair in adj:
    if pair in excl:
        mixed.add(pair)
    else:
        safe.add(pair)

safe -= mixed # clean up the mixed ones

import networkx as nx
G = nx.Graph()

for pair in safe:
    parts = pair.split(',')
    d1,d2 = parts[0], parts[-1]
    if freq[d1] > 1 and freq[d2] > 1: # neither are sole occurrences
        G.add_edge(d1, d2, weight = adj[pair])

cliques = nx.find_cliques(G)

membership = defaultdict(set)
c = 0
groups = dict()
for group in cliques:
    label = f'C{c}'
    c += 1
    groups[label] = set(group)
    for d in group:
        membership[d].add(label)

merge = set()
        
for g in groups:
    separate = True
    for d in groups[g]:
        if len(membership[d]) > 1:
            separate = False
            break
        if not separate:
            break
    if separate:
        merge |= groups[g] # mark as safe to merge


import matplotlib.pyplot as plt
plt.rcParams['figure.figsize'] = [ 32 , 16 ]

i = 1
for cc in nx.connected_components(G):
    S = G.subgraph(cc)
    W = [ S[u][v]['weight'] for u, v in S.edges() ]
    V = S.nodes()    
    palette = [ 'green' if v in merge else 'yellow' for v in V ]
    coords = nx.kamada_kawai_layout(S, scale = 3)
    plt.clf()
    nx.draw(S, width = W, pos = coords, node_size = 2000,
            nodelist = V, node_color = palette,
            font_size = 15, with_labels = True)
    plt.savefig(f'disc{i}.png')
    i += 1
