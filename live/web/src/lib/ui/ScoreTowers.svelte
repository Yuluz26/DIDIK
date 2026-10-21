<!--
	Towers of coins (or harvest) for the leading children, growing as they earn. A big-screen picture
	of who is ahead that a child can read from across the room.
-->
<script lang="ts">
	import type { Person } from '$lib/types';
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

	const shown = $derived(rows.slice(0, limit));
	const top = $derived(Math.max(1, ...shown.map((r) => r.score)));
</script>

<ol class="towers {kind}" aria-label="Kedudukan">
	{#each shown as row (row.id)}
		{@const person = people.get(row.id)}
		<li class="tower">
			<span class="amount">{row.score.toLocaleString('ms-MY')}<small>{unit}</small></span>
			<span class="track"><span class="fill" style:transform="scaleY({Math.max(0.04, row.score / top)})"></span></span>
			<Avatar animal={person?.avatar} colour={person?.colour} size={46} mood={row.rank === 1 ? 'cheer' : 'happy'} />
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
		border-radius: var(--r-lg);
		background: linear-gradient(#cdebff 0 70%, #f6d58e 70%);
		list-style: none;
		box-shadow: var(--card-shadow);
	}
	.harvest {
		background: linear-gradient(#cdebff 0 70%, #9b6a43 70%);
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
		width: 70%;
		height: 11rem;
	}
	.fill {
		width: 100%;
		height: 100%;
		border-radius: 0.6rem 0.6rem 0.2rem 0.2rem;
		transform-origin: bottom;
		transition: transform 900ms var(--spring);
		background: repeating-linear-gradient(#ffd34d 0 8px, #e9a800 8px 11px);
		box-shadow: inset -6px 0 0 rgb(0 0 0 / 0.08);
	}
	.harvest .fill {
		background: repeating-linear-gradient(#8fd05e 0 10px, #6cb33f 10px 14px);
	}
	.name {
		max-width: 100%;
		font-weight: 800;
		font-size: 0.8rem;
		text-align: center;
		line-height: 1.15;
		overflow-wrap: break-word;
	}
</style>
