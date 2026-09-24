#!/usr/bin/env python3
"""
Regressionstest fuer den Export zwischen zwei Editor-Versionen.

Seit V51 beginnt jede exportierte Initializer-Datei mit Kommentarzeilen
(Version, Namensmodus). Zwei Exporte aus verschiedenen Versionen
unterscheiden sich damit immer in der Versionszeile, ein nackter diff
schlaegt bei jedem Versionssprung an und sagt nichts mehr aus.

Dieses Skript trennt deshalb:
  Kopf  = fuehrende Zeilen, die mit # beginnen, samt Leerzeilen danach
  Rumpf = alles ab der ersten Zeile, die weder leer ist noch mit # beginnt

Die Koepfe werden nebeneinander gezeigt, der Rumpf muss bytegleich sein.
Stimmt der Namensmodus der beiden Koepfe nicht ueberein, bricht der Test ab,
denn dann vergleicht man zwei verschiedene Exportvertraege und nicht zwei
Versionen. (Genau das ist beim ersten V49/V50-Vergleich passiert.)

Usage: python3 compare_exports.py <alt.txt> <neu.txt>
Exit 0 = Rumpf bytegleich, 1 = Unterschied, 2 = Aufruffehler
"""

import hashlib
import sys

if len(sys.argv) != 3:
    print("usage: compare_exports.py <alt.txt> <neu.txt>")
    sys.exit(2)


def split(path):
    with open(path, "rb") as fh:
        raw = fh.read()
    if raw.startswith(b"\xef\xbb\xbf"):
        print("Hinweis: " + path + " beginnt mit einem UTF-8-BOM.")
    text = raw.decode("utf-8")
    lines = text.split("\n")
    i = 0
    while i < len(lines) and (lines[i].startswith("#") or lines[i].strip() == ""):
        i += 1
    head = [l for l in lines[:i] if l.startswith("#")]
    body = "\n".join(lines[i:])
    return head, body


def mode_of(head):
    for line in head:
        if line.startswith("# Names:"):
            return "plain" if "plain text" in line else "keys"
    return None


old_path, new_path = sys.argv[1], sys.argv[2]
old_head, old_body = split(old_path)
new_head, new_body = split(new_path)

print("Kopf alt: " + (" | ".join(old_head) if old_head else "(keiner, vor V51)"))
print("Kopf neu: " + (" | ".join(new_head) if new_head else "(keiner, vor V51)"))

m_old, m_new = mode_of(old_head), mode_of(new_head)
if m_old and m_new and m_old != m_new:
    print("")
    print("ABBRUCH: die Exporte wurden in verschiedenen Namensmodi erzeugt")
    print("  alt: " + m_old + "   neu: " + m_new)
    print("Beide mit derselben Einstellung der Checkbox neu exportieren.")
    sys.exit(1)

h_old = hashlib.sha256(old_body.encode("utf-8")).hexdigest()
h_new = hashlib.sha256(new_body.encode("utf-8")).hexdigest()
print("")
print("Rumpf alt: %d Bytes  sha256 %s" % (len(old_body.encode("utf-8")), h_old))
print("Rumpf neu: %d Bytes  sha256 %s" % (len(new_body.encode("utf-8")), h_new))

if old_body == new_body:
    print("")
    print("OK - der Rumpf ist bytegleich.")
    sys.exit(0)

old_lines = old_body.split("\n")
new_lines = new_body.split("\n")
print("")
print("UNTERSCHIED im Rumpf. Erste Abweichungen:")
shown = 0
for n in range(max(len(old_lines), len(new_lines))):
    a = old_lines[n] if n < len(old_lines) else "<Ende>"
    b = new_lines[n] if n < len(new_lines) else "<Ende>"
    if a != b:
        print("  Zeile %d" % (n + 1))
        print("    alt: " + a)
        print("    neu: " + b)
        shown += 1
        if shown >= 10:
            break
sys.exit(1)
