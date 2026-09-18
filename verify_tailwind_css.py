#!/usr/bin/env python3
"""
Prueft, ob ein lokal gebautes Tailwind-CSS alle Utility-Klassen abdeckt,
die im Editor tatsaechlich vorkommen.

Warum das noetig ist: ein zu scharfer Purge meldet nichts. Es fehlt einfach
eine Regel, und das Layout verschiebt sich an einer Stelle, die niemand
sofort ansieht. Deshalb wird jede Klasse einzeln gegen das CSS gehalten.

Gesucht wird an zwei Stellen:
  1. class="..."-Attribute, auch die in JS-Template-Literalen
  2. Zeichenkettenliterale im Script, aus denen Klassen zusammengesetzt
     werden (z. B. 'mt-4 p-3 rounded-lg border ' + tones[tone])

Usage: python3 verify_tailwind_css.py <editor.html> <tailwind-built.css>
"""

import re
import sys

if len(sys.argv) != 3:
    sys.exit("usage: verify_tailwind_css.py <editor.html> <tailwind-built.css>")

HTML_PATH, CSS_PATH = sys.argv[1], sys.argv[2]

with open(HTML_PATH, encoding="utf-8") as fh:
    html = fh.read()
with open(CSS_PATH, encoding="utf-8") as fh:
    css = fh.read()

# Utilities ohne Bindestrich, Schraegstrich oder Doppelpunkt. Ohne diese
# Liste wuerde der Filter unten sie fuer normale Woerter halten.
BARE_UTILITIES = {
    "container", "flex", "grid", "block", "inline", "hidden", "relative",
    "absolute", "fixed", "sticky", "static", "truncate", "italic",
    "underline", "uppercase", "lowercase", "capitalize", "rounded",
    "border", "shadow", "transition", "transform", "resize", "sr",
}

# Kein Tailwind, taucht aber in denselben Attributen auf.
IGNORE = {
    "stellaris-panel", "stellaris-btn", "stellaris-input", "stellaris-header",
    "stellaris-badge", "stellaris-btn-secondary", "stellaris-btn-success",
    "stellaris-btn-danger", "badge-primary", "badge-secondary",
    "system-selector-item", "multi-system-layout", "system-list-panel",
    "system-editor-panel", "planet-item", "moon-item", "modal",
    "modal-content", "notification", "canvas-info", "label", "active",
}


def looks_like_utility(token):
    if token in IGNORE:
        return False
    if token in BARE_UTILITIES:
        return True
    if not re.fullmatch(r"[a-z0-9][a-z0-9:\[\]\/\.\,\%\#\(\)_-]*", token):
        return False
    # Echte Utilities tragen fast immer einen Bindestrich, Schraegstrich
    # oder einen Variantenpraefix mit Doppelpunkt.
    return ("-" in token) or ("/" in token) or (":" in token)


def css_escape(token):
    """Selektor-Schreibweise, wie Tailwind sie erzeugt: Sonderzeichen
    bekommen einen Backslash."""
    out = []
    for ch in token:
        if ch in ":/.[]%#(),":
            out.append("\\" + ch)
        else:
            out.append(ch)
    return "." + "".join(out)


candidates = set()

# 1) class="..."  und class='...'
for match in re.finditer(r'class\s*=\s*"([^"]*)"', html):
    for token in match.group(1).split():
        candidates.add(token)
for match in re.finditer(r"class\s*=\s*'([^']*)'", html):
    for token in match.group(1).split():
        candidates.add(token)

# 2) Zeichenkettenliterale im Script. Nur solche, die ausschliesslich aus
#    utility-artigen Token bestehen, sonst waere das Rauschen unbrauchbar.
script = html
for match in re.finditer(r"'([^'\n]{2,200})'", script):
    inner = match.group(1).strip()
    if not inner:
        continue
    tokens = inner.split()
    if len(tokens) > 12:
        continue
    if all(looks_like_utility(t) or t in IGNORE for t in tokens):
        for token in tokens:
            candidates.add(token)

# Template-Ausdruecke wie ${...} sind zur Laufzeit gebaut und nicht
# statisch aufloesbar. Sie werden verworfen, aber gezaehlt und gemeldet.
dynamic = {t for t in candidates if "${" in t or "}" in t}
candidates -= dynamic

utilities = sorted(t for t in candidates if looks_like_utility(t))

missing = []
for token in utilities:
    if css_escape(token) not in css:
        missing.append(token)

print("Editor : " + HTML_PATH)
print("CSS    : " + CSS_PATH + "  (" + str(len(css)) + " Zeichen)")
print("geprueft: " + str(len(utilities)) + " Utility-Kandidaten")
if dynamic:
    print("dynamisch zusammengesetzt, nicht pruefbar: " + str(len(dynamic)))
    for token in sorted(dynamic):
        print("    ? " + token)

if missing:
    print("")
    print("FEHLEN IM CSS (" + str(len(missing)) + "):")
    for token in missing:
        print("    x " + token)
    print("")
    print("Jede Zeile einzeln ansehen. Ein Treffer, der kein Tailwind ist,")
    print("ist harmlos. Ein echter Treffer heisst: Layout bricht still.")
    sys.exit(1)

print("")
print("OK - jede gefundene Utility-Klasse hat eine Regel im CSS.")
