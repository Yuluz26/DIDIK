<!--
	Skrol Purba: the sentence written on an unrolled parchment between two wooden rods, with gaps in it.
	The words to fill them are red wax seals: tap a seal to press it into the next gap, or drag it to any
	gap; tap a pressed word to lift it out. Without a word bank, each gap is written in by hand.
-->
<script lang="ts">
	import { play } from '$lib/sound';
	import { dragTap } from '$lib/questions/drag';
	import Checks from '../Checks.svelte';
	import Mark from '../Mark.svelte';
	import { type GameProps, isLocked } from '../kit.svelte';

	let p: GameProps = $props();

	const parts = $derived((p.question.parts ?? []) as (string | { blank: number })[]);
	const blanks = $derived(p.question.blanks ?? 1);
	const bank = $derived(p.question.bank ?? null);
	const locked = $derived(isLocked(p));
	// with a bank, which seal (by its place in the bank) is in each gap; without, the words written
	let seals = $state<(number | null)[]>([]);
	let written = $state<string[]>([]);
	$effect.pre(() => {
		if (seals.length !== blanks) seals = Array(blanks).fill(null);
		if (written.length !== blanks) written = Array(blanks).fill('');
	});
	const words = $derived<string[]>(bank ? seals.map((s) => (s === null ? '' : bank[s])) : written);
	const shown = $derived<string[]>(p.mine !== undefined ? p.mine : p.reveal ? p.reveal.correct : words);
	const right = $derived<string[] | null>(p.reveal ? p.reveal.correct : null);
	const norm = (s: string) => s.toLowerCase().trim();
	const used = $derived(new Set(seals.filter((s): s is number => s !== null)));
	const ready = $derived(words.length === blanks && words.every((w) => w.trim()));

	function press(seal: number, at?: number) {
		if (locked) return;
		const next = [...seals];
		const from = next.indexOf(seal);
		if (from >= 0) next[from] = null;
		const gap = at ?? next.indexOf(null);
		if (gap < 0) return;
		next[gap] = seal;
		seals = next;
		play('pop');
	}
	function lift(at: number) {
		if (locked || !bank) return;
		const next = [...seals];
		next[at] = null;
		seals = next;
		play('tap');
	}
	import { asset } from '../assets';
	// a real skin of parchment, under the writing
	const SKIN = asset('hist/parchment');
</script>

<div class="scroll" style:--skin={SKIN ? `url(${SKIN.src})` : 'none'}>
	<span class="rod" aria-hidden="true"></span>
	<div class="parchment">
		<p class="text">
			{#each parts as part, i (i)}
				{#if typeof part === 'string'}{part}{:else}
					{@const n = part.blank}
					{@const ok = right ? norm(shown[n] ?? '') === norm(right[n]) : null}
					<span class="gap" class:filled={!!shown[n]} data-zone="b-{n}">
						{#if bank && !locked}
							{#if seals[n] !== null}
								<button
									type="button"
									class="word"
									{@attach dragTap({ enabled: () => !locked, home: () => `b-${n}`, tap: () => lift(n), drop: (zone) => zone.startsWith('b-') ? press(seals[n]!, Number(zone.slice(2))) : zone === 'bank' && lift(n) })}
								>{shown[n]}</button>
							{:else}<span class="blank">&nbsp;</span>{/if}
						{:else if !bank && !locked}
							<input
								class="write"
								value={written[n] ?? ''}
								size={Math.max(6, (written[n] ?? '').length + 1)}
								oninput={(e) => {
									const next = [...written];
									next[n] = (e.currentTarget as HTMLInputElement).value;
									written = next;
								}}
								aria-label="Tempat kosong {n + 1}"
							/>
						{:else}
							<span class="word done" class:ok={ok === true} class:off={ok === false}>{shown[n] || '…'}{#if ok !== null}<Mark {ok} size={11} />{/if}</span>
							{#if ok === false && right}<span class="should">({right[n]})</span>{/if}
						{/if}
					</span>
				{/if}
			{/each}
		</p>
	</div>
	<span class="rod" aria-hidden="true"></span>
</div>

{#if bank && !locked}
	<ul class="seals" data-zone="bank" aria-label="Perkataan">
		{#each bank as w, i (i)}
			{#if !used.has(i)}
				<li>
					<button type="button" class="seal" {@attach dragTap({ enabled: () => !locked, home: () => 'bank', tap: () => press(i), drop: (zone) => zone.startsWith('b-') && press(i, Number(zone.slice(2))) })}>
						<span>{w}</span>
					</button>
				</li>
			{/if}
		{/each}
	</ul>
{/if}
{#if !locked}
	<Checks
		tip={bank ? 'Ketik cop mohor untuk isi tempat kosong, atau seret ke tempatnya.' : 'Tulis perkataan di setiap tempat kosong.'}
		ready={ready}
		dirty={words.some((w) => w)}
		onreset={() => ((seals = Array(blanks).fill(null)), (written = Array(blanks).fill('')))}
		oncheck={() => p.onanswer?.(words.map((w) => w.trim()))}
	/>
{/if}

<style>
	.parchment {
		background-image: linear-gradient(rgb(250 236 200 / 0.72), rgb(240 220 170 / 0.72)), var(--skin) !important;
		background-size: cover !important;
		background-position: center !important;
	}
	.scroll {
		display: grid;
		justify-items: center;
	}
	.rod {
		width: 100%;
		height: 1.1rem;
		border-radius: 0.6rem;
		background: linear-gradient(180deg, #8a5a2c, #c08a52 40%, #6b4220);
		box-shadow: 0 3px 6px rgb(60 30 10 / 0.35);
	}
	.parchment {
		width: 94%;
		padding: 1.1rem 1rem;
		background:
			radial-gradient(circle at 15% 20%, rgb(255 255 255 / 0.4), transparent 35%),
			radial-gradient(circle at 85% 80%, rgb(160 110 40 / 0.18), transparent 40%),
			linear-gradient(90deg, #ead6a6, #f6e9c8 15%, #f6e9c8 85%, #ead6a6);
		box-shadow: inset 0 0 30px rgb(140 100 40 / 0.3);
	}
	.text {
		color: #3a2410;
		font: 600 clamp(1.15rem, 1rem + 0.8vw, 1.45rem) / 2.1 var(--font-display);
		text-align: center;
	}
	.gap {
		display: inline-flex;
		align-items: baseline;
		gap: 0.2rem;
		min-width: 4.5rem;
		margin: 0 0.15rem;
		border-bottom: 3px dotted #8a5a2c;
		vertical-align: baseline;
	}
	.gap:global(.zone-hover) {
		background: rgb(255 210 120 / 0.45);
	}
	.blank {
		display: inline-block;
		min-width: 4.5rem;
	}
	.word {
		position: relative;
		padding: 0 0.45rem;
		border: 0;
		border-radius: 6px;
		background: rgb(150 30 30 / 0.12);
		color: #7a1717;
		font: inherit;
		cursor: grab;
		touch-action: none;
	}
	.word.done {
		cursor: default;
	}
	.word.ok {
		background: rgb(40 150 80 / 0.15);
		color: #1d6b3c;
	}
	.word.off {
		background: rgb(220 110 40 / 0.18);
		color: #8a3b12;
	}
	.should {
		color: #1d6b3c;
		font-size: 0.85em;
	}
	.write {
		min-width: 4.5rem;
		border: 0;
		background: transparent;
		color: #7a1717;
		font: inherit;
		text-align: center;
	}
	.write:focus {
		outline: 2px solid #c08a52;
		border-radius: 4px;
	}
	.seals {
		display: flex;
		flex-wrap: wrap;
		justify-content: center;
		gap: 0.7rem;
		margin: 0;
		padding: 0.6rem;
		list-style: none;
	}
	.seal {
		display: grid;
		place-items: center;
		min-width: 4.6rem;
		min-height: 4.6rem;
		padding: 0.4rem;
		border: 0;
		border-radius: 46% 54% 50% 50% / 50% 48% 52% 50%;
		background: radial-gradient(circle at 35% 30%, #e0564a, #a51e1e 70%);
		box-shadow:
			inset 0 0 0 4px rgb(255 255 255 / 0.15),
			0 5px 0 #6e1010,
			0 8px 12px rgb(0 0 0 / 0.25);
		color: #fff4e6;
		font: 700 0.9rem/1.1 var(--font-display);
		cursor: grab;
		touch-action: none;
		transition: transform var(--t-state) var(--spring);
	}
	.seal:hover {
		transform: rotate(-6deg) scale(1.05);
	}
	.seal:global(.dragging) {
		z-index: 50;
	}
</style>
