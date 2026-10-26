// @ts-nocheck — procedural canvas renderer; API typed at the Svelte boundary.
/**
 * DIDIK Legenda pixel art engine. 512x288 internal pixels, scaled by the browser
 * using nearest-neighbour. No Three.js, image downloads, or third-party assets.
 * The five locales share a consistent palette and genuinely different scenery.
 */
export const REALMS = [
  { key:'chini', name:'Tasik Chini', boss:'Naga Chini', subtitle:'Di bawah kabus tasik, naga menjaga rahsia lama.', weakness:'petir',
    sky:['#132e47','#245a70','#3d8d95','#9fc2a0'], ground:['#182d37','#294a43','#3a5940'],
    mist:'#c2d9be', highlight:'#f2d492', shadow:'#0c202e'},
  { key:'lupar', name:'Batang Lupar', boss:'Bujang Senang', subtitle:'Di tebing sungai, jelmaan legenda sedang menunggu.', weakness:'api',
    sky:['#1d263b','#504655','#93586a','#ec9474'], ground:['#233837','#385044','#5b6551'],
    mist:'#d6aa8d', highlight:'#f8c07b', shadow:'#161e31'},
  { key:'larut', name:'Hutan Larut', boss:'Gajah Rimba', subtitle:'Deruman gajah penjaga rimba memecah denai.', weakness:'angin',
    sky:['#0f242b','#26483e','#527e5a','#8bb27b'], ground:['#19352d','#315340','#53704a'],
    mist:'#bed7a9', highlight:'#c9dfa3', shadow:'#0c2425'},
  { key:'kancil', name:'Rimba Bayangan', boss:'Sang Kancil Bayangan', subtitle:'Sang Kancil berdepan jelmaan bayangannya.', weakness:'tanah',
    sky:['#121c38','#292b54','#4f4175','#9070a6'], ground:['#22243c','#3a3552','#594864'],
    mist:'#bdb4e4', highlight:'#dda5eb', shadow:'#11162b'},
  { key:'ledang', name:'Gunung Ledang', boss:'Penunggu Kabus', subtitle:'Kabut di puncak menyimpan ujian terakhir.', weakness:'air',
    sky:['#17273b','#394f62','#879294','#dbb7a0'], ground:['#303b49','#546071','#7e8182'],
    mist:'#eee3ce', highlight:'#ffe1a7', shadow:'#152435'},
];

const W=512,H=288;
const r=(c,x,y,w,h,color)=>{if(w>0&&h>0){c.fillStyle=color;c.fillRect(Math.round(x),Math.round(y),Math.ceil(w),Math.ceil(h));}};
const hash=(x,y,seed=0)=>{let n=Math.imul(x+71,374761393)+Math.imul(y+137,668265263)+seed*1274126177;n=Math.imul(n^(n>>>13),1274126177);return (n^(n>>>16))>>>0};
const rand=(x,y,seed=0)=>hash(x,y,seed)/4294967295;
const translucent=(c,alpha,cb)=>{c.save();c.globalAlpha=alpha;cb();c.restore();};

function sky(c,p,t){
  const band=42;
  for(let i=0;i<4;i++)r(c,0,i*band,W,band+1,p.sky[i]);
  // horizon atmosphere and layered distant hills
  for(let x=0;x<W;x+=8){
    const far=102+Math.floor(rand(Math.floor(x/8),1,4)*27);
    r(c,x,far,8,166-far,p.sky[1]);
    const near=129+Math.floor(rand(Math.floor(x/8),4,7)*17);
    r(c,x,near,8,174-near,p.sky[0]);
  }
  // thin light through foliage or cloud bands
  for(let i=0;i<6;i++){
    const x=(i*105+35+Math.sin(t*.12+i)*9)%W;
    translucent(c,.085,()=>r(c,x,20+i*17,75,4,p.mist));
  }
  const sunX=p.key==='lupar'?380:400;
  translucent(c,.45,()=>{r(c,sunX,35,36,26,p.highlight);r(c,sunX+7,29,22,38,p.highlight)});
}
function ground(c,p,t){
  r(c,0,162,W,126,p.ground[0]);
  r(c,0,186,W,102,p.ground[1]);
  r(c,0,235,W,53,p.ground[2]);
  // stepped, stone-studded old path
  r(c,0,205,W,36,p.key==='ledang'?'#555d68':p.key==='kancil'?'#443c51':'#586250');
  r(c,0,206,W,2,p.highlight);
  translucent(c,.25,()=>{for(let i=0;i<85;i++){let x=hash(i,32)%W,y=209+(hash(i,34)%26);r(c,x,y,2+(i%3),1,i%2?p.mist:p.shadow)}});
  for(let i=0;i<210;i++){
    const x=hash(i,19)%W,y=170+hash(i,27)%118;
    r(c,x,y,2+(hash(i,6)%3),1,hash(i,15)%4===0?p.highlight:p.shadow);
  }
  if(p.key==='chini'||p.key==='lupar'){
    r(c,0,155,W,35,p.sky[2]);
    for(let x=0;x<W;x+=23){const y=163+Math.sin((x+t*12)/18)*5; r(c,x,y,12,2,p.mist);}
    // dark water reflections
    translucent(c,.3,()=>{for(let i=0;i<45;i++){let x=hash(i,2)%W;r(c,x,175+hash(i,3)%15,4+hash(i,5)%16,1,p.highlight)}});
  }
  if(p.key==='larut')for(let i=0;i<85;i++){const x=hash(i,5)%W,y=(hash(i,9)+Math.floor(t*92))%H;translucent(c,.17,()=>r(c,x,y,1,7,p.mist))}
  if(p.key==='kancil')for(let i=0;i<35;i++){let x=hash(i,19)%W,y=90+hash(i,15)%170;translucent(c,.24+Math.sin(t+i)*.15,()=>r(c,x,y,2,2,p.highlight))}
  if(p.key==='ledang')for(let i=0;i<18;i++){let x=hash(i,10)%W,y=130+hash(i,7)%80;translucent(c,.11,()=>r(c,x,y,42,8,p.mist))}
}
function tree(c,x,y,p,variant=0){
  let h=30+(hash(x,y)%25),trunk=p.key==='kancil'?'#342b42':'#403a31';
  r(c,x-3,y-h/2,7,h/2,trunk);r(c,x-5,y-h/2,2,9,'#92755b');
  for(let i=0;i<4;i++){
    let tw=38-i*6,th=10+((i+variant)%3)*3;
    r(c,x-tw/2,y-h+4+i*9,tw,th,i%2?p.ground[0]:p.ground[2]);
    r(c,x-tw/2+5,y-h+5+i*9,5,2,p.mist);
  }
  r(c,x-15,y+1,32,4,p.shadow);
}
function props(c,p){
  for(let i=0;i<22;i++){
    const x=hash(i,16)%W,y=169+hash(i,8)%103;
    if(y>201&&y<243)continue;
    if(i%3===0)tree(c,x,y,p,i);
    else if(i%3===1){r(c,x,y-5,14,8,p.ground[2]);r(c,x+4,y-8,6,4,p.mist)}
    else {r(c,x,y-3,8,4,p.highlight);r(c,x+3,y-7,2,5,p.mist)}
  }
  if(p.key==='ledang')for(let i=0;i<7;i++){let x=i*91-30; r(c,x,159,13,36,'#6a7481');r(c,x-7,153,27,9,'#939ca8')}
  if(p.key==='lupar')for(let i=0;i<13;i++){const x=i*45-14; r(c,x,150,3,45,'#302c30');r(c,x-12,146,28,8,'#384c40')}
  if(p.key==='chini')for(let i=0;i<17;i++){let x=i*31+5; r(c,x,165,13,3,p.highlight);r(c,x+5,161,3,6,p.ground[2])}
}
function sword(c,x,y,el='api'){
  const light={api:'#ff8957',angin:'#b7f4d0',petir:'#f9df60',tanah:'#d0a578',air:'#79d6fb'}[el]||'#f9df60';
  r(c,x+11,y-22,4,17,light);r(c,x+10,y-26,3,5,'#fff1ba');r(c,x+8,y-10,10,3,'#f4dba2');
}
export const HEROES=[
 {key:'tuah',name:'Hang Tuah',body:'#ae544b',helm:'#f7d39a'},
 {key:'jebat',name:'Hang Jebat',body:'#495f82',helm:'#e8ad73'},
 {key:'teja',name:'Tun Teja',body:'#9c6685',helm:'#fae3af'},
 {key:'mahsuri',name:'Mahsuri',body:'#d6a576',helm:'#faf1db'},
 {key:'saadong',name:'Puteri Saadong',body:'#417e80',helm:'#f6d8a8'},
 {key:'bendahara',name:'Bendahara',body:'#637a52',helm:'#edd099'}
];
function hero(c,x,y,key='tuah',element='api',walking=false,scale=1){
  const q=HEROES.find(h=>h.key===key)||HEROES[0];c.save();c.translate(Math.round(x),Math.round(y));c.scale(scale,scale);
  r(c,-11,0,22,4,'#15252c'); // cast shadow
  const bob=walking?1:0;
  r(c,-7,-12+bob,5,12,'#1a2936');r(c,2,-13-bob,5,13,'#1a2936');
  r(c,-11,-30,22,19,q.body);r(c,-11,-28,4,17,'#273440');r(c,7,-28,4,17,'#d3aa78');
  r(c,-9,-32,18,6,'#d0b173');r(c,-10,-44,20,13,'#b87958');r(c,-7,-40,3,3,'#29232c');r(c,4,-40,3,3,'#29232c');
  r(c,-12,-49,24,8,q.helm);r(c,-6,-53,12,5,'#1f2b3b');
  r(c,-9,-33,18,2,'#f6dca2');sword(c,0,-11,element);
  c.restore();
}
function foe(c,x,y,p,i){
  r(c,x-12,y,24,5,p.shadow);r(c,x-8,y-23,16,24,p.shadow);
  r(c,x-11,y-26,22,14,p.key==='kancil'?'#704c81':'#936c55');
  r(c,x-7,y-32,6,8,'#d6a077');r(c,x+2,y-32,6,8,'#d6a077');
  r(c,x-8,y-19,5,3,'#fff3b0');r(c,x+4,y-19,5,3,'#fff3b0');
  r(c,x-9,y-1,5,5,p.ground[0]);r(c,x+5,y-1,5,5,p.ground[0]);
}
function boss(c,x,y,p,t){
  const fx=Math.sin(t*2)*2;
  c.save();c.translate(Math.round(x),Math.round(y+fx));
  r(c,-64,1,120,9,p.shadow);
  if(p.key==='chini'){
    // Coiling lake dragon, scales, whiskers and sweeping horns
    for(let i=0;i<5;i++){r(c,-67+i*22,-43+(i%2)*9,34,32,i%2?'#2e8d82':'#3eafa0');r(c,-62+i*22,-46+(i%2)*9,18,6,'#b9d89c')}
    r(c,4,-68,49,40,'#2f9588');r(c,26,-54,35,21,'#3bac9e');
    r(c,18,-79,7,18,'#eedb97');r(c,45,-80,7,21,'#eedb97');r(c,47,-51,7,6,'#e7d25e');
    r(c,7,-34,7,22,'#c2dc92');r(c,-35,-19,8,16,'#d6e2a1');
  }else if(p.key==='lupar'){
    // Bujang Senang as a fictional giant crocodile warrior
    r(c,-30,-67,57,65,'#355e4d');r(c,-36,-72,67,30,'#538d68');
    r(c,13,-55,56,16,'#70a17b');r(c,40,-37,26,7,'#293c38');
    r(c,31,-58,6,6,'#ffd87d');r(c,-49,-60,17,12,'#415846');
    for(let i=0;i<8;i++)r(c,-16+i*9,-39,5,4,'#b9b58a');
    r(c,-22,-8,18,19,'#24433b');r(c,12,-8,18,19,'#24433b');
  }else if(p.key==='larut'){
    // Giant forest elephant, ears, ivory and trunk
    r(c,-48,-65,95,63,'#66756f');r(c,-64,-73,42,48,'#738980');
    r(c,22,-73,41,48,'#84988b');r(c,-32,-82,66,62,'#81918c');
    r(c,-8,-39,19,46,'#677e7b');r(c,-42,-24,13,36,'#dee5c5');
    r(c,31,-25,13,36,'#dee5c5');r(c,-20,-61,7,6,'#e9c66a');
    r(c,13,-61,7,6,'#e9c66a');r(c,-43,-4,18,14,'#465b53');r(c,27,-4,18,14,'#465b53');
  }else if(p.key==='kancil'){
    r(c,-33,-65,66,59,'#5c466e');r(c,-26,-79,18,34,'#826e8e');r(c,8,-79,18,34,'#826e8e');
    r(c,-37,-49,74,35,'#71507b');r(c,-20,-45,9,8,'#efacd9');r(c,14,-45,9,8,'#efacd9');
    r(c,-14,-12,28,25,'#493753');r(c,-45,-18,20,8,'#8b7ca5');r(c,28,-18,20,8,'#8b7ca5');
  }else{
    for(let i=0;i<5;i++){r(c,-45+i*14,-84+i*5,36,53,i%2?'#9fb3b5':'#627b89')}
    r(c,-27,-90,54,48,'#d2d9cd');r(c,-15,-72,8,7,'#ffda8d');r(c,10,-72,8,7,'#ffda8d');
    r(c,-22,-39,43,38,'#6f8f98');r(c,-55,-37,30,11,'#9fbec3');r(c,25,-37,30,11,'#9fbec3');
  }
  c.restore();
}
function frame(c,p){
  r(c,0,0,W,5,p.shadow);r(c,0,H-5,W,5,p.shadow);
  r(c,0,0,5,H,p.shadow);r(c,W-5,0,5,H,p.shadow);
  for(let x=11;x<W-10;x+=12){r(c,x,9,4,2,p.highlight);r(c,x,H-11,4,2,p.highlight)}
}
export function renderStory(canvas,opts={}){
  if(!canvas)return;
  canvas.width=W;canvas.height=H;
  const c=canvas.getContext('2d',{alpha:false});if(!c)return;c.imageSmoothingEnabled=false;
  const realm=Math.max(0,Math.min(4,opts.realm??0)),p=REALMS[realm],t=opts.time||0;
  sky(c,p,t);ground(c,p,t);props(c,p);
  const phase=opts.phase||'obstacles',cleared=opts.cleared||0;
  if(phase==='obstacles'){
    [5,8.5,12,15.5,19].forEach((a,i)=>{if(i>=cleared)foe(c,a/24*W,208,p,i)});
  }else if((opts.bossHp??5)>0)boss(c,449,205,p,t);
  else {r(c,437,172,36,28,p.highlight);r(c,447,162,16,11,p.mist)}
  const members=opts.peers||[];
  for(const peer of members){
    const x=(peer.pos?.[0]??2.5)/24*W, y=189+((peer.pos?.[1]??10)-7.5)*7;
    hero(c,x,y,peer.hero||'tuah',opts.element||'api',false,.85);
  }
  if(opts.hero!==null){
    const heroX=(opts.x??2.5)/24*W;
    hero(c,heroX,221,opts.hero||'tuah',opts.element||'api',Boolean(opts.walking),1.1);
  }
  frame(c,p);
}
