<!--
	A raised bed in Kebun Ajaib, in pixels: a wooden frame with its soil seen from above, the crop
	growing on it, and along the front one drop for each watering the crop needs (blue once given).
	Land not bought yet is grass behind a dashed line. The foot is the middle of the front edge.
-->
<script lang="ts">
	import { TILE } from '$lib/pixel/cache';
	import Sprite from '$lib/pixel/Sprite.svelte';
	import Crop from './Crop.svelte';
	import { BED, CROP, bedSheet, bedFrontSheet, dropSheet, sparkleSheet } from './garden';

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
	// Broad crops take one bed; flowers and chillies grow as a pair inside the soil.
	const spots = $derived(crop === 'durian' ? [[23, 30]] : crop === 'tembikai' || crop === 'jagung' ? [[23, 29]] : [[14, 27], [32, 27]]);
</script>

<span class="bed" style:width="{BED.w * s}px" style:height="{BED.h * s}px">
	<span class="at"><Sprite sheet={bedSheet(locked)} {s} /></span>
	{#if !locked && crop}
		<span class="plants" style:left="{4 * s}px" style:width="{(BED.w - 8) * s}px" style:height="{BED.h * s}px">
			{#each spots as [x, y] (`${x}-${y}`)}
				<span class="at crop" style:left="{(x - 4 - CROP.w / 2) * s}px" style:top="{(y - CROP.h + 3) * s}px"><Crop {crop} {grow} {ready} {s} /></span>
			{/each}
		</span>
		<span class="at rim"><Sprite sheet={bedFrontSheet()} {s} /></span>
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
	.plants {
		position: absolute;
		top: 0;
		overflow: hidden;
		pointer-events: none;
	}
	.rim {
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
