#!/usr/bin/env python3
# Patch: V52 -> V53  "Mehrfachsterne nach Stellaris 4.5.0"
#
#  V1-V3  Versionsnummer auf V53 (Titel, Ueberschrift, Export-Kopfzeile)
#  C1     STAR_CLASS_CONFIG: 14 Binary/Trinary-Eintraege mit den Sterntypen
#         aus 00_star_classes.txt, dazu 9 Crisis-Eintraege
#  D1     Sternklassen-Dropdown: Beschriftung nennt die echte Zusammensetzung
#  W1     Stern-Assistent: pc_m_giant_star und pc_t_star im Auswahlfeld
#
# Befund: Keiner der 14 Binary/Trinary-Eintraege stimmte mit dem Spiel ueberein
# (Beispiel sc_binary_1: Editor G + K, Spiel A + Pulsar). Die Crisis-Klassen
# fehlten ganz, wer sie waehlte, bekam keinen Assistenten. Die Dropdown-Texte
# ("Both Main Sequence" usw.) hatten keine Grundlage in den Spieldateien.
#
# Wirkung: STAR_CLASS_CONFIG liefert nur die Startvorschlaege des Assistenten.
# Exportiert wird, was im Assistenten steht. Vanilla-Autoren waehlen Reihenfolge
# und Abstaende frei (Alpha Centauri, sol_initializers.txt: sc_trinary_1 mit
# G bei 15, K bei -35, M bei 260). Die Reihenfolge hier folgt der Spieldatei.
#
# W1 ist Voraussetzung fuer C1: fuenf Vanilla-Kompositionen brauchen Roten
# Riesen oder T-Stern. Ohne die Optionen zeigte das Feld "A-Star", waehrend
# der Assistent intern den Roten Riesen hielt.
#
# Usage:
#   python3 patch_v52_to_v53.py <input.html> <output.html> [00_star_classes.txt]
# Mit dem dritten Argument wird TABLE vor dem Patchen gegen die Spieldatei
# geprueft (Brace-Matching, keine Regex ueber verschachtelte Bloecke).

import re
import sys

if len(sys.argv) not in (3, 4):
    sys.exit("usage: patch_v52_to_v53.py <input.html> <output.html> [00_star_classes.txt]")

SRC, DST = sys.argv[1], sys.argv[2]
GAME = sys.argv[3] if len(sys.argv) == 4 else None

# Einzige Datenquelle dieses Patches. Werte aus Stellaris 4.5.0,
# common/star_classes/00_star_classes.txt, planet = { key = ... } je Block.
TABLE = [
    ("sc_binary_1",            "Binary 1",            ["pc_a_star", "pc_pulsar"]),
    ("sc_binary_2",            "Binary 2",            ["pc_b_star", "pc_neutron_star"]),
    ("sc_binary_3",            "Binary 3",            ["pc_m_giant_star", "pc_b_star"]),
    ("sc_binary_4",            "Binary 4",            ["pc_m_giant_star", "pc_f_star"]),
    ("sc_binary_5",            "Binary 5",            ["pc_b_star", "pc_b_star"]),
    ("sc_binary_6",            "Binary 6",            ["pc_m_star", "pc_g_star"]),
    ("sc_binary_7",            "Binary 7",            ["pc_k_star", "pc_f_star"]),
    ("sc_binary_8",            "Binary 8",            ["pc_g_star", "pc_f_star"]),
    ("sc_binary_9",            "Binary 9",            ["pc_a_star", "pc_f_star"]),
    ("sc_binary_10",           "Binary 10",           ["pc_a_star", "pc_t_star"]),
    ("sc_trinary_1",           "Trinary 1",           ["pc_g_star", "pc_m_star", "pc_k_star"]),
    ("sc_trinary_2",           "Trinary 2",           ["pc_b_star", "pc_a_star", "pc_f_star"]),
    ("sc_trinary_3",           "Trinary 3",           ["pc_k_star", "pc_f_star", "pc_g_star"]),
    ("sc_trinary_4",           "Trinary 4",           ["pc_b_star", "pc_k_star", "pc_t_star"]),
    ("sc_crisis_binary_1",     "Crisis Binary 1",     ["pc_m_giant_star", "pc_pulsar"]),
    ("sc_crisis_binary_2",     "Crisis Binary 2",     ["pc_m_giant_star", "pc_neutron_star"]),
    ("sc_crisis_binary_5",     "Crisis Binary 5",     ["pc_m_star", "pc_b_star"]),
    ("sc_crisis_binary_7_8_9", "Crisis Binary 7/8/9", ["pc_m_star", "pc_f_star"]),
    ("sc_crisis_binary_10",    "Crisis Binary 10",    ["pc_m_star", "pc_t_star"]),
    ("sc_crisis_trinary_1",    "Crisis Trinary 1",    ["pc_m_star", "pc_m_star", "pc_k_star"]),
    ("sc_crisis_trinary_2",    "Crisis Trinary 2",    ["pc_m_giant_star", "pc_a_star", "pc_f_star"]),
    ("sc_crisis_trinary_3",    "Crisis Trinary 3",    ["pc_m_star", "pc_f_star", "pc_g_star"]),
    ("sc_crisis_trinary_4",    "Crisis Trinary 4",    ["pc_m_giant_star", "pc_k_star", "pc_t_star"]),
]

SHORT = {
    "pc_a_star": "A-Star", "pc_b_star": "B-Star", "pc_f_star": "F-Star",
    "pc_g_star": "G-Star", "pc_k_star": "K-Star", "pc_m_star": "M-Star",
    "pc_m_giant_star": "Red Giant", "pc_t_star": "T-Star",
    "pc_pulsar": "Pulsar", "pc_neutron_star": "Neutron Star",
}

# ------------------------------------------------ optional: gegen Spiel pruefen
if GAME:
    with open(GAME, encoding="utf-8-sig") as fh:
        game = fh.read()
    for sc, _, keys in TABLE:
        m = re.search(r"^" + re.escape(sc) + r"\s*=\s*\{", game, re.M)
        assert m, f"{sc}: nicht in {GAME}"
        i, depth = m.end(), 1
        while depth:
            c = game[i]
            if c == "#":                      # Kommentar bis Zeilenende
                i = game.index("\n", i)
                continue
            depth += (c == "{") - (c == "}")
            i += 1
        block = re.sub(r"#[^\n]*", "", game[m.end():i - 1])
        found = re.findall(r"\bkey\s*=\s*(\w+)", block)
        assert found == keys, f"{sc}: Spiel {found}, Tabelle {keys}"
    print(f"  ok  TABLE stimmt mit {GAME} ueberein ({len(TABLE)} Klassen)")

with open(SRC, encoding="utf-8") as fh:
    data = fh.read()

def js_list(keys):
    return "[" + ", ".join("'" + k + "'" for k in keys) + "]"

def label(title, keys):
    return title + " (" + " + ".join(SHORT[k] for k in keys) + ")"

# ---------------------------------------------------------------- V1-V3
V1_OLD = "<title>Stellaris Solar System Editor V52 - Full Editor</title>"
V1_NEW = "<title>Stellaris Solar System Editor V53 - Full Editor</title>"
V2_OLD = '<h1 class="stellaris-header">Stellaris Solar System Editor V52</h1>'
V2_NEW = '<h1 class="stellaris-header">Stellaris Solar System Editor V53</h1>'
V3_OLD = "        const EDITOR_VERSION = 'V52';"
V3_NEW = "        const EDITOR_VERSION = 'V53';"

# ---------------------------------------------------------------- C1
C1_OLD = "\n".join([
    "            // Binary Systems",
    "            'sc_binary_1': { count: 2, types: ['pc_g_star', 'pc_k_star'] },",
    "            'sc_binary_2': { count: 2, types: ['pc_g_star', 'pc_m_star'] },",
    "            'sc_binary_3': { count: 2, types: ['pc_g_star', 'pc_neutron_star'] },",
    "            'sc_binary_4': { count: 2, types: ['pc_m_star', 'pc_m_star'] },",
    "            'sc_binary_5': { count: 2, types: ['pc_g_star', 'pc_black_hole'] },",
    "            'sc_binary_6': { count: 2, types: ['pc_neutron_star', 'pc_black_hole'] },",
    "            'sc_binary_7': { count: 2, types: ['pc_black_hole', 'pc_black_hole'] },",
    "            'sc_binary_8': { count: 2, types: ['pc_neutron_star', 'pc_neutron_star'] },",
    "            'sc_binary_9': { count: 2, types: ['pc_pulsar', 'pc_pulsar'] },",
    "            'sc_binary_10': { count: 2, types: ['pc_pulsar', 'pc_black_hole'] },",
    "            ",
    "            // Trinary Systems",
    "            'sc_trinary_1': { count: 3, types: ['pc_g_star', 'pc_k_star', 'pc_m_star'] },",
    "            'sc_trinary_2': { count: 3, types: ['pc_g_star', 'pc_k_star', 'pc_m_star'] },",
    "            'sc_trinary_3': { count: 3, types: ['pc_g_star', 'pc_k_star', 'pc_neutron_star'] },",
    "            'sc_trinary_4': { count: 3, types: ['pc_g_star', 'pc_neutron_star', 'pc_black_hole'] }",
    "        };",
])

def cfg_lines(prefix):
    return ["            '%s': { count: %d, types: %s }," % (sc, len(k), js_list(k))
            for sc, _, k in TABLE if sc.startswith(prefix)]

c1 = [
    "            // V53: Multi-star entries follow Stellaris 4.5.0,",
    "            // common/star_classes/00_star_classes.txt (planet = { key = ... },",
    "            // in file order). These are only the wizard's starting values;",
    "            // the export writes whatever the wizard holds.",
    "            // Binary Systems",
] + cfg_lines("sc_binary_") + [
    "            ",
    "            // Trinary Systems",
] + cfg_lines("sc_trinary_") + [
    "            ",
    "            // Crisis variants (crisis_star_class of the regular classes)",
] + cfg_lines("sc_crisis_")
c1[-1] = c1[-1].rstrip(",")
C1_NEW = "\n".join(c1 + ["        };"])

# ---------------------------------------------------------------- D1
OLD_LABELS = {
    "sc_binary_1": "Binary 1 (Both Main Sequence)",
    "sc_binary_2": "Binary 2 (Main Sequence + Compact)",
    "sc_binary_3": "Binary 3 (Main Sequence + Neutron)",
    "sc_binary_4": "Binary 4 (Both Compact)",
    "sc_binary_5": "Binary 5 (Main Sequence + Black Hole)",
    "sc_binary_6": "Binary 6 (Neutron + Black Hole)",
    "sc_binary_7": "Binary 7 (Both Black Holes)",
    "sc_binary_8": "Binary 8 (Both Neutron Stars)",
    "sc_binary_9": "Binary 9 (Both Pulsars)",
    "sc_binary_10": "Binary 10 (Pulsar + Black Hole)",
    "sc_trinary_1": "Trinary 1 (Three Main Sequence)",
    "sc_trinary_2": "Trinary 2 (Two Main Sequence + Compact)",
    "sc_trinary_3": "Trinary 3 (Two Main Sequence + Neutron)",
    "sc_trinary_4": "Trinary 4 (Main Sequence + Two Compact)",
    "sc_crisis_binary_1": "Crisis Binary 1",
    "sc_crisis_binary_2": "Crisis Binary 2",
    "sc_crisis_binary_5": "Crisis Binary 5",
    "sc_crisis_binary_7_8_9": "Crisis Binary 7/8/9",
    "sc_crisis_binary_10": "Crisis Binary 10",
    "sc_crisis_trinary_1": "Crisis Trinary 1",
    "sc_crisis_trinary_2": "Crisis Trinary 2",
    "sc_crisis_trinary_3": "Crisis Trinary 3",
    "sc_crisis_trinary_4": "Crisis Trinary 4",
}

D1 = []
for sc, title, keys in TABLE:
    D1.append((
        f"D1  Label {sc}",
        f'<option value="{sc}">{OLD_LABELS[sc]}</option>',
        f'<option value="{sc}">{label(title, keys)}</option>',
        1,
    ))

# ---------------------------------------------------------------- W1
W1_OLD = "\n".join([
    "                                <option value=\"pc_m_star\" ${star.class === 'pc_m_star' ? 'selected' : ''}>M-Star (Red)</option>",
    "                                <option value=\"pc_black_hole\" ${star.class === 'pc_black_hole' ? 'selected' : ''}>Black Hole</option>",
])
W1_NEW = "\n".join([
    "                                <option value=\"pc_m_star\" ${star.class === 'pc_m_star' ? 'selected' : ''}>M-Star (Red)</option>",
    "                                <option value=\"pc_m_giant_star\" ${star.class === 'pc_m_giant_star' ? 'selected' : ''}>Red Giant</option>",
    "                                <option value=\"pc_t_star\" ${star.class === 'pc_t_star' ? 'selected' : ''}>T-Star (Brown Dwarf)</option>",
    "                                <option value=\"pc_black_hole\" ${star.class === 'pc_black_hole' ? 'selected' : ''}>Black Hole</option>",
])

PATCHES = [
    ("V1  Titel auf V53",                V1_OLD, V1_NEW, 1),
    ("V2  Ueberschrift auf V53",         V2_OLD, V2_NEW, 1),
    ("V3  Export-Kopfzeile auf V53",     V3_OLD, V3_NEW, 1),
    ("C1  STAR_CLASS_CONFIG",            C1_OLD, C1_NEW, 1),
] + D1 + [
    ("W1  Assistent: Red Giant, T-Star", W1_OLD, W1_NEW, 1),
]

for name, old, new, expected in PATCHES:
    found = data.count(old)
    assert found == expected, f"{name}: erwartet {expected} Fundstelle(n), gefunden {found}"
    assert data.count(new) == 0, f"{name}: Ersetzung liegt bereits vor, Abbruch"
    data = data.replace(old, new, expected)
    print(f"  ok  {name}")

# ------------------------------------------------ Nachkontrollen
# Jede Mehrfachklasse im Dropdown hat einen Config-Eintrag mit passender
# Sternzahl, und jeder vorgeschlagene Typ ist im Assistenten waehlbar.
sel = re.search(r'<select id="systemStarClass".*?</select>', data, re.S).group(0)
multi = [v for v in re.findall(r'<option value="([^"]+)"', sel)
         if "binary" in v or "trinary" in v]
cfg = re.search(r"const STAR_CLASS_CONFIG = \{(.*?)\n        \};", data, re.S).group(1)
wiz = set(re.findall(r'<option value="(pc_[a-z_]+)" \$\{star\.class', data))
for sc in multi:
    m = re.search(r"'" + re.escape(sc) + r"': \{ count: (\d), types: \[([^\]]*)\] \}", cfg)
    assert m, f"{sc}: kein Eintrag in STAR_CLASS_CONFIG"
    types = re.findall(r"'([^']+)'", m.group(2))
    assert int(m.group(1)) == len(types), f"{sc}: count passt nicht zu types"
    missing = [t for t in types if t not in wiz]
    assert not missing, f"{sc}: im Assistenten nicht waehlbar: {missing}"
print(f"  ok  {len(multi)} Mehrfachklassen: Config vorhanden, count stimmt, Typen waehlbar")

with open(DST, "w", encoding="utf-8") as fh:
    fh.write(data)

print(f"geschrieben: {DST}")
