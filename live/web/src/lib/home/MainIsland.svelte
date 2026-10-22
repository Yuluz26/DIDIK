<!--
	The front page's main island: the town square where children gather before a game (the same arch
	and fountain as the waiting room), children in their animal hoodies wandering about, and the jetty
	where a sampan waits to take them to the game islands.
-->
<script lang="ts">
	import World, { type WorldActor, type WorldProp } from '$lib/worlds/World.svelte';
	import Sampan from '$lib/worlds/Sampan.svelte';
	import { blob } from './islands';

	const W = 12;
	const H = 7.8;
	const LAND = { cx: 6, cy: 4.15, rx: 5.65, ry: 3.05, reach: [1, 0.95, 1.04, 0.97, 1.02, 0.94, 1.05, 0.98, 1, 0.96] };
	const land = (k: number, dy = 0) => blob(LAND.cx, LAND.cy + dy, LAND.rx * k, LAND.ry * k, LAND.reach, 0.3);

	const PROPS: WorldProp[] = [
		{ id: 'arch', kind: 'arch', x: 6.1, y: 2.55 },
		{ id: 't1', kind: 'tree', x: 2.3, y: 2.55, variant: 0 },
		{ id: 't2', kind: 'palm', x: 3.6, y: 2.0, variant: 1 },
		{ id: 't3', kind: 'tree', x: 8.6, y: 2.05, variant: 2 },
		{ id: 't4', kind: 'palm', x: 9.9, y: 2.6, variant: 0 },
		{ id: 't5', kind: 'pine', x: 1.75, y: 4.15, variant: 2 },
		{ id: 'hibiscus', kind: 'hibiscus', x: 10.75, y: 4.3 },
		{ id: 'lamp1', kind: 'lamp', x: 4.15, y: 3.65 },
		{ id: 'lamp2', kind: 'lamp', x: 8.1, y: 3.65 },
		{ id: 'fountain', kind: 'fountain', x: 6.1, y: 5.15 },
		{ id: 'bench1', kind: 'bench', x: 2.75, y: 5.0 },
		{ id: 'bench2', kind: 'bench', x: 9.55, y: 5.25 },
		{ id: 'cat', kind: 'cat', x: 10.35, y: 5.55 },
		{ id: 'flowers1', kind: 'flowers', x: 3.5, y: 6.6 },
		{ id: 'flowers2', kind: 'flowers', x: 1.9, y: 5.9, variant: 1 },
		{ id: 'boat', kind: 'sampan', x: 9.55, y: 7.75, custom: true }
	];

	const CAST = [
		{ id: 'a', animal: 'harimau', colour: 'jingga', skin: 's2' },
		{ id: 'b', animal: 'penyu', colour: 'teal', skin: 's4' },
		{ id: 'c', animal: 'enggang', colour: 'kuning', skin: 's1' },
		{ id: 'd', animal: 'gajah', colour: 'biru', skin: 's5' },
		{ id: 'e', animal: 'arnab', colour: 'jambu', skin: 's3' },
		{ id: 'f', animal: 'beruang', colour: 'hijau', skin: 's2' }
	];
	const SPOTS: [number, number][] = [
		[4.1, 5.0], [8.2, 4.7], [5.1, 6.35], [7.3, 6.2], [3.3, 3.95], [9.0, 4.05], [6.1, 3.3], [4.8, 4.15], [8.8, 6.0], [6.9, 7.0]
	];

	let places = $state(CAST.map((_, i) => ({ at: SPOTS[i], walking: false, facing: i % 2 ? -1 : 1 })));
	let width = $state(0);
	const tile = $derived(Math.max(22, width / W));

	// Every few seconds one child strolls to a free spot; nobody moves when motion is reduced.
	$effect(() => {
		if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
		const timer = setInterval(() => {
			const who = Math.floor(Math.random() * places.length);
			const taken = new Set(places.map((p) => p.at.join()));
			const free = SPOTS.filter((s) => !taken.has(s.join()));
			const to = free[Math.floor(Math.random() * free.length)];
			if (!to) return;
			const from = places[who].at;
			places[who] = { at: to, walking: true, facing: to[0] < from[0] ? -1 : 1 };
			setTimeout(() => (places[who] = { ...places[who], walking: false }), 1600);
		}, 2400);
		return () => clearInterval(timer);
	});

	const actors = $derived<WorldActor[]>(
		CAST.map((c, i) => ({
			id: c.id,
			x: places[i].at[0],
			y: places[i].at[1],
			facing: places[i].facing,
			walking: places[i].walking,
			animal: c.animal,
			colour: c.colour,
			skin: c.skin,
			name: '',
			mood: i % 3 === 0 ? 'cheer' : 'happy'
		}))
	);
</script>

{#snippet ground()}
	<path d={land(1.08, 0.08)} fill="#3d97cc" />
	<path d={land(1.025, 0.04)} fill="#e8f6fc" opacity=".75" />
	<path d={land(1, 0.2)} fill="#d9a94f" />
	<path d={land(1)} fill="#f3d28a" />
	<path d={land(0.93, -0.02)} fill="#6cb33f" />
	<path d={land(0.93, -0.1)} fill="#8fd05e" />
	<!-- The square, a path in from the arch, and one down to the jetty. -->
	<path d="M5.45 2.3 H6.75 L6.95 3.5 H5.25z" fill="#e9cf98" />
	<path d="M7.7 5.6 C8.3 6.2 8.6 6.6 8.75 7.1 L9.45 7.0 C9.2 6.4 8.8 5.9 8.2 5.4z" fill="#e9cf98" />
	<ellipse cx="6.1" cy="4.75" rx="3.1" ry="1.55" fill="#e9cf98" />
	<ellipse cx="6.1" cy="4.75" rx="2.8" ry="1.32" fill="none" stroke="#d8b77a" stroke-width="0.06" stroke-dasharray="0.25 0.18" />
	<!-- The jetty, out over the water to the sampan. -->
	<path d="M8.6 6.95 L9.65 6.8 L10.0 7.55 L8.85 7.75z" fill="#c98a54" />
	<path d="M8.95 6.95 L9.2 7.68 M9.3 6.9 L9.55 7.62" stroke="#a46a37" stroke-width="0.05" />
	{#each [[1.7, 3.0], [9.9, 3.3], [3.2, 6.0], [10.2, 6.2], [7.6, 2.7], [1.2, 5.0]] as [x, y] (`${x}-${y}`)}
		<path d="M{x} {y} l0.06 -0.16 l0.06 0.16 M{x + 0.3} {y - 0.2} l0.05 -0.13 l0.05 0.13" stroke="#6cb33f" stroke-width="0.05" fill="none" stroke-linecap="round" />
	{/each}
{/snippet}

{#snippet art(_prop: WorldProp, t: number)}
	<Sampan tile={t} animal="kancil" colour="hijau" skin="s2" />
{/snippet}

<div class="main-island" bind:clientWidth={width} aria-hidden="true">
	<World width={W} height={H} {tile} {ground} props={PROPS} {actors} names={false} step={1600} {art} />
</div>

<style>
	.main-island {
		width: 100%;
		aspect-ratio: 12 / 7.8;
	}
	.main-island :global(.viewport) {
		overflow: visible;
		border-radius: 0;
		background: transparent;
		box-shadow: none; /* taste-skill-ignore: removes the world frame's shadow */
	}
</style>
