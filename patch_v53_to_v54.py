#!/usr/bin/env python3
# Patch: V53 -> V54  "Mehrfachsterne im Canvas und Systemklasse beim Import"
#
#  V1-V3  Versionsnummer auf V54
#  A      Parser: Systemklasse nur aus der Systemebene, mit oder ohne
#         Anfuehrungszeichen. Vorher griff die Suche nur class = "..." und
#         durchsuchte den ganzen Block. Vanilla sol_initializers.txt:
#         Alpha Centauri (class = sc_trinary_1) und Procyon (sc_binary_8)
#         kamen als sc_g an und wurden so auch wieder exportiert.
#  C1-C8  Canvas: eine Kette mit Vorzeichen fuer alle Koerper (dieselbe Summe
#         wie Export und Validierung), S-Type-Kinder von Sternen, feste
#         orbit_angle fuer Planeten, Farben fuer Red Giant und T-Star.
#
# Annahmen, im Code markiert:
#  - orbit_angle wird als absoluter Winkel gezeichnet (wie bisher bei Sternen).
#  - count > 1 schiebt den Zeiger im Canvas nicht mehrfach weiter (unveraendert).
#
# Export-Code ist nicht beruehrt. Aendern kann sich der Export nur ueber A:
# importierte Systeme tragen jetzt ihre echte Klasse.
#
# Usage: python3 patch_v53_to_v54.py <input.html> <output.html>

import sys

if len(sys.argv) != 3:
    sys.exit("usage: patch_v53_to_v54.py <input.html> <output.html>")

SRC, DST = sys.argv[1], sys.argv[2]
with open(SRC, encoding="utf-8") as fh:
    data = fh.read()

PATCHES = [
    ("V1  Titel auf V54",
     "<title>Stellaris Solar System Editor V53 - Full Editor</title>",
     "<title>Stellaris Solar System Editor V54 - Full Editor</title>", 1),
    ("V2  Ueberschrift auf V54",
     '<h1 class="stellaris-header">Stellaris Solar System Editor V53</h1>',
     '<h1 class="stellaris-header">Stellaris Solar System Editor V54</h1>', 1),
    ("V3  Export-Kopfzeile auf V54",
     "        const EDITOR_VERSION = 'V53';",
     "        const EDITOR_VERSION = 'V54';", 1),
    ('A   Parser: Systemklasse nur aus der Systemebene',
     '                const classMatch = blockContent.match(/class\\s*=\\s*"([^"]+)"/);\n                if (classMatch) {\n                    system.class = classMatch[1];\n                }',
     '                // V54 A: the system class is the depth-0 \'class\' key of the\n                // system block, quoted or not (vanilla writes class = sc_trinary_1\n                // without quotes). Planet and moon blocks are stripped first, and\n                // nested blocks like init_effect { create_species { class = ... } }\n                // are skipped by the depth counter, so no child class can leak in.\n                {\n                    const own = this.stripChildBodies(blockContent).replace(/#[^\\n]*/g, \'\');\n                    let depth = 0;\n                    for (let i = 0; i < own.length; i++) {\n                        const ch = own[i];\n                        if (ch === \'{\') { depth++; continue; }\n                        if (ch === \'}\') { depth--; continue; }\n                        if (depth === 0 && ch === \'c\' && !(i > 0 && /[A-Za-z0-9_]/.test(own[i - 1]))) {\n                            const m = own.slice(i).match(/^class\\s*=\\s*"?([A-Za-z0-9_]+)"?/);\n                            if (m) { system.class = m[1]; break; }\n                        }\n                    }\n                }', 1),
    ('C1  Canvas: gemeinsame Kette mit Vorzeichen',
     '            const actualPlanets = system.planets.filter(p => !isStarClass(p.class));\n            const starPlanets = system.planets.filter(p => isStarClass(p.class));',
     '            const actualPlanets = system.planets.filter(p => !isStarClass(p.class));\n            const starPlanets = system.planets.filter(p => isStarClass(p.class));\n\n            // V54 B: one signed orbit_distance chain over ALL bodies in list\n            // order, the same sum export and validation use. Negative values are\n            // vanilla-legal (Alpha Centauri B: -35) and put the body on the\n            // opposite side. Before V54 stars and planets had separate chains\n            // and negative steps were dropped.\n            const bodyPos = new Map();\n            let _chainPtr = 0;\n            system.planets.forEach(p => {\n                _chainPtr += Number.isFinite(p.orbitDistance) ? p.orbitDistance : 0;\n                bodyPos.set(p, _chainPtr);\n            });', 1),
    ('C2  Canvas: Sternposition aus der Kette',
     '                let cumulativeStarOrbit = 0;\n                // Calculate cumulative orbit for this star\n                const starIndex = system.planets.indexOf(starPlanet);\n                for (let i = 0; i <= starIndex; i++) {\n                    if (system.planets[i].orbitDistance > 0) {\n                        cumulativeStarOrbit += system.planets[i].orbitDistance;\n                    }\n                }\n                \n                const distance = cumulativeStarOrbit * canvasScale;',
     '                // V54 B: position from the shared signed chain\n                const distance = (bodyPos.get(starPlanet) || 0) * canvasScale;', 1),
    ('C3  Canvas: Farben Red Giant, T-Star',
     "                    'pc_pulsar': '#FF1493'\n                };\n                ",
     "                    'pc_pulsar': '#FF1493',\n                    'pc_m_giant_star': '#B22222',\n                    'pc_t_star': '#8B4513'\n                };\n                ", 1),
    ('C4  Canvas: S-Type-Kinder von Sternen',
     '                    ctx.fillText(starPlanet.displayName, x, y - radius - 8);\n                }\n            });',
     '                    ctx.fillText(starPlanet.displayName, x, y - radius - 8);\n                }\n\n                // V54 C: S-type bodies nested in a star block (Proxima b and c)\n                drawBodyChildren(starPlanet, bodyPos.get(starPlanet) || 0, angle);\n            });', 1),
    ('C5  Canvas: Planeten auf der gemeinsamen Kette',
     '            // ✅ CUMULATIVE orbit calculation for REAL planets with orbit_distance = 0 support\n            let cumulativePlanetOrbit = 0;\n            let sharedOrbitGroup = []; // group of planets on the same orbit\n            let globalPlanetAngleIndex = 0; // ✅ global angle counter for visual distribution\n            \n            actualPlanets.forEach((planet, index) => {\n                // Compute cumulative orbit position\n                if (planet.orbitDistance > 0) {\n                    // Draw previous group with orbit_distance = 0\n                    if (sharedOrbitGroup.length > 0) {\n                        drawPlanetsAndMoons(sharedOrbitGroup, cumulativePlanetOrbit, globalPlanetAngleIndex);\n                        globalPlanetAngleIndex += sharedOrbitGroup.length; // increment counter\n                        sharedOrbitGroup = [];\n                    }\n                    \n                    cumulativePlanetOrbit += planet.orbitDistance;\n                    drawOrbit(cumulativePlanetOrbit);\n                }\n                \n                // First planet with orbit_distance = 0\n                if (index === 0 && planet.orbitDistance === 0) {\n                    cumulativePlanetOrbit = 30;\n                    drawOrbit(cumulativePlanetOrbit);\n                }\n                \n                // Add planet to the current orbit group\n                sharedOrbitGroup.push({\n                    planet: planet,\n                    orbitDistance: cumulativePlanetOrbit\n                });\n            });\n            \n            // Draw last group\n            if (sharedOrbitGroup.length > 0) {\n                drawPlanetsAndMoons(sharedOrbitGroup, cumulativePlanetOrbit, globalPlanetAngleIndex);\n            }',
     '            // V54 B: planets sit on the shared signed chain (bodyPos). Bodies\n            // on the same position as the previous planet share its orbit and\n            // are drawn as one group, as before.\n            let sharedOrbitGroup = []; // group of planets on the same orbit\n            let sharedOrbitPos = 0;\n            let globalPlanetAngleIndex = 0; // global angle counter for visual distribution\n\n            actualPlanets.forEach((planet, index) => {\n                let pos = bodyPos.get(planet) || 0;\n                // Kept display rule: a first body with orbit_distance = 0 on\n                // position 0 is drawn on orbit 30 instead of inside the star.\n                if (index === 0 && planet.orbitDistance === 0 && pos === 0) pos = 30;\n                if (index === 0 || pos !== sharedOrbitPos) {\n                    if (sharedOrbitGroup.length > 0) {\n                        drawPlanetsAndMoons(sharedOrbitGroup, sharedOrbitPos, globalPlanetAngleIndex);\n                        globalPlanetAngleIndex += sharedOrbitGroup.length;\n                        sharedOrbitGroup = [];\n                    }\n                    sharedOrbitPos = pos;\n                    drawOrbit(Math.abs(pos)); // arc() rejects negative radii\n                }\n                sharedOrbitGroup.push({ planet: planet, orbitDistance: sharedOrbitPos });\n            });\n\n            // Draw last group\n            if (sharedOrbitGroup.length > 0) {\n                drawPlanetsAndMoons(sharedOrbitGroup, sharedOrbitPos, globalPlanetAngleIndex);\n            }', 1),
    ('C6  Canvas: feste orbit_angle fuer Planeten',
     '                const angleIndex = useGlobalDistribution ? startAngleIndex : index;\n                const planetAngle = (angleIndex * angleStep) * Math.PI / 180;',
     "                const angleIndex = useGlobalDistribution ? startAngleIndex : index;\n                // V54 D: a fixed orbit_angle wins for a single instance. ASSUMPTION:\n                // read as absolute angle, as the editor already does for stars.\n                // Whether Stellaris reads it relative to the previous body is not\n                // verified. Ranges and count > 1 keep the even distribution.\n                const _fixedAngle = planet.orbitAngleType === 'fixed' && Number.isFinite(planet.orbitAngle)\n                    && clampCount(planet.countMax ?? planet.countMin ?? 1) <= 1;\n                const planetAngle = (_fixedAngle ? planet.orbitAngle : angleIndex * angleStep) * Math.PI / 180;", 1),
    ('C7  Canvas: Mondblock ausgelagert',
     '                // ✅ Draw moons around this planet\n                if (planet.moons && planet.moons.length > 0) {\n                    const planetDistance = orbitDistance * canvasScale;\n                    const planetX = canvasOffsetX + Math.cos(planetAngle) * planetDistance;\n                    const planetY = canvasOffsetY + Math.sin(planetAngle) * planetDistance;\n                    \n                    let cumulativeMoonOrbit = 0;\n                    let sharedMoonGroup = [];\n                    \n                    planet.moons.forEach((moon, moonIndex) => {\n                        if (moon.orbitDistance > 0) {\n                            // Draw previous moon group\n                            if (sharedMoonGroup.length > 0) {\n                                drawMoonGroup(sharedMoonGroup, planetX, planetY, cumulativeMoonOrbit);\n                                sharedMoonGroup = [];\n                            }\n                            \n                            cumulativeMoonOrbit += moon.orbitDistance;\n                            drawMoonOrbit(orbitDistance, planetAngle, cumulativeMoonOrbit);\n                        }\n                        \n                        if (moonIndex === 0 && moon.orbitDistance === 0) {\n                            cumulativeMoonOrbit = 10;\n                            drawMoonOrbit(orbitDistance, planetAngle, cumulativeMoonOrbit);\n                        }\n                        \n                        sharedMoonGroup.push(moon);\n                    });\n                    \n                    // Draw last moon group\n                    if (sharedMoonGroup.length > 0) {\n                        drawMoonGroup(sharedMoonGroup, planetX, planetY, cumulativeMoonOrbit);\n                    }\n                }\n            });',
     '                // V54 C: children drawing moved to drawBodyChildren (shared with stars)\n                drawBodyChildren(planet, orbitDistance, planetAngle);\n            });', 1),
    ('C8  Canvas: drawBodyChildren',
     '        // ✅ NEW: Draw moon group around planet',
     '        // V54 C: draw the nested bodies (moon = {} and S-type planet = {})\n        // of a planet or a star around that parent. Body of the former\n        // moon block in drawPlanetsAndMoons, unchanged.\n        function drawBodyChildren(planet, orbitDistance, planetAngle) {\n        if (planet.moons && planet.moons.length > 0) {\n            const planetDistance = orbitDistance * canvasScale;\n            const planetX = canvasOffsetX + Math.cos(planetAngle) * planetDistance;\n            const planetY = canvasOffsetY + Math.sin(planetAngle) * planetDistance;\n            \n            let cumulativeMoonOrbit = 0;\n            let sharedMoonGroup = [];\n            \n            planet.moons.forEach((moon, moonIndex) => {\n                if (moon.orbitDistance > 0) {\n                    // Draw previous moon group\n                    if (sharedMoonGroup.length > 0) {\n                        drawMoonGroup(sharedMoonGroup, planetX, planetY, cumulativeMoonOrbit);\n                        sharedMoonGroup = [];\n                    }\n                    \n                    cumulativeMoonOrbit += moon.orbitDistance;\n                    drawMoonOrbit(orbitDistance, planetAngle, cumulativeMoonOrbit);\n                }\n                \n                if (moonIndex === 0 && moon.orbitDistance === 0) {\n                    cumulativeMoonOrbit = 10;\n                    drawMoonOrbit(orbitDistance, planetAngle, cumulativeMoonOrbit);\n                }\n                \n                sharedMoonGroup.push(moon);\n            });\n            \n            // Draw last moon group\n            if (sharedMoonGroup.length > 0) {\n                drawMoonGroup(sharedMoonGroup, planetX, planetY, cumulativeMoonOrbit);\n            }\n        }\n        }\n\n        // ✅ NEW: Draw moon group around planet', 1),
]

for name, old, new, expected in PATCHES:
    found = data.count(old)
    assert found == expected, f"{name}: erwartet {expected} Fundstelle(n), gefunden {found}"
    assert data.count(new) == 0, f"{name}: Ersetzung liegt bereits vor, Abbruch"
    data = data.replace(old, new, expected)
    print(f"  ok  {name}")

# Nachkontrollen: alte Ketten sind weg, neue Funktion genau einmal definiert.
for gone in ("cumulativeStarOrbit", "cumulativePlanetOrbit", 'blockContent.match(/class\\s*=\\s*"'):
    assert gone not in data, f"Rest gefunden: {gone}"
assert data.count("function drawBodyChildren(") == 1
assert data.count("drawBodyChildren(") == 3
print("  ok  Nachkontrollen")

with open(DST, "w", encoding="utf-8") as fh:
    fh.write(data)
print(f"geschrieben: {DST}")
