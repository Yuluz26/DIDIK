<!--
	Bayar dengan wang: something with a price tag, a purse of Malaysian coins and notes, and a counter to
	pay on. Tap a coin or note in the purse to put it on the counter (or drag it there); tap one on the
	counter to take it back. There is no running total: adding up the money is the point. Semak sends how
	many of each coin and note are on the counter.
-->
<script lang="ts">
	import { crossfade } from 'svelte/transition';
	import { backOut } from 'svelte/easing';
	import type { Reveal } from '$lib/types';
	import { play } from '$lib/sound';
	import { moneyLook, ringgit } from '$lib/money';
	import Icon from '$ui/Icon.svelte';
	import Sticker from '$ui/Sticker.svelte';
	import { dragTap, still } from './drag';

	let {
		amount,
		money,
		sticker = null,
		disabled = false,
		mine = undefined,
		reveal = null,
		onanswer
	}: {
		amount: number;
		money: number[];
		sticker?: string | null;
		disabled?: boolean;
		mine?: Record<string, number>;
		reveal?: Reveal | null;
		onanswer?: (answer: Record<string, number>) => void;
	} = $props();

	let paid = $state<{ id: number; value: number }[]>([]);
	let next = 0;
	const asList = (counts: Record<string, number>) =>
		Object.entries(counts).flatMap(([value, count], k) => Array.from({ length: count }, (_, i) => ({ id: k * 100 + i, value: Number(value) })));
	const shown = $derived(mine ? asList(mine) : reveal?.pay ? asList(reveal.pay) : paid);
	const locked = $derived(disabled || !!reveal || mine !== undefined);
	const given = $derived(shown.reduce((sum, p) => sum + p.value, 0));
	const ok = $derived(!!reveal && (mine === undefined || given === amount));

	const [send, receive] = crossfade({
		duration: () => (still() ? 0 : 340),
		easing: backOut,
		fallback: (node) => ({ duration: still() ? 0 : 220, css: (t) => `opacity: ${t}; transform: scale(${0.5 + 0.5 * t}) rotate(${(1 - t) * -20}deg)` })
	});

	function pay(value: number) {
		if (locked) return;
		play('coin');
		paid = [...paid, { id: next++, value }];
	}

	function back(id: number) {
		if (locked) return;
		play('tap');
		paid = paid.filter((p) => p.id !== id);
	}

	function counts(): Record<string, number> {
		const out: Record<string, number> = {};
		for (const p of paid) out[p.value] = (out[p.value] ?? 0) + 1;
		return out;
	}
</script>

{#snippet cash(value: number)}
	{@const look = moneyLook(value)}
	{#if look.kind === 'coin'}
		<span class="coin" style:--fill={look.fill} style:--edge={look.edge} style:--ink={look.ink} style:--size="{look.size}rem">
			<b>{value}</b><small>sen</small>
		</span>
	{:else}
		<span class="note" style:--fill={look.fill} style:--edge={look.edge} style:--ink={look.ink}>
			<b>RM{value / 100}</b>
		</span>
	{/if}
{/snippet}

<div class="money-q">
	<div class="shop">
		{#if sticker}<span class="item" aria-hidden="true"><Sticker key={sticker} size={86} alt="" eager /></span>{/if}
		<span class="tag" aria-label="Harga {ringgit(amount)}">{ringgit(amount)}</span>
	</div>

	<div class="counter" data-zone="counter" class:ok={reveal && ok} class:off={reveal && mine !== undefined && !ok}>
		<p class="counter-name">Kaunter bayaran</p>
		<ul class="paid" aria-label="Wang di kaunter">
			{#each shown as p (p.id)}
				<li in:receive={{ key: `c${p.id}` }} out:send={{ key: `c${p.id}` }}>
					<button
						type="button"
						class="cash-btn"
						disabled={locked}
						aria-label="{ringgit(p.value)} di kaunter. Ketik untuk ambil semula"
						{@attach dragTap({ enabled: () => !locked, home: () => 'counter', tap: () => back(p.id), drop: (zone) => zone === 'purse' && back(p.id) })}
					>
						{@render cash(p.value)}
					</button>
				</li>
			{:else}
				<li class="empty">Letak wang di sini</li>
			{/each}
		</ul>
	</div>

	{#if !reveal && mine === undefined}
		<div class="purse" data-zone="purse" aria-label="Dompet">
			{#each money as value (value)}
				<button
					type="button"
					class="cash-btn"
					disabled={locked}
					aria-label="Bayar {ringgit(value)}"
					{@attach dragTap({ enabled: () => !locked, home: () => 'purse', tap: () => pay(value), drop: (zone) => zone === 'counter' && pay(value) })}
				>
					{@render cash(value)}
				</button>
			{/each}
		</div>
		{#if !locked}
			<div class="row">
				<button type="button" class="btn btn--plain" disabled={!paid.length} onclick={() => ((paid = []), play('tap'))}>
					<Icon name="shuffle" /> Ambil semula
				</button>
				<button type="button" class="btn btn--big check" disabled={!paid.length} onclick={() => onanswer?.(counts())}>
					Bayar <Icon name="check" />
				</button>
			</div>
		{/if}
	{/if}

	{#if reveal}
		<p class="answer" class:ok>
			Harga: <strong>{ringgit(amount)}</strong>
			{#if mine !== undefined}<span class="mine">Kamu bayar {ringgit(given)}{given === amount ? '. Tepat!' : given > amount ? ', terlebih.' : ', tidak cukup.'}</span>{/if}
			{#if mine !== undefined && !ok && reveal.pay}
				<span class="mine">Satu cara: {Object.entries(reveal.pay).sort((a, b) => Number(b[0]) - Number(a[0])).map(([v, c]) => `${c} × ${ringgit(Number(v))}`).join(' + ')}</span>
			{/if}
		</p>
	{/if}
</div>

<style>
	.money-q {
		display: grid;
		gap: 0.8rem;
	}
	.shop {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 0.6rem;
	}
	.item {
		filter: drop-shadow(0 6px 8px rgb(31 45 39 / 0.18));
	}
	.tag {
		position: relative;
		padding: 0.45rem 1rem 0.45rem 1.3rem;
		border-radius: 10px 999px 999px 10px;
		background: #fff1a8;
		color: #5e4a10;
		font: 600 1.5rem var(--font-display);
		box-shadow: 0 4px 0 #e0c55a;
		transform: rotate(-4deg);
	}
	.tag::before {
		content: '';
		position: absolute;
		left: 0.45rem;
		top: 50%;
		width: 0.45rem;
		height: 0.45rem;
		border-radius: 50%;
		background: #fff;
		transform: translateY(-50%);
	}
	.counter {
		display: grid;
		gap: 0.4rem;
		min-height: 7rem;
		padding: 0.6rem;
		border: 3px dashed #c9b28a;
		border-radius: var(--r-lg);
		background: repeating-linear-gradient(90deg, #f6e7cf 0 18px, #f1dfc2 18px 36px);
		transition: transform var(--t-state) var(--spring);
	}
	.counter:global(.zone-hover) {
		border-style: solid;
		transform: scale(1.02);
	}
	.counter.ok {
		border-style: solid;
		border-color: var(--good);
	}
	.counter.off {
		border-style: solid;
		border-color: var(--almost);
	}
	.counter-name {
		font: 600 0.95rem var(--font-display);
		color: #7a5a2a;
	}
	.paid {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: 0.35rem;
		margin: 0;
		padding: 0;
		list-style: none;
	}
	.empty {
		color: #9a7f55;
		font-weight: 800;
	}
	.purse {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		justify-content: center;
		gap: 0.55rem;
		padding: 0.7rem;
		border-radius: var(--r-lg);
		background: #f3eefc;
	}
	.cash-btn {
		display: grid;
		place-items: center;
		min-width: 2.75rem;
		min-height: 2.75rem;
		padding: 0;
		border: 0;
		background: none;
		cursor: grab;
		touch-action: none;
		transition: transform var(--t-state) var(--spring);
	}
	.cash-btn:not(:disabled):hover {
		transform: translateY(-3px) rotate(-3deg);
	}
	.cash-btn:disabled {
		cursor: default;
	}
	.cash-btn:global(.dragging) {
		z-index: 50;
	}
	.cash-btn:focus-visible {
		outline: 3px solid var(--sky);
		outline-offset: 2px;
		border-radius: 8px;
	}
	.coin {
		display: grid;
		place-items: center;
		align-content: center;
		width: var(--size);
		height: var(--size);
		border: 3px solid var(--edge);
		border-radius: 50%;
		background: radial-gradient(circle at 35% 30%, #fff 0 12%, var(--fill) 45%);
		color: var(--ink);
		line-height: 1;
		box-shadow:
			inset 0 0 0 3px rgb(255 255 255 / 0.5),
			0 3px 0 var(--edge);
	}
	.coin b {
		font: 700 0.95rem var(--font-display);
	}
	.coin small {
		font-size: 0.55rem;
		font-weight: 800;
	}
	.note {
		display: grid;
		place-items: center;
		width: 5rem;
		height: 2.6rem;
		border: 3px solid var(--edge);
		border-radius: 6px;
		background:
			radial-gradient(circle at 78% 50%, rgb(255 255 255 / 0.55) 0 22%, transparent 23%),
			var(--fill);
		color: var(--ink);
		box-shadow: 0 3px 0 var(--edge);
	}
	.note b {
		font: 700 1.05rem var(--font-display);
	}
	.row {
		display: flex;
		flex-wrap: wrap;
		justify-content: space-between;
		gap: 0.6rem;
	}
	.check {
		flex: 1;
		max-width: 16rem;
		margin-left: auto;
	}
	.answer {
		padding: 0.6rem 0.9rem;
		border-radius: var(--r-md);
		background: var(--almost-soft);
		color: var(--on-almost-soft);
		font-weight: 800;
		text-align: center;
	}
	.answer.ok {
		background: var(--good-soft);
		color: var(--on-good-soft);
	}
	.mine {
		display: block;
		font-weight: 700;
	}
</style>
