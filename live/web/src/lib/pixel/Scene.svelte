<!--
	A pixel scene: a picture `w` × `h` base pixels that `paint` draws at that size, shown as wide as
	its box with every base pixel an even block. While it is on screen it is painted again about `fps`
	times a second, so things move a whole pixel at a time like an old console's; for a child who asks
	for less movement it is painted once, and again whenever what it shows changes. Anything set over
	the picture (name tags, a catch card) goes in `children`, placed in percent of the scene.
-->
<script lang="ts">
	import type { Snippet } from 'svelte';
	import { untrack } from 'svelte';
	import { type G, stillWanted } from './scene';

	let {
		w,
		h,
		paint,
		fps = 15,
		label = '',
		children
	}: {
		w: number;
		h: number;
		/** Draws one frame; `t` is the page's clock in milliseconds. */
		paint: (g: G, t: number) => void;
		fps?: number;
		label?: string;
		children?: Snippet;
	} = $props();

	let box: HTMLDivElement;
	let canvas: HTMLCanvasElement;
	let still = $state(false);
	let draw: ((t: number) => void) | null = null;

	$effect(() => {
		const W = w;
		const H = h;
		const off = document.createElement('canvas');
		off.width = W;
		off.height = H;
		const g = off.getContext('2d')!;
		g.imageSmoothingEnabled = false;
		const out = canvas.getContext('2d')!;
		let k = 0;
		let shown = true;
		let frame = 0;
		let last = -Infinity;

		const render = (t: number) => {
			g.clearRect(0, 0, W, H);
			paint(g, t);
			out.imageSmoothingEnabled = false;
			out.clearRect(0, 0, canvas.width, canvas.height);
			out.drawImage(off, 0, 0, W * k, H * k);
		};
		const resize = () => {
			// the smallest whole magnification that covers the screen's real pixels
			const next = Math.max(1, Math.min(12, Math.ceil(((box.clientWidth || W) * (devicePixelRatio || 1)) / W - 0.01)));
			if (next === k) return;
			k = next;
			canvas.width = W * k;
			canvas.height = H * k;
			untrack(() => render(performance.now()));
		};
		const tick = (t: number) => {
			frame = requestAnimationFrame(tick);
			if (!shown || t - last < 1000 / fps - 2) return;
			last = t;
			untrack(() => render(t));
		};

		still = stillWanted();
		resize();
		const sizes = new ResizeObserver(resize);
		sizes.observe(box);
		const seen = new IntersectionObserver(([entry]) => (shown = entry.isIntersecting));
		seen.observe(box);
		if (!still) frame = requestAnimationFrame(tick);
		draw = (t) => k && render(t);
		return () => {
			cancelAnimationFrame(frame);
			sizes.disconnect();
			seen.disconnect();
			draw = null;
		};
	});

	// For less movement, paint again whenever anything the picture reads changes (painting here,
	// not in a frame, is what lets the effect see what it read).
	$effect(() => {
		if (still) draw?.(0);
	});
</script>

<div class="scene" bind:this={box} role={label ? 'img' : undefined} aria-label={label || undefined}>
	<canvas bind:this={canvas} style:aspect-ratio="{w} / {h}" aria-hidden="true"></canvas>
	{@render children?.()}
</div>

<style>
	.scene {
		position: relative;
		line-height: 0;
		/* words set over the picture size with it (cqw) */
		container-type: inline-size;
	}
	canvas {
		display: block;
		width: 100%;
		height: auto;
		image-rendering: pixelated;
	}
</style>
