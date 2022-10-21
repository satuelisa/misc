from sys import argv

def value(s):
    pts = 0.0
    if len(s) > 0:
        if '#' not in s:
            if '-' == s:
                return 0
            if '_' in s:
                parts = s.split('_')
                if len(parts) == 2:
                    up = int(parts.pop(0))
                    down = int(parts.pop(0))
                    value = up / (1.0 * down)
                    pts += float(value)
                else:
                    assert len(parts) == 3
                    whole = int(parts.pop(0))
                    up = int(parts.pop(0))
                    down = int(parts.pop(0))
                    value = whole + up / (1.0 * down)
                    pts += float(value)
            else:
                pts += float(s)
    return pts

with open(argv[1]) as data:
    for line in data:
        line = line.strip()
        if len(line) > 0:
            f = line.split()
            s  = f.pop(0) + " "
            for v in f:
                s += str(value(v)) + ' '
            print(s)
        
