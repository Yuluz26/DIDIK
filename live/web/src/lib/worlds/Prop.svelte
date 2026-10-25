<!--
	Things that stand in the worlds, in pixel art seen from the front and a little above. The bottom
	centre of every picture is its foot, so the world can sort props and characters by how far down the
	screen they stand (things lower down are in front). The pictures are painted in lib/pixel/props.ts;
	Kampung Kita's buildings are drawn by Building. A banner, an arch or a gate carries a word, set in
	the pixel font over the sign.
-->
<script lang="ts">
	import { TILE } from '$lib/pixel/cache';
	import { propArt } from '$lib/pixel/props';
	import Sprite from '$lib/pixel/Sprite.svelte';
	import Building, { BUILDING_KINDS } from './Building.svelte';

	let {
		kind,
		variant = 0,
		tile = 44,
		state = '',
		progress = 0
	}: { kind: string; variant?: number; tile?: number; state?: string; progress?: number } = $props();

	const s = $derived(tile / TILE);
	const art = $derived(propArt(kind, variant, state));
	const word = $derived(kind === 'gate' ? 'KELUAR' : kind === 'arch' ? state || 'SELAMAT DATANG' : kind === 'banner' ? state : '');
	const colour = $derived(kind === 'banner' && variant === 0 ? '#e2483d' : kind === 'banner' ? '#ffffff' : '#6b4220');
</script>

{#if BUILDING_KINDS.includes(kind)}
	<Building {kind} {tile} {state} {progress} />
{:else if art}
	<span class="prop prop-{kind}" style:--s="{s}px">
		<Sprite sheet={art.sheet} {s} frames={art.frames} ms={art.ms} />
		{#if art.sign && word}
			<span
				class="sign"
				style:left="{art.sign.x * s}px"
				style:top="{art.sign.y * s}px"
				style:width="{art.sign.w * s}px"
				style:height="{art.sign.h * s}px"
				style:color={colour}
				style:font-size="{Math.min(art.sign.h * s * 0.78, (art.sign.w * s) / (word.length * 0.62))}px"
			>{word}</span>
		{/if}
	</span>
{/if}

<style>
	.prop {
		position: relative;
		display: block;
		line-height: 0;
	}
	.sign {
		position: absolute;
		display: grid;
		place-items: center;
		font-family: var(--font-pixel);
		font-weight: 700;
		line-height: 1;
		letter-spacing: 0.04em;
		white-space: nowrap;
		pointer-events: none;
	}
</style>
