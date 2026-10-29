<!--
	The host's big screen for Pancing Ikan, Kubu Pasir, Kereta Api Kampung and Pasar Malam: the three
	best worlds side by side (the leader's larger), each with its owner and score, so the room sees
	what a good catch, castle, train or stall looks like.
-->
<script lang="ts">
	import type { Person } from '$lib/types';
	import Sprite from '$lib/pixel/Sprite.svelte';
	import Avatar from '$ui/Avatar.svelte';
	import { fish } from './art';
	import CastleWorld from './CastleWorld.svelte';
	import MarketWorld from './MarketWorld.svelte';
	import TrainWorld from './TrainWorld.svelte';

	// eslint-disable-next-line @typescript-eslint/no-explicit-any
	let { game, world, people, unit }: { game: string; world: any; people: Map<string, Person>; unit: string } = $props();

	// eslint-disable-next-line @typescript-eslint/no-explicit-any
	const top = $derived(((world?.top ?? []) as any[]).filter((t) => people.has(t.id)));
	const TITLE: Record<string, string> = { pancing: 'Pemancing terhebat', kubu: 'Istana paling tinggi', keretapi: 'Kereta api paling jauh', pasar: 'Gerai paling laris' };
	const EMPTY: Record<string, string> = {
		pancing: 'Tangkapan pertama akan muncul di sini.',
		kubu: 'Istana pertama akan muncul di sini.',
		keretapi: 'Kereta api pertama akan muncul di sini.',
		pasar: 'Gerai pertama akan muncul di sini.'
	};
</script>

<section class="tops" aria-label={TITLE[game]}>
	<h2>{TITLE[game]}</h2>
	{#if top.length}
		<ol class="board" class:solo={top.length === 1}>
			{#each top as t, i (t.id)}
				{@const owner = people.get(t.id)!}
				<li class:first={i === 0}>
					<div class="world">
						{#if game === 'pancing'}
							<div class="catch">
								{#if t.best}<Sprite sheet={fish(t.best)} s={i === 0 ? 6 : 4} />{/if}
								<p>{t.caught} ekor</p>
								<div class="net">{#each t.net ?? [] as kind, j (j)}<Sprite sheet={fish(kind)} s={2} />{/each}</div>
							</div>
						{:else if game === 'kubu'}
							<CastleWorld world={t} s={i === 0 ? 4 : 2} />
						{:else if game === 'keretapi'}
							<TrainWorld world={{ ...t, stations: world.stations }} s={i === 0 ? 3 : 2} />
						{:else if game === 'pasar'}
							<MarketWorld world={{ mine: t.upgrades ?? [], good: t.good, upgrades: world.upgrades }} s={i === 0 ? 4 : 2} />
						{/if}
					</div>
					<p class="who"><span class="place">{i + 1}</span><Avatar animal={owner.avatar} colour={owner.colour} skin={owner.skin} size={30} /> <strong>{owner.name}</strong> <span class="score">{t.score} {unit}</span></p>
				</li>
			{/each}
		</ol>
	{:else}
		<p class="empty">{EMPTY[game]}</p>
	{/if}
</section>

<style>
	.tops {
		display: grid;
		gap: 0.8rem;
	}
	.tops h2 {
		font-size: 1.4rem;
	}
	.board {
		display: grid;
		grid-template-columns: minmax(0, 2fr) minmax(0, 1fr);
		gap: 0.8rem;
		margin: 0;
		padding: 0;
		list-style: none;
	}
	.board.solo {
		grid-template-columns: minmax(0, 1fr);
	}
	.board li.first {
		grid-row: span 2;
	}
	.board li {
		display: grid;
		gap: 0.4rem;
		align-content: start;
		min-width: 0;
	}
	.catch {
		display: grid;
		justify-items: center;
		gap: 0.4rem;
		padding: 1rem;
		border-radius: var(--r-lg);
		background: linear-gradient(180deg, #47b0bd, #2a88a6);
		color: #fff;
		font-weight: 800;
		image-rendering: pixelated;
	}
	.net {
		display: flex;
		flex-wrap: wrap;
		justify-content: center;
		gap: 0.2rem;
	}
	.who {
		display: flex;
		align-items: center;
		gap: 0.4rem;
		font-weight: 800;
	}
	.place {
		display: grid;
		place-items: center;
		width: 1.6rem;
		height: 1.6rem;
		border-radius: 50%;
		background: var(--sun);
		font-family: var(--font-display);
	}
	.score {
		margin-left: auto;
		color: var(--ink-2);
	}
	.empty {
		padding: 2rem;
		border-radius: var(--r-lg);
		background: var(--card);
		color: var(--ink-2);
		text-align: center;
		font-weight: 800;
	}
	@media (max-width: 720px) {
		.board {
			grid-template-columns: minmax(0, 1fr);
		}
		.board li.first {
			grid-row: auto;
		}
	}
</style>
