<!--
	Garis Masa: a rope timeline down an old ledger page, "Awal" at the top and "Kemudian" at the foot.
	Peg each event to the rope with a clothes-peg card, earliest first.
-->
<script lang="ts">
	import Mark from '../Mark.svelte';
	import OrderPlay, { type OrderView } from '../OrderPlay.svelte';
	import type { GameProps } from '../kit.svelte';

	let p: GameProps = $props();
	import GameImage from '../GameImage.svelte';
	import { find } from '../assets';
</script>

<OrderPlay {p} pool="Peristiwa" tip="Yang paling awal di atas. Ketik atau seret ke tali.">
	{#snippet thing(item)}
		{#if find('history', item.text)}<span class="snap small"><GameImage name={find('history', item.text)?.key} fit="cover" /></span>{/if}
		<span>{item.text}</span>
	{/snippet}
	{#snippet board(v: OrderView)}
		<div class="page">
			<p class="end top">Awal</p>
			<ol class="rope">
				{#each v.slots as id, i (i)}
					{@const ok = v.ok(i)}
					<li class="peg" data-zone={v.zone(i)}>
						<span class="knot" aria-hidden="true">{i + 1}</span>
						{#if id}
							<button type="button" class="card" style:--tilt="{i % 2 ? 1.2 : -1.2}deg" disabled={v.locked} {@attach v.grab(i)} aria-label="{v.text(id)}, urutan {i + 1}">
								<span class="clip" aria-hidden="true"></span>
								{#if find('history', v.text(id))}
									<span class="snap"><GameImage name={find('history', v.text(id))?.key} eager fit="cover" /></span>
								{/if}
								<span class="words">{v.text(id)}</span>
								{#if ok !== null}<Mark {ok} />{/if}
							</button>
							{#if v.should(i)}<span class="should">→ {v.should(i)}</span>{/if}
						{:else}
							<span class="empty">Gantung peristiwa ke-{i + 1}</span>
						{/if}
					</li>
				{/each}
			</ol>
			<p class="end">Kemudian</p>
		</div>
	{/snippet}
</OrderPlay>

<style>
	/* a photograph pinned to the card: the place the event stands for */
	.snap {
		display: block;
		flex: none;
		width: 3.2rem;
		height: 2.4rem;
		overflow: hidden;
		border: 2px solid #fff;
		border-radius: 3px;
		box-shadow: 0 2px 4px rgb(60 40 10 / 0.35);
		rotate: -2deg;
	}
	.snap.small {
		width: 2.5rem;
		height: 1.9rem;
	}
	.snap :global(img.g-img) {
		width: 100%;
		height: 100%;
		filter: sepia(0.25);
	}
	.card {
		display: flex !important;
		align-items: center;
		gap: 0.5rem;
	}
	.words {
		flex: 1;
	}
	.page {
		position: relative;
		padding: 0.8rem 0.8rem 0.6rem 0.8rem;
		border-radius: var(--r-lg);
		background:
			repeating-linear-gradient(180deg, transparent 0 27px, rgb(120 90 50 / 0.12) 27px 28px),
			linear-gradient(90deg, #f5e6c4, #fbf1da 30%, #f3e1b9);
		box-shadow:
			inset 0 0 0 3px #c9a46a,
			inset 0 0 30px rgb(140 100 40 / 0.2);
	}
	.end {
		margin-left: 0.2rem;
		color: #7a5426;
		font: 700 0.85rem var(--font-display);
		letter-spacing: 0.08em;
		text-transform: uppercase;
	}
	.end.top::after {
		content: ' ↓';
	}
	.rope {
		position: relative;
		display: grid;
		gap: 0.55rem;
		margin: 0.4rem 0;
		padding: 0 0 0 2.4rem;
		list-style: none;
	}
	.rope::before {
		content: '';
		position: absolute;
		left: 0.95rem;
		top: -0.4rem;
		bottom: -0.4rem;
		width: 6px;
		border-radius: 3px;
		background: repeating-linear-gradient(160deg, #b0844a 0 5px, #8c6232 5px 10px);
		box-shadow: 1px 0 0 rgb(0 0 0 / 0.15);
	}
	.peg {
		position: relative;
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: 0.4rem;
		min-height: 3.1rem;
		padding: 0.25rem 0.4rem;
		border: 2px dashed rgb(160 120 60 / 0.5);
		border-radius: 10px;
	}
	.peg:global(.zone-hover) {
		border-color: #d1871e;
		background: rgb(255 220 150 / 0.35);
	}
	.knot {
		position: absolute;
		left: -2.1rem;
		top: 50%;
		translate: 0 -50%;
		display: grid;
		place-items: center;
		width: 1.6rem;
		height: 1.6rem;
		border: 3px solid #fbf1da;
		border-radius: 50%;
		background: #7a4f1f;
		color: #fff;
		font: 700 0.78rem var(--font-display);
	}
	.card {
		position: relative;
		max-width: 100%;
		padding: 0.5rem 0.8rem 0.45rem;
		border: 0;
		border-radius: 4px;
		background: #fffdf6;
		color: #3b2a14;
		font: 700 0.95rem/1.2 var(--font-body);
		text-align: left;
		rotate: var(--tilt);
		box-shadow: 0 4px 10px rgb(80 50 15 / 0.2);
		cursor: grab;
		touch-action: none;
		animation: hang 0.45s var(--spring, ease-out);
	}
	.card:disabled {
		cursor: default;
	}
	.clip {
		position: absolute;
		left: 50%;
		top: -0.55rem;
		width: 0.7rem;
		height: 1.2rem;
		translate: -50% 0;
		border-radius: 2px;
		background: linear-gradient(90deg, #c7a16a, #e9cf9f, #c7a16a);
		box-shadow: 0 1px 2px rgb(0 0 0 / 0.25);
	}
	.empty {
		color: #9b7a4b;
		font-weight: 700;
		font-size: 0.85rem;
	}
	.should {
		color: #8a2a00;
		font-weight: 800;
		font-size: 0.82rem;
	}
	@keyframes hang {
		from {
			transform: translateY(-10px) rotate(-6deg);
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.card {
			animation: none;
		}
	}
</style>
