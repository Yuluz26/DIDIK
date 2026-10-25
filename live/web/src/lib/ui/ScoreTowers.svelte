<!--
	Towers of coins (or harvest) for the leading children, growing as they earn. A big-screen picture
	of who is ahead that a child can read from across the room.
-->
<script lang="ts">
	import type { Person } from '$lib/types';
	import { prescale, urlOf } from '$lib/pixel/cache';
	import { stackTile } from '$lib/pixel/icons';
	import Avatar from './Avatar.svelte';

	interface Row {
		id: string;
		score: number;
		rank: number;
	}

	let {
		rows,
		people,
		unit = 'syiling',
		kind = 'coins',
		limit = 8
	}: { rows: Row[]; people: Map<string, Person>; unit?: string; kind?: 'coins' | 'harvest'; limit?: number } = $props();

	const S = 2;
	const tile = $derived(urlOf(stackTile(kind), prescale(S)));
	const shown = $derived(rows.slice(0, limit));
	const top = $derived(Math.max(1, ...shown.map((r) => r.score)));
</script>

<ol class="towers {kind}" aria-label="Kedudukan" style:--tile="url({tile})" style:--s="{S}px">
	{#each shown as row (row.id)}
		{@const person = people.get(row.id)}
		<li class="tower">
			<span class="amount">{row.score.toLocaleString('ms-MY')}<small>{unit}</small></span>
			<span class="track"><span class="fill" style:height="{Math.max(1, Math.round(((row.score / top) * 88) / 4) * 4)}px"></span></span>
			<Avatar animal={person?.avatar} colour={person?.colour} skin={person?.skin} size={46} mood={row.rank === 1 ? 'cheer' : 'happy'} />
			<span class="name">{person?.name ?? ''}</span>
		</li>
	{/each}
</ol>

<style>
	.towers {
		display: flex;
		align-items: flex-end;
		justify-content: center;
		gap: clamp(0.4rem, 1.5vw, 1.2rem);
		min-height: 18rem;
		margin: 0;
		padding: 1rem;
		border: 2px solid var(--edge, transparent);
		border-radius: var(--r-lg);
		background: linear-gradient(#bfe6f6 0 70%, #e9c78d 70%);
		list-style: none;
		box-shadow: var(--card-shadow);
	}
	.harvest {
		background: linear-gradient(#bfe6f6 0 70%, #9b6a43 70%);
	}
	.tower {
		display: grid;
		justify-items: center;
		gap: 0.3rem;
		width: clamp(3.4rem, 9vw, 6rem);
	}
	.amount {
		display: grid;
		justify-items: center;
		font: 600 1.15rem/1 var(--font-display);
		font-variant-numeric: tabular-nums;
	}
	.amount small {
		font: 700 0.7rem var(--font-body);
		color: var(--ink-2);
	}
	.track {
		display: flex;
		align-items: flex-end;
		justify-content: center;
		width: 100%;
		height: 11rem;
	}
	/* A stack of coins: the picture of one repeats upwards, so the tower grows a coin at a time. */
	.fill {
		display: block;
		width: calc(var(--s) * 14);
		background-image: var(--tile);
		background-size: calc(var(--s) * 14) calc(var(--s) * 4);
		background-position: bottom;
		background-repeat: repeat-y;
		transition: height 900ms steps(12);
	}
	/* Every name keeps room for two lines, so a long name never lifts its tower above the rest. */
	.name {
		display: -webkit-box;
		max-width: 100%;
		min-height: 2.3em;
		overflow: hidden;
		-webkit-box-orient: vertical;
		-webkit-line-clamp: 2;
		line-clamp: 2;
		font-weight: 800;
		font-size: 0.8rem;
		text-align: center;
		line-height: 1.15;
		overflow-wrap: break-word;
	}
</style>
