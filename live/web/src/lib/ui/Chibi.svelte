<!--
	A child in the game worlds: a pixel chibi in an animal hoodie (the hood tells you the animal, the
	hoodie is the child's colour). It is a cell of the character's sprite sheet (lib/pixel/chibi.ts):
	`dir` picks the view (facing us, away, or sideways, to the left unless `facing` says right),
	`walking` plays the four walking frames, and the moods use their own cells.
	Either `size` (the width of the picture in pixels) or `s` (CSS pixels per sprite pixel, which the
	worlds use so every sprite in a scene shares one pixel size) sets how large it is drawn.
-->
<script lang="ts">
	import { snapScale } from '$lib/pixel/cache';
	import { CH, CW, ROW, chibiSheet, type Mood } from '$lib/pixel/chibi';
	import Sprite from '$lib/pixel/Sprite.svelte';

	let {
		animal = 'kancil',
		colour = 'hijau',
		skin = 's2',
		size = 64,
		s,
		mood = 'happy',
		walking = false,
		facing = 1,
		dir = 'front',
		label = ''
	}: {
		animal?: string;
		colour?: string;
		skin?: string;
		size?: number;
		s?: number;
		mood?: Mood;
		walking?: boolean;
		/** Which way a sideways character looks: -1 left, 1 right. */
		facing?: number;
		dir?: 'front' | 'back' | 'side';
		idle?: boolean;
		label?: string;
	} = $props();

	const scale = $derived(s ?? snapScale(size / CW, 1));
	const sheet = $derived(chibiSheet(animal, colour, skin));
	const view = $derived(mood === 'happy' ? dir : 'front');
</script>

<span
	class="chibi"
	style:width="{Math.round(CW * scale)}px"
	style:height="{Math.round(CH * scale)}px"
	role={label ? 'img' : undefined}
	aria-label={label || undefined}
	aria-hidden={label ? undefined : 'true'}
>
	{#if mood === 'cheer'}
		<Sprite {sheet} s={scale} row={ROW.mood} col={0} frames={2} ms={560} />
	{:else if mood === 'oops'}
		<Sprite {sheet} s={scale} row={ROW.mood} col={2} />
	{:else if mood === 'sleep'}
		<Sprite {sheet} s={scale} row={ROW.mood} col={3} />
	{:else}
		<Sprite {sheet} s={scale} row={ROW[view]} frames={walking ? 4 : 1} ms={460} flip={view === 'side' && facing > 0} />
	{/if}
</span>

<style>
	.chibi {
		display: inline-block;
		flex: none;
		line-height: 0;
	}
</style>
