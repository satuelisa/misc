import pandas as pd
obs = pd.read_csv('obsolete.csv', sep=';')
flag = set()
for i, r in obs.iterrows():
    s = [ str(v) for v in r ]
    if 'JAMAIS' in s[-1]: # last
        flag.add(s[0]) # first

anon = False # enable for the text file analysis
        
from collections import defaultdict
# ID,Nom,Prenom,Disc,Dept,Statut
hr = pd.read_csv('disc.csv', sep='Montreal_', encoding = 'latin_1',
                 header = None, skiprows = 1, engine = 'python')

disciplines = set()
people = defaultdict(set)
adj = defaultdict(int)
freq = defaultdict(int)

for i, r in hr.iterrows():
    parts = [ str(v) for v in r ]
    fields = parts[0].split(',')
    if len(fields) > 3:
        d = fields[3]
        s = parts[-1]
        n = f'{fields[1]}, {fields[2]}'
        disciplines.add(d)
        people[n].add(d)
    else:
        print('too short', fields)

for (person, dl) in people.items():
    for d1 in dl:
        freq[d1] += 1
        for d2 in dl:
            if d1 != d2:
                al = f'{min(d1, d2)},{max(d1, d2)}'
                adj[al] += 1

apart = defaultdict(int)                        
for (al, c) in adj.items():
    if c > 0: 
        e = al.split(',')
        d1 = e[0]
        d2 = e[-1]
        for dl in people.values():
            if d1 in dl and d2 not in dl:
                apart[f'{d1},{d2}'] += 1
            if d1 not in dl and d2 in dl:
                apart[f'{d2},{d1}'] += 1                

import networkx as nx

skip = [ 'MAQUI', 'IC', 'DI', 'IG', 'Lx', 'Design', 'ilas' ]

prune = True

G = nx.Graph()
for d in disciplines:
    ignore = False
    for s in skip:
        if s in d:
            ignore = True
    if ignore:
        continue
    if 'i' in d.lower() or d == '420' : # I, IN, AI
        if prune and d in flag:
            continue
        G.add_node(d)

edges = set(apart.keys()) | set(adj.keys())

ec = dict() # 1 = pull, -1 = push, 0 = neutral

for e in edges:
    al = e.split(',')
    d1 = al[0]
    d2 = al[-1]
    if G.has_node(d1) and G.has_node(d2):
        c = f'{d2},{d1}' # opposite direction edge
        if e in apart and (e not in adj and c not in adj):
            ec[e] = -1 # repulsion
            ec[c] = -1 # repulsion        
            G.add_edge(d1, d2, weight = apart[e])
        elif e not in apart and (e in adj or c in adj):
            ec[e] = 1 # attraction
            ec[c] = 1 # attraction
            G.add_edge(d1, d2, weight = adj[e])
        elif e in apart and (e in adj or c in adj):
            ec[e] = 0 # mixed
            ec[c] = 0 # mixed
            G.add_edge(d1, d2, weight = 1)
        else:
            print('# unclear', e)

import matplotlib.pyplot as plt
import seaborn as sns

plt.rcParams['figure.figsize'] = [ 32 , 16 ]

i = 1
for cc in nx.connected_components(G):
    S = G.subgraph(cc)
    W = [ S[u][v]['weight'] for u, v in S.edges() ]
    V = S.nodes()

    groups = nx.community.greedy_modularity_communities(S)
    gid = 0
    g = dict()
    for group in groups:
        for member in group:
            g[member] = gid
        gid += 1
    palette = sns.color_palette('husl', len(groups))
    
    np = [ palette[g[v]] for v in V ]
    ns = [ 100 if v in flag else 2000 for v in V ]
    ep = []
    for e in S.edges():
        s, t = e
        l = f'{s},{t}'
        if ec[l] == -1:
            ep.append('red')
        elif ec[l] == 1:
            ep.append('blue')
        else:
            ep.append('gray')
    coords = nx.kamada_kawai_layout(S, scale = 3)
    plt.clf()
    nx.draw(S, width = W, pos = coords, node_size = ns,
            nodelist = V, node_color = np, edge_color = ep,
            font_size = 15, with_labels = True)
            
    plt.savefig(f'disc{i}.png')
    i += 1

    j = 0
    for sub in groups: # divide clusters further
        SG = S.subgraph(sub)
        SV = SG.nodes()
        sgroups = nx.community.greedy_modularity_communities(SG)
        gid = 0
        sg = dict()
        for group in sgroups:
            for member in group:
                sg[member] = gid
            gid += 1
        palette = sns.color_palette('husl', len(sgroups))
        np = [ palette[sg[v]] for v in SV ]
        plt.clf()
        cs = nx.kamada_kawai_layout(SG, scale = 3)        
        nx.draw(SG, pos = cs, node_size = 2000,
                nodelist = SV, node_color = np, edge_color = 'black',
                font_size = 15, with_labels = True)
        plt.savefig(f'disc{i}sub{j}.png')
        j += 1
                
if not anon:
    quit()

disciplines = defaultdict(set)
people = defaultdict(set)
adj = defaultdict(int)
freq = defaultdict(int)
flag.add('OTHERS') # skip also this
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
