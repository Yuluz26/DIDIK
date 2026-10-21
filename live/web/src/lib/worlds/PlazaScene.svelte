<!--
	The front page's picture: a small town square in the worlds' 3/4 view, with a fountain, trees and
	benches, and children in their animal hoodies wandering about, as they will in the games.
-->
<script lang="ts">
	import World, { type WorldActor, type WorldProp } from './World.svelte';

	const W = 12;
	const H = 7.4;

	const PROPS: WorldProp[] = [
		{ id: 'fountain', kind: 'fountain', x: 6.1, y: 4.3 },
		{ id: 't1', kind: 'tree', x: 1.0, y: 1.6, variant: 0 },
		{ id: 't2', kind: 'palm', x: 2.6, y: 1.2, variant: 1 },
		{ id: 't3', kind: 'tree', x: 9.4, y: 1.3, variant: 2 },
		{ id: 't4', kind: 'tree', x: 11.2, y: 1.9, variant: 1 },
		{ id: 't5', kind: 'pine', x: 0.6, y: 6.9, variant: 2 },
		{ id: 'lamp1', kind: 'lamp', x: 3.4, y: 3.2 },
		{ id: 'lamp2', kind: 'lamp', x: 8.9, y: 3.2 },
		{ id: 'bench1', kind: 'bench', x: 2.3, y: 5.3 },
		{ id: 'bench2', kind: 'bench', x: 10.0, y: 5.6 },
		{ id: 'flowers1', kind: 'flowers', x: 4.4, y: 6.8 },
		{ id: 'flowers2', kind: 'flowers', x: 7.8, y: 6.9, variant: 1 },
		{ id: 'bush', kind: 'bush', x: 11.4, y: 7.0, variant: 0 },
		{ id: 'cat', kind: 'cat', x: 8.9, y: 5.9 }
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
		[3.9, 4.9], [8.4, 4.6], [5.0, 6.3], [7.3, 6.1], [2.0, 3.6], [10.3, 3.9], [6.1, 2.6], [4.6, 3.5], [9.6, 6.6]
	];

	let places = $state(CAST.map((_, i) => ({ at: SPOTS[i], walking: false, facing: i % 2 ? -1 : 1 })));
	let width = $state(0);
	const tile = $derived(Math.max(22, Math.min(56, width / W)));

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
		}, 2600);
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

<div class="plaza" bind:clientWidth={width} aria-hidden="true">
	<World width={W} height={H} {tile} props={PROPS} {actors} names={false} step={1600}>
		{#snippet ground()}
			<rect width={W} height={H} fill="#8fd05e" />
			<path d="M-0.2 4.6 C3 4.2 4 4.6 6 4.5 C8 4.4 9.5 4.8 12.2 4.4 V5.4 C9.5 5.8 8 5.4 6 5.5 C4 5.6 3 5.2 -0.2 5.6z" fill="#e9cf98" />
			<path d="M5.6 7.6 C5.7 6.5 5.4 5.6 5.8 4.4 H6.6 C6.9 5.6 6.6 6.5 6.8 7.6z" fill="#e9cf98" />
			<ellipse cx="6.1" cy="4.6" rx="3.1" ry="1.7" fill="#e9cf98" />
			<ellipse cx="6.1" cy="4.6" rx="2.85" ry="1.5" fill="none" stroke="#d8b77a" stroke-width="0.06" stroke-dasharray="0.25 0.18" />
			{#each [[1.4, 2.6], [9.8, 2.4], [3.1, 6.2], [10.8, 6.4], [7.6, 1.9], [0.7, 4.1]] as [x, y] (`${x}-${y}`)}
				<path d="M{x} {y} l0.06 -0.16 l0.06 0.16 M{x + 0.3} {y - 0.2} l0.05 -0.13 l0.05 0.13" stroke="#6cb33f" stroke-width="0.05" fill="none" stroke-linecap="round" />
			{/each}
		{/snippet}
	</World>
</div>

<style>
	.plaza {
		width: 100%;
	}
	.plaza :global(.viewport) {
		box-shadow: var(--lift-low);
	}
</style>
