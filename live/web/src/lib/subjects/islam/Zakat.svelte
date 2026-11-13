<!--
	Tabung Zakat: a wooden zakat box with a slot, and Malaysian coins and notes to pay with. Tap a coin or
	note to drop it in (it falls through the slot); "Keluarkan" takes the last one back. The total shows on
	the box's brass plate. Semak pays it.
-->
<script lang="ts">
	import { moneyLook, ringgit } from '$lib/money';
	import { play } from '$lib/sound';
	import Icon from '$ui/Icon.svelte';
	import Checks from '../Checks.svelte';
	import Mark from '../Mark.svelte';
	import { type GameProps, isLocked } from '../kit.svelte';

	let p: GameProps = $props();

	const money = $derived(p.question.money ?? [5, 10, 20, 50, 100]);
	const amount = $derived(p.question.amount ?? 0);
	const locked = $derived(isLocked(p));
	let paid = $state<number[]>([]);
	let drop = $state(0);
	const counts = (list: number[]) => list.reduce<Record<string, number>>((acc, v) => ((acc[v] = (acc[v] ?? 0) + 1), acc), {});
	const given = $derived<Record<string, number>>(p.mine !== undefined ? p.mine : p.reveal ? (p.reveal.pay ?? {}) : counts(paid));
	const total = $derived(Object.entries(given).reduce((sum, [v, n]) => sum + Number(v) * n, 0));
	const ok = $derived(p.reveal ? total === amount : null);

	function give(v: number) {
		if (locked || paid.length >= 40) return;
		paid = [...paid, v];
		drop++;
		play('coin');
	}
	function takeBack() {
		if (locked || !paid.length) return;
		paid = paid.slice(0, -1);
		play('tap');
	}
	import GameImage from '../GameImage.svelte';
</script>

<div class="counter">
	<span class="real-box" aria-hidden="true"><GameImage name="isl/donation" eager fit="cover" /></span>
	<div class="box">
		<span class="slot" aria-hidden="true"></span>
		{#key drop}{#if drop && !locked}<span class="falling" aria-hidden="true"></span>{/if}{/key}
		<p class="title">TABUNG ZAKAT</p>
		<p class="plate">
			<span>Dibayar</span>
			<strong class:ok={ok === true} class:off={ok === false}>{ringgit(total)}</strong>
		</p>
		<p class="due">Perlu dibayar: <b>{ringgit(amount)}</b></p>
		{#if ok !== null}<span class="mark"><Mark {ok} size={16} /></span>{/if}
	</div>
	{#if !locked}
		<ul class="purse" aria-label="Wang untuk membayar">
			{#each money as v (v)}
				{@const look = moneyLook(v)}
				<li>
					<button type="button" class={look.kind} style:--fill={look.fill} style:--edge={look.edge} style:--ink={look.ink} style:--size="{look.size}rem" onclick={() => give(v)} aria-label="Masukkan {ringgit(v)}">
						<b>{v < 100 ? v : `RM${v / 100}`}</b>{#if v < 100}<small>sen</small>{/if}
					</button>
				</li>
			{/each}
		</ul>
		<div class="actions">
			<button type="button" class="btn btn--plain" disabled={!paid.length} onclick={takeBack}><Icon name="back" /> Keluarkan</button>
		</div>
	{:else if ok === false}
		<p class="should">Bayar tepat {ringgit(amount)}.</p>
	{/if}
</div>
{#if !locked}
	<Checks tip="Masukkan wang sehingga jumlahnya tepat." label="Bayar zakat" ready={total > 0} dirty={paid.length > 0} onreset={() => (paid = [])} oncheck={() => p.onanswer?.(counts(paid))} />
{/if}

<style>
	.real-box {
		display: block;
		width: 5.5rem;
		height: 7.5rem;
		margin: 0 auto -0.4rem;
		overflow: hidden;
		border: 3px solid #fff;
		border-radius: 0.7rem;
		box-shadow: 0 4px 10px rgb(0 0 0 / 0.25);
		rotate: -2deg;
	}
	.real-box :global(img.g-img) {
		width: 100%;
		height: 100%;
	}
	.counter {
		display: grid;
		gap: 0.8rem;
		justify-items: center;
		padding: 0.9rem 0.6rem;
		border-radius: var(--r-lg);
		background:
			radial-gradient(circle at 50% 0%, rgb(255 255 255 / 0.6), transparent 60%),
			linear-gradient(180deg, #e8f3ec, #cfe6d8);
		box-shadow: inset 0 0 0 3px #a9cdb6;
	}
	.box {
		position: relative;
		display: grid;
		justify-items: center;
		gap: 0.3rem;
		width: min(100%, 17rem);
		padding: 1.4rem 0.8rem 0.9rem;
		border-radius: 10px;
		background:
			repeating-linear-gradient(90deg, rgb(0 0 0 / 0.05) 0 3px, transparent 3px 14px),
			linear-gradient(180deg, #7a4a24, #5a3416);
		box-shadow:
			inset 0 0 0 3px #3e220c,
			0 10px 18px rgb(40 20 5 / 0.35);
	}
	.slot {
		position: absolute;
		top: 0.5rem;
		left: 50%;
		width: 5rem;
		height: 0.5rem;
		translate: -50% 0;
		border-radius: 999px;
		background: #1a0e04;
		box-shadow: inset 0 2px 2px rgb(0 0 0 / 0.6);
	}
	.falling {
		position: absolute;
		top: -2rem;
		left: 50%;
		width: 1.4rem;
		height: 1.4rem;
		translate: -50% 0;
		border-radius: 50%;
		background: radial-gradient(circle at 35% 30%, #fff3c4, #d9a83a);
		animation: fall 0.45s ease-in forwards;
	}
	.title {
		color: #f6dc8c;
		font: 700 0.9rem var(--font-display);
		letter-spacing: 0.14em;
	}
	.plate {
		display: grid;
		justify-items: center;
		padding: 0.3rem 1rem;
		border-radius: 6px;
		background: linear-gradient(180deg, #f6dc8c, #c99a3a);
		color: #3a2408;
		box-shadow: inset 0 0 0 2px #8a6418;
	}
	.plate span {
		font: 700 0.7rem var(--font-body);
		text-transform: uppercase;
		letter-spacing: 0.08em;
	}
	.plate strong {
		font: 700 1.7rem/1.1 var(--font-display);
	}
	.plate strong.off {
		color: #9a2a10;
	}
	.due {
		color: #f3e2bd;
		font-size: 0.85rem;
		font-weight: 700;
	}
	.mark {
		position: absolute;
		right: 0.6rem;
		top: 0.6rem;
		width: 1.4rem;
		height: 1.4rem;
	}
	.purse {
		display: flex;
		flex-wrap: wrap;
		justify-content: center;
		align-items: center;
		gap: 0.5rem;
		margin: 0;
		padding: 0;
		list-style: none;
	}
	.coin,
	.note {
		display: grid;
		place-items: center;
		align-content: center;
		border: 0;
		color: var(--ink);
		font-family: var(--font-display);
		cursor: pointer;
		transition: transform var(--t-state) var(--spring);
	}
	.coin {
		width: var(--size);
		height: var(--size);
		border-radius: 50%;
		background: radial-gradient(circle at 35% 30%, #fff, var(--fill) 60%);
		box-shadow:
			inset 0 0 0 3px var(--edge),
			0 3px 0 var(--edge);
	}
	.note {
		width: 4.6rem;
		height: 2.4rem;
		border-radius: 4px;
		background: linear-gradient(135deg, var(--fill), #fff 140%);
		box-shadow:
			inset 0 0 0 2px var(--edge),
			0 3px 0 var(--edge);
	}
	.coin b,
	.note b {
		color: var(--ink);
		font-size: 0.85rem;
		line-height: 1;
	}
	.coin small {
		color: var(--ink);
		font-size: 0.55rem;
	}
	.coin:hover,
	.note:hover {
		transform: translateY(-3px);
	}
	.actions {
		display: flex;
		justify-content: center;
	}
	.should {
		color: #8a3b12;
		font-weight: 700;
	}
	@keyframes fall {
		to {
			top: 0.3rem;
			scale: 0.4;
			opacity: 0;
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.falling {
			animation: none;
			display: none;
		}
	}
</style>
