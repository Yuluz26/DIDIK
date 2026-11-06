<!--
	Towers of coins (or harvest) for the leading children, growing as they earn. A big-screen picture
	of who is ahead that a child can read from across the room. Each child stands on the grass beside
	their own tower, feet and tower on the same ground, with their name on a little plaque below.
-->
<script lang="ts">
	import type { Person } from '$lib/types';
	import { prescale, urlOf } from '$lib/pixel/cache';
	import { daySky, towerGround } from '$lib/pixel/backdrop';
	import { stackTile } from '$lib/pixel/icons';
	import Chibi from './Chibi.svelte';

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
	const sky = urlOf(daySky(), prescale(S));
	const ground = $derived(urlOf(towerGround(kind), prescale(S)));
	const shown = $derived(rows.slice(0, limit));
	const top = $derived(Math.max(1, ...shown.map((r) => r.score)));
</script>

<ol class="towers {kind}" aria-label="Kedudukan" style:--tile="url({tile})" style:--sky="url({sky})" style:--ground="url({ground})" style:--s="{S}px">
	{#each shown as row (row.id)}
		{@const person = people.get(row.id)}
		<li class="tower">
			<span class="stand">
				<span class="track"><span class="amount">{row.score.toLocaleString('ms-MY')}<small>{unit}</small></span><span class="fill" style:height="{Math.max(1, Math.round(((row.score / top) * 88) / 4) * 4)}px"></span></span>
				<Chibi animal={person?.avatar} colour={person?.colour} skin={person?.skin} s={2} mood={row.rank === 1 ? 'cheer' : 'happy'} />
			</span>
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
		padding: 1rem 1rem 0.7rem;
		/* the grass line: where the children's feet and the towers stand, above the name plaques */
		--foot: 3.3rem;
		border: 2px solid var(--edge, transparent);
		border-radius: var(--r-lg);
		/* the ground along the foot, the sky above it, both repeating sideways */
		background:
			var(--ground) left 0 bottom calc(var(--foot) - var(--s) * 48) / calc(var(--s) * 64) calc(var(--s) * 48) repeat-x,
			var(--sky) left top / calc(var(--s) * 96) calc(var(--s) * 96) repeat-x,
			#e0f3fb;
		image-rendering: pixelated;
		list-style: none;
		box-shadow: var(--card-shadow);
	}
	.towers > * {
		image-rendering: auto;
	}
	.tower {
		display: grid;
		justify-items: center;
		gap: 0.3rem;
		width: clamp(4.6rem, 10vw, 6.4rem);
	}
	.stand {
		display: flex;
		align-items: flex-end;
		justify-content: center;
		gap: 2px;
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
	/* the amount rides on top of its tower */
	.track {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: flex-end;
		gap: 0.25rem;
		height: 13rem;
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
		padding: 0 0.3rem;
		border: 2px solid #2a1f2d;
		border-radius: 4px;
		background: #fff6e6;
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
