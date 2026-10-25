<!--
	A sampan with a child paddling it, in pixels: the far side of the hull, the child, then the near
	side, so the child sits inside the boat. A pennant in the child's colour flies from the mast.
	`rowing` plays the paddle and leaves a little wake. Anything passed as children (a name tag) is
	placed by the caller inside the boat's box, whose size in CSS pixels is `--t` times the tile.
-->
<script lang="ts">
	import type { Snippet } from 'svelte';
	import { TILE } from '$lib/pixel/cache';
	import { BOAT_H, BOAT_W, RIDER, paddle, pennant, sampanBack, sampanFront, wake } from '$lib/games/race/sprites';
	import Sprite from '$lib/pixel/Sprite.svelte';
	import Chibi from '$ui/Chibi.svelte';

	let {
		tile,
		animal,
		colour,
		skin,
		mood = 'happy',
		rowing = false,
		facing = 1,
		children
	}: {
		tile: number;
		animal: string;
		colour: string;
		skin?: string;
		mood?: 'happy' | 'cheer' | 'oops' | 'sleep';
		rowing?: boolean;
		facing?: number;
		children?: Snippet;
	} = $props();

	const s = $derived(tile / TILE);
</script>

<div class="boat" class:back={facing < 0} style:--t="{tile}px" style:--s="{s}px" style:width="{BOAT_W * s}px" style:height="{BOAT_H * s}px">
	{@render children?.()}
	<div class="hull">
		<span class="at" style:left="0" style:top="0"><Sprite sheet={sampanBack()} {s} /></span>
		<span class="at" style:left="{-1 * s}px" style:top="{8 * s}px"><Sprite sheet={pennant(colour)} {s} frames={2} ms={700} /></span>
		<span class="at" style:left="{RIDER.x * s}px" style:top="{RIDER.y * s}px">
			<Chibi {animal} {colour} {skin} {s} {mood} dir={mood === 'happy' ? 'side' : 'front'} facing={1} walking={rowing} />
		</span>
		<span class="at" style:left="0" style:top="0"><Sprite sheet={sampanFront()} {s} /></span>
		{#if rowing}
			<span class="at" style:left="{28 * s}px" style:top="{19 * s}px"><Sprite sheet={paddle()} {s} frames={3} ms={450} /></span>
			<span class="at" style:left="{-10 * s}px" style:top="{31 * s}px"><Sprite sheet={wake()} {s} frames={2} ms={500} /></span>
		{/if}
	</div>
</div>

<style>
	.boat {
		position: relative;
	}
	.hull {
		position: absolute;
		inset: 0;
		animation: bob-boat 1.6s steps(1) infinite;
	}
	/* Sailing left: the whole boat turns round, the child with it. */
	.back .hull {
		scale: -1 1;
	}
	.at {
		position: absolute;
		line-height: 0;
	}
	/* The boat rises and settles one sprite pixel at a time. */
	@keyframes bob-boat {
		0% {
			transform: translateY(0);
		}
		50% {
			transform: translateY(calc(var(--s) * -1));
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.hull {
			animation: none;
		}
	}
</style>
