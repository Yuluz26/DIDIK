<!--
	A child's character standing on a small patch of lawn, as it will in the game worlds. Used where a
	child first meets their character: joining, and waiting in the lobby. The character and the lawn
	share one pixel size, so they look like they were drawn together.
-->
<script lang="ts">
	import { snapScale } from '$lib/pixel/cache';
	import { CH, CW } from '$lib/pixel/chibi';
	import Sprite from '$lib/pixel/Sprite.svelte';
	import { PATCH, lawnPatch } from '$lib/pixel/stage';
	import Chibi from './Chibi.svelte';

	let {
		animal,
		colour,
		skin,
		size = 96,
		mood = 'cheer'
	}: { animal: string; colour: string; skin?: string; size?: number; mood?: 'happy' | 'cheer' | 'oops' | 'sleep' } = $props();

	const s = $derived(snapScale(size / CW, 1));
	// The lawn hangs a few pixels below the character's feet.
	const SKIRT = 4;
</script>

<div class="stage" style:width="{Math.round(PATCH.w * s)}px" style:height="{Math.round((CH + SKIRT) * s)}px" aria-hidden="true">
	<span class="ground"><Sprite sheet={lawnPatch()} {s} /></span>
	{#key animal + colour + skin}
		<span class="me" style:bottom="{Math.round(SKIRT * s)}px"><Chibi {animal} {colour} {skin} {s} {mood} /></span>
	{/key}
</div>

<style>
	.stage {
		position: relative;
		flex: none;
	}
	.ground {
		position: absolute;
		inset: auto 0 0;
		display: flex;
		justify-content: center;
	}
	.me {
		position: absolute;
		left: 50%;
		translate: -50% 0;
		animation: hop-in 360ms steps(6) both;
	}
	@keyframes hop-in {
		from {
			opacity: 0;
			transform: translateY(1.2rem);
		}
		to {
			opacity: 1;
			transform: none;
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.me {
			animation: none;
		}
	}
</style>
