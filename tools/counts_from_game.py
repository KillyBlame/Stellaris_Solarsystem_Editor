# Unabhaengige count-Liste je System (Python, Brace-Matching), Gegenprobe
# fuer regress_v55.js. Ausgabe: datei \t system \t min-max,min-max,...
import os, re, sys
d = sys.argv[1]
WORD = re.compile(r'[A-Za-z0-9_]')
def close(t, j):
    dep = 1
    while dep:
        c = t[j]; dep += c == '{'; dep -= c == '}'; j += 1
    return j
def depth0_count(body):
    dep = 0; k = 0
    while k < len(body):
        c = body[k]
        if c == '{': dep += 1
        elif c == '}': dep -= 1
        elif dep == 0 and (k == 0 or not WORD.match(body[k-1])):
            m = re.compile(r'count\s*=\s*(\{\s*min\s*=\s*(\d+)\s*max\s*=\s*(\d+)\s*\}|(\d+))').match(body, k)
            if m:
                return (m.group(2), m.group(3)) if m.group(4) is None else (m.group(4), m.group(4))
        k += 1
    return ('1', '1')
def bodies(t, out):
    # depth-0 planet/moon blocks of t, recursive into their own depth-0 bodies
    dep = 0; i = 0
    while i < len(t):
        c = t[i]
        if c == '{': dep += 1; i += 1; continue
        if c == '}': dep -= 1; i += 1; continue
        if dep == 0 and (i == 0 or not WORD.match(t[i-1])):
            m = re.compile(r'(planet|moon)\s*=\s*\{').match(t, i)
            if m:
                j = close(t, m.end()); body = t[m.end():j-1]
                out.append(depth0_count(body)); bodies(body, out); i = j; continue
        i += 1
for f in sorted(x for x in os.listdir(d) if x.endswith('.txt')):
    t = re.sub(r'#[^\n]*', '', open(os.path.join(d, f), encoding='utf-8-sig').read())
    i = 0
    while True:
        m = re.compile(r'(?m)^([A-Za-z0-9_]+)\s*=\s*\{').search(t, i)
        if not m: break
        j = close(t, m.end()); out = []; bodies(t[m.end():j-1], out)
        print(f"{f}\t{m.group(1)}\t" + ",".join(f"{a}-{b}" for a, b in out))
        i = j
