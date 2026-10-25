<!--
	One game as a small island in the worlds' pixel art, built from the same props and characters the
	game itself uses: a river jetty and a racing sampan, lily islets, treasure sand, a forest, team
	hexagons, a kampung house, a gallery easel, a garden bed. The ground is painted in isles.ts.
	`active` makes the island come alive (the children cheer, the sampan rows, the flags wave).
-->
<script lang="ts">
	import World, { type WorldActor, type WorldProp } from '$lib/worlds/World.svelte';
	import { TILE, snapScale } from '$lib/pixel/cache';
	import Sprite from '$lib/pixel/Sprite.svelte';
	import GardenBed from '$lib/worlds/GardenBed.svelte';
	import Sampan from '$lib/worlds/Sampan.svelte';
	import { ISLE, gameGround } from './isles';
	import { easelSprite, flagSprite, markBadge } from './sprites';

	let { game, width, active = false }: { game: string; width: number; active?: boolean } = $props();

	const { w: W, h: H } = ISLE;
	// A whole or half step of the sprite size, so every pixel on the island is the same size.
	const tile = $derived(TILE * snapScale(width / W / TILE, 1));
	const s = $derived(tile / TILE);
	const cheer = $derived(active ? 'cheer' : 'happy');

	const PROPS: Record<string, WorldProp[]> = {
		lumba: [
			{ id: 'palm', kind: 'palm', x: 0.85, y: 2.45, variant: 1 },
			{ id: 'finish', kind: 'banner', x: 2.7, y: 2.2, variant: 0, state: 'PENAMAT' },
			{ id: 'reeds', kind: 'reeds', x: 3.7, y: 3.35 },
			{ id: 'flowers', kind: 'flowers', x: 1.6, y: 3.35 },
			{ id: 'boat', kind: 'sampan', x: 4.75, y: 4.35, custom: true }
		],
		lompat: [
			{ id: 'l1', kind: 'lily', x: 0.5, y: 4.1 },
			{ id: 'l2', kind: 'lily', x: 5.55, y: 2.15 },
			{ id: 'l3', kind: 'lily', x: 2.35, y: 4.0 },
			{ id: 'tick', kind: 'mark', x: 3.95, y: 2.0, state: 'yes', custom: true },
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
			{ id: 'bed', kind: 'bed', x: 2.6, y: 3.45, state: 'jagung', custom: true },
			{ id: 'scarecrow', kind: 'scarecrow', x: 4.75, y: 2.75 },
			{ id: 'jar', kind: 'tempayan', x: 0.95, y: 2.8 },
			{ id: 'flowers', kind: 'flowers', x: 4.6, y: 3.65 }
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
		kebun: [{ id: 'a', x: 4.0, y: 3.95, animal: 'kancil', colour: 'teal', skin: 's2' }]
	};

	const things = $derived(PROPS[game] ?? []);
	const actors = $derived<WorldActor[]>((CAST[game] ?? []).map((a) => ({ ...a, name: '', mood: cheer })));
	const ground = $derived(gameGround(game));
</script>

{#snippet art(prop: WorldProp, t: number)}
	{#if prop.kind === 'sampan'}
		<Sampan tile={t} animal="harimau" colour="jingga" skin="s3" mood={cheer} rowing={active} />
	{:else if prop.kind === 'mark'}
		<Sprite sheet={markBadge(prop.state === 'yes')} {s} />
	{:else if prop.kind === 'flag'}
		<Sprite sheet={flagSprite(prop.state ?? '#f28c28')} {s} frames={active ? 2 : 1} ms={600} />
	{:else if prop.kind === 'easel'}
		<Sprite sheet={easelSprite()} {s} />
	{:else if prop.kind === 'bed'}
		<GardenBed crop={prop.state} stage={4} need={3} tile={t} />
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
</style>
