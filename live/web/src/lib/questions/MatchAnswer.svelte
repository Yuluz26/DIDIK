<!--
	Padankan: tap something on the left, then its partner on the right. Matched pairs share a colour
	and a number. Tap either half of a pair to undo it.
-->
<script lang="ts">
	import type { Choice, Reveal } from '$lib/types';
	import { play } from '$lib/sound';
	import Icon from '$ui/Icon.svelte';

	let {
		left,
		right,
		disabled = false,
		mine = undefined,
		reveal = null,
		onanswer
	}: {
		left: Choice[];
		right: Choice[];
		disabled?: boolean;
		mine?: Record<string, string>;
		reveal?: Reveal | null;
		onanswer?: (answer: Record<string, string>) => void;
	} = $props();

	const PAIR_COLOURS = ['#e8553f', '#14958a', '#ffb627', '#2f7fcf', '#d63e94'];

	let pairs = $state<Record<string, string>>({});
	let active = $state<string | null>(null);
	const current = $derived(mine ?? pairs);
	const locked = $derived(disabled || !!reveal || mine !== undefined);
	const correct = $derived<Record<string, string>>(reveal ? reveal.correct : {});
	const leftOf = $derived(Object.fromEntries(Object.entries(current).map(([l, r]) => [r, l])));
	const colourOf = (leftId: string) => PAIR_COLOURS[left.findIndex((l) => l.id === leftId) % PAIR_COLOURS.length];
	const rightText = $derived(new Map(right.map((r) => [r.id, r.text])));

	function tapLeft(id: string) {
		if (locked) return;
		play('tap');
		if (current[id]) {
			const { [id]: _removed, ...rest } = pairs;
			pairs = rest;
			return;
		}
		active = active === id ? null : id;
	}

	function tapRight(id: string) {
		if (locked) return;
		if (leftOf[id]) {
			play('tap');
			const { [leftOf[id]]: _removed, ...rest } = pairs;
			pairs = rest;
			return;
		}
		if (!active) return;
		play('pop');
		pairs = { ...pairs, [active]: id };
		active = null;
	}
</script>

<div class="match">
	<div class="column" role="group" aria-label="Kiri">
		{#each left as item, i (item.id)}
			{@const partner = current[item.id]}
			{@const ok = reveal ? correct[item.id] === partner : null}
			<button
				type="button"
				class="item"
				class:active={active === item.id}
				class:paired={!!partner}
				style:--pair={partner ? colourOf(item.id) : 'transparent'}
				style:--i={i}
				disabled={locked}
				aria-pressed={active === item.id}
				onclick={() => tapLeft(item.id)}
			>
				{#if partner}<span class="badge">{i + 1}</span>{/if}
				<span>{item.text}</span>
				{#if reveal}<span class="result" class:ok><Icon name={ok ? 'check' : 'close'} size={18} /></span>{/if}
			</button>
		{/each}
	</div>
	<div class="column" role="group" aria-label="Kanan">
		{#each right as item, i (item.id)}
			{@const owner = leftOf[item.id]}
			<button
				type="button"
				class="item right"
				class:paired={!!owner}
				class:waiting={!!active && !owner}
				style:--pair={owner ? colourOf(owner) : 'transparent'}
				style:--i={i}
				disabled={locked}
				onclick={() => tapRight(item.id)}
			>
				{#if owner}<span class="badge">{left.findIndex((l) => l.id === owner) + 1}</span>{/if}
				<span>{item.text}</span>
			</button>
		{/each}
	</div>
</div>

{#if !locked}
	<div class="row">
		<span class="hint">{active ? 'Sekarang ketik pasangannya di kanan.' : 'Ketik satu di kiri dahulu.'}</span>
		<button type="button" class="btn btn--big" disabled={Object.keys(pairs).length !== left.length} onclick={() => onanswer?.(pairs)}>Hantar <Icon name="next" /></button>
	</div>
{/if}

{#if reveal}
	<ul class="answers">
		{#each left as item (item.id)}
			<li><strong>{item.text}</strong> → {rightText.get(correct[item.id])}</li>
		{/each}
	</ul>
{/if}

<style>
	.match {
		display: grid;
		grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
		gap: 0.8rem;
	}
	.column {
		display: grid;
		gap: 0.55rem;
		align-content: start;
	}
	.item {
		position: relative;
		display: flex;
		align-items: center;
		gap: 0.55rem;
		min-height: 3.6rem;
		padding: 0.5rem 0.8rem;
		border: 3px solid var(--pair);
		border-radius: var(--r-md);
		background: var(--card);
		box-shadow: 0 4px 0 var(--line);
		font: 600 1.12rem/1.2 var(--font-display);
		text-align: left;
		cursor: pointer;
		transition: transform var(--t-state) var(--spring), border-color var(--t-state), background-color var(--t-state);
		animation: rise-in var(--t-enter) var(--ease-out) both;
		animation-delay: calc(var(--i) * 50ms);
	}
	.item:not(:disabled):hover {
		transform: translateY(-2px);
	}
	.item.active {
		background: #fff3cf;
		border-color: var(--sun);
		transform: scale(1.04);
	}
	.item.waiting {
		border-color: #f0d58a;
		border-style: dashed;
	}
	.item:disabled {
		cursor: default;
	}
	.badge {
		display: grid;
		place-items: center;
		flex: none;
		width: 1.7rem;
		height: 1.7rem;
		border-radius: var(--r-sm);
		background: var(--pair);
		color: #fff;
		font-size: 0.95rem;
	}
	.result {
		margin-left: auto;
		color: var(--almost);
	}
	.result.ok {
		color: var(--good);
	}
	.row {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 0.75rem;
		margin-top: 1rem;
		flex-wrap: wrap;
	}
	.hint {
		color: var(--ink-2);
		font-weight: 800;
	}
	.answers {
		margin: 0.9rem 0 0;
		padding-left: 1.2rem;
		display: grid;
		gap: 0.2rem;
	}
</style>
