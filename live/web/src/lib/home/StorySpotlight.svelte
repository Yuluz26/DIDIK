<!-- Five legendary locations, rendered by the same 8-bit canvas used inside the actual game. -->
<script lang="ts">
 import StoryScene from '$lib/games/story/StoryScene.svelte';
 import {REALMS} from '$lib/games/story/art.js';
 let selected=$state(0);
 const world=$derived({realm:selected,scene:REALMS[selected],bossHearts:5,players:[]});
</script>
<section id="legenda" class="spotlight" aria-labelledby="legend-title">
 <div class="wrap story-inner">
  <header>
   <span class="overline">DIDIK / 01 — DUNIA BAHARU</span>
   <h2 id="legend-title">Lima dunia. Satu legenda.</h2>
   <p>Masuki dunia mitos Melayu dalam pengembaraan pixel-art moden. Tulis sepuluh soalan, pilih Story Mode, dan berjuang solo atau bersama kawan.</p>
  </header>
  <div class="preview">
   <div class="frame"><StoryScene {world} hero="tuah" x={17.8} y={10} phase="boss" element="petir" /></div>
   <aside>
    <span class="overline">PILIH DUNIA</span>
    <div class="realms">
     {#each REALMS as realm,i}
      <button type="button" class:active={selected===i} onclick={()=>selected=i} aria-pressed={selected===i}>
       <span class="index">{String(i+1).padStart(2,'0')}</span>
       <span class="place">{realm.name}<small>{realm.boss}</small></span>
       <span class="chevron">↗</span>
      </button>
     {/each}
    </div>
    <p class="note">Ilustrasi ini dijana secara langsung oleh enjin pixel 2D permainan DIDIK, tanpa grafik 3D.</p>
    <a class="cta" href="/ibu-bapa">Cipta kuiz &amp; pilih Story Mode <span>→</span></a>
   </aside>
  </div>
 </div>
</section>
<style>
 .spotlight{background:#101a29;color:#e9dfc8;padding:clamp(50px,7vw,92px) 0;overflow:hidden}
 .story-inner{display:grid;gap:28px}
 header{max-width:720px}header h2{font-family:'Pixelify Sans',var(--font-display,sans-serif);color:#ffe3ad;font-size:clamp(2.5rem,6vw,5.5rem);line-height:1;letter-spacing:-.04em;margin:14px 0}
 header p{color:#aebdc6;font-size:1.08rem;line-height:1.65}
 .overline{font-size:.67rem;font-weight:1000;letter-spacing:.2em;color:#d9aa71}
 .preview{display:grid;grid-template-columns:minmax(0,1.55fr) minmax(220px,.85fr);gap:28px;align-items:center}
 .realms{display:grid;margin-top:12px}
 .realms button{display:grid;grid-template-columns:38px 1fr 22px;gap:12px;align-items:center;border:0;border-bottom:1px solid #304153;background:none;color:#b8c9ce;padding:15px 11px;text-align:left;cursor:pointer;transition:background .15s}
 .realms button.active{background:#25374b;color:#ffdfaf}
 .realms button:hover{background:#203146}
 .index{color:#cfab74;font-family:'Pixelify Sans',monospace;font-size:1.1rem}
 .place{font-size:.95rem;font-weight:1000}.place small{display:block;font-size:.73rem;color:#95a9b3;margin-top:2px;font-weight:600}
 .chevron{font-size:1.2rem}
 .note{font-size:.75rem;color:#95a8b5;margin:15px 0}
 .cta{display:flex;align-items:center;justify-content:space-between;border-radius:6px;padding:16px 18px;background:#f0c081;color:#152333;font-weight:1000;text-decoration:none}
 @media(max-width:840px){.preview{grid-template-columns:1fr}.realms{grid-template-columns:1fr 1fr;gap:5px}.realms button{grid-template-columns:25px 1fr 10px;padding:10px 6px}.note{margin:10px 0}}
 @media(max-width:500px){.realms{grid-template-columns:1fr}}
</style>
