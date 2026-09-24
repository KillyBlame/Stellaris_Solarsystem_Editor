#!/usr/bin/env python3
# Patch: V51 -> V52  "Abgleich mit Stellaris 4.5.0"
#
#  V1-V3  Versionsnummer auf V52 (Titel, Ueberschrift, Export-Kopfzeile)
#  S1     Sternklassen-Dropdown: sc_m_giant, sc_toxoid_star, sc_rift_star
#  H1     Validierung: HABITABLE-Liste um pc_volcanic, pc_nanotech, pc_city
#  O1     pc_o_star in der toten Parser-Liste als Mod-Wert kennzeichnen
#
# Grundlage: Stellaris 4.5.0 "Cygnus" (build 8697).
#
# S1: Alle drei Klassen stehen in common/star_classes/00_star_classes.txt.
#     sc_m_giant liegt zusaetzlich in rl_standard_stars, rl_red_stars und
#     rl_all_stars (randomizers/00_random_lists.txt), ist also eine normale
#     Zufallsklasse. sc_toxoid_star und sc_rift_star haben spawn_odds = 0,
#     kommen im Spiel nur ueber Initializer vor. Genau dafuer ist der Editor da.
#     Bisher liessen sich die drei nur ueber "Custom" eintragen, und ein
#     importiertes System mit dieser Klasse oeffnete sich als Custom-Eintrag.
#     Die Liste der gueltigen Werte wird beim Oeffnen aus den <option>-Tags
#     gelesen, deshalb reicht der Eintrag im Markup. STAR_CLASS_CONFIG braucht
#     keinen Eintrag: fehlender Eintrag = Einzelstern, kein Assistent.
#
# H1: Alle drei haben colonizable = yes und planet_size bis max. 25
#     (@habitable_planet_max_size bzw. max = 25 bei pc_nanotech).
#     Quelle: 00_planet_classes.txt, 02_planet_classes_megacorp.txt.
#     Nicht aufgenommen: Klassen mit fester Groesse (Ringwelt, Habitat,
#     pc_warden_guardian = 30 usw.), dort ist die Warnung sinnlos.
#
# O1: pc_o_star ist in keiner Vanilla-4.5-Datei definiert. Die Liste ist seit
#     V44 ohne Wirkung (isStarClass delegiert an die globale Funktion). Der
#     Wert bleibt stehen, weil Abwesenheit in Vanilla nicht Ungueltigkeit
#     bedeutet; er bekommt nur einen Vermerk.
#
# Der Export aendert sich nur in der Versionszeile des Kopfes. Der Rumpf muss
# bytegleich zu V51 bleiben, geprueft mit compare_exports.py.
#
# Usage: python3 patch_v51_to_v52.py <input.html> <output.html>

import sys

if len(sys.argv) != 3:
    sys.exit("usage: patch_v51_to_v52.py <input.html> <output.html>")

SRC, DST = sys.argv[1], sys.argv[2]

with open(SRC, encoding="utf-8") as fh:
    data = fh.read()

# ---------------------------------------------------------------- V1-V3
V1_OLD = "<title>Stellaris Solar System Editor V51 - Full Editor</title>"
V1_NEW = "<title>Stellaris Solar System Editor V52 - Full Editor</title>"

V2_OLD = '<h1 class="stellaris-header">Stellaris Solar System Editor V51</h1>'
V2_NEW = '<h1 class="stellaris-header">Stellaris Solar System Editor V52</h1>'

V3_OLD = "        const EDITOR_VERSION = 'V51';"
V3_NEW = "        const EDITOR_VERSION = 'V52';"

# ---------------------------------------------------------------- S1
S1_OLD = "\n".join([
    '                                <option value="sc_pulsar">Pulsar</option>',
    '                            </optgroup>',
    '                            <optgroup label="🌟 Binary Systems">',
])

S1_NEW = "\n".join([
    '                                <option value="sc_pulsar">Pulsar</option>',
    '                                <!-- V52: in 00_star_classes.txt (4.5.0) definiert, fehlten hier -->',
    '                                <option value="sc_m_giant">M-Giant (Red Giant)</option>',
    '                                <option value="sc_toxoid_star">Toxoid Star</option>',
    '                                <option value="sc_rift_star">Rift Star (Astral Planes DLC)</option>',
    '                            </optgroup>',
    '                            <optgroup label="🌟 Binary Systems">',
])

# ---------------------------------------------------------------- H1
H1_OLD = "\n".join([
    "            // Habitable classes above the usual vanilla size range (max. 25).",
    "            // Class list verified against 00_planet_classes.txt (+ pc_relic",
    "            // from 03_planet_classes_ancient_relics.txt).",
    "            const HABITABLE = ['pc_continental', 'pc_ocean', 'pc_desert', 'pc_tropical', 'pc_arid',",
    "                'pc_tundra', 'pc_arctic', 'pc_alpine', 'pc_savannah', 'pc_gaia', 'pc_nuked',",
    "                'pc_relic', 'pc_hive', 'pc_machine'];",
])

H1_NEW = "\n".join([
    "            // Habitable classes above the usual vanilla size range (max. 25).",
    "            // V52: re-checked against Stellaris 4.5.0. Every colonizable class",
    "            // with a size range up to 25: 00_planet_classes.txt, pc_city from",
    "            // 02_planet_classes_megacorp.txt, pc_relic from",
    "            // 03_planet_classes_ancient_relics.txt. Fixed-size classes",
    "            // (ringworld, habitat, pc_warden_guardian ...) are left out.",
    "            const HABITABLE = ['pc_continental', 'pc_ocean', 'pc_desert', 'pc_tropical', 'pc_arid',",
    "                'pc_tundra', 'pc_arctic', 'pc_alpine', 'pc_savannah', 'pc_gaia', 'pc_nuked',",
    "                'pc_relic', 'pc_hive', 'pc_machine', 'pc_volcanic', 'pc_nanotech', 'pc_city'];",
])

# ---------------------------------------------------------------- O1
O1_OLD = "\n".join([
    "                this.starClasses = [",
    "                    'pc_b_star', 'pc_a_star', 'pc_f_star', 'pc_g_star', ",
])

O1_NEW = "\n".join([
    "                // V52: pc_o_star is not defined in any vanilla 4.5.0 file. Kept",
    "                // as a mod value. The list itself has no effect since V44.",
    "                this.starClasses = [",
    "                    'pc_b_star', 'pc_a_star', 'pc_f_star', 'pc_g_star', ",
])

PATCHES = [
    ("V1  Titel auf V52",                  V1_OLD, V1_NEW, 1),
    ("V2  Ueberschrift auf V52",           V2_OLD, V2_NEW, 1),
    ("V3  Export-Kopfzeile auf V52",       V3_OLD, V3_NEW, 1),
    ("S1  Sternklassen-Dropdown",          S1_OLD, S1_NEW, 1),
    ("H1  HABITABLE-Liste",                H1_OLD, H1_NEW, 1),
    ("O1  pc_o_star als Mod-Wert",         O1_OLD, O1_NEW, 1),
]

for name, old, new, expected in PATCHES:
    found = data.count(old)
    assert found == expected, f"{name}: erwartet {expected} Fundstelle(n), gefunden {found}"
    assert data.count(new) == 0, f"{name}: Ersetzung liegt bereits vor, Abbruch"
    data = data.replace(old, new, expected)
    print(f"  ok  {name}")

# Kein sc_-Wert darf im Dropdown doppelt stehen.
import re
m = re.search(r'<select id="systemStarClass".*?</select>', data, re.S)
vals = re.findall(r'<option value="([^"]+)"', m.group(0))
dups = sorted({v for v in vals if vals.count(v) > 1})
assert not dups, f"doppelte Dropdown-Werte: {dups}"
print(f"  ok  Dropdown: {len(vals)} Eintraege, keine Dubletten")

with open(DST, "w", encoding="utf-8") as fh:
    fh.write(data)

print(f"geschrieben: {DST}")
