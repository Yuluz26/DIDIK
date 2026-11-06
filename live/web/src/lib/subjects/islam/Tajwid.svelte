<!--
	Warna Tajwid: a page like a colour-coded mushaf. Each kalimah stays where it is on the page; pick a pen
	(one for each hukum) and tap a kalimah to colour it with that hukum, or tap a kalimah and then a pen.
	Tap a coloured kalimah with its own pen to clear it. Semak once every kalimah has its colour.
-->
<script lang="ts">
	import '@fontsource/amiri/arabic-400.css';
	import '@fontsource/amiri/arabic-700.css';
	import { play } from '$lib/sound';
	import Checks from '../Checks.svelte';
	import Mark from '../Mark.svelte';
	import { type GameProps, Pairs, isLocked, rightOf, shown } from '../kit.svelte';

	let p: GameProps = $props();

	const PENS = ['#d6342c', '#1f9d55', '#2f6fd1', '#e28a12', '#8a4fd1', '#7b8794'];
	const groups = $derived(p.question.groups ?? []);
	const items = $derived(p.question.items ?? []);
	const colour = $derived(new Map(groups.map((g, i) => [g.id, PENS[i % PENS.length]])));
	const names = $derived(new Map(groups.map((g) => [g.id, g.name])));
	const pairs = new Pairs(false);
	let pen = $state<string | null>(null);
	const locked = $derived(isLocked(p));
	const map = $derived(shown<Record<string, string>>(p, pairs.map));
	const right = $derived(rightOf<Record<string, string>>(p));
	const done = $derived(items.every((i) => pairs.map[i.id]));

	function tapWord(id: string) {
		if (locked) return;
		if (pen) {
			if (pairs.map[id] === pen) pairs.unset(id);
			else pairs.set(id, pen);
		} else pairs.pick(id);
	}
	function tapPen(g: string) {
		if (locked) return;
		if (pairs.picked) {
			pairs.set(pairs.picked, g);
			pen = g;
		} else {
			pen = pen === g ? null : g;
			play('tap');
		}
	}
</script>

<div class="tajwid">
	<div class="page">
		<div class="words" dir="rtl" lang="ar">
			{#each items as item (item.id)}
				{@const g = map[item.id]}
				{@const ok = right ? right[item.id] === g : null}
				<span class="slot">
					<button
						type="button"
						class="word"
						class:painted={!!g}
						class:picked={pairs.picked === item.id}
						style:--c={g ? colour.get(g) : 'transparent'}
						disabled={locked}
						onclick={() => tapWord(item.id)}
						aria-label="{item.text}{g ? `, ${names.get(g)}` : ''}"
					>
						{item.text}
						{#if ok !== null}<Mark {ok} />{/if}
					</button>
					{#if right && ok === false}<span class="should" dir="ltr">→ {names.get(right[item.id])}</span>{/if}
				</span>
			{/each}
		</div>
	</div>

	<div class="pens" role="group" aria-label="Hukum tajwid">
		{#each groups as g (g.id)}
			<button type="button" class="pen" class:on={pen === g.id} style:--c={colour.get(g.id)} disabled={locked} aria-pressed={pen === g.id} onclick={() => tapPen(g.id)}>
				<span class="nib" aria-hidden="true"></span>
				{g.name}
			</button>
		{/each}
	</div>

	{#if !locked}
		<Checks
			tip={pairs.picked ? 'Sekarang pilih warna hukumnya.' : pen ? `Ketik kalimah untuk diwarnakan ${names.get(pen)}.` : 'Pilih pen hukum, kemudian ketik kalimah. Atau ketik kalimah dahulu.'}
			ready={done}
			dirty={pairs.count() > 0}
			onreset={() => (pairs.clear(), (pen = null))}
			oncheck={() => p.onanswer?.(pairs.map)}
		/>
	{/if}
</div>

<style>
	.tajwid {
		display: grid;
		gap: 0.8rem;
	}
	.page {
		padding: 0.7rem;
		border-radius: 10px;
		background: #fbf4e2;
		box-shadow:
			inset 0 0 0 3px #b8892c,
			inset 0 0 0 6px #fbf4e2,
			inset 0 0 0 8px #2f6f4e,
			inset 0 0 0 11px #fbf4e2,
			inset 0 0 0 13px #b8892c,
			0 8px 18px rgb(90 60 10 / 0.18);
	}
	.words {
		display: flex;
		flex-wrap: wrap;
		justify-content: center;
		gap: 0.7rem 0.6rem;
		padding: 1.3rem 1rem;
	}
	.slot {
		display: inline-grid;
		justify-items: center;
		gap: 0.15rem;
	}
	.word {
		position: relative;
		padding: 0.15rem 0.7rem 0.35rem;
		border: 2px dashed #d9c08a;
		border-radius: 12px;
		background: color-mix(in srgb, var(--c) 18%, #fffdf6);
		color: var(--c, #2a1f12);
		font: 400 2rem/1.7 'Amiri', 'Scheherazade New', 'Traditional Arabic', serif;
		cursor: pointer;
		transition:
			transform var(--t-state) var(--spring),
			background var(--t-state);
	}
	.word:not(.painted) {
		color: #2a1f12;
	}
	.word.painted {
		border-style: solid;
		border-color: var(--c);
		font-weight: 700;
	}
	.word.picked {
		transform: translateY(-3px) scale(1.05);
		outline: 3px solid var(--berry, #e0457b);
		outline-offset: 2px;
	}
	.word:disabled {
		cursor: default;
	}
	.should {
		color: #8a2a00;
		font-weight: 800;
		font-size: 0.78rem;
	}
	.pens {
		display: flex;
		flex-wrap: wrap;
		justify-content: center;
		gap: 0.5rem;
	}
	.pen {
		display: inline-flex;
		align-items: center;
		gap: 0.45rem;
		min-height: 2.8rem;
		padding: 0.3rem 0.9rem 0.3rem 0.4rem;
		border: 2px solid var(--c);
		border-radius: 999px;
		background: #fff;
		color: var(--ink);
		font: 700 0.95rem var(--font-body);
		cursor: pointer;
		transition: transform var(--t-state) var(--spring);
	}
	.pen.on {
		transform: translateY(-3px);
		background: color-mix(in srgb, var(--c) 16%, #fff);
		box-shadow: 0 4px 0 color-mix(in srgb, var(--c) 60%, #000);
	}
	.nib {
		width: 1.6rem;
		height: 1.6rem;
		border-radius: 50% 0 50% 50%;
		rotate: -45deg;
		background: var(--c);
		box-shadow: inset -3px -3px 0 rgb(0 0 0 / 0.15);
	}
</style>
