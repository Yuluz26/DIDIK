<!--
	A child in the game worlds: a small full-body character in an animal hoodie (the hood tells you the
	animal, the hoodie body is the child's colour). Drawn facing the viewer in a 3/4 top-down world;
	`facing` flips it, `walking` swings the legs, moods change the face and arms.
-->
<script lang="ts">
	import { COLOURS, SKINS } from '$lib/names';

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

	const HOODS: Record<string, { hood: string; rim: string; inner?: string }> = {
		kancil: { hood: '#c98f5a', rim: '#e7b98a', inner: '#f7c6c0' },
		harimau: { hood: '#f28c28', rim: '#ffb35c', inner: '#fff6ec' },
		penyu: { hood: '#4fa35b', rim: '#8fd05e' },
		enggang: { hood: '#2d2a32', rim: '#4a4652' },
		gajah: { hood: '#9aa7b3', rim: '#b8c3cc', inner: '#efc6c6' },
		kucing: { hood: '#f5efe6', rim: '#fffaf3', inner: '#f7b7b2' },
		arnab: { hood: '#fbf7f4', rim: '#ffffff', inner: '#f7b7b2' },
		beruang: { hood: '#5a4337', rim: '#7a5c4c', inner: '#e3b67a' }
	};

	const hood = $derived(HOODS[animal] ?? HOODS.kancil);
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
				<!-- Ears and other parts of the hood that sit behind it. -->
				{#if animal === 'kancil'}
					<g transform="rotate(28 15 22)"><ellipse cx="15" cy="22" rx="13" ry="6.5" fill={hood.hood} /><ellipse cx="16" cy="22" rx="8" ry="3.4" fill={hood.inner} /></g>
					<g transform="rotate(-28 65 22)"><ellipse cx="65" cy="22" rx="13" ry="6.5" fill={hood.hood} /><ellipse cx="64" cy="22" rx="8" ry="3.4" fill={hood.inner} /></g>
				{:else if animal === 'harimau' || animal === 'beruang'}
					<circle cx="20" cy="12" r="8" fill={hood.hood} /><circle cx="20" cy="12" r="4" fill={hood.inner} />
					<circle cx="60" cy="12" r="8" fill={hood.hood} /><circle cx="60" cy="12" r="4" fill={hood.inner} />
				{:else if animal === 'gajah'}
					<ellipse cx="11" cy="36" rx="10" ry="15" fill={hood.hood} /><ellipse cx="12" cy="36" rx="6" ry="10" fill={hood.inner} />
					<ellipse cx="69" cy="36" rx="10" ry="15" fill={hood.hood} /><ellipse cx="68" cy="36" rx="6" ry="10" fill={hood.inner} />
				{:else if animal === 'kucing'}
					<path d="M15 20 L19 0 L33 12 Z" fill={hood.hood} /><path d="M18 16 L20 5 L28 12 Z" fill={hood.inner} />
					<path d="M65 20 L61 0 L47 12 Z" fill="#f29c4b" /><path d="M62 16 L60 5 L52 12 Z" fill={hood.inner} />
				{:else if animal === 'arnab'}
					<g transform="rotate(-12 30 4)"><ellipse cx="30" cy="2" rx="6.5" ry="16" fill={hood.hood} /><ellipse cx="30" cy="3" rx="3.2" ry="11" fill={hood.inner} /></g>
					<g transform="rotate(12 50 4)"><ellipse cx="50" cy="2" rx="6.5" ry="16" fill={hood.hood} /><ellipse cx="50" cy="3" rx="3.2" ry="11" fill={hood.inner} /></g>
				{/if}

				<circle cx="40" cy="33" r="27" fill={hood.hood} />
				{#if animal === 'harimau'}
					<path d="M40 7 v8 M31 9 q2 5 0 9 M49 9 q-2 5 0 9 M15 30 h7 M65 30 h-7" stroke="#2a201b" stroke-width="3" stroke-linecap="round" fill="none" />
				{:else if animal === 'penyu'}
					<path d="M28 12 l6 -4 h12 l6 4" fill="none" stroke="#8fd05e" stroke-width="2.4" stroke-linejoin="round" />
				{:else if animal === 'kucing'}
					<path d="M40 6 q22 2 26 22 q-12 -8 -26 -10z" fill="#f29c4b" />
				{:else if animal === 'beruang'}
					<ellipse cx="40" cy="11" rx="8" ry="5" fill={hood.inner} /><ellipse cx="40" cy="9" rx="3" ry="2" fill="#2a201b" />
				{:else if animal === 'gajah'}
					<path d="M40 8 q-2 -8 4 -10" stroke={hood.hood} stroke-width="6" stroke-linecap="round" fill="none" />
				{/if}

				<!-- The face in the hood's opening, with a fringe of hair under the rim. -->
				<circle cx="40" cy="38" r="19.5" fill={hood.rim} />
				<circle cx="40" cy="39" r="17.5" class="face" />
				<path d="M23 34 q5 -11 17 -12 q12 1 17 12 q-6 -5 -12 -4 q-3 -4 -6 -1 q-6 -3 -16 5z" fill="#3b2a20" />

				{#if animal === 'enggang'}
					<path d="M24 22 q16 -14 34 -4 q-4 3 -6 7 q-14 -6 -28 -3z" fill="#e2483d" />
					<path d="M26 26 q18 -6 30 0 q10 2 16 8 q-14 2 -22 -2 q-12 -2 -24 -6z" fill="#f7c948" />
				{/if}

				<g class="eyes">
					{#if mood === 'cheer'}
						<path d="M30 42 q3 -5 6 0 M44 42 q3 -5 6 0" stroke="#2a2433" stroke-width="2.4" fill="none" stroke-linecap="round" />
					{:else if mood === 'sleep'}
						<path d="M30 42 q3 3 6 0 M44 42 q3 3 6 0" stroke="#2a2433" stroke-width="2.2" fill="none" stroke-linecap="round" />
					{:else}
						<ellipse class="eye" cx="33" cy="41" rx={mood === 'oops' ? 3 : 2.7} ry={mood === 'oops' ? 3 : 3.5} fill="#2a2433" />
						<ellipse class="eye" cx="47" cy="41" rx={mood === 'oops' ? 3 : 2.7} ry={mood === 'oops' ? 3 : 3.5} fill="#2a2433" />
						<circle cx="34" cy="39.6" r="1.1" fill="#fff" />
						<circle cx="48" cy="39.6" r="1.1" fill="#fff" />
					{/if}
				</g>
				<circle cx="28.5" cy="46" r="3" fill="#f28fa0" opacity=".5" />
				<circle cx="51.5" cy="46" r="3" fill="#f28fa0" opacity=".5" />
				{#if mood === 'cheer'}
					<path d="M35.5 47.5 q4.5 6 9 0z" fill="#7a2b2b" />
				{:else if mood === 'oops'}
					<ellipse cx="40" cy="49" rx="2" ry="2.4" fill="#7a2b2b" />
					<path d="M57 30 q3 4 0 6 q-3 -2 0 -6z" fill="#7fd0f0" />
				{:else if mood !== 'sleep'}
					<path d="M36.5 48 q3.5 3.2 7 0" stroke="#2a2433" stroke-width="1.8" fill="none" stroke-linecap="round" />
				{/if}
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
	.face,
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
	.eye {
		transform-box: fill-box;
		transform-origin: center;
		animation: blink 5s var(--delay) infinite;
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
	@keyframes blink {
		0%,
		94%,
		100% {
			transform: scaleY(1);
		}
		96% {
			transform: scaleY(0.1);
		}
	}
</style>
