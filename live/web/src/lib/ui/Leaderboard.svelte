<!--
	Ranked list that animates places changing (FLIP), so overtaking a friend is visible.
-->
<script lang="ts">
	import { flip } from 'svelte/animate';
	import Avatar from './Avatar.svelte';
	import type { Person } from '$lib/types';

	interface Row {
		id: string;
		score: number;
		rank: number;
		gained?: number;
	}

	let {
		rows,
		people,
		me = null,
		unit = 'mata',
		limit = 10,
		compact = false
	}: { rows: Row[]; people: Map<string, Person>; me?: string | null; unit?: string; limit?: number; compact?: boolean } = $props();

	const shown = $derived(rows.slice(0, limit));
</script>

<ol class="board" class:compact>
	{#each shown as row (row.id)}
		{@const person = people.get(row.id)}
		<li class:me={row.id === me} animate:flip={{ duration: 520 }}>
			<span class="rank" class:top={row.rank <= 3}>{row.rank}</span>
			<Avatar animal={person?.avatar} colour={person?.colour} size={compact ? 30 : 38} />
			<span class="name">{person?.name ?? 'Pemain'}{#if person?.bot}<span class="bot">bot</span>{/if}</span>
			{#if row.gained}<span class="gained">+{row.gained}</span>{/if}
			<span class="score">{row.score.toLocaleString('ms-MY')} <small>{unit}</small></span>
		</li>
	{/each}
</ol>

<style>
	.board {
		display: grid;
		gap: 0.45rem;
		margin: 0;
		padding: 0;
		list-style: none;
	}
	li {
		display: flex;
		align-items: center;
		gap: 0.6rem;
		padding: 0.45rem 0.8rem 0.45rem 0.5rem;
		border-radius: var(--r-md);
		background: var(--card);
		box-shadow: 0 3px 0 var(--line);
	}
	.compact li {
		padding: 0.3rem 0.6rem 0.3rem 0.4rem;
		gap: 0.45rem;
		font-size: 0.95rem;
	}
	li.me {
		background: #fff3cf;
		box-shadow: 0 3px 0 #f0d58a;
	}
	.rank {
		display: grid;
		place-items: center;
		width: 1.9rem;
		height: 1.9rem;
		border-radius: 50%;
		background: var(--paper-2);
		font: 600 1rem/1 var(--font-display);
		flex: none;
	}
	.rank.top {
		background: var(--sun);
	}
	.name {
		flex: 1;
		min-width: 0;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
		font-weight: 800;
	}
	.bot {
		margin-left: 0.4rem;
		padding: 0 0.4rem;
		border-radius: var(--r-pill);
		background: var(--paper-2);
		color: var(--ink-3);
		font-size: 0.72rem;
		vertical-align: middle;
	}
	.gained {
		color: var(--good);
		font: 600 0.95rem var(--font-display);
		animation: rise-in var(--t-enter) var(--spring);
	}
	.score {
		font: 600 1.05rem var(--font-display);
		font-variant-numeric: tabular-nums;
		white-space: nowrap;
	}
	small {
		color: var(--ink-3);
		font: 700 0.75rem var(--font-body);
	}
</style>
