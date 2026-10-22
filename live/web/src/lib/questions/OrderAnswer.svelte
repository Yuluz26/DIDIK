<!--
	Susun turutan by tapping: tap items in order to drop them into the numbered slots; tap a slot to
	take its item back. Easier than dragging for small hands, and it works with a keyboard.
-->
<script lang="ts">
	import type { Choice, Reveal } from '$lib/types';
	import { play } from '$lib/sound';
	import Icon from '$ui/Icon.svelte';

	let {
		items,
		disabled = false,
		mine = undefined,
		reveal = null,
		onanswer
	}: { items: Choice[]; disabled?: boolean; mine?: string[]; reveal?: Reveal | null; onanswer?: (answer: string[]) => void } = $props();

	let placed = $state<string[]>([]);
	const order = $derived(mine ?? placed);
	const byId = $derived(new Map(items.map((i) => [i.id, i])));
	const pool = $derived(items.filter((i) => !order.includes(i.id)));
	const correct = $derived<string[]>(reveal ? reveal.correct : []);
	const locked = $derived(disabled || !!reveal || mine !== undefined);

	function place(id: string) {
		if (locked) return;
		play('pop');
		placed = [...placed, id];
	}

	function unplace(id: string) {
		if (locked) return;
		play('tap');
		placed = placed.filter((p) => p !== id);
	}
</script>

<div class="order">
	<ol class="slots">
		{#each items as _, i (i)}
			{@const id = order[i]}
			{@const ok = reveal && id === correct[i]}
			<li class="slot" class:filled={!!id} class:ok class:off={reveal && id && !ok}>
				<span class="num">{i + 1}</span>
				{#if id}
					<button type="button" class="piece" disabled={locked} onclick={() => unplace(id)} aria-label="Keluarkan {byId.get(id)?.text}">
						{byId.get(id)?.text}
					</button>
					{#if reveal}<Icon name={ok ? 'check' : 'close'} size={20} />{/if}
				{:else}
					<span class="empty">Ketik item di bawah</span>
				{/if}
			</li>
		{/each}
	</ol>

	{#if !locked}
		<div class="pool" aria-label="Item untuk disusun">
			{#each pool as item, i (item.id)}
				<button type="button" class="tile t{(i + 1) % 6}" style:--i={i} onclick={() => place(item.id)}>
					<span class="text">{item.text}</span>
				</button>
			{/each}
		</div>
		<div class="row">
			<button type="button" class="btn btn--plain" disabled={!placed.length} onclick={() => (placed = [])}><Icon name="shuffle" /> Susun semula</button>
			<button type="button" class="btn btn--big" disabled={placed.length !== items.length} onclick={() => onanswer?.(placed)}>Hantar <Icon name="next" /></button>
		</div>
	{/if}

	{#if reveal}
		<p class="answer">Susunan betul: <strong>{correct.map((id) => byId.get(id)?.text).join(' → ')}</strong></p>
	{/if}
</div>

<style>
	.order {
		display: grid;
		gap: 0.9rem;
	}
	.slots {
		display: grid;
		gap: 0.5rem;
		margin: 0;
		padding: 0;
		list-style: none;
	}
	.slot {
		display: flex;
		align-items: center;
		gap: 0.6rem;
		min-height: 3.6rem;
		padding: 0.35rem 0.8rem 0.35rem 0.45rem;
		border: 2px dashed color-mix(in srgb, var(--line) 70%, var(--ink-3));
		border-radius: var(--r-md);
		background: color-mix(in srgb, var(--card) 55%, transparent);
	}
	.slot.filled {
		border-style: solid;
		border-color: transparent;
		background: var(--card);
		box-shadow: 0 3px 0 var(--line);
	}
	.slot.ok {
		color: var(--good);
	}
	.slot.off {
		color: var(--almost);
	}
	.num {
		display: grid;
		place-items: center;
		flex: none;
		width: 2.3rem;
		height: 2.3rem;
		border-radius: 50%;
		background: var(--sun);
		color: var(--on-bright);
		font: 600 1.15rem var(--font-display);
	}
	.piece {
		flex: 1;
		min-height: 2.6rem;
		border: 0;
		background: none;
		color: var(--ink);
		font: 600 1.2rem var(--font-display);
		text-align: left;
		cursor: pointer;
		animation: pop-in 360ms var(--spring);
	}
	.piece:disabled {
		cursor: default;
	}
	.empty {
		color: var(--ink-3);
		font-weight: 700;
	}
	.pool {
		display: flex;
		flex-wrap: wrap;
		gap: 0.6rem;
	}
	.pool .tile {
		min-height: 3.4rem;
		flex: 1 1 auto;
		justify-content: center;
	}
	.row {
		display: flex;
		justify-content: space-between;
		gap: 0.75rem;
		flex-wrap: wrap;
	}
	.answer {
		font-size: 1.1rem;
	}
</style>
