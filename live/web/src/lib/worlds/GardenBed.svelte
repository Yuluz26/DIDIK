<!--
	A raised bed in Kebun Ajaib, in pixels: a wooden frame with its soil seen from above, the crop
	growing on it, and along the front one drop for each watering the crop needs (blue once given).
	Land not bought yet is grass behind a dashed line. The foot is the middle of the front edge.
-->
<script lang="ts">
	import { TILE } from '$lib/pixel/cache';
	import Sprite from '$lib/pixel/Sprite.svelte';
	import Crop from './Crop.svelte';
	import { BED, CROP, bedSheet, dropSheet, sparkleSheet } from './garden';

	let {
		crop = null,
		stage = 0,
		need = 0,
		locked = false,
		tile = 44
	}: { crop?: string | null; stage?: number; need?: number; locked?: boolean; tile?: number } = $props();

	const s = $derived(tile / TILE);
	const ready = $derived(!!crop && stage >= need);
	const grow = $derived(need ? stage / need : 0);
	// Small crops grow three to a bed; a watermelon or a durian tree takes the whole bed.
	const spots = $derived(crop === 'tembikai' || crop === 'durian' ? [[23, 29]] : [[10, 27], [36, 27], [23, 30]]);
</script>

<span class="bed" style:width="{BED.w * s}px" style:height="{BED.h * s}px">
	<span class="at"><Sprite sheet={bedSheet(locked)} {s} /></span>
	{#if !locked && crop}
		{#each spots as [x, y] (`${x}-${y}`)}
			<span class="at crop" style:left="{(x - CROP.w / 2) * s}px" style:top="{(y - CROP.h + 3) * s}px"><Crop {crop} {grow} {ready} {s} /></span>
		{/each}
		{#if need}
			<span class="drops" style:bottom="{1.5 * s}px">
				{#each Array.from({ length: need }, (_, i) => i) as i (i)}
					<Sprite sheet={dropSheet(i < stage)} {s} />
				{/each}
			</span>
		{/if}
	{/if}
	{#if ready}
		<span class="at spark" style:left="{34 * s}px" style:top="{8 * s}px"><Sprite sheet={sparkleSheet()} {s} frames={2} ms={900} /></span>
		<span class="at spark" style:left="{2 * s}px" style:top="{14 * s}px"><Sprite sheet={sparkleSheet()} {s} frames={2} ms={900} delay={450} /></span>
	{/if}
</span>

<style>
	.bed {
		position: relative;
		display: block;
		line-height: 0;
	}
	.at {
		position: absolute;
		left: 0;
		top: 0;
		line-height: 0;
	}
	.crop {
		pointer-events: none;
	}
	.drops {
		position: absolute;
		left: 0;
		right: 0;
		display: flex;
		justify-content: center;
		gap: 2px;
		line-height: 0;
	}
	.spark {
		pointer-events: none;
	}
</style>
