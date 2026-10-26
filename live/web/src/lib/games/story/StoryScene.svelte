<!-- Canvas is genuine nearest-neighbour pixel art, never a 3D/WebGL scene. -->
<script lang="ts">
  import { onMount } from 'svelte';
  import { renderStory } from './art.js';
  let {
    world, hero = 'tuah', element = 'api', phase = 'obstacles', cleared = 0,
    x = 2.5, y = 10, meId = '', walking = false, impact = null
  }: {
    world: any; hero?: string | null; element?: string; phase?: string;
    cleared?: number; x?: number; y?: number; meId?: string; walking?: boolean; impact?: {kind:string;element?:string}|null;
  } = $props();
  let canvas: HTMLCanvasElement;
  onMount(() => {
    let frame = 0;
    let last = 0;
    function paint(t: number) {
      if (t - last >= 85) {
        last = t;
        renderStory(canvas, {
          realm: world?.realm ?? 0, hero, element, phase, cleared, x, y, walking, impact,
          peers: (world?.players ?? []).filter((p: any) => p.id !== meId),
          bossHp: world?.bossHearts ?? 5, time: t / 1000
        });
      }
      frame = requestAnimationFrame(paint);
    }
    frame = requestAnimationFrame(paint);
    return () => cancelAnimationFrame(frame);
  });
</script>

<div class="pixel-stage" role="img" aria-label="Dunia pengembaraan 2D dalam gaya pixel-art 8-bit">
  <canvas bind:this={canvas} width="640" height="360" aria-label="Pemandangan {world?.scene?.title ?? 'Legenda Melayu'}"></canvas>
  <div class="corner tl" aria-hidden="true"></div>
  <div class="corner tr" aria-hidden="true"></div>
  <div class="corner bl" aria-hidden="true"></div>
  <div class="corner br" aria-hidden="true"></div>
</div>

<style>
  .pixel-stage{position:relative;width:100%;overflow:hidden;border-radius:12px;
    padding:5px;background:#15202c;box-shadow:0 20px 52px rgba(10,20,32,.3),inset 0 0 0 1px rgba(255,232,167,.4)}
  canvas{display:block;width:100%;height:auto;aspect-ratio:16/9;image-rendering:pixelated;background:#142735}
  .corner{position:absolute;width:10px;height:10px;border-color:#f8dca1;border-style:solid;pointer-events:none}
  .tl{left:10px;top:10px;border-width:2px 0 0 2px}.tr{right:10px;top:10px;border-width:2px 2px 0 0}
  .bl{left:10px;bottom:10px;border-width:0 0 2px 2px}.br{right:10px;bottom:10px;border-width:0 2px 2px 0}
</style>
