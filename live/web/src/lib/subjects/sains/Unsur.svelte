<!--
	Jadual Berkala: the left-hand things as squares of a periodic table (a big symbol, a small number in
	the corner, coloured by family); drop the matching card into each square.
-->
<script lang="ts">
	import MatchCard from '../MatchCard.svelte';
	import MatchPlay, { type MatchView } from '../MatchPlay.svelte';
	import type { GameProps } from '../kit.svelte';

	let p: GameProps = $props();

	// atomic numbers for the symbols a child is likely to meet; others are numbered in turn
	const Z: Record<string, number> = { H: 1, He: 2, Li: 3, C: 6, N: 7, O: 8, F: 9, Ne: 10, Na: 11, Mg: 12, Al: 13, Si: 14, P: 15, S: 16, Cl: 17, Ar: 18, K: 19, Ca: 20, Fe: 26, Cu: 29, Zn: 30, Ag: 47, Sn: 50, I: 53, Au: 79, Hg: 80, Pb: 82 };
	const FAMILY = ['#ffd6a5', '#caffbf', '#9bf6ff', '#bdb2ff', '#ffc6ff', '#fdffb6'];
	const short = (t: string) => t.length <= 3;
</script>

<MatchPlay {p} pool="Kad">
	{#snippet board(v: MatchView)}
		<div class="table">
			{#each v.left as l, i (l.id)}
				<!-- svelte-ignore a11y_click_events_have_key_events, a11y_no_static_element_interactions -->
				<div class="cell" class:filled={!!v.placed(l.id)} style:--c={FAMILY[i % FAMILY.length]} data-zone={v.zone(l.id)} onclick={() => v.tapLeft(l.id)}>
					<span class="z">{Z[l.text] ?? i + 1}</span>
					<span class="sym" class:long={!short(l.text)}>{l.text}</span>
					<span class="slot"><MatchCard {v} left={l.id} empty="Nama?" /></span>
				</div>
			{/each}
		</div>
	{/snippet}
</MatchPlay>

<style>
	.table {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(7.5rem, 1fr));
		gap: 0.5rem;
		padding: 0.6rem;
		border-radius: var(--r-lg);
		background: linear-gradient(180deg, #23263a, #171926);
		box-shadow: inset 0 0 0 3px #0e1019;
	}
	.cell {
		position: relative;
		display: grid;
		justify-items: center;
		align-content: start;
		gap: 0.25rem;
		min-height: 8rem;
		padding: 0.55rem 0.35rem 0.45rem;
		border: 2px solid rgb(0 0 0 / 0.25);
		border-radius: 6px;
		background: var(--c);
		color: #1b1d2b;
		box-shadow: inset 0 -5px 0 rgb(0 0 0 / 0.12);
	}
	.cell:global(.zone-hover) {
		outline: 3px solid #fff;
		outline-offset: 2px;
	}
	.z {
		position: absolute;
		left: 0.4rem;
		top: 0.25rem;
		font: 700 0.75rem var(--font-display);
		opacity: 0.75;
	}
	.sym {
		margin-top: 0.4rem;
		font: 700 2.3rem/1 var(--font-display);
		letter-spacing: -0.02em;
	}
	.sym.long {
		font-size: 1.05rem;
		line-height: 1.15;
		text-align: center;
	}
	.slot {
		display: grid;
		place-items: center;
		min-height: 2.4rem;
	}
</style>
