<!--
	Jadual Berkala: each left-hand thing is an element, shown as its square of the periodic table: its real
	atomic number, its symbol, its name's family colour, and a small map of the table with its own square
	lit, so a child sees where it lives. Drop the matching card into each square.

	The server gives this game only to pairs whose left-hand things are all elements (lexicon "elements"),
	so the numbers and places are always the real ones.
-->
<script lang="ts">
	import MatchCard from '../MatchCard.svelte';
	import MatchPlay, { type MatchView } from '../MatchPlay.svelte';
	import { element } from '../assets';
	import type { GameProps } from '../kit.svelte';

	let p: GameProps = $props();

	// one colour for each family, as on a classroom wall chart
	const FAMILY: Record<string, [string, string]> = {
		'logam alkali': ['#ffd9d2', '#c9412b'],
		'logam alkali bumi': ['#ffe8c2', '#b9770e'],
		'logam peralihan': ['#ffe3ef', '#b03a6f'],
		'logam lain': ['#dfe7f2', '#48608a'],
		'separa logam': ['#dff3e3', '#2f7d4a'],
		'bukan logam': ['#dff1ff', '#1f6fa8'],
		halogen: ['#e9e2ff', '#5b3fb0'],
		'gas adi': ['#d9f6f4', '#12786f']
	};
	/** Whether the table has a square at this group and period (the main table, periods 1 to 6). */
	const real = (group: number, period: number) => (period === 1 ? group === 1 || group === 18 : period <= 3 ? group <= 2 || group >= 13 : true);
</script>

<MatchPlay {p} pool="Kad">
	{#snippet board(v: MatchView)}
		<div class="table">
			{#each v.left as l (l.id)}
				{@const e = element(l.text)}
				{@const tint = FAMILY[e?.family ?? ''] ?? ['#f1efe9', '#5c5a52']}
				<!-- svelte-ignore a11y_click_events_have_key_events, a11y_no_static_element_interactions -->
				<div class="cell" class:filled={!!v.placed(l.id)} style:--c={tint[0]} style:--k={tint[1]} data-zone={v.zone(l.id)} onclick={() => v.tapLeft(l.id)}>
					<span class="z">{e?.z ?? ''}</span>
					<span class="sym">{e?.sym ?? l.text}</span>
					<span class="called">{e && l.text.trim() !== e.sym ? l.text : (e?.family ?? '')}</span>
					{#if e}
						<span class="map" aria-hidden="true">
							{#each [1, 2, 3, 4, 5, 6] as period (period)}
								{#each Array.from({ length: 18 }, (_, g) => g + 1) as group (group)}
									<i class:real={real(group, period)} class:here={e.group === group && e.period === period}></i>
								{/each}
							{/each}
						</span>
					{/if}
					<span class="slot"><MatchCard {v} left={l.id} empty="Kad?" /></span>
				</div>
			{/each}
		</div>
	{/snippet}
</MatchPlay>

<style>
	.table {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(8.4rem, 1fr));
		gap: 0.6rem;
		padding: 0.7rem;
		border-radius: var(--r-lg);
		background: linear-gradient(180deg, #2b3340, #1c222c);
		box-shadow: inset 0 0 0 3px #11151c;
	}
	.cell {
		position: relative;
		display: grid;
		grid-template-columns: 1fr auto;
		align-items: start;
		gap: 0 0.3rem;
		min-height: 8.4rem;
		padding: 0.4rem 0.5rem 0.5rem;
		border-radius: 0.6rem;
		background: linear-gradient(160deg, #fff, var(--c) 45%);
		box-shadow:
			inset 0 0 0 2px var(--k),
			0 4px 0 rgb(0 0 0 / 0.35);
		cursor: pointer;
	}
	.cell:global(.zone-hover) {
		outline: 3px solid #ffd23f;
		outline-offset: 2px;
	}
	.z {
		color: var(--k);
		font: 700 0.95rem var(--font-display);
	}
	.sym {
		grid-column: 1;
		color: #1c222c;
		font: 700 2.2rem/1 var(--font-display);
	}
	.called {
		grid-column: 1 / -1;
		color: var(--k);
		font: 700 0.68rem/1.2 var(--font-body);
		text-transform: capitalize;
	}
	/* where the element sits in the table */
	.map {
		grid-column: 2;
		grid-row: 1 / span 2;
		display: grid;
		grid-template-columns: repeat(18, 3px);
		gap: 1px;
		align-self: start;
		padding: 2px;
		border-radius: 3px;
		background: rgb(255 255 255 / 0.6);
	}
	.map i {
		width: 3px;
		height: 3px;
	}
	.map i.real {
		background: rgb(40 50 70 / 0.22);
	}
	.map i.here {
		background: var(--k);
		box-shadow: 0 0 0 1.5px var(--k);
	}
	.slot {
		grid-column: 1 / -1;
		display: grid;
		margin-top: 0.3rem;
	}
</style>
