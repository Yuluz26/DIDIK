<!--
	A child's own island in Pulau Harta Karun, in the worlds' 3/4 view: twelve spots marked with an X
	in the sand among palms and rocks. A right answer earns a shovel; tap a spot and the child's
	character walks over and digs. What is found is decided on the server at the moment of digging.
-->
<script lang="ts">
	import type { Person } from '$lib/types';
	import { play } from '$lib/sound';
	import { confetti } from '$lib/confetti';
	import World, { type WorldActor, type WorldProp } from '$lib/worlds/World.svelte';
	import Loot from './Loot.svelte';
	import { LOOT_NAMES } from './loot';

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
	const tile = $derived(Math.max(20, Math.min(52, width / W)));

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
	<span class="spot" class:dug={!!found} class:ready={!found && world.canDig} class:digging={digging === i} class:fresh={fresh === i} style:--t="{tile}px" style:--n={i}>
		{#if found}
			<svg class="hole" viewBox="0 0 60 30" aria-hidden="true">
				<ellipse cx="30" cy="20" rx="27" ry="9" fill="#e0b871" />
				<ellipse cx="30" cy="18" rx="19" ry="6" fill="#8e5a2e" />
			</svg>
			<span class="loot"><Loot kind={found.found} size={Math.round(tile * 0.95)} /></span>
			{#if found.amount}<span class="amount" class:minus={found.amount < 0}>{found.amount > 0 ? '+' : ''}{found.amount}</span>{/if}
		{:else}
			<svg class="mound" viewBox="0 0 60 36" aria-hidden="true">
				<ellipse cx="30" cy="28" rx="27" ry="8" fill="#000" opacity=".1" />
				<ellipse cx="30" cy="26" rx="26" ry="9" fill="#e0b871" />
				<ellipse cx="30" cy="22" rx="18" ry="9" fill="#f2d49b" />
				<path d="M24 14l12 10M36 14l-12 10" stroke="#c0503a" stroke-width="3.5" stroke-linecap="round" opacity=".85" />
			</svg>
		{/if}
	</span>
{/snippet}

<figure class="treasure" class:dig-now={world.canDig}>
	<div class="map" bind:clientWidth={width}>
		<div class="fit" style:max-width="{W * tile}px">
			<World width={W} height={H} {tile} props={items} {actors} me={me?.id ?? null} names="me" step={480} {art}>
				{#snippet ground()}
					<rect width={W} height={H} fill="#3ba7d9" />
					{#each [[1.0, 1.2], [11.5, 0.9], [0.8, 9.2], [12.6, 9.4], [6.5, 0.6]] as [x, y] (`${x}-${y}`)}
						<path d="M{x} {y} q0.3 -0.15 0.6 0 t0.6 0" stroke="#9fd8f0" stroke-width="0.08" fill="none" stroke-linecap="round" />
					{/each}
					<path d="M1.6 5.6 C1.4 2.8 4.4 1.7 7.1 1.8 C10.2 1.7 13.1 2.6 13.3 5.6 C13.5 8.6 11.1 9.8 7.2 9.7 C3.4 9.8 1.8 8.4 1.6 5.6z" fill="#bfe6f6" />
					<path d="M1.95 5.6 C1.8 3.1 4.5 2.1 7.1 2.2 C10.0 2.1 12.8 2.9 12.95 5.6 C13.1 8.3 10.9 9.4 7.2 9.35 C3.6 9.4 2.1 8.1 1.95 5.6z" fill="#e0b871" />
					<path d="M2.25 5.5 C2.1 3.3 4.6 2.45 7.1 2.5 C9.9 2.45 12.5 3.2 12.6 5.5 C12.75 8.0 10.7 9.0 7.2 8.95 C3.8 9.0 2.4 7.8 2.25 5.5z" fill="#f2d49b" />
					<ellipse cx="7.4" cy="3.2" rx="4.4" ry="0.85" fill="#8fd05e" />
					{#each [[4.6, 5.6], [9.5, 7.3], [5.2, 8.6], [11.4, 6.9], [7.0, 5.2]] as [x, y] (`s${x}`)}
						<circle cx={x} cy={y} r="0.06" fill="#d6aa62" /><circle cx={x + 0.25} cy={y + 0.1} r="0.05" fill="#d6aa62" />
					{/each}
				{/snippet}
			</World>
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
		display: grid;
		place-items: end center;
		width: calc(var(--t) * 1.55);
		height: calc(var(--t) * 1.25);
	}
	.mound,
	.hole {
		width: 100%;
		height: auto;
	}
	.ready .mound {
		animation: bob 1.4s ease-in-out infinite;
		animation-delay: calc(var(--n) * 90ms);
	}
	.digging {
		animation: wiggle 0.3s ease-in-out infinite;
	}
	.loot {
		position: absolute;
		left: 50%;
		bottom: calc(var(--t) * 0.22);
		translate: -50% 0;
		line-height: 0;
	}
	.fresh .loot {
		animation: pop-in 600ms var(--spring);
	}
	.amount {
		position: absolute;
		top: calc(var(--t) * -0.35);
		right: calc(var(--t) * -0.2);
		padding: 0 0.35rem;
		border-radius: var(--r-pill);
		background: #fff;
		color: var(--good);
		font: 600 0.8rem/1.5 var(--font-display);
		box-shadow: 0 2px 0 rgb(0 0 0 / 0.12);
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
		border-radius: var(--r-pill);
		background: var(--card);
		font-weight: 700;
		text-align: center;
		box-shadow: 0 2px 0 var(--line);
	}
	.dig-now .tip {
		background: var(--sun);
		animation: pop-in 400ms var(--spring);
	}
</style>
