<!-- Legenda: mobile-first 2D adventure. Parents only provide questions and pick this game. -->
<script lang="ts">
  import { onMount } from 'svelte';
  import type { RoomClient } from '$lib/room.svelte';
  import type { Me, Person } from '$lib/types';
  import { livePositions } from '../forest/positions.svelte';
  import Joystick from '../forest/Joystick.svelte';
  import QuestionCard from '$lib/questions/QuestionCard.svelte';
  import Answer from '$lib/questions/Answer.svelte';
  import Feedback from '$lib/questions/Feedback.svelte';
  import Countdown from '$ui/Countdown.svelte';
  import StoryScene from './StoryScene.svelte';
  import { HEROES, REALMS } from './art.js';

  let { client, game, me, people }: {
    client: RoomClient; game: any; me: Me; people: Map<string, Person>;
  } = $props();

  const world = $derived(game.world ?? {});
  const seat = $derived(game.seat ?? {});
  const story = $derived(seat.story ?? {});
  const realm = $derived(REALMS[Math.min(story.realm ?? 0, 4)]);
  const positions = livePositions(client);
  const mine = $derived.by(() => {
    const fromSocket = positions.all[me.id];
    if (fromSocket) return fromSocket;
    const peer = world.players?.find((p: any) => p.id === me.id);
    return peer ? {x: peer.pos[0], y: peer.pos[1], f: 1} : undefined;
  });
  const x = $derived(mine?.x ?? 2.5);
  const approaching = $derived(story.phase === 'boss' ? 21.5 : (world.foes?.[story.obstacle ?? 0] ?? 5));
  const near = $derived(Math.abs(x - approaching) <= 1.6);
  const choosing = $derived(seat.step === 'question' || seat.step === 'result');
  const halves = $derived(story.hearts ?? 12);
  const hitPoints = $derived(world.bossHearts ?? 5);
  const elementNames: Record<string,string> = {api:'Api',angin:'Angin',petir:'Petir',tanah:'Tanah',air:'Air'};
  const elementGlyphs: Record<string,string> = {api:'🔥',angin:'💨',petir:'⚡',tanah:'🪨',air:'💧'};
  const keys: Record<string,[number,number]> = {
    ArrowUp:[0,-1],ArrowDown:[0,1],ArrowLeft:[-1,0],ArrowRight:[1,0],
    w:[0,-1],s:[0,1],a:[-1,0],d:[1,0]
  };
  const held = new Set<string>();
  let speed = {dx:0,dy:0};
  let notice = $state('');
  function move(dx:number,dy:number){
    if(choosing || seat.step !== 'explore'){dx=0;dy=0;}
    if(Math.abs(speed.dx-dx)<.02 && Math.abs(speed.dy-dy)<.02)return;
    speed={dx,dy};
    client.send({t:'move',dx,dy});
  }
  // Hold a key to walk; input refresh is needed because the server expires old input.
  onMount(()=>{
    const down=(e:KeyboardEvent)=>{if((e.target as HTMLElement).closest('input,textarea,select'))return;
      const k=e.key.length===1?e.key.toLowerCase():e.key;
      if(keys[k]){held.add(k);e.preventDefault();}
      if(k===' '||k==='Enter'){if(seat.step==='explore'){client.send({t:'engage'});e.preventDefault();}}
    };
    const up=(e:KeyboardEvent)=>held.delete(e.key.length===1?e.key.toLowerCase():e.key);
    const blur=()=>{held.clear();move(0,0)};
    window.addEventListener('keydown',down);window.addEventListener('keyup',up);window.addEventListener('blur',blur);
    const pump=setInterval(()=>{
      if(!held.size){if(speed.dx||speed.dy)move(0,0);return;}
      let dx=0,dy=0;
      for(const key of held){const direction=keys[key];if(direction){dx+=direction[0];dy+=direction[1];}}
      const size=Math.max(1,Math.hypot(dx,dy));
      client.send({t:'move',dx:dx/size,dy:dy/size});
    },90);
    return()=>{clearInterval(pump);window.removeEventListener('keydown',down);window.removeEventListener('keyup',up);window.removeEventListener('blur',blur);client.send({t:'move',dx:0,dy:0});};
  });
  function engage(){client.send({t:'engage'});}
</script>

{#if game.stage === 'intro'}
  <main class="intro">
    <p class="eyebrow">DIDIK · PENGEMBARAAN 8-BIT</p>
    <Countdown clock={game.clock} offset={client.offset} title="Legenda Melayu" />
  </main>
{:else}
  <main class="story">
    <header class="top">
      <div>
        <div class="eyebrow">DIDIK <span> / </span> STORY MODE <span> / </span> DUNIA {(story.realm??0)+1} DARIPADA 5</div>
        <h1>{realm.name} <span class="subtitle">{realm.boss}</span></h1>
      </div>
      <div class="stat">
        <span>NYAWA</span>
        <strong>{(halves/2).toFixed(1)} / 6</strong>
        <div class="heartbar" aria-label="{halves/2} daripada 6 nyawa">
          {#each Array(12) as _,i}<i class:alive={i<halves}></i>{/each}
        </div>
      </div>
    </header>

    <nav class="chapters" aria-label="Kemajuan lima dunia">
      {#each REALMS as place,i}
        <div class:current={i===(story.realm??0)} class:clear={i<(story.realm??0)}>
          <span>{i<(story.realm??0)?'✓':String(i+1).padStart(2,'0')}</span>
          <span class="chapter-name">{place.name}</span>
        </div>
      {/each}
    </nav>

    <section class="arena">
      <div class="arena-head">
        <span class="chapter-label">{story.phase==='boss'?'BOSS ENCOUNTER':'THE JOURNEY'}</span>
        <span>{realm.subtitle}</span>
        <span class="chapter-label">{story.phase==='boss'?'PERTARUNGAN':'HALANGAN '+Math.min(5,(story.obstacle??0)+1)+'/5'}</span>
      </div>
      <StoryScene {world} hero={story.hero??'tuah'} element={story.weapon??'api'}
        phase={story.phase??'obstacles'} cleared={story.obstacle??0} {x} meId={me.id}
        walking={!!positions.moving[me.id]} />
      {#if story.phase==='boss'}
        <div class="bossline">
          <strong>{realm.boss}</strong>
          <div class="bossbars" aria-label="Nyawa boss {hitPoints} daripada 5">
            {#each Array(5) as _,i}<span class:on={i<hitPoints}></span>{/each}
          </div>
          <small>5 HP</small>
        </div>
      {:else}
        <div class="progress-track">
          {#each Array(5) as _,i}
            <span class:done={i<(story.obstacle??0)}>◆</span>
          {/each}
          <small>{story.obstacle??0} / 5 HALANGAN</small>
        </div>
      {/if}
    </section>

    {#if seat.step==='explore'}
      <section class="command">
        <div class="guide">
          <p class="label">{story.phase==='boss'?'AKHIR PERJALANAN':'MISI SEMASA'}</p>
          <h2>{story.phase==='boss'?'Tumbangkan '+realm.boss:'Temui penjaga halangan'}</h2>
          <p>{story.phase==='boss'
            ? 'Jawab betul untuk satu serangan percuma. Salah, boss menyerang dan 1.5 nyawa hilang.'
            : 'Berjalan ke arah musuh. Jawab lima soalan untuk mendapat senjata elemen.'}</p>
        </div>
        <div class="controls">
          <Joystick onmove={move}/>
          <button class="action" type="button" disabled={!near} onclick={engage}>
            {story.phase==='boss'?'⚔ LAWAN BOSS':'⚔ LAWAN MUSUH'}
            <small>{near?'TEKAN UNTUK BERTARUNG':'DEKATI MUSUH DAHULU'}</small>
          </button>
        </div>
      </section>
    {/if}

    {#if story.weapons && seat.step!=='victory'}
      <section class="weapons">
        <div class="heading"><span class="label">ARSENAL PAHLAWAN</span><strong>5 Elemen</strong></div>
        <div class="weapon-row">
          {#each ['api','angin','petir','tanah','air'] as e}
            <button type="button" class:active={story.weapon===e} onclick={()=>client.send({t:'element',element:e})}
              aria-pressed={story.weapon===e}>
              <span class="element">{elementGlyphs[e]}</span><strong>{elementNames[e]}</strong>
            </button>
          {/each}
        </div>
        <p class="tip">Setiap senjata menghasilkan kesan serangan berbeza. Elemen kelemahan boss memberikan mata bonus.</p>
      </section>
    {/if}

    {#if seat.step==='explore' && !story.weapons}
      <section class="heroes">
        <span class="label">PILIH PAHLAWAN</span>
        <div class="hero-row">
          {#each HEROES as h}
            <button type="button" class:active={story.hero===h.key} onclick={()=>client.send({t:'hero',hero:h.key})} aria-pressed={story.hero===h.key}>{h.name}</button>
          {/each}
        </div>
      </section>
    {/if}

    {#if seat.step==='question' || seat.step==='result'}
      <div class="question-overlay">
        <section class="question-panel" aria-label="Soalan pertempuran">
          <div class="battle-top">
            <span>{story.phase==='boss'?'⚔ PERTARUNGAN BOSS':'⚔ HALANGAN '+(story.obstacle??0)+'/5'}</span>
            <span>NYAWA {(halves/2).toFixed(1)} ♥</span>
          </div>
          {#if seat.question}
            <QuestionCard question={seat.question}/>
            {#if seat.step==='result' && seat.result}
              <Feedback correct={seat.result.correct} fraction={seat.result.fraction}
                extra={seat.result.correct
                  ? story.phase==='boss'?'Serangan berjaya! Boss kehilangan satu bar nyawa.':'Hebat! Nyawa pulih 0.5.'
                  :'Musuh menyerang! Kamu kehilangan 1.5 nyawa.'}/>
            {/if}
            <Answer question={seat.question} disabled={seat.step!=='question'}
              mine={seat.step==='result'?seat.result?.answer:undefined}
              reveal={seat.step==='result'?seat.result?.reveal:null}
              allRight={seat.result?.correct}
              onanswer={(a)=>client.send({t:'answer',a})}/>
          {/if}
          {#if seat.step==='result'}
            <button type="button" class="advance" onclick={()=>client.send({t:'next'})}>
              {halves<=0?'Lihat keputusan':'Teruskan pengembaraan →'}
            </button>
          {/if}
        </section>
      </div>
    {/if}

    {#if seat.step==='dead'}
      <section class="end-panel" role="status">
        <h2>Perjalanan belum berakhir.</h2>
        <p>Nyawa habis di {realm.name}. Cuba lagi dari checkpoint dunia ini. Soalan masih boleh dipelajari semula.</p>
        <button type="button" class="advance" onclick={()=>client.send({t:'retry'})}>Cuba semula ↻</button>
      </section>
    {/if}
    {#if seat.step==='victory'}
      <section class="end-panel win" role="status">
        <h2>Legenda sudah tercipta!</h2>
        <p>Kelima-lima dunia berjaya dibebaskan. Tahniah, pendekar ilmu!</p>
      </section>
    {/if}
  </main>
{/if}

<style>
  .story{--gold:#f7cc83;--cream:#fff5de;min-height:100dvh;background:#0f1927;color:#ede8d9;
    padding:clamp(12px,2vw,26px);font-family:var(--font-body,'Nunito',sans-serif);overflow:hidden}
  .top{display:flex;justify-content:space-between;align-items:flex-start;gap:12px;max-width:1140px;margin:0 auto 12px}
  .eyebrow,.label,.chapter-label{font-size:.65rem;letter-spacing:.16em;color:#aebccc;font-weight:900}
  .eyebrow span{color:#e6a960;margin:0 6px}
  .top h1{font-family:'Pixelify Sans',var(--font-display,sans-serif);font-size:clamp(1.5rem,3vw,2.45rem);font-weight:800;margin:6px 0;line-height:1.05;color:#f9e6b7}
  .subtitle{display:block;font:700 .8rem var(--font-body,'Nunito',sans-serif);color:#9dadb5;letter-spacing:.04em;margin-top:7px}
  .stat{min-width:110px;text-align:right}.stat>span{font-size:.62rem;letter-spacing:.2em;color:#abc0c7}.stat strong{display:block;font-size:1.15rem;color:#ffd29c}
  .heartbar{display:flex;gap:2px;justify-content:flex-end;margin-top:5px}.heartbar i{width:7px;height:11px;display:block;background:#384253;transform:skew(-10deg)}.heartbar i.alive{background:#ed7282}
  .chapters{max-width:1140px;margin:0 auto 13px;display:grid;grid-template-columns:repeat(5,1fr);gap:5px}
  .chapters div{display:flex;align-items:center;gap:8px;padding:7px 10px;border:1px solid #344253;border-radius:5px;background:#182838;color:#7f909d}
  .chapters div.current{border-color:#e4b46e;color:#ffdeaa;background:#283243}.chapters div.clear{border-color:#668a7d;color:#b7e4b9}
  .chapters span:first-child{font-family:'Pixelify Sans',monospace;font-size:.94rem}.chapter-name{font-size:.7rem;font-weight:800}
  .arena{max-width:1140px;margin:0 auto}
  .arena-head{display:flex;justify-content:space-between;gap:12px;align-items:center;padding:8px 4px;font-size:.7rem;color:#afb9bf;text-align:center}
  .arena-head .chapter-label{color:#e7c17f;flex:none}
  .bossline,.progress-track{display:flex;align-items:center;gap:13px;justify-content:space-between;padding:11px 3px;font-size:.8rem}
  .bossline strong{color:#ffdab4}.bossbars{flex:1;max-width:560px;display:flex;gap:5px}.bossbars span{height:12px;flex:1;background:#3d3440;border:1px solid #78606a;transform:skew(-13deg)}.bossbars span.on{background:#b74b66;border-color:#f28fa0}
  .bossline small,.progress-track small{color:#8fa0b0;letter-spacing:.08em;font-weight:900}
  .progress-track{justify-content:center}.progress-track span{font-size:1.25rem;color:#546277}.progress-track span.done{color:#f2d68d}
  .command,.weapons,.heroes,.end-panel{max-width:1140px;margin:12px auto 0;border:1px solid #344356;border-radius:10px;background:#172535;padding:14px}
  .command{display:flex;justify-content:space-between;align-items:center;gap:15px}.guide h2{font-size:1rem;color:#ffe0ae;margin:5px 0}.guide p:last-child{font-size:.83rem;color:#aebbc7;max-width:530px}.controls{display:flex;align-items:center;gap:9px}
  .action,.advance{border:1px solid #fae2a0;border-radius:6px;background:#e5ab60;color:#19212a;padding:14px 18px;font-weight:1000;cursor:pointer;box-shadow:inset 0 -4px 0 #ae733d}
  .action:disabled{opacity:.4;cursor:not-allowed}.action small{font-size:.55rem;letter-spacing:.03em;display:block;margin-top:2px}
  .heading{display:flex;justify-content:space-between;align-items:center}.heading strong{color:var(--gold)}
  .weapon-row{display:grid;grid-template-columns:repeat(5,1fr);gap:7px;margin:10px 0}
  .weapon-row button{border:1px solid #44546b;background:#203044;border-radius:6px;color:#c9d8e4;padding:8px 3px;cursor:pointer}
  .weapon-row button.active{border-color:#f9d38f;background:#3e3941;color:#fff0c4}
  .weapon-row strong{display:block;font-size:.72rem}.element{display:block;font-size:1.3rem;margin-bottom:4px}
  .tip{font-size:.72rem;color:#9fadb7}
  .hero-row{display:flex;flex-wrap:wrap;gap:7px;margin-top:9px}
  .hero-row button{border:1px solid #53637b;background:#263749;border-radius:4px;padding:8px 10px;color:#d9e5e6;font-size:.75rem;cursor:pointer}
  .hero-row button.active{border-color:var(--gold);color:var(--gold)}
  .intro{background:#111b29;min-height:100dvh;padding:24px;color:#fff;text-align:center}
  .question-overlay{position:fixed;inset:0;z-index:40;display:grid;place-items:center;overflow:auto;background:#080e18df;padding:14px}
  .question-panel{background:#fff7e8;color:#243043;border:5px solid #c9a16c;border-radius:10px;box-shadow:0 0 0 5px #273748,0 30px 90px #030911;
    width:min(560px,100%);max-height:95dvh;overflow-y:auto;padding:clamp(14px,3vw,24px);display:grid;gap:14px}
  .battle-top{display:flex;justify-content:space-between;gap:10px;font-size:.63rem;letter-spacing:.1em;font-weight:1000;color:#715b49}
  .advance{width:100%}.end-panel{text-align:center}.end-panel h2{font-size:1.5rem;color:#ffe1a7}.end-panel p{margin:10px auto;max-width:510px;color:#d1d8dc}.end-panel.win{border-color:#87c9a1}
  @media(max-width:690px){.story{padding:9px}.chapters{gap:3px}.chapters div{padding:7px 4px;justify-content:center}.chapter-name{display:none}
    .arena-head{font-size:.58rem}.arena-head>span:nth-child(2){display:none}.command{flex-direction:column;align-items:stretch;padding:10px}
    .controls{justify-content:space-between}.top h1{font-size:1.5rem}.weapons{padding:9px}.weapon-row{gap:3px}.weapon-row button{padding:7px 0}
    .weapon-row strong{font-size:.59rem}.stat strong{font-size:.92rem}}
  @media(prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}
</style>
