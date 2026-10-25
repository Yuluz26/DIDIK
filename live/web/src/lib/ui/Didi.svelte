<!--
	Didi the mouse-deer, the mascot of DIDIK, in pixels (see lib/pixel/didi.ts). Moods change the eyes,
	the mouth and the arms only. `look` (each part from -1 to 1) turns the eyes toward something, such
	as the pointer. `size` is the width of the picture in pixels, drawn at a whole or half step of the
	sprite size.
-->
<script lang="ts">
	import { snapScale } from '$lib/pixel/cache';
	import { DIDI, type DidiMood, didiSheet } from '$lib/pixel/didi';
	import Sprite from '$lib/pixel/Sprite.svelte';

	let {
		mood = 'happy',
		size = 140,
		label = '',
		look = null
	}: {
		mood?: DidiMood;
		size?: number;
		label?: string;
		look?: { x: number; y: number } | null;
	} = $props();

	const s = $derived(snapScale(size / DIDI.w, 1));
	// The eyes can sit in one of nine places, so only nine pictures are ever made.
	const gaze = $derived<[number, number]>(look ? [Math.round(look.x * 1.4), Math.round(look.y * 1.2)] : [0, 0]);
	const open = $derived(didiSheet(mood, gaze, false));
	const shut = $derived(didiSheet(mood, gaze, true));
	const frames = $derived(mood === 'cheer' || mood === 'wave' ? 2 : 1);
</script>

<span
	class="didi didi--{mood}"
	style:width="{Math.round(DIDI.w * s)}px"
	style:height="{Math.round(DIDI.h * s)}px"
	role={label ? 'img' : undefined}
	aria-label={label || undefined}
	aria-hidden={label ? undefined : 'true'}
>
	<Sprite sheet={open} {s} {frames} ms={frames > 1 ? 700 : 1000} />
	<span class="blink"><Sprite sheet={shut} {s} {frames} ms={frames > 1 ? 700 : 1000} /></span>
</span>

<style>
	.didi {
		position: relative;
		display: inline-block;
		flex: none;
		line-height: 0;
	}
	/* The eyes shut for a moment every few seconds. */
	.blink {
		position: absolute;
		inset: 0;
		opacity: 0;
		animation: blink 4.6s steps(1) infinite;
	}
	@keyframes blink {
		0%,
		95%,
		100% {
			opacity: 0;
		}
		96%,
		98% {
			opacity: 1;
		}
	}
</style>
