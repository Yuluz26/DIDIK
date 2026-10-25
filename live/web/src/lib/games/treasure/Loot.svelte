<!--
	What can be found under the sand on Pulau Harta Karun, in pixels. `size` is the width of the
	picture in CSS pixels, drawn at a whole or half step of the sprite size.
-->
<script lang="ts">
	import { snapScale } from '$lib/pixel/cache';
	import Sprite from '$lib/pixel/Sprite.svelte';
	import { LOOT, lootSprite } from './sprites';

	let { kind, size = 48 }: { kind: string; size?: number } = $props();

	const sheet = $derived(lootSprite(kind));
	const s = $derived(snapScale(size / sheet.cw, 1));
</script>

<span class="loot" style:width="{Math.round(Math.max(sheet.cw, LOOT) * s)}px"><Sprite {sheet} {s} /></span>

<style>
	.loot {
		display: inline-flex;
		justify-content: center;
		line-height: 0;
	}
</style>
