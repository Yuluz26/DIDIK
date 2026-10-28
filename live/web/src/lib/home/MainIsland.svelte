<!--
	The front page's main island: the town square where children gather before a game (the same arch
	and fountain as the waiting room), children in their animal hoodies wandering about, and the jetty
	where a sampan waits to take them to the game islands.
-->
<script lang="ts">
	import { TILE, snapScale } from '$lib/pixel/cache';
	import World, { type WorldActor, type WorldProp } from '$lib/worlds/World.svelte';
	import Sampan from '$lib/worlds/Sampan.svelte';
	import { MAIN, townGround } from './isles';
	import { route, type Spot } from '$lib/worlds/route';

	const { w: W, h: H } = MAIN;

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

	let places = $state(CAST.map((_, i) => ({ at: SPOTS[i], walking: false, facing: i % 2 ? -1 : 1, ms: 1600 })));
	// Where each child is going (or stands), so two never head for the same spot.
	const goals: Spot[] = CAST.map((_, i) => SPOTS[i]);
	const busy = new Set<number>();
	let width = $state(0);
	// A whole or half step of the sprite size, so every pixel on the island is the same size.
	const tile = $derived(TILE * snapScale(width / W / TILE, 1));

	// The fountain's basin, where nobody walks (in tiles, with room for a child's width); a walk that
	// would cross it goes round it.
	const BASIN = { x: 6.1, y: 4.6, rx: 1.5, ry: 0.72 };

	// Every few seconds one child strolls to a free spot, round the fountain if it is in the way; nobody
	// moves when motion is reduced.
	$effect(() => {
		if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
		const timers = new Set<ReturnType<typeof setTimeout>>();
		const later = (fn: () => void, ms: number) => {
			const t = setTimeout(() => {
				timers.delete(t);
				fn();
			}, ms);
			timers.add(t);
		};
		const walk = (who: number, path: Spot[], leg = 1) => {
			if (leg >= path.length) {
				places[who] = { ...places[who], walking: false };
				busy.delete(who);
				return;
			}
			const from = path[leg - 1];
			const to = path[leg];
			// about two and a half tiles a second
			const ms = Math.max(350, Math.round(Math.hypot(to[0] - from[0], to[1] - from[1]) * 400));
			places[who] = { at: to, walking: true, facing: to[0] < from[0] ? -1 : 1, ms };
			later(() => walk(who, path, leg + 1), ms);
		};
		const timer = setInterval(() => {
			const idle = places.map((_, i) => i).filter((i) => !busy.has(i));
			const who = idle[Math.floor(Math.random() * idle.length)];
			if (who === undefined) return;
			const taken = new Set(goals.map((g) => g.join()));
			const free = SPOTS.filter((s) => !taken.has(s.join()));
			const to = free[Math.floor(Math.random() * free.length)];
			if (!to) return;
			busy.add(who);
			goals[who] = to;
			walk(who, route(places[who].at, to, BASIN));
		}, 2400);
		return () => {
			clearInterval(timer);
			for (const t of timers) clearTimeout(t);
		};
	});

	const actors = $derived<WorldActor[]>(
		CAST.map((c, i) => ({
			id: c.id,
			x: places[i].at[0],
			y: places[i].at[1],
			facing: places[i].facing,
			walking: places[i].walking,
			ms: places[i].ms,
			animal: c.animal,
			colour: c.colour,
			skin: c.skin,
			name: '',
			mood: i % 3 === 0 ? 'cheer' : 'happy'
		}))
	);
</script>

{#snippet art(_prop: WorldProp, t: number)}
	<Sampan tile={t} animal="kancil" colour="hijau" skin="s2" />
{/snippet}

<div class="main-island" bind:clientWidth={width} aria-hidden="true">
	<World width={W} height={H} {tile} ground={townGround()} props={PROPS} {actors} names={false} step={1600} {art} />
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
