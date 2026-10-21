<!--
	The head of a child's character: their face (with its skin tone and a fringe) inside an animal
	hood, in the 80 x 100 drawing of the full character. Used by the full-body character in the worlds
	and by the round avatar in lists, so a child looks the same everywhere.
-->
<svelte:options namespace="svg" />

<script lang="ts" module>
	export const HOODS: Record<string, { hood: string; rim: string; inner?: string }> = {
		kancil: { hood: '#c98f5a', rim: '#e7b98a', inner: '#f7c6c0' },
		harimau: { hood: '#f28c28', rim: '#ffb35c', inner: '#fff6ec' },
		penyu: { hood: '#4fa35b', rim: '#8fd05e' },
		enggang: { hood: '#2d2a32', rim: '#4a4652' },
		gajah: { hood: '#9aa7b3', rim: '#b8c3cc', inner: '#efc6c6' },
		kucing: { hood: '#f5efe6', rim: '#fffaf3', inner: '#f7b7b2' },
		arnab: { hood: '#fbf7f4', rim: '#ffffff', inner: '#f7b7b2' },
		beruang: { hood: '#5a4337', rim: '#7a5c4c', inner: '#e3b67a' }
	};
</script>

<script lang="ts">
	import { SKINS } from '$lib/names';

	let {
		animal = 'kancil',
		skin = 's2',
		mood = 'happy'
	}: { animal?: string; skin?: string; mood?: 'happy' | 'cheer' | 'oops' | 'sleep' } = $props();

	const hood = $derived(HOODS[animal] ?? HOODS.kancil);
	const tone = $derived(SKINS[skin] ?? SKINS.s2);
</script>

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
	<circle cx="40" cy="39" r="17.5" fill={tone} />
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

<style>
	.eye {
		transform-box: fill-box;
		transform-origin: center;
		animation: blink 5s var(--delay, 0s) infinite;
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
