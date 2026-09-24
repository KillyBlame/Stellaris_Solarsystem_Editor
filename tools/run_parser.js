const fs=require('fs');
const js=fs.readFileSync(process.argv[2],'utf8');
function grab(startStr){const i=js.indexOf(startStr);if(i<0)throw startStr;let j=js.indexOf('{',i),d=0;for(;;j++){if(js[j]=='{')d++;else if(js[j]=='}'){d--;if(!d)break;}}return js.slice(i,j+1);}
const code=[grab('function isStarClass(cls)'),grab('function clampCount'),grab('function createEmptySystem'),(()=>{const a=js.indexOf('class MultiSystemParser');const e=js.lastIndexOf('// =====',js.indexOf('AUTOMATIC IDENTIFIER GENERATION'));return js.slice(a,e);})()].join('\n');
const stub=new Proxy({},{has:(t,k)=>!['MultiSystemParser','isStarClass','clampCount','createEmptySystem'].includes(k)&&!(k in globalThis),get:()=>()=>undefined});
const P=new Function('stubs',`with(stubs){${code}; return MultiSystemParser;}`)(stub);
const txt=fs.readFileSync(process.argv[3],'utf8');
const sys=new P().parseMultipleSystems(txt);
for(const s of sys.filter(s=>/^sol_neighbor_t1_first_colony$|^sol_neighbor_t2$/.test(s.name))){
  console.log('==',s.name,s.class);
  let ptr=0;(s.planets||[]).forEach(p=>{ptr+=p.orbitDistance||0;console.log(`  ${p.class||'-'} ${p.displayName||''} od=${p.orbitDistance} ptr=${ptr} ang=${p.orbitAngle}/${p.orbitAngleType} co=${p.changeOrbit} cnt=${p.countMin}-${p.countMax} moons=${(p.moons||[]).map(m=>(m.class||'-')+':'+m.orbitDistance).join(',')}`)});
}
