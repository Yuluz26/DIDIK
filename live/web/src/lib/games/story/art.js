// @ts-nocheck -- Canvas game renderer. The public Svelte component is typed.
// DIDIK LEGENDA / handcrafted top-down 2D pixel-adventure renderer.
// Artwork is drawn in logical pixels, nearest-neighbour scaled; no WebGL or 3D.
export const REALMS = [
 {key:'chini',name:'Tasik Chini',boss:'Naga Chini',subtitle:'Di bawah kabus tasik, naga menjaga rahsia lama.',weakness:'petir',
  sky:['#083c51','#0e8091','#27bdc2','#b3ded4'],ground:['#294d3b','#51784b','#8daa5e'],mist:'#c4f5e8',highlight:'#f8d99c',shadow:'#0b2630'},
 {key:'lupar',name:'Batang Lupar',boss:'Bujang Senang',subtitle:'Di tebing sungai, jelmaan legenda sedang menunggu.',weakness:'api',
  sky:['#243b49','#366e6a','#65afa0','#d6c4a1'],ground:['#344b3c','#688455','#aaa970'],mist:'#d8f1d7',highlight:'#ffcb92',shadow:'#182c34'},
 {key:'larut',name:'Hutan Larut',boss:'Gajah Rimba',subtitle:'Deruman gajah penjaga rimba memecah denai.',weakness:'angin',
  sky:['#143c42','#28695c','#58a39a','#a8d2ae'],ground:['#1e4035','#3c7352','#83a46b'],mist:'#e1f3ca',highlight:'#ffe0a1',shadow:'#112a2d'},
 {key:'kancil',name:'Rimba Bayangan',boss:'Sang Kancil Bayangan',subtitle:'Sang Kancil berdepan jelmaan bayangannya.',weakness:'tanah',
  sky:['#292b52','#514b7e','#8378a7','#cfbcdd'],ground:['#332f50','#615373','#a17e99'],mist:'#e9d5fb',highlight:'#f4c4eb',shadow:'#201d39'},
 {key:'ledang',name:'Gunung Ledang',boss:'Penunggu Kabus',subtitle:'Kabut di puncak menyimpan ujian terakhir.',weakness:'air',
  sky:['#294557','#4b7985','#87bab6','#d9dad2'],ground:['#394c55','#60767a','#a0a69a'],mist:'#f4eee1',highlight:'#f9dea8',shadow:'#26333b'}
];
export const HEROES=[
 {key:'tuah',name:'Hang Tuah',body:'#275b9c',helm:'#264d8b'},
 {key:'jebat',name:'Hang Jebat',body:'#9a343f',helm:'#672c44'},
 {key:'teja',name:'Tun Teja',body:'#b05994',helm:'#783f73'},
 {key:'mahsuri',name:'Mahsuri',body:'#eac49d',helm:'#ecdfcb'},
 {key:'saadong',name:'Puteri Saadong',body:'#3d9b86',helm:'#245a79'},
 {key:'bendahara',name:'Bendahara',body:'#667f48',helm:'#4b664d'}
];
const W=640,H=360,STEP=40,LENGTH=24,REACH=20;
const rect=(c,x,y,w,h,a)=>{if(w>0&&h>0){c.fillStyle=a;c.fillRect(Math.round(x),Math.round(y),Math.ceil(w),Math.ceil(h));}};
const hash=(a,b=0,z=0)=>{let n=Math.imul((a|0)+87,374761393)^Math.imul((b|0)+31,668265263)^Math.imul(z+5,1274126177);n=Math.imul(n^(n>>>13),1274126177);return (n^(n>>>16))>>>0};
const rnd=(a,b=0,z=0)=>hash(a,b,z)/4294967295;
const path=(c,pts,fill,stroke=null,weight=1)=>{
 c.beginPath();pts.forEach(([x,y],i)=>i?c.lineTo(x,y):c.moveTo(x,y));c.closePath();
 if(fill){c.fillStyle=fill;c.fill()}if(stroke){c.lineWidth=weight;c.strokeStyle=stroke;c.stroke()}
};
const oval=(c,x,y,rx,ry,fill,stroke=null,sw=1)=>{
 c.beginPath();c.ellipse(Math.round(x),Math.round(y),rx,ry,0,0,Math.PI*2);
 if(fill){c.fillStyle=fill;c.fill()}if(stroke){c.strokeStyle=stroke;c.lineWidth=sw;c.stroke()}
};
const line=(c,x1,y1,x2,y2,col,width=1)=>{
 c.beginPath();c.moveTo(Math.round(x1),Math.round(y1));c.lineTo(Math.round(x2),Math.round(y2));c.strokeStyle=col;c.lineWidth=width;c.stroke();
};
const glow=(c,x,y,rgb,r)=>{const g=c.createRadialGradient(x,y,1,x,y,r);g.addColorStop(0,rgb);g.addColorStop(1,'transparent');c.fillStyle=g;c.fillRect(x-r,y-r,2*r,2*r)};
const cameraState=new WeakMap();
function polyline(c,pts,stroke,width){c.lineWidth=width;c.lineJoin='round';c.lineCap='round';c.strokeStyle=stroke;c.beginPath();pts.forEach(([x,y],i)=>i?c.lineTo(x,y):c.moveTo(x,y));c.stroke()}
function water(c,p,t,ox){
 const g=c.createLinearGradient(0,0,0,H);g.addColorStop(0,p.sky[0]);g.addColorStop(.5,p.sky[1]);g.addColorStop(1,p.sky[2]);
 rect(c,0,0,W,H,g);
 // Painterly bands of water, small animated glitter and underwater mosaic
 for(let y=0;y<350;y+=18)for(let x=0;x<660;x+=27){
  const v=rnd(x+Math.floor(ox),y,2),col=v>.79?'#60e3d9':v>.43?p.sky[2]:p.sky[1];
  c.globalAlpha=.055+(v%1)*.075;rect(c,x+((y%3)*5),y,26,16,col);
 }
 c.globalAlpha=1;
 for(let i=0;i<110;i++){
  const x=(hash(i,2,7)%1120-ox*.25+1250)%700-30;
  const y=hash(i,13,3)%335;const len=3+hash(i,6,2)%16;
  c.globalAlpha=.15+.26*Math.max(0,Math.sin(t*.7+i*3));
  rect(c,x+Math.sin(t+i)*2,y,len,1,p.mist);
 }
 c.globalAlpha=1;
}
function terrain(c,p,t,ox){
 water(c,p,t,ox);
 // River and lake in the upper half, with an organic stone-edged bank.
 const top=[],bank=[],low=[];
 for(let x=-24;x<=W+24;x+=12){
   const wx=x+ox;
   const v=158+Math.sin(wx*.008)*18+Math.sin(wx*.022)*7;
   bank.push([x,v]);top.push([x,0]);low.push([x,v+4]);
 }
 path(c,[...bank,[W+24,H],[-24,H]],p.ground[0]);
 polyline(c,bank,'#c7dfad',8);polyline(c,bank,'#7fac89',4);
 // Soil and foliage gradients with irregular transparent patches.
 for(let gy=10;gy<H;gy+=19)for(let gx=0;gx<W;gx+=21){
  const wx=Math.floor((gx+ox)/21),q=rnd(wx,gy,5);
  if(gy<153)continue;
  if(q>.29){c.globalAlpha=.12+(q*.1);rect(c,gx,gy,21,19,p.ground[q>.7?2:1]);}
 }
 c.globalAlpha=1;
 // Carved central walking trail, irregular not rectangular.
 const route=(yy,xx)=>yy+Math.sin((xx+ox)*.013)*12+Math.cos((xx+ox)*.027)*7;
 const upper=[],lower=[];for(let x=-28;x<W+35;x+=12){
  upper.push([x,route(211,x)-37]);lower.push([x,route(211,x)+45]);
 }
 path(c,[...upper,...lower.slice().reverse()],'#5f6552','#344938',6);
 polyline(c,upper,'#b1a47c',3);polyline(c,lower,'#8d9168',3);
 // Sandy central trail and individually placed flat cobblestones.
 const inlayUpper=upper.map(([x,y])=>[x,y+8]),inlayLower=lower.map(([x,y])=>[x,y-9]);
 path(c,[...inlayUpper,...inlayLower.slice().reverse()],'#bfa77e');
 for(let wx=0;wx<LENGTH*STEP;wx+=19){
   const sx=wx-ox;
   if(sx<-30||sx>W+30)continue;
   const wob=rnd(wx,44);const py=route(211,sx)+(wob-.5)*51;
   const stones=2+hash(wx,6)%3;
   for(let j=0;j<stones;j++){
     const bx=sx+((j*11)%15),by=py+(j*11)%23;
     rect(c,bx+2,by+3,9,6,'#726e5b');rect(c,bx,by,9,6,j%2?'#d5c29b':'#e2d1ac');rect(c,bx+2,by,5,1,'#fff3d0');
   }
 }
 // Readable scattered grass, flowers and herbs around walkway.
 for(let wx=0;wx<LENGTH*STEP;wx+=8){
  const x=wx-ox;if(x<-15||x>W+15)continue;
  for(const yy of [169,299,326]){
   const v=rnd(wx,yy);const y=yy+(rnd(wx,yy+2)-.5)*18;
   if(v>.34){
     const col=v>.66?'#7bb56c':'#406d53';
     line(c,x,y,x+3,y-6,col,2);line(c,x+3,y,x+6,y-4,col,2);
     if(v>.85){rect(c,x+1,y-8,3,3,'#fff3c0');rect(c,x+2,y-7,1,2,'#ed84a8');}
   }
  }
 }
 // Reflected large lily pads and lotus flowers in lake.
 for(let wx=40;wx<LENGTH*STEP;wx+=53){
  const x=wx-ox;if(x<-18||x>W+18)continue;
  const y=70+hash(wx,12)%65;const radius=6+hash(wx,16)%8;
  oval(c,x,y,radius,radius*.62,'#1f7d66','#92b980',1);
  path(c,[[x,y],[x+radius+2,y-2],[x+radius,y+5]],p.sky[1]);
  if(hash(wx,22)%3===0)lotus(c,x+8,y-4,1);
  if(hash(wx,4)%5===0){rect(c,x+23,y+9,11,2,'#b8ece0');rect(c,x+27,y+6,7,1,'#92d8cf');}
 }
}
function lotus(c,x,y,s=1){
 c.save();c.translate(x,y);c.scale(s,s);
 oval(c,0,2,12,4,'#215c4e');
 for(let i=0;i<5;i++){const a=i*Math.PI*2/5;oval(c,Math.sin(a)*5,Math.cos(a)*3,3,6,i%2?'#f19abb':'#f6c6d6');}
 oval(c,0,-2,2.5,2.5,'#fadd73');c.restore();
}
function foliage(c,x,y,seed,p,size=1){
 c.save();c.translate(x,y);c.scale(size,size);
 oval(c,0,3,19,6,'#1e3d37');
 rect(c,-3,-22,6,24,'#765f44');rect(c,1,-21,2,20,'#a88a59');
 const edges=[[0,-27,24,15],[-16,-29,17,14],[15,-31,18,13],[-7,-38,20,14],[6,-40,19,14]];
 for(let i=0;i<edges.length;i++){
  const [a,b,rx,ry]=edges[i];
  oval(c,a,b,rx,ry,i%2?p.ground[0]:'#346851','#183c37',2);
  oval(c,a-3,b-4,rx*.67,ry*.43,i%2?'#699c68':'#559764');
 }
 for(let i=0;i<15;i++){
  const tx=hash(seed,i)%46-23,ty=-40+hash(seed,i,4)%24;
  rect(c,tx,ty,2,2,hash(i,seed)%3===0?'#c4df8c':'#8ec27b');
 }
 c.restore();
}
function palm(c,x,y,p){
 c.save();c.translate(x,y);oval(c,0,0,15,5,'#16382f');
 rect(c,-2,-30,6,30,'#896d4b');rect(c,0,-30,2,30,'#be9660');
 for(let i=0;i<7;i++){
  const a=i*Math.PI*2/7;
  const dx=Math.cos(a)*24,dy=Math.sin(a)*12;
  polyline(c,[[0,-34],[dx*.55,-39+dy*.4],[dx,-30+dy]],'#1e5246',8);
  polyline(c,[[0,-35],[dx*.55,-40+dy*.4],[dx,-32+dy]],'#72b37a',4);
 }
 c.restore();
}
function stone(c,x,y,p,variant=0){
 const w=21+(variant%3)*6,h=25+(variant%4)*7;
 rect(c,x-w/2+3,y-h+5,w,h+1,'#283f42');
 path(c,[[x-w/2,y-h+6],[x-w/2+7,y-h],[x+w/2-2,y-h+2],[x+w/2+4,y-h+7],[x+w/2,y],[x-w/2,y]],'#859a90','#425b5b',2);
 rect(c,x-w/2+5,y-h+8,w-11,3,'#ccd1b4');
 line(c,x-3,y-h+12,x-3,y-7,'#4c7775',2);
 line(c,x-3,y-7,x+3,y-7,'#4c7775',2);
 rect(c,x-6,y-5,8,3,'#67866c');
}
function lantern(c,x,y,t){
 rect(c,x-4,y-26,8,26,'#5a3e31');rect(c,x-6,y-28,12,4,'#e4c789');
 rect(c,x-7,y-37,14,12,'#503928');rect(c,x-4,y-35,8,8,'#ffe5a0');
 rect(c,x-2,y-35,4,7,'#ffb955');
 rect(c,x-9,y-40,18,3,'#bb9866');
 const alpha=.08+.07*Math.sin(t*4+x);
 c.globalAlpha=.45+alpha;glow(c,x,y-30,'#ffc7737f',35);c.globalAlpha=1;
}
function shrine(c,x,y,p){
 oval(c,x,y+5,48,13,'#223d40');
 // Ancient square tiled arena
 path(c,[[x-38,y-27],[x+32,y-27],[x+46,y-13],[x+46,y+14],[x+31,y+29],[x-33,y+29],[x-46,y+15],[x-46,y-12]],'#7a8d7c','#d5d6b6',3);
 for(let py=-23;py<27;py+=9)for(let px=-36;px<36;px+=11){
  rect(c,x+px,y+py,10,7,(hash(px,py)%3===0)?'#9fa997':'#708c82');
  rect(c,x+px+1,y+py,3,1,'#c1c8a5');
 }
 oval(c,x,y,26,11,'#567f74','#c2d2ae',2);
 lotus(c,x,y+2,.85);
 for(const xx of [-38,38]){stone(c,x+xx,y+5,p,2);lantern(c,x+xx,y-6,0)}
}
function bridge(c,x,y){
 rect(c,x-38,y-10,78,48,'#183a40');
 for(let j=-2;j<=7;j++){
  const by=y+j*8;
  rect(c,x-36,by,70,7,j%2?'#9f7654':'#ba9160');
  rect(c,x-31,by+2,58,1,'#e2c091');
 }
 for(const xx of [-36,34]){
  rect(c,x+xx,y-20,4,66,'#4d352a');
  for(let yy=-20;yy<48;yy+=10)rect(c,x+xx-1,y+yy,7,3,'#dfb781');
 }
}
function hut(c,x,y){
 oval(c,x,y+4,48,11,'#365046');
 rect(c,x-33,y-26,64,27,'#855c43');rect(c,x-27,y-19,16,14,'#dec69c');
 rect(c,x+12,y-18,11,13,'#40322d');
 path(c,[[x-46,y-29],[x-33,y-51],[x+31,y-51],[x+46,y-29],[x+39,y-27],[x-40,y-27]],'#c6a36c','#7e6040',3);
 for(let i=0;i<12;i++)line(c,x-37+i*7,y-45,x-42+i*7,y-30,i%2?'#e6c990':'#977452',2);
 rect(c,x-37,y-20,4,25,'#70523e');rect(c,x+28,y-20,4,25,'#70523e');
}
function mapDecor(c,p,t,ox){
 const island=p.key==='chini';const shift=ox;
 // Fixed world objects with depth, never randomised per frame.
 const scenery=[
  [65,154,'palm'],[155,163,'tree'],[320,164,'palm'],[445,146,'tree'],
  [555,165,'tree'],[675,160,'palm'],[765,151,'tree'],
  [80,343,'tree'],[230,334,'tree'],[369,341,'palm'],[550,335,'tree'],[708,328,'palm'],
  [881,326,'tree'],[947,336,'palm'],[286,117,'lotus'],[566,103,'lotus'],
  [118,286,'lamp'],[355,291,'lamp'],[502,281,'lamp'],[694,286,'lamp'],
  [854,269,'lamp'],[430,109,'rock'],[795,91,'rock'],[80,114,'rock']
 ];
 for(const [wx,y,kind] of scenery){
  const x=wx-shift;if(x<-65||x>W+65)continue;
  if(kind==='palm')palm(c,x,y,p);else if(kind==='tree')foliage(c,x,y,wx,p,1);
  else if(kind==='lamp')lantern(c,x,y,t);else if(kind==='rock')stone(c,x,y,p,wx);
  else if(kind==='lotus')lotus(c,x,y,1.2);
 }
 // Wooden crossing and a small Malay lakeside house make the world recognisable.
 if(365-shift>-110 && 365-shift<W+100)hut(c,365-shift,156);
 if(554-shift>-80 && 554-shift<W+80)bridge(c,554-shift,151);
 if(725-shift>-130 && 725-shift<W+100){
  const x=725-shift;path(c,[[x-47,155],[x-30,133],[x+30,133],[x+47,155]],'#566f65','#c9bb98',3);
  stone(c,x-34,164,p,3);stone(c,x+34,164,p,2);
 }
 // Tall wildflowers/fens and small stone remnants
 for(let wx=22;wx<960;wx+=32){
  const x=wx-shift;if(x<-20||x>W+20)continue;
  const y=304+(hash(wx,17)%24);
  if(hash(wx,19)%5===0)stone(c,x,y,p,wx);
  else if(hash(wx,3)%3===0)lotus(c,x,125+hash(wx,6)%20,.45);
  else for(let j=0;j<4;j++){
    line(c,x+j*3,y,x+j*3-2,y-6-hash(j,wx)%9,'#80b77a',2);
    if(j%3===0)rect(c,x+j*3-3,y-13,4,3,'#ecb0cc');
  }
 }
}
function regionalArt(c,p,t,ox){
 // Environmental identity goes well beyond a palette swap.
 if(p.key==='lupar'){
   // Batang Lupar: mangrove silhouettes, river boats and sunset embers.
   for(const wx of [120,352,621,908]){
     const x=wx-ox;if(x<-60||x>W+60)continue;
     rect(c,x-3,58,7,99,'#624d42');
     for(let i=0;i<4;i++)polyline(c,[[x,128],[x+(i-2)*12,146],[x+(i-2)*15,166]],'#644f40',3);
     for(let j=0;j<6;j++){const a=j*1.02;oval(c,x+Math.cos(a)*24,64+Math.sin(a)*14,23,11,'#325c48','#254838',2);}
   }
   for(const wx of [255,745]){
     const x=wx-ox;if(x<-60||x>W+60)continue;
     path(c,[[x-34,116],[x+33,116],[x+23,125],[x-24,125]],'#825539','#382d31',3);
     rect(c,x-3,95,5,21,'#5d4b3d');
     path(c,[[x+2,97],[x+22,108],[x+2,110]],'#e6cba4','#9f9675',2);
   }
   for(let i=0;i<23;i++){
     const x=(hash(i,91)%1060-ox*.3+1080)%660-10,y=40+hash(i,13)%130;
     glow(c,x,y,'#ffa8683b',7);
   }
 }else if(p.key==='larut'){
   // Larut: old rain forest, oversized fern leaves and persistent tropical drizzle.
   for(const wx of [60,260,473,830]){
     const x=wx-ox;if(x<-60||x>W+60)continue;
     for(let i=0;i<8;i++){
       const a=(i/8)*Math.PI*2;
       polyline(c,[[x,147],[x+Math.cos(a)*18,125+Math.sin(a)*17],[x+Math.cos(a)*31,123+Math.sin(a)*26]],'#6dba82',5);
     }
   }
   for(let i=0;i<85;i++){
     const x=(hash(i,51)%1120-ox*.38+1200)%680-20;
     const y=((hash(i,31)+Math.floor(t*72))%410)-30;
     line(c,x,y,x-3,y+12,'#ccebd25a',1.2);
   }
   for(const wx of [120,555,940]){
     const x=wx-ox;if(x<-70||x>W+70)continue;
     oval(c,x,92,33,20,'#2d5f51','#8cae83',2);
     oval(c,x+10,89,17,9,'#99bb7b');
   }
 }else if(p.key==='kancil'){
   // Ghostly violet clearing: fluorescent fungus, carved spirit stones.
   for(const wx of [90,275,488,710,925]){
     const x=wx-ox;if(x<-50||x>W+50)continue;
     glow(c,x,160,'#ab82fa32',46);
     oval(c,x,165,26,6,'#332f51');
     for(let j=-2;j<=2;j++){
       rect(c,x+j*7,148-Math.abs(j)*4,3,15,'#b0a1c9');
       oval(c,x+j*7,146-Math.abs(j)*4,6,4,j%2?'#b78dd6':'#e2b9e5');
     }
   }
   for(const wx of [390,840]){
     const x=wx-ox;if(x<-50||x>W+50)continue;
     path(c,[[x-16,156],[x-18,94],[x+18,89],[x+23,157]],'#4d5674','#b9a7c8',3);
     oval(c,x,115,10,11,'#998ac4');
     line(c,x-8,130,x+10,130,'#c9b4d0',3);
   }
 }else if(p.key==='ledang'){
   // High mountain: slate slopes, cataracts and rolling ground mist.
   for(const wx of [122,388,753,933]){
     const x=wx-ox;if(x<-90||x>W+90)continue;
     path(c,[[x-46,160],[x-15,58],[x+12,46],[x+48,160]],'#687d82','#b3c5bd',3);
     path(c,[[x-15,58],[x+12,46],[x+24,83],[x,77]],'#e8e6d3');
     for(let i=0;i<9;i++){const py=85+i*8;line(c,x+3,py,x+9,py+7,'#dbead1',2);}
   }
   for(const wx of [555]){
     const x=wx-ox;
     if(x>-90&&x<W+90){
       path(c,[[x-25,18],[x+17,18],[x+18,169],[x-21,169]],'#82b9ba');
       for(let i=0;i<30;i++)rect(c,x-20+(hash(i,11)%34),17+(i*6+Math.floor(t*55))%148,3,8,'#d7eee0');
       glow(c,x,165,'#ffffff5b',43);
     }
   }
   for(let i=0;i<7;i++){
     const x=((hash(i,94)%850-ox*.31+860)%720)-30;
     c.globalAlpha=.12+Math.sin(t*.4+i)*.035;oval(c,x,92+i*35,65,12,'#ecf0e3');
   }
   c.globalAlpha=1;
 }else{
   // Tasik Chini's distinctive lotus islands, blue waterfalls and submerged ruins.
   for(const wx of [220,585]){
     const x=wx-ox;if(x<-50||x>W+50)continue;
     const sy=64+Math.sin(t*.7)*3;
     for(let i=0;i<6;i++)rect(c,x+i*6,sy+i%2*2,4,32,'#b5e9eb9c');
     oval(c,x+14,sy+33,30,5,'#a6f5e666');
   }
 }
}
function hero(c,x,y,key='tuah',element='api',t=0,walking=false){
 const q=HEROES.find(x=>x.key===key)||HEROES[0];
 const bounce=walking?Math.sin(t*16)*1.8:Math.sin(t*2)*.45;
 c.save();c.translate(Math.round(x),Math.round(y+bounce));
 oval(c,0,2,16,5,'#173a37');
 // Boots, cape and traditional sash
 rect(c,-9,-5,7,9,'#344351');rect(c,3,-5,7,9,'#283548');
 rect(c,-14,-27,27,23,'#1d3149');rect(c,-11,-28,22,20,q.body);
 rect(c,-9,-15,18,4,'#f0c57e');rect(c,0,-19,4,7,'#f5d68e');
 rect(c,-17,-26,6,19,'#c88d62');rect(c,11,-26,6,18,'#b87b59');
 // Chibi face and distinctive coiffure/tengkolok
 oval(c,0,-40,15,15,'#72452f');
 rect(c,-13,-48,27,19,'#ca9469');rect(c,-12,-50,25,8,'#4b302e');
 rect(c,-16,-54,32,7,q.helm);rect(c,-8,-60,17,7,q.helm);
 rect(c,-10,-63,8,6,'#e0b26c');rect(c,-7,-59,11,3,'#fff0bf');
 rect(c,-7,-41,3,4,'#172738');rect(c,5,-41,3,4,'#172738');
 rect(c,-2,-33,5,2,'#ad6c58');
 // A proper curved keris with selected elemental blade glow
 const shades={api:'#f7a26b',angin:'#b6eccc',petir:'#ffe17a',tanah:'#cfae75',air:'#87d9f5'};
 const blade=shades[element]||shades.api;
 line(c,17,-17,26,-42,'#263b47',6);line(c,17,-17,26,-42,blade,3);
 path(c,[[24,-37],[25,-49],[29,-52],[28,-40],[25,-36]],'#f9f4cb');
 rect(c,14,-18,8,4,'#eed6a0');rect(c,18,-15,3,6,'#705238');
 c.restore();
}
function imp(c,x,y,i,t,p){
 const bob=Math.sin(t*3+i)*2;c.save();c.translate(x,y+bob);
 oval(c,0,2,15,5,'#182f33');
 const skin=i%2?'#718b51':'#40665c';
 rect(c,-10,-20,20,20,skin);oval(c,0,-22,13,12,skin);
 path(c,[[-14,-23],[-8,-45],[0,-37],[6,-48],[14,-24]],'#6da36a','#294d3b',2);
 rect(c,-7,-25,5,4,'#ffd990');rect(c,4,-25,5,4,'#f3bf73');
 rect(c,-10,-2,6,6,'#2e493f');rect(c,4,-2,6,6,'#2e493f');
 line(c,10,-9,19,-29,'#755644',3);rect(c,15,-33,6,6,'#b8c6a1');
 c.restore();
}
function dragon(c,x,y,t,p){
 // Serpentine Malaysian lake Naga: side-profile silhouette, jade scales,
 // long sinuous neck, antler crown, ivory belly and luminous amber eyes.
 c.save();c.translate(Math.round(x-22),Math.round(y+Math.sin(t*1.6)*3));
 glow(c,0,-38,'#2ffff178',115);
 oval(c,3,25,104,24,'#0c4957');
 for(let i=0;i<4;i++)oval(c,4,25,79+i*6,14+i*3,'#58b7b533');
 // Thick winding body. Ink -> shadow -> scales -> jade-green ridge.
 const strokeBody=(color,size)=>{
   c.beginPath();c.moveTo(-81,14);
   c.bezierCurveTo(-116,-38,-40,-41,-17,-13);
   c.bezierCurveTo(5,10,-41,45,18,30);
   c.bezierCurveTo(92,17,39,-43,36,-72);
   c.strokeStyle=color;c.lineWidth=size;c.lineCap='round';c.lineJoin='round';c.stroke();
 };
 strokeBody('#0c4651',48);strokeBody('#197c78',41);strokeBody('#289a8c',32);strokeBody('#48b5a0',15);
 // Lower creamy belly, catching sunlight on the scales.
 c.beginPath();c.moveTo(-73,26);c.bezierCurveTo(-30,43,12,48,39,19);
 c.bezierCurveTo(56,-5,40,-33,41,-68);
 c.strokeStyle='#e8d5ab';c.lineWidth=13;c.stroke();
 c.beginPath();c.moveTo(-70,29);c.bezierCurveTo(-30,44,12,51,39,20);
 c.bezierCurveTo(58,-5,40,-33,41,-68);
 c.strokeStyle='#ac9a79';c.lineWidth=2;c.stroke();
 // Reticulated scales along the back: irregular highlights not an oval pile.
 for(let i=0;i<20;i++){
   const a=i/19*Math.PI*1.75;
   const px=-67+i*6.5,py=-6+Math.sin(a*2)*15;
   if(i<10){rect(c,px,py-12,5,3,i%3?'#61cbaa':'#bae4b5');rect(c,px+3,py-3,4,3,'#0d776f');}
 }
 // Dorsal golden fins rise behind the neck, carefully spaced.
 for(const [xx,yy,rot] of [[-45,-23,-1],[-13,-25,-1],[20,-18,1],[35,-43,1]]){
    path(c,[[xx-9,yy+9],[xx-5,yy-7],[xx+2,yy-20],[xx+7,yy-5],[xx+11,yy+9]],
      '#a88c5c','#523d36',2);
    line(c,xx-1,yy-10,xx+1,yy+3,'#fbe3a3',2);
 }
 // Upright neck casting a shadow; ivory segmented breast.
 path(c,[[19,-27],[10,-69],[23,-102],[46,-110],[66,-95],[58,-54],[46,-22]],
  '#176e72','#0b454e',4);
 path(c,[[31,-21],[26,-70],[34,-101],[51,-99],[48,-63],[46,-26]],
  '#eddaa7','#a07f6a',3);
 for(let i=0;i<5;i++)line(c,31+i*1.5,-64+i*8,48,-62+i*8,'#bdab85',2);
 // Opposite horn and crest behind the face.
 path(c,[[30,-100],[23,-129],[10,-144],[18,-116],[11,-122],[14,-103]],
  '#ba894c','#755338',3);
 path(c,[[47,-105],[58,-144],[72,-151],[61,-122],[75,-132],[60,-105]],
  '#d7a65a','#805538',3);
 line(c,46,-127,62,-145,'#ffe3a0',3);
 // Elegant side-profile dragon skull, not a human or rounded monster face.
 path(c,[[22,-106],[37,-119],[59,-110],[74,-96],[69,-82],
          [84,-76],[96,-62],[91,-48],[63,-45],[46,-52],[28,-68],[14,-83]],
    '#217d7c','#0d4654',5);
 path(c,[[28,-105],[46,-115],[67,-96],[62,-91],[47,-94],[38,-89],[23,-89]],
    '#57b9a0');
 // Elaborate gilded eyebrow mask, exposed cheek and turquoise crown jewel.
 path(c,[[48,-91],[61,-98],[74,-84],[65,-83],[57,-87]],'#e9be6f','#815f3d',2);
 path(c,[[51,-83],[67,-81],[79,-71],[71,-61],[51,-69]],
   '#1a636b','#0a4452',2);
 oval(c,61,-83,7,6,'#ffc567','#7e552c',2);
 oval(c,63,-83,3,4,'#1b2f40');
 rect(c,63,-85,2,2,'#fff0b6');
 // Long plated snout and smile, separate upper/lower jaw.
 path(c,[[63,-66],[91,-66],[110,-56],[109,-49],[91,-46],[71,-51]],
   '#299e91','#0b4c5a',3);
 path(c,[[74,-46],[92,-43],[103,-46],[89,-39],[72,-43]],
   '#c2d3a1','#0b4c5a',2);
 rect(c,99,-56,5,3,'#1a5253');
 rect(c,83,-43,5,3,'#fff3d0');rect(c,94,-43,5,3,'#fff3d0');
 // Pink ear/fan fins and white tendril whiskers.
 path(c,[[30,-89],[18,-104],[14,-87],[23,-74]],'#e39e91','#8a6570',2);
 path(c,[[31,-86],[22,-94],[24,-82]],'#ffe0b2');
 polyline(c,[[74,-50],[92,-33],[113,-25]],'#fae8b2',2);
 polyline(c,[[78,-55],[106,-68],[117,-81]],'#edf2c7',2);
 // Crest gem and tiny water droplets animated near the boss.
 oval(c,43,-108,9,8,'#e7bf69','#7a5738',2);
 oval(c,44,-110,5,5,'#78dff1','#e8ffff',1);
 for(let i=0;i<7;i++){
   const a=t*.8+i*1.2,px=Math.cos(a)*84,py=13+Math.sin(a)*29;
   rect(c,px,py,2+(i%3),2,'#a2f6ed');
 }
 c.restore();
}
function bossOther(c,x,y,p,t){
 c.save();c.translate(x,y+Math.sin(t*1.7)*2);
 oval(c,0,11,81,24,'#173837');
 if(p.key==='lupar'){
  // Bujang Senang: mythical crocodile guardian
  oval(c,-3,-8,66,41,'#497e59','#183f43',5);
  for(let i=-5;i<=5;i++)path(c,[[i*10,-33],[i*10+5,-47],[i*10+9,-30]],'#a9b47d');
  path(c,[[-37,-38],[16,-46],[72,-21],[74,5],[11,14],[-40,2]],'#69aa70','#2b5653',4);
  for(const xx of [-22,7]){rect(c,xx,-23,9,8,'#fbdf86');rect(c,xx+3,-23,3,5,'#172c3b');}
  for(let i=0;i<6;i++)path(c,[[12+i*8,6],[16+i*8,15],[20+i*8,5]],'#f7e1bd');
 }else if(p.key==='larut'){
  // Big but gentle giant elephant guardian
  oval(c,0,-16,62,54,'#718e88','#3c6264',5);oval(c,-42,-25,32,39,'#91afa0');
  oval(c,42,-25,32,39,'#91afa0');oval(c,0,-31,42,38,'#a3b8a7');
  polyline(c,[[0,-22],[0,5],[8,25],[14,13]],'#698d88',17);
  for(const side of [-1,1]){rect(c,side*28-4,-39,8,6,'#ffe2a7');line(c,side*23,-2,side*37,21,'#fff0cf',7);}
 }else if(p.key==='kancil'){
  oval(c,0,-13,45,62,'#604d81','#312c5c',5);
  for(const side of [-1,1]){path(c,[[side*16,-52],[side*30,-96],[side*34,-65],[side*25,-44]],'#9d81ac','#382e60',3);}
  oval(c,0,-41,41,35,'#826ba0');rect(c,-20,-46,11,9,'#ffe3a4');rect(c,10,-46,11,9,'#ffe3a4');
  path(c,[[-20,-18],[0,4],[20,-18]],'#d2afae','#4b3862',4);
 }else{
  for(let i=0;i<9;i++){const xx=i*17-66;path(c,[[xx,-48],[xx+9,-112-hash(i)%27],[xx+18,-50]],i%2?'#a5c2be':'#627e96','#3b5b65',2);}
  oval(c,0,-44,39,35,'#d8dad2','#567783',4);rect(c,-20,-49,12,8,'#ffdb94');rect(c,10,-49,12,8,'#ffdb94');
  rect(c,-37,-22,74,36,'#718e92');line(c,-29,-11,30,7,'#b8d3c0',4);
 }
 c.restore();
}
function arena(c,p,t,ox){
 const x=21.5*STEP-ox,y=222;
 if(x<-190||x>W+195)return;
 // Stage is visible early, but boss is only active at the end.
 oval(c,x,y,145,78,'#15515c','#aac6a5',4);
 for(let i=0;i<10;i++){
  const a=i*6.283/10,xx=x+Math.cos(a)*110,yy=y+Math.sin(a)*57;
  stone(c,xx,yy+10,p,i);if(i%3===0)lantern(c,xx,yy-11,t);
 }
 oval(c,x,y+22,87,37,'#67897e','#d1d7ba',5);
 for(let i=0;i<6;i++){const a=i*6.283/6;line(c,x,y+24,x+Math.cos(a)*76,y+24+Math.sin(a)*26,'#a2b3a1',2)}
 oval(c,x,y+25,22,11,'#a9bbae','#e3d9b7',2);
 if(p.key==='chini')dragon(c,x,y-14,t,p);
 else bossOther(c,x,y-6,p,t);
}
function fx(c,x,y,elem,t){
 const palette={api:'#ff8552',angin:'#d1ffc4',petir:'#ffdf5a',tanah:'#d7bb89',air:'#89dffe'};
 const color=palette[elem]||palette.api,rad=(Math.sin(t*4)+1)*7+26;
 glow(c,x,y-55,color+'99',70);
 for(let i=0;i<12;i++){const a=i*6.283/12+t*2;const px=x+Math.cos(a)*rad,py=y-55+Math.sin(a)*rad*.6;rect(c,px,py,3+i%3,4,color)}
}
function miniMap(c,p,ox,px=20,py=22){
 rect(c,px-7,py-8,91,54,'#102f3acb');rect(c,px-5,py-6,87,50,'#e4c994');
 rect(c,px-2,py-3,81,43,p.sky[1]);
 for(let i=0;i<5;i++){let a=px+i*15;rect(c,a+2,py+13,13,9,p.ground[1]);rect(c,a+5,py+10,9,12,p.ground[2])}
 oval(c,px+68,py+17,5,5,'#d25b52');rect(c,px+Math.min(73,Math.max(3,(ox/600)*65)),py+18,6,5,'#faebaf');
}
export function renderStory(canvas,opts={}){
 if(!canvas)return; if(canvas.width!==W)canvas.width=W;if(canvas.height!==H)canvas.height=H;
 const c=canvas.getContext('2d',{alpha:false});if(!c)return;
 c.imageSmoothingEnabled=false;
 const index=Math.max(0,Math.min(REALMS.length-1,opts.realm??0));
 const p=REALMS[index],t=opts.time||0,phase=opts.phase||'obstacles',cleared=opts.cleared||0;
 const hasHero=opts.hero!==null;
 const heroX=typeof opts.x==='number'?Math.max(1.5,Math.min(22,opts.x)):16.5;
 const heroY=typeof opts.y==='number'?Math.max(7.5,Math.min(12,opts.y)):10;
 const target=hasHero?Math.max(0,Math.min(LENGTH*STEP-W,heroX*STEP-W*.43)):Math.max(0,LENGTH*STEP-W);
 let cam=cameraState.get(canvas);
 if(!cam){cam={x:target,last:t};cameraState.set(canvas,cam)}
 cam.x+=(target-cam.x)*Math.min(1,.3+Math.max(0,t-cam.last)*6);cam.last=t;
 const ox=Math.round(cam.x);
 terrain(c,p,t,ox);regionalArt(c,p,t,ox);mapDecor(c,p,t,ox);
 // Five guardians line the winding footpath; each is replaced by a seal when solved.
 const encounters=[5,8.5,12,15.5,19];
 for(let i=0;i<5;i++){
  const sx=encounters[i]*STEP-ox,sy=218+(i%2)*10;
  if(sx<-40||sx>W+40)continue;
  if(i<cleared){oval(c,sx,sy,12,6,'#557866','#d9d5ad',2);rect(c,sx-2,sy-10,5,7,'#e2d7a5');}
  else if(phase==='obstacles')imp(c,sx,sy,i,t,p);
 }
 // Four original non-China-inspired environments retain the same 2D camera and landmarks.
 if(phase==='boss')arena(c,p,t,ox);
 else if(21.5*STEP-ox<W+120) {
  const x=21.5*STEP-ox;
  oval(c,x,210,88,34,p.ground[1],p.highlight,2);
  path(c,[[x-20,202],[x,171],[x+19,202],[x,230]],'#d0bb91','#557c70',3);
  rect(c,x-3,195,7,20,p.highlight);
 }
 const members=(opts.peers||[]).filter(a=>Array.isArray(a.pos));
 for(const peer of members){
  const sx=peer.pos[0]*STEP-ox,sy=197+(peer.pos[1]-7.5)*22;
  if(sx>-35&&sx<W+35)hero(c,sx,sy,peer.hero||'tuah',opts.element||'api',t,false);
 }
 if(hasHero){
  const sx=heroX*STEP-ox,sy=197+(heroY-7.5)*22;
  hero(c,sx,sy,opts.hero||'tuah',opts.element||'api',t,!!opts.walking);
  if(opts.impact?.kind==='story-hit')fx(c,21.5*STEP-ox,151,opts.impact.element||'petir',t);
  if(opts.impact?.kind==='story-hurt')glow(c,sx,sy-20,'#ff657077',51);
 }
 miniMap(c,p,ox);
 // Sunlight shafts and vignette: gives the map depth without destroying pixel crispness.
 const grd=c.createLinearGradient(0,0,W,H);grd.addColorStop(0,'#ffe6aa18');grd.addColorStop(.45,'#ffffff00');grd.addColorStop(1,'#08232f45');
 rect(c,0,0,W,H,grd);
 const edge=c.createRadialGradient(W*.52,H*.42,W*.29,W*.52,H*.42,W*.74);
 edge.addColorStop(0,'#00000000');edge.addColorStop(1,'#07192372');
 rect(c,0,0,W,H,edge);
}
