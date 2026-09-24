#!/usr/bin/env python3
# Patch: V54 -> V55  "count in der Orbit-Kette"
#
# Befund (im Spiel belegt, Screenshot Alpha Centauri 2026-09-24):
# count = 2 mit orbit_distance = 25 erzeugt zwei Koerper, der erste auf +25,
# der zweite auf +50. Der Editor zaehlte jeden Block nur einmal.
# Zweiter Befund: der Import schnitt count hart auf 1..3 zu. Vanilla 4.5.0
# nutzt 0 bis 10 auf Planeten- und Mondbloecken (min = 0 in 333 Bloecken).
#
#  V1-V3  Versionsnummer auf V55
#  K1     clampCount 0..99, neue Funktion bodyChain (Kette mit count)
#  K2     Export schreibt count = 0 wieder
#  K3-K6  change_orbit vor count-Bloecken als preShift (Import, Formular,
#         Guertel-Asteroid); Export schreibt es als change_orbit zurueck
#  E1-E3  Export: Kette mit count; change_orbit statt verfaelschtem Abstand,
#         wenn ein Koerper mit count > 1 durch das Vorziehen der Sterne rutscht
#  P1-P2  Validierung: Kette mit count, count > 10, Stern hinter Zufalls-count
#  L1-L3  Liste: Position aus der Kette, count als "x2" bzw. "x2-5"
#  F1-F3  Formulare: 0..99
#  C1-C5  Canvas: Kette mit count (max), jede Kopie auf eigener Bahn,
#         Winkel gegen den Uhrzeigersinn (Proxima 130 Grad oben links)
#
# Varianten-Entscheidung (a): Canvas rechnet mit max, Validierung und Export
# mit min.
# Offen und nicht angefasst: change_orbit innerhalb eines Planetenblocks.
#
# Usage: python3 patch_v54_to_v55.py <input.html> <output.html>

import sys

if len(sys.argv) != 3:
    sys.exit("usage: patch_v54_to_v55.py <input.html> <output.html>")

SRC, DST = sys.argv[1], sys.argv[2]
with open(SRC, encoding="utf-8") as fh:
    data = fh.read()

PATCHES = [
    ('V1  Titel auf V55',
     '<title>Stellaris Solar System Editor V54 - Full Editor</title>',
     '<title>Stellaris Solar System Editor V55 - Full Editor</title>', 1),
    ('V2  Ueberschrift auf V55',
     '<h1 class="stellaris-header">Stellaris Solar System Editor V54</h1>',
     '<h1 class="stellaris-header">Stellaris Solar System Editor V55</h1>', 1),
    ('V3  Export-Kopfzeile auf V55',
     "        const EDITOR_VERSION = 'V54';",
     "        const EDITOR_VERSION = 'V55';", 1),
    ('K1  clampCount 0..99 und bodyChain',
     '        function clampCount(v) {\n            const n = parseInt(v);\n            if (!Number.isFinite(n)) return 1;\n            return Math.min(3, Math.max(1, n));\n        }',
     "        // V55: count range 0..99. Vanilla 4.5.0 planet and moon blocks use 0\n        // (count = { min = 0 ... }, 333 blocks) up to 10. The old cap [1,3]\n        // rewrote those values on import. 99 is a sanity bound for mods, not a\n        // vanilla rule; validation flags values above 10.\n        function clampCount(v) {\n            const n = parseInt(v);\n            if (!Number.isFinite(n)) return 1;\n            return Math.min(99, Math.max(0, n));\n        }\n\n        // V55: top-level orbit chain with count. Verified in game (Alpha\n        // Centauri, screenshot 2026-09-24): count = 2 with orbit_distance = 25\n        // places two bodies, the first at +25 and the second at +50. Copy k\n        // sits at pointer + orbit_distance * k, afterwards the pointer has moved\n        // by orbit_distance * count. mode picks the count of count = { min max }:\n        // 'max' for the canvas, 'min' for validation and export.\n        // ASSUMPTION: count = 0 leaves the pointer where it was.\n        function bodyChain(bodies, mode) {\n            const first = new Map(), copies = new Map();\n            let ptr = 0;\n            bodies.forEach(p => {\n                // preShift: top-level change_orbit in front of a count block\n                // (kept separate by the importer, see parsePlanets)\n                if (Number.isFinite(p.preShift)) ptr += p.preShift;\n                const od = Number.isFinite(p.orbitDistance) ? p.orbitDistance : 0;\n                const n = clampCount(mode === 'max' ? (p.countMax ?? p.countMin ?? 1) : (p.countMin ?? 1));\n                first.set(p, ptr + od);\n                const list = [];\n                for (let k = 1; k <= n; k++) list.push(ptr + od * k);\n                copies.set(p, list);\n                ptr += od * n;\n            });\n            return { first, copies, end: ptr };\n        }\n", 1),
    ('K2  Export: count = 0 bleibt erhalten',
     '            if (_cMin === _cMax) {\n                if (_cMin > 1) code += `${tab}\\tcount = ${_cMin}\\n`;',
     '            if (_cMin === _cMax) {\n                // V55: every value except the default 1, including count = 0\n                if (_cMin !== 1) code += `${tab}\\tcount = ${_cMin}\\n`;', 1),
    ('E1  Export: Kette mit count',
     '            const _absPos = new Map();\n            let _ptr = 0;\n            system.planets.forEach(p => { _ptr += (p.orbitDistance || 0); _absPos.set(p, _ptr); });\n            let _expPtr = 0;\n            const _expDelta = new Map();\n            [...starPlanets, ...regularPlanets].forEach(p => {\n                _expDelta.set(p, _absPos.get(p) - _expPtr);\n                _expPtr = _absPos.get(p);\n            });',
     "            // V55: positions from bodyChain (count-aware, min mode). A body whose\n            // export predecessor differs from its list predecessor keeps the V45\n            // delta form when count = 1 (output unchanged). With count > 1 or a\n            // count range the delta would become the spacing of every copy, so\n            // the shift goes into a top-level change_orbit (vanilla syntax, the\n            // importer folds it) and orbit_distance stays the body's own value.\n            const _chain = bodyChain(system.planets, 'min');\n            let _expPtr = 0;\n            const _expDelta = new Map();\n            const _expShift = new Map();\n            [...starPlanets, ...regularPlanets].forEach(p => {\n                const od = Number.isFinite(p.orbitDistance) ? p.orbitDistance : 0;\n                const first = _chain.first.get(p);\n                const shift = Math.round(((first - od) - _expPtr) * 1000) / 1000;\n                // orbit_distance ranges are written verbatim, so they need the\n                // change_orbit form as well\n                const single = clampCount(p.countMin ?? 1) === 1 && clampCount(p.countMax ?? 1) === 1 && p.odType !== 'range';\n                if (shift === 0 || single) {\n                    _expDelta.set(p, first - _expPtr);\n                } else {\n                    _expShift.set(p, shift);\n                    _expDelta.set(p, od);\n                }\n                _expPtr = (first - od) + od * clampCount(p.countMin ?? 1);\n            });", 1),
    ('E2  Export: change_orbit vor Sternen',
     "                starPlanets.forEach(starPlanet => {\n                    code += generatePlanetCode(starPlanet, 1, 'planet', _expDelta.get(starPlanet));",
     "                starPlanets.forEach(starPlanet => {\n                    if (_expShift.has(starPlanet)) code += `\\n\\tchange_orbit = ${_expShift.get(starPlanet)}\\n`;\n                    code += generatePlanetCode(starPlanet, 1, 'planet', _expDelta.get(starPlanet));", 1),
    ('E3  Export: change_orbit vor Planeten',
     "            regularPlanets.forEach(planet => {\n                code += generatePlanetCode(planet, 1, 'planet', _expDelta.get(planet));",
     "            regularPlanets.forEach(planet => {\n                // V55: shift for count > 1 bodies moved by the star reordering\n                if (_expShift.has(planet)) code += `\\n\\tchange_orbit = ${_expShift.get(planet)}\\n`;\n                code += generatePlanetCode(planet, 1, 'planet', _expDelta.get(planet));", 1),
    ('K3  Import: change_orbit vor count-Block getrennt halten',
     '                        if (pendingChangeOrbit !== 0) {\n                            planet.orbitDistance += pendingChangeOrbit;\n                            pendingChangeOrbit = 0;\n                        }',
     "                        if (pendingChangeOrbit !== 0) {\n                            // V55: folding into orbit_distance is only exact for\n                            // count = 1. In a count block orbit_distance is the\n                            // spacing of every copy (vanilla Alpha Centauri:\n                            // change_orbit = -220, then count = 2 / orbit 25 gives\n                            // 45 and 70). There the shift stays separate as\n                            // preShift and is written back as change_orbit.\n                            // Same for orbit_distance = { min max }: the export writes the\n                            // range verbatim, a folded shift would be lost there.\n                            if (clampCount(planet.countMin ?? 1) === 1 && clampCount(planet.countMax ?? 1) === 1 && planet.odType !== 'range') {\n                                planet.orbitDistance += pendingChangeOrbit;\n                            } else {\n                                planet.preShift = pendingChangeOrbit;\n                            }\n                            pendingChangeOrbit = 0;\n                        }", 1),
    ('K4  Formular: preShift beim Speichern behalten',
     '                planetData.entity = existingPlanet.entity || null;',
     '                planetData.entity = existingPlanet.entity || null;\n                // V55: change_orbit in front of a count block survives editing\n                if (Number.isFinite(existingPlanet.preShift)) planetData.preShift = existingPlanet.preShift;', 1),
    ('K5  Guertel-Asteroid: Einfuegestelle aus der Kette',
     '            // Insertion point: after the last body at position <= belt radius\n            let cumulative = 0;\n            let insertAt = 0;\n            let prevCumulative = 0;\n            for (let k = 0; k < planets.length; k++) {\n                cumulative += planets[k].orbitDistance;\n                if (cumulative <= belt.radius) {\n                    insertAt = k + 1;\n                    prevCumulative = cumulative;\n                }\n            }',
     "            // Insertion point: after the last body whose chain pointer ends at\n            // or before the belt radius. V55: pointer after a body includes its\n            // count copies and preShift (bodyChain, min mode).\n            const _bChain = bodyChain(planets, 'min');\n            let insertAt = 0;\n            let prevCumulative = 0;\n            for (let k = 0; k < planets.length; k++) {\n                const pk = planets[k];\n                const odk = Number.isFinite(pk.orbitDistance) ? pk.orbitDistance : 0;\n                const endK = _bChain.first.get(pk) - odk + odk * clampCount(pk.countMin ?? 1);\n                if (endK <= belt.radius) {\n                    insertAt = k + 1;\n                    prevCumulative = endK;\n                }\n            }", 1),
    ('K6  Guertel-Asteroid: Ausgleich ohne Abstandsaenderung bei count',
     '            if (delta !== 0 && insertAt + 1 < planets.length) {\n                planets[insertAt + 1].orbitDistance -= delta;\n            }',
     "            if (delta !== 0 && insertAt + 1 < planets.length) {\n                const nx = planets[insertAt + 1];\n                // V55: a count block keeps its spacing, the shift goes to preShift\n                if (clampCount(nx.countMin ?? 1) === 1 && clampCount(nx.countMax ?? 1) === 1 && nx.odType !== 'range') {\n                    nx.orbitDistance -= delta;\n                } else {\n                    nx.preShift = (Number.isFinite(nx.preShift) ? nx.preShift : 0) - delta;\n                }\n            }", 1),
    ('P1  Validierung: Kette mit count',
     '            // Absolute top-level positions (cumulative chain in list order)\n            let ptr = 0;\n            const abs = [];\n            system.planets.forEach(p => { ptr += (p.orbitDistance || 0); abs.push({ p, pos: ptr }); });',
     '            // Absolute top-level positions, one entry per copy. V55: count-aware\n            // chain in min mode (the bodies that always exist).\n            const abs = [];\n            const _vChain = bodyChain(system.planets, \'min\');\n            system.planets.forEach(p => _vChain.copies.get(p).forEach(pos => abs.push({ p, pos })));\n\n            // V55: count above the vanilla maximum (10 on planet and moon blocks, 4.5.0)\n            const _countIssue = (b, what) => {\n                const mx = clampCount(b.countMax ?? b.countMin ?? 1);\n                if (mx > 10) issues.push(`${what} "${b.name || b.displayName || \'?\'}" has count ${mx} - above the vanilla maximum of 10`);\n            };\n            system.planets.forEach(p => { _countIssue(p, \'Body\'); (p.moons || []).forEach(m => _countIssue(m, \'Moon\')); });\n\n            // V55: the export moves stars to the front. A star listed after a body\n            // with a random count depends on the rolled count in game; the export\n            // places it for the minimum count.\n            let _randomBefore = null;\n            system.planets.forEach(p => {\n                if (isStarClass(p.class)) {\n                    if (_randomBefore) issues.push(`Star "${p.name || p.displayName || \'?\'}" is listed after "${_randomBefore}" (random count) - the export places it for the minimum count; move the star above it for an exact position`);\n                } else if (clampCount(p.countMin ?? 1) !== clampCount(p.countMax ?? 1) && (p.orbitDistance || 0) !== 0) {\n                    _randomBefore = p.name || p.displayName || \'?\';\n                }\n            });', 1),
    ('P2  Validierung: doppelte Meldungen je Kopie zusammenfassen',
     '            return issues;',
     '            // V55: one line per finding, even when several copies trigger it\n            return [...new Set(issues)];', 1),
    ('L1  Liste: Position aus der Kette',
     "            \n            // Compute cumulative positions for planets\n            let cumulativeOrbit = 0;\n            planets.forEach((planet, index) => {\n                cumulativeOrbit += planet.orbitDistance;\n                combined.push({\n                    type: 'planet',\n                    data: planet,\n                    index: index,\n                    orbit: cumulativeOrbit,  // Kumulative Position\n                    displayOrbit: planet.orbitDistance  // original for display\n                });\n            });",
     "            // V55: positions from the count-aware chain (first copy). With a\n            // count range the label shows min and max position.\n            const _lMin = bodyChain(planets, 'min');\n            const _lMax = bodyChain(planets, 'max');\n            planets.forEach((planet, index) => {\n                const _pMin = _lMin.first.get(planet), _pMax = _lMax.first.get(planet);\n                combined.push({\n                    type: 'planet',\n                    data: planet,\n                    index: index,\n                    orbit: _pMin,  // Kumulative Position\n                    orbitLabel: _pMin === _pMax ? `${_pMin}` : `${_pMin}\\u2013${_pMax}`,\n                    displayOrbit: planet.orbitDistance  // original for display\n                });\n            });", 1),
    ('L2  Liste: count sichtbar (Koerper)',
     'Size ${planet.size} • Orbit +${item.displayOrbit} (Position: ${item.orbit})</div>',
     "Size ${planet.size}${(() => { const _a = clampCount(planet.countMin ?? 1), _b = clampCount(planet.countMax ?? 1); return (_a === 1 && _b === 1) ? '' : ' \\u2022 \\u00d7' + (_a === _b ? _a : _a + '\\u2013' + _b); })()}${Number.isFinite(planet.preShift) ? ' \\u2022 change_orbit ' + planet.preShift : ''} • Orbit +${item.displayOrbit} (Position: ${item.orbitLabel ?? item.orbit})</div>", 1),
    ('L3  Liste: count sichtbar (Monde)',
     'Size ${moon.size}, Orbit ${moon.orbitDistance})${startingIcon}</span>',
     "Size ${moon.size}, Orbit ${moon.orbitDistance}${(() => { const _a = clampCount(moon.countMin ?? 1), _b = clampCount(moon.countMax ?? 1); return (_a === 1 && _b === 1) ? '' : ' \\u2022 \\u00d7' + (_a === _b ? _a : _a + '\\u2013' + _b); })()})${startingIcon}</span>", 1),
    ('F1  Formular Planet: Beschriftung',
     'Anzahl / count – Doppelplanet (max 3)',
     'Anzahl / count – Planet (0–99, Vanilla max. 10)', 1),
    ('F2  Formular Mond: Beschriftung',
     'Anzahl / count – Doppelmond (max 3)',
     'Anzahl / count – Mond (0–99, Vanilla max. 10)', 1),
    ('F3  Formular planetCountMin: min 0 max 99',
     '<input type="number" id="planetCountMin" class="stellaris-input" value="1" min="1" max="3">',
     '<input type="number" id="planetCountMin" class="stellaris-input" value="1" min="0" max="99">', 1),
    ('F3  Formular planetCountMax: min 0 max 99',
     '<input type="number" id="planetCountMax" class="stellaris-input" value="1" min="1" max="3">',
     '<input type="number" id="planetCountMax" class="stellaris-input" value="1" min="0" max="99">', 1),
    ('F3  Formular moonCountMin: min 0 max 99',
     '<input type="number" id="moonCountMin" class="stellaris-input" value="1" min="1" max="3">',
     '<input type="number" id="moonCountMin" class="stellaris-input" value="1" min="0" max="99">', 1),
    ('F3  Formular moonCountMax: min 0 max 99',
     '<input type="number" id="moonCountMax" class="stellaris-input" value="1" min="1" max="3">',
     '<input type="number" id="moonCountMax" class="stellaris-input" value="1" min="0" max="99">', 1),
    ('C1  Canvas: Kette mit count (max)',
     '            // V54 B: one signed orbit_distance chain over ALL bodies in list\n            // order, the same sum export and validation use. Negative values are\n            // vanilla-legal (Alpha Centauri B: -35) and put the body on the\n            // opposite side. Before V54 stars and planets had separate chains\n            // and negative steps were dropped.\n            const bodyPos = new Map();\n            let _chainPtr = 0;\n            system.planets.forEach(p => {\n                _chainPtr += Number.isFinite(p.orbitDistance) ? p.orbitDistance : 0;\n                bodyPos.set(p, _chainPtr);\n            });\n            ',
     "            // V55: count-aware chain (bodyChain, max mode: the canvas shows the\n            // largest possible layout). Negative steps stay legal (Alpha Centauri\n            // B: -35) and put the body on the opposite side.\n            const _cChain = bodyChain(system.planets, 'max');\n            const bodyPos = _cChain.first;", 1),
    ('C2  Canvas: Sternwinkel gegen den Uhrzeigersinn',
     '                const angle = _starAngleDeg * Math.PI / 180;',
     '                // V55: counter-clockwise, y up. Observed in game: Proxima Centauri\n                // with orbit_angle = 130 sits upper left (screenshot 2026-09-24).\n                const angle = -_starAngleDeg * Math.PI / 180;', 1),
    ('C3  Canvas: jede Kopie auf eigener Position',
     '            // V54 B: planets sit on the shared signed chain (bodyPos). Bodies\n            // on the same position as the previous planet share its orbit and\n            // are drawn as one group, as before.\n            let sharedOrbitGroup = []; // group of planets on the same orbit\n            let sharedOrbitPos = 0;\n            let globalPlanetAngleIndex = 0; // global angle counter for visual distribution\n\n            actualPlanets.forEach((planet, index) => {\n                let pos = bodyPos.get(planet) || 0;\n                // Kept display rule: a first body with orbit_distance = 0 on\n                // position 0 is drawn on orbit 30 instead of inside the star.\n                if (index === 0 && planet.orbitDistance === 0 && pos === 0) pos = 30;\n                if (index === 0 || pos !== sharedOrbitPos) {\n                    if (sharedOrbitGroup.length > 0) {\n                        drawPlanetsAndMoons(sharedOrbitGroup, sharedOrbitPos, globalPlanetAngleIndex);\n                        globalPlanetAngleIndex += sharedOrbitGroup.length;\n                        sharedOrbitGroup = [];\n                    }\n                    sharedOrbitPos = pos;\n                    drawOrbit(Math.abs(pos)); // arc() rejects negative radii\n                }\n                sharedOrbitGroup.push({ planet: planet, orbitDistance: sharedOrbitPos });\n            });\n\n            // Draw last group\n            if (sharedOrbitGroup.length > 0) {\n                drawPlanetsAndMoons(sharedOrbitGroup, sharedOrbitPos, globalPlanetAngleIndex);\n            }',
     '            // V55: every copy of a count block gets its own position from the\n            // chain (max mode). Copies on one position (orbit_distance = 0) and\n            // consecutive bodies on the same position share one orbit.\n            let sharedOrbitGroup = []; // group of planets on the same orbit\n            let sharedOrbitPos = null;\n            let globalPlanetAngleIndex = 0; // global angle counter for visual distribution\n\n            actualPlanets.forEach((planet, index) => {\n                let positions = _cChain.copies.get(planet) || [];\n                // Kept display rule: a first body with orbit_distance = 0 on\n                // position 0 is drawn on orbit 30 instead of inside the star.\n                if (index === 0 && planet.orbitDistance === 0) positions = positions.map(q => q === 0 ? 30 : q);\n                positions.forEach(pos => {\n                    if (sharedOrbitPos === null || pos !== sharedOrbitPos) {\n                        if (sharedOrbitGroup.length > 0) {\n                            drawPlanetsAndMoons(sharedOrbitGroup, sharedOrbitPos, globalPlanetAngleIndex);\n                            globalPlanetAngleIndex += sharedOrbitGroup.length;\n                            sharedOrbitGroup = [];\n                        }\n                        sharedOrbitPos = pos;\n                        drawOrbit(Math.abs(pos)); // arc() rejects negative radii\n                    }\n                    const last = sharedOrbitGroup[sharedOrbitGroup.length - 1];\n                    if (last && last.planet === planet) last.copies++;\n                    else sharedOrbitGroup.push({ planet: planet, orbitDistance: pos, copies: 1 });\n                });\n            });\n\n            // Draw last group\n            if (sharedOrbitGroup.length > 0) {\n                drawPlanetsAndMoons(sharedOrbitGroup, sharedOrbitPos, globalPlanetAngleIndex);\n            }', 1),
    ('C4  Canvas: Kopien aus der Kette statt Auffaechern',
     '            const planetInstances = [];\n            planetGroup.forEach(item => {\n                const cnt = Math.max(1, clampCount(item.planet.countMax ?? item.planet.countMin ?? 1));\n                for (let k = 0; k < cnt; k++) planetInstances.push(item.planet);\n            });',
     '            const planetInstances = [];\n            planetGroup.forEach(item => {\n                // V55: copies come from the chain; fallback for other callers\n                const cnt = item.copies ?? Math.max(1, clampCount(item.planet.countMax ?? item.planet.countMin ?? 1));\n                for (let k = 0; k < cnt; k++) planetInstances.push({ planet: item.planet, single: cnt === 1 });\n            });', 1),
    ('C5  Canvas: fester Winkel je Kopie, gegen den Uhrzeigersinn',
     "            planetInstances.forEach((planet, index) => {\n                const angleIndex = useGlobalDistribution ? startAngleIndex : index;\n                // V54 D: a fixed orbit_angle wins for a single instance. ASSUMPTION:\n                // read as absolute angle, as the editor already does for stars.\n                // Whether Stellaris reads it relative to the previous body is not\n                // verified. Ranges and count > 1 keep the even distribution.\n                const _fixedAngle = planet.orbitAngleType === 'fixed' && Number.isFinite(planet.orbitAngle)\n                    && clampCount(planet.countMax ?? planet.countMin ?? 1) <= 1;\n                const planetAngle = (_fixedAngle ? planet.orbitAngle : angleIndex * angleStep) * Math.PI / 180;",
     "            planetInstances.forEach((inst, index) => {\n                const planet = inst.planet;\n                const angleIndex = useGlobalDistribution ? startAngleIndex : index;\n                // V54 D / V55: a fixed orbit_angle wins when the body has one copy\n                // on this orbit. ASSUMPTION: absolute angle (relative reading not\n                // verified). V55: counter-clockwise, as observed in game.\n                const _fixedAngle = planet.orbitAngleType === 'fixed' && Number.isFinite(planet.orbitAngle) && inst.single;\n                const planetAngle = (_fixedAngle ? -planet.orbitAngle : angleIndex * angleStep) * Math.PI / 180;", 1),
]

for name, old, new, expected in PATCHES:
    found = data.count(old)
    assert found == expected, f"{name}: erwartet {expected} Fundstelle(n), gefunden {found}"
    assert data.count(new) == 0, f"{name}: Ersetzung liegt bereits vor, Abbruch"
    data = data.replace(old, new, expected)
    print(f"  ok  {name}")

for gone in ("Math.min(3, Math.max(1, n))", "_absPos", "_chainPtr", 'max="3"', "(max 3)"):
    assert gone not in data, f"Rest gefunden: {gone}"
assert data.count("function bodyChain(") == 1
print("  ok  Nachkontrollen")

with open(DST, "w", encoding="utf-8") as fh:
    fh.write(data)
print(f"geschrieben: {DST}")
