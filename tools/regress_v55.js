// Regressionstest V54 -> V55 ueber alle Vanilla-Initializer.
// Usage: node regress_v55.js <v54_script.js> <v55_script.js> <initializer-ordner> <counts.tsv>
// counts.tsv: unabhaengig (Python) ermittelte count-Werte je System.
const fs = require('fs'), path = require('path'), load = require('./fullload.js');
const [, , f54, f55, dir, countsFile] = process.argv;
const A = load(f54), B = load(f55);
const expectCounts = new Map();
for (const line of fs.readFileSync(countsFile, 'utf8').trim().split('\n')) {
  const [file, sys, list] = line.split('\t'); expectCounts.set(file + '|' + sys, list || '');
}
const walk = (bodies, out) => bodies.forEach(b => { out.push(`${b.countMin ?? 1}-${b.countMax ?? 1}`); walk(b.moons || [], out); });
let nSys = 0, countBad = 0, rtBad = 0, diffSys = 0; const diffKinds = new Map(); const other = [];
for (const f of fs.readdirSync(dir).filter(x => x.endsWith('.txt')).sort()) {
  const txt = fs.readFileSync(path.join(dir, f), 'utf8');
  const sa = new A.MultiSystemParser().parseMultipleSystems(txt);
  const sb = new B.MultiSystemParser().parseMultipleSystems(txt);
  sb.forEach((s, i) => {
    nSys++;
    // 1) count gegen Spieldatei
    const got = []; walk(s.planets, got); got.sort();
    const exp = (expectCounts.get(f + '|' + s.name) || '').split(',').filter(Boolean).sort();
    if (got.join(',') !== exp.join(',')) { countBad++; { const g = [...got], e = [...exp]; got.forEach(v => { const k = e.indexOf(v); if (k >= 0) e.splice(k, 1); }); exp.forEach(v => { const k = g.indexOf(v); if (k >= 0) g.splice(k, 1); }); console.log(`COUNT ${f} ${s.name}: nur Editor [${g}] nur Datei [${e}]`); } }
    // 2) Export-Diff V54 -> V55
    const ea = A.generateSystemCode(sa[i]).split('\n'), eb = B.generateSystemCode(s).split('\n');
    if (ea.join('\n') !== eb.join('\n')) {
      diffSys++;
      const ra = new Map(); ea.forEach(l => ra.set(l, (ra.get(l) || 0) + 1));
      eb.forEach(l => { if (ra.get(l)) ra.set(l, ra.get(l) - 1); else { if (!l.trim()) return; const k = (l.trim().match(/^[a-z_]+/) || ['?'])[0] + ' (neu)'; diffKinds.set(k, (diffKinds.get(k) || 0) + 1); if (l.trim() && !/^(count|change_orbit|orbit_distance)\b/.test(l.trim())) other.push(`${f} ${s.name}: + ${l.trim()}`); } });
      ra.forEach((n, l) => { if (n > 0) { const k = (l.trim().match(/^[a-z_]+/) || ['?'])[0] + ' (weg)'; diffKinds.set(k, (diffKinds.get(k) || 0) + n); if (!/^(count|change_orbit|orbit_distance)\b/.test(l.trim())) other.push(`${f} ${s.name}: - ${l.trim()}`); } });
    }
    // 3a) Round-Trip der Klassen in V54 (Vergleich: war es vorher schon so?)
    const ra54 = new A.MultiSystemParser().parseMultipleSystems(A.generateSystemCode(sa[i]))[0];
    const cls54 = sa[i].planets.map(p => p.class).sort().join(' ') === ra54.planets.map(p => p.class).sort().join(' ');
    // 3) Round-Trip der Positionen (min und max)
    const r = new B.MultiSystemParser().parseMultipleSystems(B.generateSystemCode(s))[0];
    for (const mode of ['min', 'max']) {
      const c1 = B.bodyChain(s.planets, mode), c2 = B.bodyChain(r.planets, mode);
      const k1 = s.planets.map(p => p.class + '@' + c1.copies.get(p).join('/')).sort().join(' ');
      const k2 = r.planets.map(p => p.class + '@' + c2.copies.get(p).join('/')).sort().join(' ');
      if (k1 !== k2) { rtBad++; if (rtBad <= 8) console.log(`ROUNDTRIP ${mode} ${f} ${s.name} (Klassen in V54 ${cls54 ? 'stabil' : 'schon instabil'})\n   vorher:  ${k1}\n   nachher: ${k2}`); break; }
    }
  });
}
console.log(`\n${nSys} Systeme`);
console.log(`count-Abweichungen gegen Spieldatei: ${countBad}`);
console.log(`Round-Trip-Abweichungen (Positionen): ${rtBad}`);
console.log(`Systeme mit geaendertem Export V54->V55: ${diffSys}`);
console.log('Geaenderte Zeilenarten: ' + [...diffKinds].map(([k, n]) => `${k} ${n}`).join(', '));
console.log(`Andere geaenderte Zeilen: ${other.length}`); other.slice(0, 15).forEach(l => console.log('   ' + l));
