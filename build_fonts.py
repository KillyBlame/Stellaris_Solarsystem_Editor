#!/usr/bin/env python3
"""
Erzeugt fonts-embedded.css: die fuenf Schriftschnitte, die der Editor wirklich
benutzt, als WOFF2 im latin-Subset, base64-eingebettet.

Warum genau diese fuenf: Orbitron steht in zwei CSS-Regeln, beide im Gewicht 700.
Exo 2 traegt den Rest, inklusive der Canvas-Beschriftung, und wird ueber die
Tailwind-Klassen font-medium, font-semibold und font-bold in 500, 600 und 700
angefordert. Der frueher verwendete Fremdaufruf holte sechs Orbitron-Schnitte,
von denen fuenf niemand benutzt, und liess dafuer Exo 2 in 700 weg, obwohl
font-bold 13-mal im Markup steht.

Voraussetzung, einmalig im Projektordner:

    npm install @fontsource/orbitron @fontsource/exo-2

Danach:

    python3 build_fonts.py

Ergebnis ist fonts-embedded.css neben diesem Skript. Das Patch-Skript liest die
Datei automatisch, wenn sie dort liegt.

Quelle sind die npm-Pakete von fontsource, dieselben Dateien wie bei Google
Fonts, SIL Open Font License.
"""

import base64
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "fonts-embedded.css")

WANTED = [
    ("Orbitron", 700, "@fontsource/orbitron/files/orbitron-latin-700-normal.woff2"),
    ("Exo 2",    400, "@fontsource/exo-2/files/exo-2-latin-400-normal.woff2"),
    ("Exo 2",    500, "@fontsource/exo-2/files/exo-2-latin-500-normal.woff2"),
    ("Exo 2",    600, "@fontsource/exo-2/files/exo-2-latin-600-normal.woff2"),
    ("Exo 2",    700, "@fontsource/exo-2/files/exo-2-latin-700-normal.woff2"),
]

HEADER = [
    "/* V50 K1b: Schriften eingebettet, latin-Subset, WOFF2.",
    "   Erzeugt von build_fonts.py. Nicht von Hand aendern, sondern das Skript",
    "   neu laufen lassen.",
    "   Die alten Fremd-URLs sind hier absichtlich nicht ausgeschrieben, sonst",
    "   meldet jede Suche nach externen Abhaengigkeiten einen Treffer, den es",
    "   nicht mehr gibt.",
    "   Quelle: die npm-Pakete von fontsource, dieselben Dateien wie bei",
    "   Google Fonts, SIL Open Font License. */",
]

missing = []
parts = list(HEADER)
total = 0

for family, weight, rel in WANTED:
    path = os.path.join(HERE, "node_modules", *rel.split("/"))
    if not os.path.isfile(path):
        missing.append(path)
        continue
    with open(path, "rb") as fh:
        raw = fh.read()
    total += len(raw)
    b64 = base64.b64encode(raw).decode("ascii")
    parts.append(
        "@font-face{font-family:'%s';font-style:normal;font-weight:%d;"
        "font-display:swap;src:url(data:font/woff2;base64,%s) format('woff2')}"
        % (family, weight, b64)
    )
    print("  ok  %-10s %3d  %6d Bytes roh" % (family, weight, len(raw)))

if missing:
    print("")
    print("Fehlende Schriftdateien:")
    for path in missing:
        print("    " + path)
    print("")
    sys.exit("Erst ausfuehren: npm install @fontsource/orbitron @fontsource/exo-2")

css = "\n".join(parts) + "\n"

# Dieselbe Pruefung, die auch das Patch-Skript macht: nichts darf den
# <style>-Block sprengen, und es darf kein Fremdaufruf hineinrutschen.
for forbidden in ("</style>", "@import", "http://", "https://"):
    if forbidden in css:
        sys.exit("Abbruch: erzeugtes CSS enthaelt '%s'." % forbidden)

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write(css)

print("")
print("roh gesamt : %7d Bytes" % total)
print("geschrieben: %s (%d Bytes)" % (OUT, len(css.encode("utf-8"))))
