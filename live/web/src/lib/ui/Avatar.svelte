<!--
	A child's round picture for lists, the HUD and the podium: their character's head and shoulders
	(the same face, skin tone and animal hood as in the worlds) on a pixel disc tinted with their
	colour, so a friend looks the same in a leaderboard as in the forest.
-->
<script lang="ts">
	import { ANIMALS } from '$lib/names';
	import { snapScale } from '$lib/pixel/cache';
	import { AH, AW, avatarSheet } from '$lib/pixel/chibi';
	import type { Mood } from '$lib/pixel/chibi';
	import Sprite from '$lib/pixel/Sprite.svelte';

	let {
		animal = 'kancil',
		colour = 'hijau',
		skin = 's2',
		size = 56,
		mood = 'happy',
		bob = false,
		label = ''
	}: { animal?: string; colour?: string; skin?: string; size?: number; mood?: Mood; bob?: boolean; label?: string } = $props();

	const s = $derived(snapScale(size / AW, 1));
	const sheet = $derived(avatarSheet(animal, colour, skin, mood));
	const delay = `${(Math.random() * 1.6).toFixed(2)}s`;
</script>

<span
	class="avatar"
	class:bob
	style:width="{size}px"
	style:height="{size}px"
	style:--delay={delay}
	role={label ? 'img' : undefined}
	aria-label={label || undefined}
	aria-hidden={label ? undefined : 'true'}
	title={label || undefined}
>
	<span class="pic" style:width="{Math.round(AW * s)}px" style:height="{Math.round(AH * s)}px">
		<Sprite {sheet} {s} />
	</span>
	{#if label}<span class="visually-hidden">{ANIMALS[animal] ?? ''}</span>{/if}
</span>

<style>
	.avatar {
		position: relative;
		display: inline-block;
		flex: none;
		line-height: 0;
	}
	/* The picture is centred in its box; ears may rise above it. */
	.pic {
		position: absolute;
		left: 50%;
		bottom: 0;
		translate: -50% 4%;
	}
	.bob .pic {
		animation: bob 2.6s ease-in-out var(--delay) infinite;
	}
</style>
