// Laedt das komplette Editor-Script in node mit einer tiefen DOM-Attrappe.
const vm = require('vm'), fs = require('fs');
module.exports = function load(file) {
  const deep = () => { const f = function () { return p; }; const p = new Proxy(f, {
      get: (t, k) => k === Symbol.toPrimitive ? () => '' : k === 'checked' ? false : k === 'value' ? '' : k === 'length' ? 0 : k === Symbol.iterator ? function* () {} : p,
      apply: () => p, construct: () => p, set: () => true, has: () => true }); return p; };
  const ctx = { console: { log() {}, warn() {}, error() {} }, Math, JSON, Number, String, Array, Object, Map, Set, RegExp, Date, parseInt, parseFloat, isNaN, isFinite, Promise, Symbol, Error, TypeError, Infinity, NaN, undefined, setTimeout: () => 0, clearTimeout() {}, setInterval: () => 0, requestAnimationFrame: () => 0, document: deep(), window: deep(), localStorage: deep(), navigator: deep(), alert() {}, confirm: () => true, Blob: function () {}, URL: deep(), FileReader: function () {}, TextEncoder, Uint8Array, Uint32Array, DataView, ArrayBuffer, getComputedStyle: deep() };
  Object.assign(ctx, { addEventListener() {}, removeEventListener() {}, matchMedia: deep(), location: deep(), scrollTo() {}, history: deep(), performance: { now: () => 0 } });
  ctx.window = ctx; ctx.self = ctx;
  vm.createContext(ctx);
  const src = fs.readFileSync(file, 'utf8') + '\n;globalThis.__x = { MultiSystemParser, generateSystemCode, bodyChain: typeof bodyChain === "function" ? bodyChain : null, validateSystem: typeof validateSystem === "function" ? validateSystem : null };';
  vm.runInContext(src, ctx, { filename: file });
  return ctx.__x;
};
