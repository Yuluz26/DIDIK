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
	// The children stroll one loop round the fountain, evenly spaced and at the same pace, so nobody
	// walks into anybody or through the water. The loop (in tiles) keeps clear of the basin, the lamps
	// and the benches.
	const LOOP = { x: 6.1, y: 4.7, rx: 2.1, ry: 1.3 };
	const LAP_SECONDS = 15;
	const STEP_MS = 350;
	const at = (angle: number): [number, number] => [LOOP.x + Math.cos(angle) * LOOP.rx, LOOP.y + Math.sin(angle) * LOOP.ry];
	const start = CAST.map((_, i) => (i / CAST.length) * Math.PI * 2);

	let angle = $state(0);
	let walking = $state(false);
	let width = $state(0);
	// A whole or half step of the sprite size, so every pixel on the island is the same size.
	const tile = $derived(TILE * snapScale(width / W / TILE, 1));

	const places = $derived(
		start.map((s0) => {
			const a0 = s0 + angle;
			const [x, y] = at(a0);
			// going round anticlockwise on screen: moving right along the front, left along the back
			const facing = -Math.sin(a0) >= 0 ? -1 : 1;
			return { at: [x, y] as [number, number], walking, facing, ms: STEP_MS };
		})
	);

	// Nobody moves when motion is reduced.
	$effect(() => {
		if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
		walking = true;
		const timer = setInterval(() => (angle -= ((Math.PI * 2) / LAP_SECONDS) * (STEP_MS / 1000)), STEP_MS);
		return () => clearInterval(timer);
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
