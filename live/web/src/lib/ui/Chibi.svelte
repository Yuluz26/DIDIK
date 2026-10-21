<!--
	A child in the game worlds: a small full-body character in an animal hoodie (the hood tells you the
	animal, the hoodie body is the child's colour). Drawn facing the viewer in a 3/4 top-down world;
	`facing` flips it, `walking` swings the legs, moods change the face and arms.
-->
<script lang="ts">
	import { COLOURS, SKINS } from '$lib/names';
	import ChibiHead from './ChibiHead.svelte';

	type Mood = 'happy' | 'cheer' | 'oops' | 'sleep';

	let {
		animal = 'kancil',
		colour = 'hijau',
		skin = 's2',
		size = 64,
		mood = 'happy',
		walking = false,
		facing = 1,
		idle = true,
		label = ''
	}: {
		animal?: string;
		colour?: string;
		skin?: string;
		size?: number;
		mood?: Mood;
		walking?: boolean;
		facing?: number;
		idle?: boolean;
		label?: string;
	} = $props();

	const body = $derived(COLOURS[colour] ?? COLOURS.hijau);
	const tone = $derived(SKINS[skin] ?? SKINS.s2);
	const delay = `${(Math.random() * 1.4).toFixed(2)}s`;
</script>

<span
	class="chibi"
	class:walking
	class:idle={idle && !walking}
	class:cheer={mood === 'cheer'}
	style:--size="{size}px"
	style:--body={body}
	style:--skin={tone}
	style:--delay={delay}
	role={label ? 'img' : undefined}
	aria-label={label || undefined}
	aria-hidden={label ? undefined : 'true'}
>
	<svg viewBox="0 0 80 100" focusable="false" style:transform="scaleX({facing < 0 ? -1 : 1})">
		<ellipse class="shadow" cx="40" cy="95" rx="17" ry="4.2" />

		<g class="figure">
			{#if animal === 'penyu'}
				<!-- The shell is a backpack, peeking out around the body. -->
				<ellipse cx="40" cy="72" rx="22" ry="15" fill="#3e8e57" />
				<path d="M28 66 l6 -6 h12 l6 6 l-4 10 h-16z" fill="none" stroke="#8fd05e" stroke-width="2.4" stroke-linejoin="round" />
			{/if}

			<g class="leg leg-l"><rect x="30.5" y="76" width="8" height="15" rx="4" fill="#3f4a5a" /><ellipse cx="34" cy="91" rx="6" ry="3.4" fill="#2b2f36" /></g>
			<g class="leg leg-r"><rect x="41.5" y="76" width="8" height="15" rx="4" fill="#3f4a5a" /><ellipse cx="46" cy="91" rx="6" ry="3.4" fill="#2b2f36" /></g>

			<g class="arm arm-l"><rect x="16" y="60" width="9.5" height="17" rx="4.75" class="sleeve" /><circle cx="20.75" cy="78" r="4.2" class="hand" /></g>
			<g class="arm arm-r"><rect x="54.5" y="60" width="9.5" height="17" rx="4.75" class="sleeve" /><circle cx="59.25" cy="78" r="4.2" class="hand" /></g>

			<path class="hoodie" d="M23 66 Q23 57 32 56 H48 Q57 57 57 66 V79 Q57 83 53 83 H27 Q23 83 23 79 Z" />
			<path d="M31 72 h18 v6 q0 2 -2 2 h-14 q-2 0 -2 -2z" fill="#000" opacity=".1" />
			<path d="M37 57 l3 6 3 -6" fill="none" stroke="#fff" stroke-width="1.6" stroke-linecap="round" opacity=".7" />

			<g class="head">
				<ChibiHead {animal} {skin} {mood} />
			</g>
		</g>
	</svg>
</span>

<style>
	.chibi {
		display: inline-block;
		width: var(--size);
		height: calc(var(--size) * 1.25);
		line-height: 0;
		flex: none;
	}
	svg {
		width: 100%;
		height: 100%;
		overflow: visible;
	}
	.shadow {
		fill: rgb(0 0 0 / 0.18);
	}
	.hoodie,
	.sleeve {
		fill: var(--body);
	}
	.sleeve {
		filter: brightness(0.92);
	}
	.hand {
		fill: var(--skin);
	}
	.figure,
	.leg,
	.arm,
	.head {
		transform-box: fill-box;
	}
	.leg {
		transform-origin: 50% 0;
	}
	.arm {
		transform-origin: 50% 8%;
	}
	.idle .figure {
		animation: breathe 2.8s ease-in-out var(--delay) infinite;
	}
	.walking .figure {
		animation: step-bob 0.36s ease-in-out infinite;
	}
	.walking .leg-l {
		animation: swing 0.36s ease-in-out infinite;
	}
	.walking .leg-r {
		animation: swing 0.36s ease-in-out infinite reverse;
	}
	.walking .arm-l {
		animation: swing 0.36s ease-in-out infinite reverse;
	}
	.walking .arm-r {
		animation: swing 0.36s ease-in-out infinite;
	}
	.cheer .arm-l {
		transform: rotate(150deg);
	}
	.cheer .arm-r {
		transform: rotate(-150deg);
	}
	.cheer .figure {
		animation: hop 0.7s var(--spring) 2;
	}
	@keyframes breathe {
		0%,
		100% {
			transform: translateY(0);
		}
		50% {
			transform: translateY(-1.2px);
		}
	}
	@keyframes step-bob {
		0%,
		100% {
			transform: translateY(0);
		}
		50% {
			transform: translateY(-2.5px);
		}
	}
	@keyframes swing {
		0%,
		100% {
			transform: rotate(14deg);
		}
		50% {
			transform: rotate(-14deg);
		}
	}
	@keyframes hop {
		0%,
		100% {
			transform: translateY(0);
		}
		40% {
			transform: translateY(-10px);
		}
	}
</style>
