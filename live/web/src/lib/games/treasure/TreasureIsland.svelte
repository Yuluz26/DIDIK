<!--
	A child's own island in Pulau Harta Karun, in the worlds' 3/4 view: twelve spots marked with an X
	in the sand among palms and rocks. A right answer earns a shovel; tap a spot and the child's
	character walks over and digs. What is found is decided on the server at the moment of digging.
-->
<script lang="ts">
	import type { Person } from '$lib/types';
	import { play } from '$lib/sound';
	import { confetti } from '$lib/confetti';
	import { TILE, fitTile } from '$lib/pixel/cache';
	import Sprite from '$lib/pixel/Sprite.svelte';
	import World, { type WorldActor, type WorldProp } from '$lib/worlds/World.svelte';
	import Loot from './Loot.svelte';
	import { LOOT_NAMES } from './loot';
	import { islandGround, spotHole, spotMark } from './sprites';

	interface Found {
		found: string;
		amount: number;
		from?: string | null;
		tile?: number;
	}

	let {
		world,
		me = null,
		ondig
	}: {
		world: { island: number; tiles: { i: number; dug: Found | null }[]; last: Found | null; canDig: boolean };
		me?: Person | null;
		ondig: (tile: number) => void;
	} = $props();

	const W = 14;
	const H = 10;
	const COLUMNS = [3.7, 6.0, 8.3, 10.6];
	const ROWS = [4.5, 6.3, 8.1];
	const spotAt = (i: number): [number, number] => [COLUMNS[i % 4] + (Math.floor(i / 4) % 2) * 0.35, ROWS[Math.floor(i / 4)]];
	const HOME: [number, number] = [12.2, 6.2];

	const SCENERY: WorldProp[] = [
		{ id: 'palm1', kind: 'palm', x: 2.6, y: 4.0, variant: 0 },
		{ id: 'palm2', kind: 'palm', x: 12.1, y: 3.7, variant: 1 },
		{ id: 'palm3', kind: 'palm', x: 7.4, y: 2.9, variant: 2 },
		{ id: 'bush', kind: 'bush', x: 9.6, y: 3.1, variant: 1 },
		{ id: 'rock1', kind: 'rock', x: 2.7, y: 7.6 },
		{ id: 'rock2', kind: 'rock', x: 12.4, y: 8.4 },
		{ id: 'flowers', kind: 'flowers', x: 4.9, y: 3.2 },
		{ id: 'sign', kind: 'sign', x: 12.9, y: 5.3 }
	];

	let width = $state(0);
	const tile = $derived(fitTile(width, W, { min: 1.5, max: 64 }));
	const ground = islandGround(W, H);

	let digging = $state<number | null>(null);
	let fresh = $state<number | null>(null);
	let spot = $state<[number, number] | null>(null);
	let walking = $state(false);

	function dig(i: number) {
		if (!world.canDig || digging !== null) return;
		const [x, y] = spotAt(i);
		spot = [x + 0.95, y + 0.15];
		walking = true;
		setTimeout(() => (walking = false), 520);
		digging = i;
		play('dig');
		ondig(i);
	}

	$effect(() => {
		const last = world.last;
		if (!last || last.tile === undefined || last.tile !== digging) return;
		fresh = last.tile;
		digging = null;
		if (last.found === 'gem' || last.found === 'map' || last.found === 'chest') confetti({ count: 60 });
		play(last.amount < 0 ? 'almost' : last.found === 'parrot' ? 'steal' : 'coin');
		const timer = setTimeout(() => (fresh = null), 1600);
		return () => clearTimeout(timer);
	});

	const items = $derived<WorldProp[]>([
		...SCENERY,
		...world.tiles.map((t) => {
			const [x, y] = spotAt(t.i);
			return {
				id: `spot-${t.i}`,
				kind: 'spot',
				custom: true,
				x,
				y,
				label: t.dug ? `${LOOT_NAMES[t.dug.found]} ${t.dug.amount >= 0 ? '+' : ''}${t.dug.amount}` : `Gali tempat ${t.i + 1}`,
				action: !t.dug && world.canDig ? () => dig(t.i) : undefined
			};
		})
	]);

	const actors = $derived<WorldActor[]>(
		me
			? [
					{
						id: me.id,
						x: (spot ?? HOME)[0],
						y: (spot ?? HOME)[1],
						facing: -1,
						walking,
						animal: me.avatar,
						colour: me.colour,
						skin: me.skin,
						name: me.name,
						mood: fresh !== null && (world.last?.amount ?? 0) > 0 ? 'cheer' : 'happy'
					}
				]
			: []
	);
</script>

{#snippet art(prop: WorldProp, tile: number)}
	{@const i = Number(prop.id.slice(5))}
	{@const found = world.tiles.find((t) => t.i === i)?.dug ?? null}
	{@const s = tile / TILE}
	<span class="spot" class:dug={!!found} class:ready={!found && world.canDig} class:digging={digging === i} class:fresh={fresh === i} style:--t="{tile}px" style:--s="{s}px" style:--n={i}>
		{#if found}
			<span class="hole"><Sprite sheet={spotHole()} {s} /></span>
			<span class="loot"><Loot kind={found.found} size={Math.round(tile * 1.1)} /></span>
			{#if found.amount}<span class="amount" class:minus={found.amount < 0}>{found.amount > 0 ? '+' : ''}{found.amount}</span>{/if}
		{:else}
			<span class="mound"><Sprite sheet={spotMark()} {s} /></span>
		{/if}
	</span>
{/snippet}

<figure class="treasure" class:dig-now={world.canDig}>
	<div class="map" bind:clientWidth={width}>
		<div class="fit" style:max-width="{W * tile}px">
			<World width={W} height={H} {tile} {ground} props={items} {actors} me={me?.id ?? null} names="me" step={480} {art} />
		</div>
	</div>
	<figcaption class="tip">
		{#if world.canDig}
			<strong>Kamu dapat penyodok!</strong> Ketik satu tanda X untuk menggali.
		{:else}
			Pulau {world.island} · jawab betul untuk dapat penyodok
		{/if}
	</figcaption>
</figure>

<style>
	.treasure {
		display: grid;
		gap: 0.6rem;
		margin: 0;
	}
	.map {
		min-width: 0;
	}
	.fit {
		margin-inline: auto;
	}
	.spot {
		position: relative;
		display: block;
		width: calc(var(--s) * 28);
		height: calc(var(--s) * 16);
		line-height: 0;
	}
	.mound,
	.hole {
		position: absolute;
		inset: 0;
	}
	.ready .mound {
		animation: bob 1.4s steps(2) infinite;
		animation-delay: calc(var(--n) * 90ms);
	}
	.digging {
		animation: wiggle 0.3s steps(3) infinite;
	}
	.loot {
		position: absolute;
		left: 50%;
		bottom: calc(var(--s) * 4);
		translate: -50% 0;
		line-height: 0;
	}
	.fresh .loot {
		animation: pop-in 600ms var(--spring);
	}
	.amount {
		position: absolute;
		top: calc(var(--s) * -14);
		right: calc(var(--s) * -3);
		padding: 0 0.35rem;
		border: 2px solid #2a1f2d;
		border-radius: 4px;
		background: #fff6e6;
		color: var(--good);
		font: 700 0.8rem/1.4 var(--font-pixel);
	}
	.amount.minus {
		color: var(--almost);
	}
	.fresh .amount {
		animation: rise-in 500ms var(--spring);
	}
	.tip {
		justify-self: center;
		max-width: 100%;
		padding: 0.4rem 1rem;
		border: 2px solid #2a1f2d;
		border-radius: 4px;
		background: #fff6e6;
		font-weight: 700;
		text-align: center;
		box-shadow: 0 3px 0 #2a1f2d;
	}
	.dig-now .tip {
		background: var(--sun);
		animation: pop-in 400ms var(--spring);
	}
</style>
