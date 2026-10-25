<!--
	The painted ground of a world on a canvas: the pixels of `pix` magnified by a whole number, then
	shown at the size of the world (`tile` CSS pixels to a tile).
-->
<script lang="ts">
	import { TILE, prescale } from './cache';
	import type { Pix } from './pix';

	let { pix, tile }: { pix: Pix; tile: number } = $props();

	let canvas: HTMLCanvasElement;
	const s = $derived(tile / TILE);

	$effect(() => {
		pix.toCanvas(Math.min(prescale(s), 4), canvas);
	});
</script>

<canvas bind:this={canvas} style:width="{pix.w * s}px" style:height="{pix.h * s}px" aria-hidden="true"></canvas>

<style>
	canvas {
		display: block;
		max-width: none;
	}
</style>
