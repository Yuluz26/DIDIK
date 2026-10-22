<!--
	One game as a small island in the worlds' 3/4 view, built from the same props and characters the
	game itself uses: a river jetty and a racing sampan, lily islets, treasure sand, a forest, team
	hexagons, a kampung house, a gallery easel, garden beds. `active` makes the island come alive (the
	children cheer, the sampan rows, the flags wave).
-->
<script lang="ts">
	import World, { type WorldActor, type WorldProp } from '$lib/worlds/World.svelte';
	import GardenBed from '$lib/worlds/GardenBed.svelte';
	import Sampan from '$lib/worlds/Sampan.svelte';
	import { blob } from './islands';

	let { game, width, active = false }: { game: string; width: number; active?: boolean } = $props();

	const W = 6;
	const H = 4.4;
	const tile = $derived(width / W);
	const cheer = $derived(active ? 'cheer' : 'happy');

	interface Land {
		cx: number;
		cy: number;
		rx: number;
		ry: number;
		reach: number[];
		sand?: number;
	}

	const LANDS: Record<string, Land[]> = {
		lumba: [{ cx: 2.4, cy: 2.5, rx: 2.0, ry: 1.15, reach: [1, 0.95, 1.05, 0.9, 1, 1.08, 0.92, 1] }],
		lompat: [
			{ cx: 1.3, cy: 3.0, rx: 0.85, ry: 0.48, reach: [1, 0.95, 1.05, 1, 0.95, 1] },
			{ cx: 3.0, cy: 2.2, rx: 0.9, ry: 0.5, reach: [1, 1.05, 0.95, 1, 1.05, 0.95] },
			{ cx: 4.75, cy: 3.25, rx: 0.8, ry: 0.45, reach: [1, 0.9, 1.05, 1, 0.95, 1.05] }
		],
		harta: [{ cx: 3, cy: 2.65, rx: 2.45, ry: 1.3, reach: [1, 0.92, 1.06, 1, 0.94, 1.08, 1, 0.95], sand: 0.55 }],
		hutan: [{ cx: 3, cy: 2.6, rx: 2.55, ry: 1.32, reach: [1.04, 0.95, 1, 1.06, 0.93, 1, 1.05, 0.96] }],
		pasukan: [{ cx: 3, cy: 2.62, rx: 2.6, ry: 1.36, reach: [1, 1.04, 0.96, 1, 1.03, 0.97, 1, 1.02] }],
		kampung: [{ cx: 3, cy: 2.6, rx: 2.55, ry: 1.32, reach: [1, 0.94, 1.05, 1, 0.96, 1.06, 0.97, 1] }],
		teka: [{ cx: 3, cy: 2.62, rx: 2.45, ry: 1.28, reach: [1.02, 0.96, 1, 1.05, 0.95, 1, 1.04, 0.97] }],
		kebun: [{ cx: 3, cy: 2.62, rx: 2.55, ry: 1.32, reach: [1, 1.05, 0.95, 1, 1.04, 0.96, 1, 1.03] }]
	};

	const scale = (l: Land, k: number, dy = 0) => blob(l.cx, l.cy + dy, l.rx * k, l.ry * k, l.reach);

	const PROPS: Record<string, WorldProp[]> = {
		lumba: [
			{ id: 'palm', kind: 'palm', x: 0.95, y: 2.35, variant: 1 },
			{ id: 'finish', kind: 'banner', x: 2.45, y: 2.25, variant: 0, state: 'PENAMAT' },
			{ id: 'reeds', kind: 'reeds', x: 3.7, y: 3.35 },
			{ id: 'flowers', kind: 'flowers', x: 1.6, y: 3.35 },
			{ id: 'boat', kind: 'sampan', x: 4.75, y: 4.35, custom: true }
		],
		lompat: [
			{ id: 'l1', kind: 'lily', x: 0.5, y: 4.1 },
			{ id: 'l2', kind: 'lily', x: 5.55, y: 2.15 },
			{ id: 'l3', kind: 'lily', x: 2.35, y: 4.0 },
			{ id: 'tick', kind: 'mark', x: 3.55, y: 2.15, state: 'yes', custom: true },
			{ id: 'cross', kind: 'mark', x: 5.15, y: 3.15, state: 'no', custom: true }
		],
		harta: [
			{ id: 'palm1', kind: 'palm', x: 1.55, y: 2.15, variant: 1 },
			{ id: 'palm2', kind: 'palm', x: 4.5, y: 1.85, variant: 0 },
			{ id: 'chest', kind: 'chest', x: 2.75, y: 2.95, state: 'open' },
			{ id: 'rock', kind: 'rock', x: 5.0, y: 3.15 }
		],
		hutan: [
			{ id: 't1', kind: 'tree', x: 1.0, y: 2.3, variant: 0 },
			{ id: 't2', kind: 'pine', x: 1.95, y: 1.8, variant: 1 },
			{ id: 't3', kind: 'pine', x: 4.25, y: 1.75, variant: 2 },
			{ id: 't4', kind: 'tree', x: 5.15, y: 2.45, variant: 2 },
			{ id: 'chest', kind: 'chest', x: 3.55, y: 2.6 },
			{ id: 'bush', kind: 'bush', x: 4.75, y: 3.5, variant: 1 },
			{ id: 'm1', kind: 'mushroom', x: 1.45, y: 3.25 },
			{ id: 'm2', kind: 'mushroom', x: 4.1, y: 3.65 }
		],
		pasukan: [
			{ id: 'f1', kind: 'flag', x: 1.55, y: 2.35, state: '#f28c28', custom: true },
			{ id: 'f2', kind: 'flag', x: 4.5, y: 2.3, state: '#14958a', custom: true }
		],
		kampung: [
			{ id: 'house', kind: 'rumah', x: 2.45, y: 2.8 },
			{ id: 'palm', kind: 'palm', x: 4.7, y: 2.15, variant: 1 },
			{ id: 'hen', kind: 'hen', x: 4.15, y: 3.35 },
			{ id: 'flowers', kind: 'flowers', x: 0.95, y: 3.2, variant: 1 }
		],
		teka: [
			{ id: 'easel', kind: 'easel', x: 3.0, y: 2.95, custom: true },
			{ id: 'flowers', kind: 'flowers', x: 0.95, y: 2.5 },
			{ id: 'bush', kind: 'bush', x: 5.2, y: 2.7, variant: 0 }
		],
		kebun: [
			{ id: 'bed1', kind: 'bed', x: 1.95, y: 3.25, state: 'jagung', custom: true },
			{ id: 'bed2', kind: 'bed', x: 3.55, y: 2.45, state: 'tembikai', custom: true },
			{ id: 'scarecrow', kind: 'scarecrow', x: 4.9, y: 2.7 },
			{ id: 'jar', kind: 'tempayan', x: 0.95, y: 2.75 },
			{ id: 'flowers', kind: 'flowers', x: 4.45, y: 3.7 }
		]
	};

	const CAST: Record<string, Omit<WorldActor, 'name'>[]> = {
		lumba: [],
		lompat: [
			{ id: 'a', x: 3.0, y: 2.45, animal: 'kucing', colour: 'jambu', skin: 's2' },
			{ id: 'b', x: 1.25, y: 3.2, animal: 'arnab', colour: 'kuning', skin: 's4', facing: 1 }
		],
		harta: [{ id: 'a', x: 3.7, y: 3.6, animal: 'enggang', colour: 'merah', skin: 's3', facing: -1 }],
		hutan: [{ id: 'a', x: 2.65, y: 3.4, animal: 'gajah', colour: 'biru', skin: 's5' }],
		pasukan: [
			{ id: 'a', x: 2.15, y: 3.4, animal: 'harimau', colour: 'jingga', skin: 's2' },
			{ id: 'b', x: 3.9, y: 3.35, animal: 'penyu', colour: 'teal', skin: 's4', facing: -1 }
		],
		kampung: [{ id: 'a', x: 4.95, y: 3.65, animal: 'beruang', colour: 'hijau', skin: 's3', facing: -1 }],
		teka: [
			{ id: 'a', x: 1.45, y: 3.35, animal: 'arnab', colour: 'ungu', skin: 's1' },
			{ id: 'b', x: 4.6, y: 3.45, animal: 'kucing', colour: 'kuning', skin: 's5', facing: -1 }
		],
		kebun: [{ id: 'a', x: 2.9, y: 3.85, animal: 'kancil', colour: 'teal', skin: 's2' }]
	};

	const lands = $derived(LANDS[game] ?? LANDS.hutan);
	const things = $derived(PROPS[game] ?? []);
	const actors = $derived<WorldActor[]>(
		(CAST[game] ?? []).map((a) => ({ ...a, name: '', mood: cheer }))
	);

	// Team hexagons for Pasukan Warna, squashed for the 3/4 view.
	const HEX = [
		[1.35, 2.0, '#f28c28'], [2.15, 2.0, '#f28c28'], [2.95, 2.0, '#e9d7b0'], [3.75, 2.0, '#14958a'], [4.55, 2.0, '#14958a'],
		[0.95, 2.62, '#f28c28'], [1.75, 2.62, '#f28c28'], [2.55, 2.62, '#e9d7b0'], [3.35, 2.62, '#e9d7b0'], [4.15, 2.62, '#14958a'], [4.95, 2.62, '#14958a'],
		[1.35, 3.24, '#f28c28'], [2.15, 3.24, '#e9d7b0'], [2.95, 3.24, '#f28c28'], [3.75, 3.24, '#14958a'], [4.55, 3.24, '#14958a']
	] as const;
	const hex = (x: number, y: number) =>
		Array.from({ length: 6 }, (_, i) => {
			const a = (Math.PI / 3) * i + Math.PI / 6;
			return `${(x + Math.cos(a) * 0.4).toFixed(3)},${(y + Math.sin(a) * 0.29).toFixed(3)}`;
		}).join(' ');
</script>

{#snippet ground()}
	{#each lands as land, i (i)}
		<path d={scale(land, 1.16, 0.06)} fill="#3d97cc" />
		<path d={scale(land, 1.06, 0.03)} fill="#e8f6fc" opacity=".75" />
		<path d={scale(land, 1, 0.16)} fill="#d9a94f" />
		<path d={scale(land, 1)} fill="#f3d28a" />
		{#if game !== 'harta' || land.sand}
			<path d={scale(land, land.sand ?? 0.88, land.sand ? -0.28 : -0.04)} fill="#6cb33f" />
			<path d={scale(land, land.sand ?? 0.88, land.sand ? -0.34 : -0.1)} fill={game === 'hutan' ? '#7cc35a' : '#8fd05e'} />
		{/if}
		{#if game === 'lompat' && i === 2}
			<!-- The wrong islet is going under. -->
			<path d={scale(land, 1.02)} fill="#1f78ab" opacity=".35" />
			<circle cx="4.2" cy="2.85" r="0.07" fill="#e8f6fc" /><circle cx="5.35" cy="3.0" r="0.05" fill="#e8f6fc" />
		{/if}
	{/each}

	{#if game === 'lumba'}
		<!-- A jetty into the river, and the finish buoys. -->
		<path d="M3.85 2.55 L5.75 2.72 L5.7 3.0 L3.8 2.85z" fill="#c98a54" />
		<path d="M4.25 2.6 L4.22 2.88 M4.7 2.64 L4.67 2.92 M5.15 2.68 L5.12 2.96" stroke="#a46a37" stroke-width="0.04" />
		<rect x="5.55" y="2.95" width="0.09" height="0.3" fill="#8e5a2e" />
		{#each [[4.0, 3.75], [4.45, 3.62], [4.9, 3.5]] as [x, y] (x)}
			<circle cx={x} cy={y} r="0.09" fill="#e2483d" /><circle cx={x} cy={y - 0.03} r="0.04" fill="#fff" />
		{/each}
	{:else if game === 'lompat'}
		<path d="M1.5 2.75 Q2.1 1.7 2.75 2.0" stroke="#fff" stroke-width="0.06" stroke-dasharray="0.01 0.14" stroke-linecap="round" fill="none" />
	{:else if game === 'harta'}
		<path d="M3.85 3.05 l0.36 0.24 M4.21 3.05 l-0.36 0.24" stroke="#c0503a" stroke-width="0.09" stroke-linecap="round" />
		<ellipse cx="1.85" cy="3.35" rx="0.32" ry="0.13" fill="#c49a52" />
		<ellipse cx="4.75" cy="2.55" rx="0.28" ry="0.11" fill="#c49a52" />
		<circle cx="4.82" cy="2.5" r="0.05" fill="#ffd34d" />
	{:else if game === 'hutan'}
		<path d="M3.1 3.95 C2.9 3.4 3.5 3.0 3.25 2.55 C3.1 2.2 3.4 1.9 3.3 1.6" stroke="#e8c98f" stroke-width="0.32" fill="none" stroke-linecap="round" />
	{:else if game === 'pasukan'}
		{#each HEX as [x, y, fill] (`${x}-${y}`)}
			<polygon points={hex(x, y)} fill={fill} stroke="#fff" stroke-width="0.04" />
		{/each}
	{:else if game === 'kampung'}
		<path d="M2.45 2.85 C2.6 3.3 3.3 3.5 3.6 3.95" stroke="#e8c98f" stroke-width="0.26" fill="none" stroke-linecap="round" />
	{/if}
{/snippet}

{#snippet art(prop: WorldProp, t: number)}
	{#if prop.kind === 'sampan'}
		<Sampan tile={t * 0.9} animal="harimau" colour="jingga" skin="s3" mood={cheer} rowing={active} />
	{:else if prop.kind === 'mark'}
		<svg class="mark" class:no={prop.state === 'no'} viewBox="0 0 40 40" width={t * 0.62} height={t * 0.62} aria-hidden="true" focusable="false">
			<circle cx="20" cy="20" r="18" fill={prop.state === 'yes' ? '#1f9d55' : '#e8553f'} stroke="#fff" stroke-width="3" />
			{#if prop.state === 'yes'}
				<path d="M11 21 l6 6 12 -13" stroke="#fff" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round" />
			{:else}
				<path d="M13 13 l14 14 M27 13 l-14 14" stroke="#fff" stroke-width="5" stroke-linecap="round" />
			{/if}
		</svg>
	{:else if prop.kind === 'flag'}
		<svg class="flag" viewBox="0 0 40 90" width={t * 0.6} height={t * 1.35} aria-hidden="true" focusable="false">
			<ellipse cx="8" cy="86" rx="8" ry="3" fill="#000" opacity=".16" />
			<rect x="6" y="4" width="4" height="84" rx="2" fill="#8e5a2e" />
			<path class="cloth" d="M10 6 Q24 2 38 9 Q26 16 10 22z" fill={prop.state} />
		</svg>
	{:else if prop.kind === 'easel'}
		<svg viewBox="0 0 190 230" width={t * 1.9} height={t * 2.3} aria-hidden="true" focusable="false">
			<ellipse cx="95" cy="224" rx="70" ry="6" fill="#000" opacity=".15" />
			<path d="M60 226 L84 40 M130 226 L106 40 M95 40 V226" stroke="#8e5a2e" stroke-width="7" stroke-linecap="round" />
			<rect x="34" y="150" width="122" height="9" rx="3" fill="#a46a37" />
			<rect x="20" y="20" width="150" height="130" rx="6" fill="#fff4e6" stroke="#8e5a2e" stroke-width="6" />
			<rect x="30" y="30" width="130" height="110" fill="#cdebff" />
			<circle cx="128" cy="60" r="14" fill="#ffd34d" />
			<path d="M30 112 Q70 82 104 104 Q130 90 160 104 V140 H30z" fill="#7dbe4e" />
			<path d="M60 112 h30 v-18 l-15 -12 l-15 12z" fill="#c0503a" />
			{#each [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15] as i (i)}
				{#if [1, 2, 4, 7, 8, 11, 13, 14].includes(i)}
					<rect x={30 + (i % 4) * 32.5} y={30 + Math.floor(i / 4) * 27.5} width="32.5" height="27.5" fill="#ffb627" stroke="#fff4e6" stroke-width="2.5" />
					<text x={30 + (i % 4) * 32.5 + 16.25} y={30 + Math.floor(i / 4) * 27.5 + 20} text-anchor="middle" font-family="Fredoka Variable, sans-serif" font-size="16" font-weight="600" fill="#7a4c00">?</text>
				{/if}
			{/each}
		</svg>
	{:else if prop.kind === 'bed'}
		<GardenBed crop={prop.state} stage={4} need={prop.state === 'tembikai' ? 4 : 3} tile={t * 0.5} />
	{/if}
{/snippet}

<div class="island" class:active>
	<World width={W} height={H} {tile} {ground} props={things} {actors} names={false} {art} />
</div>

<style>
	.island {
		width: 100%;
		aspect-ratio: 6 / 4.4;
	}
	/* An island sits straight on the sea: no frame, nothing clipped. */
	.island :global(.viewport) {
		overflow: visible;
		border-radius: 0;
		background: transparent;
		box-shadow: none; /* taste-skill-ignore: removes the world frame's shadow */
	}
	.flag .cloth {
		transform-box: fill-box;
		transform-origin: 0 50%;
	}
	.active .flag .cloth {
		animation: flutter 0.5s ease-in-out infinite alternate;
	}
	.mark.no {
		rotate: 14deg;
		opacity: 0.85;
	}
	@keyframes flutter {
		to {
			transform: scaleX(0.82) skewY(-4deg);
		}
	}
</style>
