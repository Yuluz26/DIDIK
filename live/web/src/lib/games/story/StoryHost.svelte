<!-- Large shared-screen presentation for parents, teachers and multiplayer spectators. -->
<script lang="ts">
 import type {RoomClient} from '$lib/room.svelte';
 import type {Person} from '$lib/types';
 import StoryScene from './StoryScene.svelte';
 import { REALMS } from './art.js';
 let { client, game, people }: {client:RoomClient;game:any;people:Map<string,Person>}=$props();
 const world=$derived(game.world??{});
 const realm=$derived(REALMS[Math.min(world.realm??0,4)]);
</script>

<section class="host">
 <header class="heading">
  <div><span class="tag">DIDIK / LEGENDA MELAYU</span><h1>STORY MODE</h1><p>{realm.name} — {realm.boss}</p></div>
  <div class="chapter">DUNIA <strong>{(world.realm??0)+1} / 5</strong></div>
 </header>
 <StoryScene {world} hero={null} />
 <div class="status">
  <div>
   <span class="tag">BOSS GUARDIAN</span>
   <h2>{realm.boss}</h2>
   <div class="bars">{#each Array(5) as _,i}<span class:on={i<(world.bossHearts??5)}></span>{/each}</div>
  </div>
  <div><span class="tag">PARTY MEMBERS</span><strong>{world.players?.length??0} PEJUANG</strong><p>Setiap pelajar ada 6 nyawa sendiri.</p></div>
 </div>
 <div class="roster">
  {#each world.players??[] as person}
   <div><strong>{people.get(person.id)?.name??'Pendekar'}</strong><span>{(person.hearts/2).toFixed(1)} ♥</span></div>
  {/each}
 </div>
 <div class="actions">
  <button type="button" class="btn btn--sea" onclick={()=>client.send({t:'pause'})}>Jeda / sambung</button>
  <button type="button" class="btn btn--plain" onclick={()=>client.send({t:'end'})}>Tamatkan permainan</button>
 </div>
</section>
<style>
 .host{background:#101c2b;border-radius:16px;padding:clamp(14px,2.5vw,30px);min-height:480px;color:#f7e7c4;display:grid;gap:15px}
 .heading,.status{display:flex;justify-content:space-between;align-items:center;gap:16px}
 .tag{font-size:.65rem;letter-spacing:.16em;color:#9bb8c6;font-weight:900}
 .heading h1{font-family:'Pixelify Sans',monospace;font-size:2rem;line-height:1.1;color:#ffe0a8}
 .heading p,.status p{color:#a9bcc3}.chapter{text-align:right;font-size:.8rem;letter-spacing:.1em;color:#9db1b8}.chapter strong{display:block;font-size:1.4rem;color:#ffe1aa}
 .status{background:#1a2c3e;border:1px solid #435468;padding:14px;border-radius:8px}
 .status h2{font-size:1.2rem;color:#edc68a}.status strong{display:block;color:#edc68a}
 .bars{display:flex;gap:5px;width:min(340px,47vw);margin-top:7px}.bars span{flex:1;height:12px;border:1px solid #6e4b5c;background:#3b3544;transform:skew(-13deg)}.bars span.on{background:#c75568}
 .roster{display:flex;gap:7px;flex-wrap:wrap}.roster div{display:flex;gap:10px;padding:8px 12px;background:#26374a;border:1px solid #476174;border-radius:6px;font-size:.75rem}.roster span{color:#ed8b98}
 .actions{display:flex;gap:8px;justify-content:flex-end}
 @media(max-width:600px){.heading,.status{align-items:flex-start}.status{flex-direction:column}.bars{width:70vw}}
</style>
