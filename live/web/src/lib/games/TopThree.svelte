<script lang="ts">
	import type { Me, Person } from '$lib/types';
	import Avatar from '$ui/Avatar.svelte';

	type Row = { id: string; rank: number; score: number };
	let { rows = [], people, me, rank = null, unit = 'mata', inline = false }: {
		rows?: Row[];
		people: Map<string, Person>;
		me: Me;
		rank?: number | null;
		unit?: string;
		inline?: boolean;
	} = $props();

	const rivals = $derived(rows.filter((row) => row.id !== me.id).slice(0, 3));
</script>

{#if rivals.length}
	<aside class="top-three" class:inline aria-label="Tiga rakan teratas semasa permainan">
		<div class="label"><strong>Top 3 rakan</strong><span>Kamu {rank ? `#${rank}` : 'sedang bermain'}</span></div>
		<ol>
			{#each rivals as row (row.id)}
				{@const person = people.get(row.id)}
				<li title="Tempat {row.rank}: {person?.name ?? 'Pemain'}, {row.score} {unit}">
					<span class="place" class:first={row.rank === 1}>{row.rank}</span>
					<Avatar animal={person?.avatar} colour={person?.colour} skin={person?.skin} size={24} />
					<span class="name">{person?.name ?? 'Pemain'}</span>
					<span class="score">{row.score.toLocaleString('ms-MY')} <small>{unit}</small></span>
				</li>
			{/each}
		</ol>
	</aside>
{/if}

<style>
	.top-three {
		position: fixed;
		z-index: 11;
		top: calc(env(safe-area-inset-top, 0px) + var(--hud-h, 4.1rem) + 0.35rem);
		left: 50%;
		translate: -50% 0;
		width: min(42rem, calc(100% - 1rem));
		padding: 0.32rem 0.55rem 0.4rem;
		border: 2px solid #7f6855;
		border-radius: 0.8rem;
		background: #fff8e9;
		box-shadow: 0 0.3rem 0.9rem rgb(52 41 31 / 0.17);
		color: #302e29;
		pointer-events: none;
	}
	.top-three.inline {
		position: sticky;
		top: calc(env(safe-area-inset-top, 0px) + 3.7rem);
		left: auto;
		translate: none;
		margin: 0.2rem auto 0;
		background: #fffafc;
		border-color: #dbc6e8;
	}
	.label { display: flex; justify-content: space-between; gap: 0.5rem; margin-bottom: 0.15rem; font-size: 0.7rem; line-height: 1.1; }
	.label strong { color: #5e4d3c; text-transform: uppercase; letter-spacing: 0.04em; }
	.label span { font-weight: 800; color: #276c52; }
	ol { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 0.3rem; margin: 0; padding: 0; list-style: none; }
	li { display: grid; grid-template-columns: auto auto minmax(0, 1fr); grid-template-rows: auto auto; column-gap: 0.25rem; align-items: center; min-width: 0; padding: 0.18rem 0.28rem; border-radius: 0.45rem; background: #f1e6d2; }
	.place { display: grid; place-items: center; grid-row: 1 / 3; width: 1.15rem; height: 1.15rem; border-radius: 0.3rem; background: #d5d9dc; font: 800 0.72rem var(--font-display); }
	.place.first { background: #f5c451; }
	li :global(.avatar) { grid-row: 1 / 3; }
	.name { min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font: 800 0.78rem/1.1 var(--font-display); }
	.score { grid-column: 3; font-size: 0.68rem; font-weight: 800; line-height: 1.1; font-variant-numeric: tabular-nums; white-space: nowrap; }
	.score small { font-size: 0.6rem; color: #5c5143; }
	@media (max-width: 420px) {
		.top-three { padding-inline: 0.35rem; }
		li { grid-template-columns: auto minmax(0, 1fr); column-gap: 0.2rem; padding-inline: 0.2rem; }
		li :global(.avatar) { display: none; }
		.name, .score { grid-column: 2; }
	}
</style>
