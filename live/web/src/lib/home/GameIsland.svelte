<!--
	One game as a small island in the worlds' pixel art, built from the same props and characters the
	game itself uses: a river jetty and a racing sampan, lily islets, treasure sand, a forest, team
	hexagons, a kampung house, a gallery easel, a garden bed, a fishing pond, kites, a sandcastle, a
	kampung train, a night-market stall, a starry sky. The ground is painted in isles.ts. `active`
	makes the island come alive (the children cheer, the sampan rows, the flags wave, the kites fly).
-->
<script lang="ts">
	import World, { type WorldActor, type WorldProp } from '$lib/worlds/World.svelte';
	import { TILE, snapScale } from '$lib/pixel/cache';
	import Sprite from '$lib/pixel/Sprite.svelte';
	import GardenBed from '$lib/worlds/GardenBed.svelte';
	import Sampan from '$lib/worlds/Sampan.svelte';
	import { carriage, castleFloor, engine, fish, flag, kite, stall, star } from '$lib/games/fun/art';
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
		],
		pancing: [
			{ id: 'palm', kind: 'palm', x: 0.95, y: 2.4, variant: 0 },
			{ id: 'reeds', kind: 'reeds', x: 4.95, y: 2.75 },
			{ id: 'lily', kind: 'lily', x: 4.3, y: 3.35 },
			{ id: 'fish', kind: 'fish', x: 3.55, y: 3.2, state: 'arowana', custom: true }
		],
		wau: [
			{ id: 'k1', kind: 'kite', x: 2.0, y: 1.55, variant: 0, custom: true },
			{ id: 'k2', kind: 'kite', x: 4.35, y: 1.25, variant: 2, custom: true },
			{ id: 'bush', kind: 'bush', x: 5.0, y: 3.1, variant: 1 },
			{ id: 'flowers', kind: 'flowers', x: 0.9, y: 3.0 }
		],
		kubu: [
			{ id: 'castle', kind: 'castle', x: 2.85, y: 3.2, custom: true },
			{ id: 'palm', kind: 'palm', x: 4.75, y: 2.1, variant: 1 },
			{ id: 'rock', kind: 'rock', x: 1.05, y: 3.05 }
		],
		keretapi: [
			{ id: 'train', kind: 'train', x: 3.0, y: 3.4, custom: true },
			{ id: 'tree', kind: 'tree', x: 1.2, y: 2.35, variant: 1 },
			{ id: 'pine', kind: 'pine', x: 4.85, y: 2.2, variant: 0 },
			{ id: 'flowers', kind: 'flowers', x: 3.0, y: 2.25 }
		],
		pasar: [
			{ id: 'stall', kind: 'stall', x: 3.0, y: 3.05, custom: true },
			{ id: 'lamp', kind: 'lamp', x: 0.95, y: 3.0 },
			{ id: 'pelita', kind: 'pelita', x: 5.1, y: 3.1 }
		],
		bintang: [
			{ id: 's1', kind: 'star', x: 1.1, y: 1.0, custom: true },
			{ id: 's2', kind: 'star', x: 2.3, y: 0.55, custom: true },
			{ id: 's3', kind: 'star', x: 3.7, y: 0.8, custom: true },
			{ id: 's4', kind: 'star', x: 4.9, y: 0.45, custom: true },
			{ id: 's5', kind: 'star', x: 3.1, y: 1.6, custom: true },
			{ id: 'pine', kind: 'pine', x: 0.95, y: 2.75, variant: 2 },
			{ id: 'lamp', kind: 'pelita', x: 5.0, y: 3.05 }
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
		kebun: [{ id: 'a', x: 4.0, y: 3.95, animal: 'kancil', colour: 'teal', skin: 's2' }],
		pancing: [{ id: 'a', x: 2.1, y: 2.85, animal: 'kucing', colour: 'jingga', skin: 's3' }],
		wau: [
			{ id: 'a', x: 2.4, y: 3.45, animal: 'arnab', colour: 'jambu', skin: 's2' },
			{ id: 'b', x: 3.9, y: 3.3, animal: 'gajah', colour: 'biru', skin: 's4', facing: -1 }
		],
		kubu: [{ id: 'a', x: 4.0, y: 3.6, animal: 'penyu', colour: 'teal', skin: 's1', facing: -1 }],
		keretapi: [{ id: 'a', x: 5.0, y: 3.95, animal: 'beruang', colour: 'kuning', skin: 's5', facing: -1 }],
		pasar: [
			{ id: 'a', x: 1.75, y: 3.75, animal: 'enggang', colour: 'merah', skin: 's2' },
			{ id: 'b', x: 4.35, y: 3.8, animal: 'kancil', colour: 'ungu', skin: 's4', facing: -1 }
		],
		bintang: [
			{ id: 'a', x: 2.2, y: 3.4, animal: 'harimau', colour: 'jingga', skin: 's3' },
			{ id: 'b', x: 3.85, y: 3.35, animal: 'penyu', colour: 'teal', skin: 's2', facing: -1 }
		]
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
	{:else if prop.kind === 'fish'}
		<span class="leap" class:go={active}><Sprite sheet={fish(prop.state ?? 'arowana')} {s} flip /></span>
	{:else if prop.kind === 'kite'}
		<span class="fly" class:go={active}><Sprite sheet={kite(prop.variant ?? 0)} {s} /></span>
	{:else if prop.kind === 'castle'}
		<span class="stack">
			<Sprite sheet={flag(0)} {s} />
			<Sprite sheet={castleFloor(true)} {s} />
			<Sprite sheet={castleFloor(false)} {s} />
			<Sprite sheet={castleFloor(false)} {s} />
		</span>
	{:else if prop.kind === 'train'}
		<span class="train" class:go={active}>
			<Sprite sheet={carriage(1, 2)} {s} />
			<Sprite sheet={carriage(0, 3)} {s} />
			<Sprite sheet={engine()} {s} />
		</span>
	{:else if prop.kind === 'stall'}
		<Sprite sheet={stall(['lampu', 'kanopi'], 'satay')} {s} />
	{:else if prop.kind === 'star'}
		<span class="twinkle" class:go={active}><Sprite sheet={star(true)} {s} /></span>
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
	.stack,
	.train {
		display: flex;
		line-height: 0;
	}
	.stack {
		flex-direction: column;
		align-items: center;
	}
	.train {
		align-items: flex-end;
	}
	.leap,
	.fly,
	.twinkle {
		display: block;
	}
	.leap.go {
		animation: leap 1.6s steps(4) infinite;
	}
	.fly.go {
		animation: fly 1.8s steps(3) infinite;
	}
	.train.go {
		animation: chug 0.5s steps(2) infinite;
	}
	.twinkle.go {
		animation: twinkle 1.2s steps(2) infinite;
	}
	.twinkle {
		opacity: 0.85;
	}
	@keyframes leap {
		50% {
			transform: translateY(-6px);
		}
	}
	@keyframes fly {
		50% {
			transform: translate(3px, -4px) rotate(4deg);
		}
	}
	@keyframes chug {
		50% {
			transform: translateY(-1px);
		}
	}
	@keyframes twinkle {
		50% {
			opacity: 0.45;
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.go {
			animation: none !important;
		}
	}
</style>
