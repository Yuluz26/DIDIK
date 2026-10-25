<!--
	One crop of Kebun Ajaib in pixels, standing on the bottom centre of its picture. `grow` runs from
	0 (just planted) to 1 (fully grown); fruit and flowers appear only when `ready`. `s` is CSS pixels
	to a sprite pixel.
-->
<script lang="ts">
	import Sprite from '$lib/pixel/Sprite.svelte';
	import { cropSheet, stageOf } from './garden';

	let { crop, grow = 1, ready = false, s = 2 }: { crop: string; grow?: number; ready?: boolean; s?: number } = $props();

	const sheet = $derived(cropSheet(crop, stageOf(grow, ready)));
</script>

<Sprite {sheet} {s} />
