<!--
	The eight animals children play as. One face per animal on a disc in the child's colour, so a
	friend is easy to spot in a crowded river or forest. Moods change only eyes and mouth.
-->
<script lang="ts">
	import { ANIMALS, COLOURS } from '$lib/names';

	type Mood = 'happy' | 'cheer' | 'oops' | 'sleep';

	let {
		animal = 'kancil',
		colour = 'hijau',
		size = 56,
		mood = 'happy',
		bob = false,
		label = ''
	}: { animal?: string; colour?: string; size?: number; mood?: Mood; bob?: boolean; label?: string } = $props();

	// Where each face keeps its eyes and mouth, and whether the face is dark (eyes need white).
	const FACE: Record<string, { eyes: [number, number][]; mouth: [number, number]; dark?: boolean }> = {
		kancil: { eyes: [[40, 51], [60, 51]], mouth: [50, 71] },
		harimau: { eyes: [[39, 51], [61, 51]], mouth: [50, 71] },
		penyu: { eyes: [[41, 59], [59, 59]], mouth: [50, 70] },
		enggang: { eyes: [[38, 50]], mouth: [40, 63], dark: true },
		gajah: { eyes: [[41, 49], [59, 49]], mouth: [43, 62] },
		kucing: { eyes: [[40, 54], [60, 54]], mouth: [50, 69] },
		arnab: { eyes: [[41, 58], [59, 58]], mouth: [50, 73] },
		beruang: { eyes: [[40, 50], [60, 50]], mouth: [50, 72], dark: true }
	};

	const face = $derived(FACE[animal] ?? FACE.kancil);
	const ring = $derived(COLOURS[colour] ?? COLOURS.hijau);
	const delay = `${(Math.random() * 1.6).toFixed(2)}s`;
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
		<circle class="disc" cx="50" cy="54" r="45" />

		{#if animal === 'kancil'}
			<g transform="rotate(28 22 40)"><ellipse cx="22" cy="40" rx="17" ry="8.5" fill="#e7b98a" /><ellipse cx="23" cy="40" rx="11" ry="4.5" fill="#f7c6c0" /></g>
			<g transform="rotate(-28 78 40)"><ellipse cx="78" cy="40" rx="17" ry="8.5" fill="#e7b98a" /><ellipse cx="77" cy="40" rx="11" ry="4.5" fill="#f7c6c0" /></g>
			<ellipse cx="50" cy="50" rx="28" ry="24" fill="#e7b98a" />
			<ellipse cx="50" cy="67" rx="17" ry="15" fill="#e7b98a" />
			<ellipse cx="50" cy="75" rx="11" ry="6" fill="#fff4e6" />
			<ellipse cx="50" cy="66" rx="4.5" ry="3.3" fill="#1f2d27" />
		{:else if animal === 'harimau'}
			<circle cx="27" cy="30" r="10" fill="#f7943b" /><circle cx="27" cy="31" r="5" fill="#fff6ec" />
			<circle cx="73" cy="30" r="10" fill="#f7943b" /><circle cx="73" cy="31" r="5" fill="#fff6ec" />
			<circle cx="50" cy="55" r="30" fill="#f7943b" />
			<path d="M50 27 v9 M41 29 q2 6 0 10 M59 29 q-2 6 0 10 M22 52 h8 M23 60 h7 M78 52 h-8 M77 60 h-7" stroke="#2a201b" stroke-width="3.2" stroke-linecap="round" fill="none" />
			<ellipse cx="43" cy="68" rx="10" ry="8" fill="#fff6ec" /><ellipse cx="57" cy="68" rx="10" ry="8" fill="#fff6ec" />
			<path d="M45.5 62 h9 l-4.5 5 z" fill="#c4553b" />
		{:else if animal === 'penyu'}
			<ellipse cx="50" cy="40" rx="36" ry="23" fill="#3e8e57" />
			<path d="M30 30 l10 -8 h20 l10 8 l-6 12 h-28 z" fill="none" stroke="#7cc47c" stroke-width="3" stroke-linejoin="round" />
			<ellipse cx="50" cy="61" rx="24" ry="22" fill="#9ad27f" />
			<ellipse cx="50" cy="72" rx="13" ry="6" fill="#c3e8a9" />
		{:else if animal === 'enggang'}
			<circle cx="44" cy="54" r="27" fill="#2d2a32" />
			<ellipse cx="42" cy="68" rx="14" ry="8" fill="#f4f1ea" />
			<path d="M56 46 q20 -16 36 0 q-8 1 -12 6 q-12 -6 -24 -2 z" fill="#e2483d" />
			<path d="M58 52 q22 -6 36 10 q-18 4 -36 2 z" fill="#f7c948" />
			<path d="M80 60 q8 2 14 2 q-6 4 -14 2 z" fill="#f2a541" />
		{:else if animal === 'gajah'}
			<ellipse cx="20" cy="52" rx="17" ry="22" fill="#b8c3cc" /><ellipse cx="22" cy="53" rx="10" ry="14" fill="#efc6c6" />
			<ellipse cx="80" cy="52" rx="17" ry="22" fill="#b8c3cc" /><ellipse cx="78" cy="53" rx="10" ry="14" fill="#efc6c6" />
			<circle cx="50" cy="50" r="27" fill="#9aa7b3" />
			<path d="M50 60 q2 18 10 26" stroke="#9aa7b3" stroke-width="12" stroke-linecap="round" fill="none" />
			<path d="M38 64 q-4 8 -10 9 M62 64 q4 8 10 9" stroke="#fffdf5" stroke-width="4" stroke-linecap="round" fill="none" />
		{:else if animal === 'kucing'}
			<path d="M20 40 L27 12 L45 30 Z" fill="#f5efe6" /><path d="M24 34 L28 19 L38 29 Z" fill="#f7b7b2" />
			<path d="M80 40 L73 12 L55 30 Z" fill="#f29c4b" /><path d="M76 34 L72 19 L62 29 Z" fill="#f7b7b2" />
			<ellipse cx="50" cy="55" rx="31" ry="28" fill="#f5efe6" />
			<path d="M50 28 q24 0 30 22 q-14 -6 -30 -8 z" fill="#f29c4b" />
			<path d="M46.5 63 h7 l-3.5 4 z" fill="#f27b8b" />
			<path d="M33 64 l-14 -2 M33 68 l-13 3 M67 64 l14 -2 M67 68 l13 3" stroke="#8a7f74" stroke-width="1.8" stroke-linecap="round" />
		{:else if animal === 'arnab'}
			<g transform="rotate(-10 38 22)"><ellipse cx="38" cy="22" rx="8.5" ry="21" fill="#fbf7f4" /><ellipse cx="38" cy="23" rx="4" ry="14" fill="#f7b7b2" /></g>
			<g transform="rotate(10 62 22)"><ellipse cx="62" cy="22" rx="8.5" ry="21" fill="#fbf7f4" /><ellipse cx="62" cy="23" rx="4" ry="14" fill="#f7b7b2" /></g>
			<circle cx="50" cy="60" r="26" fill="#fbf7f4" />
			<ellipse cx="50" cy="67" rx="3.5" ry="2.6" fill="#f27b8b" />
			<rect x="47.5" y="75" width="5" height="5" rx="1" fill="#ffffff" stroke="#d9cfc7" stroke-width="1" />
		{:else}
			<circle cx="29" cy="32" r="9" fill="#3b302b" /><circle cx="29" cy="33" r="4" fill="#5a4a42" />
			<circle cx="71" cy="32" r="9" fill="#3b302b" /><circle cx="71" cy="33" r="4" fill="#5a4a42" />
			<circle cx="50" cy="55" r="28" fill="#3b302b" />
			<ellipse cx="50" cy="66" rx="16" ry="12" fill="#e3b67a" />
			<ellipse cx="50" cy="61" rx="5" ry="3.6" fill="#1f1a17" />
		{/if}

		<circle cx="33" cy="64" r="5" fill="#f28fa0" opacity="0.45" />
		<circle cx="67" cy="64" r="5" fill="#f28fa0" opacity="0.45" />

		<g class="eyes">
			{#each face.eyes as [x, y] (x)}
				{#if mood === 'cheer'}
					<path d="M{x - 5} {y + 2} q5 -8 10 0" stroke={face.dark ? '#ffffff' : '#1f2d27'} stroke-width="3" fill="none" stroke-linecap="round" />
				{:else if mood === 'sleep'}
					<path d="M{x - 5} {y} q5 5 10 0" stroke={face.dark ? '#ffffff' : '#1f2d27'} stroke-width="3" fill="none" stroke-linecap="round" />
				{:else}
					{#if face.dark}<circle cx={x} cy={y} r="6.5" fill="#ffffff" />{/if}
					<ellipse class="eye" cx={x} cy={y} rx={mood === 'oops' ? 4.8 : 4.4} ry={mood === 'oops' ? 4.8 : 5.4} fill="#1f2d27" />
					<circle cx={x + 1.6} cy={y - 2} r="1.6" fill="#ffffff" />
				{/if}
			{/each}
		</g>

		{#if mood === 'cheer'}
			<path d="M{face.mouth[0] - 6} {face.mouth[1] - 2} q6 9 12 0 z" fill="#7a2b2b" />
		{:else if mood === 'oops'}
			<ellipse cx={face.mouth[0]} cy={face.mouth[1]} rx="3" ry="3.6" fill="#7a2b2b" />
		{:else if mood !== 'sleep'}
			<path d="M{face.mouth[0] - 4.5} {face.mouth[1] - 1.5} q4.5 5 9 0" stroke={face.dark ? '#ffffff' : '#1f2d27'} stroke-width="2.6" fill="none" stroke-linecap="round" />
		{/if}
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
		fill: var(--ring);
	}

	.bob svg {
		animation: bob 2.6s ease-in-out var(--delay) infinite;
	}

	.eye {
		transform-box: fill-box;
		transform-origin: center;
		animation: blink 5.2s var(--delay) infinite;
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
