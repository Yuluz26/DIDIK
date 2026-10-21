<!--
	A child's round picture for lists, the HUD and the podium: their character's head and shoulders
	(the same face, skin tone and animal hood as in the worlds) on a disc tinted with their colour,
	so a friend looks the same in a leaderboard as in the forest.
-->
<script lang="ts">
	import { ANIMALS, COLOURS } from '$lib/names';
	import ChibiHead from './ChibiHead.svelte';

	type Mood = 'happy' | 'cheer' | 'oops' | 'sleep';

	let {
		animal = 'kancil',
		colour = 'hijau',
		skin = 's2',
		size = 56,
		mood = 'happy',
		bob = false,
		label = ''
	}: { animal?: string; colour?: string; skin?: string; size?: number; mood?: Mood; bob?: boolean; label?: string } = $props();

	const ring = $derived(COLOURS[colour] ?? COLOURS.hijau);
	const delay = `${(Math.random() * 1.6).toFixed(2)}s`;
	const clip = `avatar-${Math.random().toString(36).slice(2, 8)}`;
</script>

<span
	class="avatar"
	class:bob
	style:--size="{size}px"
	style:--ring={ring}
	style:--delay={delay}
	role={label ? 'img' : undefined}
	aria-label={label || undefined}
	aria-hidden={label ? undefined : 'true'}
	title={label || undefined}
>
	<svg viewBox="0 0 100 100" focusable="false">
		<defs>
			<!-- The disc trims the shoulders; above it, ears and hoods may rise past the edge. -->
			<clipPath id={clip}>
				<circle cx="50" cy="54" r="45" />
				<rect x="-20" y="-40" width="140" height="78" />
			</clipPath>
		</defs>
		<circle class="disc" cx="50" cy="54" r="45" />
		<g clip-path="url(#{clip})">
			<g transform="translate(2 14) scale(1.2)">
				<path class="hoodie" d="M10 70 Q10 55 30 53 H50 Q70 55 70 70 V100 H10 Z" />
				<path d="M36 55 l4 7 4 -7" fill="none" stroke="#fff" stroke-width="1.8" stroke-linecap="round" opacity=".7" />
				<ChibiHead {animal} {skin} {mood} />
			</g>
		</g>
	</svg>
	{#if label}<span class="visually-hidden">{ANIMALS[animal] ?? ''}</span>{/if}
</span>

<style>
	.avatar {
		display: inline-block;
		width: var(--size);
		height: var(--size);
		flex: none;
		line-height: 0;
	}

	svg {
		width: 100%;
		height: 100%;
		overflow: visible;
	}

	.disc {
		fill: color-mix(in srgb, var(--ring) 26%, #fff);
	}

	.hoodie {
		fill: var(--ring);
	}

	.bob svg {
		animation: bob 2.6s ease-in-out var(--delay) infinite;
	}
</style>
