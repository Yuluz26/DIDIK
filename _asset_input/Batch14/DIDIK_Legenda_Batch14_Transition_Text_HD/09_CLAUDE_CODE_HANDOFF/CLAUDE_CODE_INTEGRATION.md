# Prompt untuk Claude Code — Integrasi DIDIK Legenda Transition Text HD (Batch 14)

Integrate the provided Batch 14 transition text assets into DIDIK Legenda Story Mode's existing SvelteKit battle flow.

1. Inspect the repository and existing battle event state before editing. Preserve all 8 existing 2D games and unrelated design.
2. Read `README_FIRST.md` and `asset_manifest.json`. Copy only assets actively referenced into `live/web/static/assets/didik/transition_text/`. Do not commit the full asset input folder, ZIPs, GIF previews or contact sheets.
3. Display `boss_akan_menyerang` when server confirms incorrect boss question and before playing boss counterattack animation. Never display it from speculative client state.
4. Map `jawapan_betul`, `jawapan_salah`, `giliran_awak`, `boss_muncul`, `boss_dikalahkan`, `nyawa_berkurang`, `nyawa_bertambah`, `senjata_diperoleh`, `dunia_seterusnya`, and `pertarungan_bermula` to already-existing server-authoritative events.
5. Use `banner_png` for simplest integration, or `text_only_png` when overlaying game-specific particles. For six key banners, use APNG or frame-sequence animation; APNG/PNG have real transparency and GIF is preview-only.
6. Keep overlay centred and non-interactive: `pointer-events:none`, `max-width:100vw`, aspect-ratio 4/1, avoid covering quiz answer buttons; use transitions before/after answering, never block the question form for too long.
7. Implement `prefers-reduced-motion` (static PNG) and a text equivalent for accessibility using the `text_ms` string from the manifest. Avoid flashing more than 3 times per second.
8. Validate Desktop + mobile responsive layouts and run `npm run check` and `npm run build` from `live/web`. Take screenshots from a working game, not only mockups. Do not merge/deploy without approval.

Example Svelte 5 snippet (adjust to project state flow):

```svelte
<script lang="ts">
  let { bannerId, message } : { bannerId: string; message: string } = $props();
  const path = '/assets/didik/transition_text/';
</script>
{#if bannerId}
  <div class="jrpg-transition" aria-live="assertive" role="status">
    <img aria-hidden="true" src={`${path}${bannerId}.png`} alt="" />
    <span class="sr-only">{message}</span>
  </div>
{/if}
<style>
  .jrpg-transition {position:absolute;left:50%;top:23%;transform:translateX(-50%);width:min(94vw,960px);z-index:30;pointer-events:none;animation:appear .8s ease both;}
  .jrpg-transition img {width:100%;display:block;}
  .sr-only {position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;}
  @keyframes appear {from{opacity:0;filter:blur(8px);transform:translateY(-16px) scale(.96)}to{opacity:1;filter:blur(0);transform:translateY(0) scale(1)}}
  @media(prefers-reduced-motion:reduce){.jrpg-transition{animation:none}}
</style>
```

Note: snippet's `path` assumes you copied flat banner PNG files from `01_STATIC_BANNERS_PNG/`. Adjust imports and exact battle events to repository.
