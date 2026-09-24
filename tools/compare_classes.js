// Vergleicht die importierte Systemklasse zweier Editor-Versionen ueber alle
// Initializer-Dateien eines Ordners. Usage: node compare_classes.js alt.js neu.js <ordner>
const fs = require('fs'), path = require('path');
function load(file) {
  const js = fs.readFileSync(file, 'utf8');
  const grab = s => { const i = js.indexOf(s); let j = js.indexOf('{', i), d = 0;
    for (;; j++) { if (js[j] == '{') d++; else if (js[j] == '}') { d--; if (!d) break; } } return js.slice(i, j + 1); };
  const a = js.indexOf('class MultiSystemParser');
  const e = js.lastIndexOf('// =====', js.indexOf('AUTOMATIC IDENTIFIER GENERATION'));
  const code = [grab('function isStarClass(cls)'), grab('function clampCount'), grab('function createEmptySystem'), js.slice(a, e)].join('\n');
  const keep = ['MultiSystemParser', 'isStarClass', 'clampCount', 'createEmptySystem'];
  const stub = new Proxy({}, { has: (t, k) => !keep.includes(k) && !(k in globalThis), get: () => () => undefined });
  return new Function('stubs', `with(stubs){${code}; return MultiSystemParser;}`)(stub);
}
const [A, B] = [load(process.argv[2]), load(process.argv[3])];
const dir = process.argv[4];
const quiet = console.error; console.error = () => {};
let total = 0, changed = 0;
for (const f of fs.readdirSync(dir).filter(f => f.endsWith('.txt')).sort()) {
  const txt = fs.readFileSync(path.join(dir, f), 'utf8');
  const ra = new A().parseMultipleSystems(txt), rb = new B().parseMultipleSystems(txt);
  const mb = new Map(rb.map(s => [s.name, s]));
  for (const s of ra) {
    total++;
    const n = mb.get(s.name);
    if (!n) { console.log(`${f}  ${s.name}: fehlt in neu`); changed++; continue; }
    if (s.class !== n.class) { changed++; console.log(`${f}  ${s.name}: ${s.class} -> ${n.class}`); }
  }
  if (ra.length !== rb.length) console.log(`${f}: Anzahl ${ra.length} -> ${rb.length}`);
}
console.error = quiet;
console.log(`\n${total} Systeme, ${changed} mit geaenderter Klasse`);
