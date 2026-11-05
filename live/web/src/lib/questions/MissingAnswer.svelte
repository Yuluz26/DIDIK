<!--
	Huruf hilang: a word with one to three letters missing, under its picture. A tap puts a letter tile in
	the first gap; dragging puts it in the gap it is dropped on. A tap on a filled gap takes the letter out.
	Semak once every gap is filled.
-->
<script lang="ts">
	import { untrack } from 'svelte';
	import { crossfade } from 'svelte/transition';
	import { backOut } from 'svelte/easing';
	import type { Reveal } from '$lib/types';
	import { play } from '$lib/sound';
	import Icon from '$ui/Icon.svelte';
	import Sticker from '$ui/Sticker.svelte';
	import { dragTap, still } from './drag';

	type Part = { ch: string } | { blank: number };

	let {
		parts,
		tiles,
		blanks,
		sticker = null,
		disabled = false,
		mine = undefined,
		reveal = null,
		onanswer
	}: {
		parts: Part[];
		tiles: { id: string; ch: string }[];
		blanks: number;
		sticker?: string | null;
		disabled?: boolean;
		mine?: string[];
		reveal?: Reveal | null;
		onanswer?: (answer: string[]) => void;
	} = $props();

	let filled = $state<(string | null)[]>(Array.from({ length: untrack(() => blanks) }, () => null));
	const shown = $derived<(string | null)[]>(mine ?? (reveal ? (reveal.correct as string[]) : filled));
	const byId = $derived(new Map(tiles.map((t) => [t.id, t.ch])));
	const pool = $derived(tiles.filter((t) => !shown.includes(t.id)));
	const locked = $derived(disabled || !!reveal || mine !== undefined);
	const word = $derived(reveal?.word ?? '');
	const gapAt = $derived(parts.flatMap((p, i) => ('blank' in p ? [i] : [])));
	const rightAt = (k: number) => !!word && !!shown[k] && byId.get(shown[k]!)?.toLowerCase() === word[gapAt[k]]?.toLowerCase();

	const [send, receive] = crossfade({
		duration: () => (still() ? 0 : 300),
		easing: backOut,
		fallback: (node) => ({ duration: still() ? 0 : 200, css: (t) => `opacity: ${t}; transform: scale(${0.6 + 0.4 * t})` })
	});

	function put(id: string, at = filled.indexOf(null)) {
		if (locked || at < 0) return;
		play('pop');
		const next = filled.map((f) => (f === id ? null : f));
		next[at] = id;
		filled = next;
	}

	function takeOut(at: number) {
		if (locked || !filled[at]) return;
		play('tap');
		filled = filled.map((f, i) => (i === at ? null : f));
	}

	const zoneGap = (zone: string) => (zone.startsWith('gap-') ? Number(zone.slice(4)) : -1);
</script>

<div class="missing">
	{#if sticker}<div class="hint" aria-hidden="true"><Sticker key={sticker} size={104} alt="" eager /></div>{/if}

	<p class="word" aria-label="Perkataan dengan huruf hilang">
		{#each parts as part, i (i)}
			{#if 'ch' in part}
				<span class="fixed">{part.ch}</span>
			{:else}
				{@const k = part.blank}
				{@const id = shown[k]}
				<span class="gap" data-zone="gap-{k}" class:filled={!!id} class:ok={reveal && rightAt(k)} class:off={reveal && id && !rightAt(k)}>
					{#if id}
						{#key id}
							<button
								type="button"
								class="letter in-gap"
								in:receive|global={{ key: id }}
								out:send|global={{ key: id }}
								disabled={locked}
								aria-label="Huruf {byId.get(id)}. Ketik untuk keluarkan"
								{@attach dragTap({
									enabled: () => !locked,
									home: () => `gap-${k}`,
									tap: () => takeOut(k),
									drop: (zone) => (zone === 'pool' ? takeOut(k) : zoneGap(zone) >= 0 && put(id, zoneGap(zone)))
								})}>{byId.get(id)}</button
							>
						{/key}
					{:else}
						<span class="q" aria-label="Huruf hilang">?</span>
					{/if}
				</span>
			{/if}
		{/each}
	</p>

	{#if !reveal && mine === undefined}
		<div class="pool" data-zone="pool" aria-label="Pilih huruf">
			{#each pool as tile, i (tile.id)}
				<button
					type="button"
					class="letter t{i % 4}"
					in:receive={{ key: tile.id }}
					out:send={{ key: tile.id }}
					disabled={locked}
					aria-label="Huruf {tile.ch}"
					{@attach dragTap({ enabled: () => !locked, home: () => 'pool', tap: () => put(tile.id), drop: (zone) => zoneGap(zone) >= 0 && put(tile.id, zoneGap(zone)) })}
					>{tile.ch}</button
				>
			{/each}
		</div>
		{#if !locked}
			<div class="row">
				<button type="button" class="btn btn--plain" disabled={!filled.some(Boolean)} onclick={() => ((filled = filled.map(() => null)), play('tap'))}>
					<Icon name="shuffle" /> Mula semula
				</button>
				<button type="button" class="btn btn--big check" disabled={!filled.every(Boolean)} onclick={() => onanswer?.(filled as string[])}>
					Semak <Icon name="check" />
				</button>
			</div>
		{/if}
	{/if}

	{#if reveal && word}
		<p class="answer" class:ok={shown.every((_, k) => rightAt(k))}>Perkataan: <strong>{word}</strong></p>
	{/if}
</div>

<style>
	.missing {
		display: grid;
		justify-items: center;
		gap: 0.9rem;
	}
	.hint {
		display: grid;
		place-items: center;
		width: 8rem;
		height: 8rem;
		border-radius: 50%;
		background: radial-gradient(circle at 50% 40%, #fff 0 40%, #eef7ff 70%, #dcefff);
		box-shadow: 0 6px 14px rgb(45 120 196 / 0.14);
	}
	.word {
		display: flex;
		flex-wrap: wrap;
		justify-content: center;
		gap: 0.35rem;
	}
	.fixed,
	.gap {
		--size: clamp(2.6rem, 11vw, 3.4rem);
		display: grid;
		place-items: center;
		width: var(--size);
		height: calc(var(--size) * 1.12);
		border-radius: var(--r-md);
		font: 600 clamp(1.4rem, 1.1rem + 1.6vw, 1.9rem) / 1 var(--font-display);
	}
	.fixed {
		background: #fff;
		color: var(--ink);
		box-shadow:
			inset 0 0 0 2px #e6e0f0,
			0 3px 0 #e6e0f0;
	}
	.gap {
		border: 3px dashed #9fc6ef;
		background: #f2f8ff;
		transition:
			transform var(--t-state) var(--spring),
			border-color var(--t-state);
	}
	.gap.filled {
		border-color: transparent;
		background: none;
	}
	.gap:global(.zone-hover) {
		border-style: solid;
		border-color: var(--sky);
		transform: translateY(-3px);
	}
	.q {
		color: #7aa6d6;
	}
	.gap.ok :global(.letter) {
		--c: var(--good);
		--shade: #13723c;
		color: #fff;
	}
	.gap.off :global(.letter) {
		--c: var(--almost);
		--shade: #a5550f;
		color: #fff;
	}
	.pool {
		display: flex;
		flex-wrap: wrap;
		justify-content: center;
		gap: 0.55rem;
		min-height: 3.6rem;
		padding: 0.5rem;
		border-radius: var(--r-lg);
	}
	.letter {
		--c: #b8d4ff;
		--shade: #5d8fe0;
		display: grid;
		place-items: center;
		width: clamp(2.6rem, 11vw, 3.4rem);
		height: clamp(2.9rem, 12.3vw, 3.8rem);
		border: 0;
		border-radius: var(--r-md);
		background: var(--c);
		color: var(--ink);
		font: 600 clamp(1.4rem, 1.1rem + 1.6vw, 1.9rem) / 1 var(--font-display);
		box-shadow:
			0 5px 0 var(--shade),
			inset 0 3px 0 rgb(255 255 255 / 0.45);
		cursor: grab;
		touch-action: none;
		transition: transform var(--t-state) var(--spring);
	}
	.letter.in-gap {
		width: 100%;
		height: 100%;
	}
	.letter:not(:disabled):hover {
		transform: translateY(-3px) rotate(-2deg);
	}
	.letter:disabled {
		cursor: default;
	}
	.letter:focus-visible {
		outline: 3px solid var(--sky);
		outline-offset: 3px;
	}
	.letter:global(.dragging) {
		position: relative;
		z-index: 50;
	}
	.letter.t1 {
		--c: #ffd36b;
		--shade: #d99a12;
	}
	.letter.t2 {
		--c: #b6ecdf;
		--shade: #5fc0a6;
	}
	.letter.t3 {
		--c: #ffc2d4;
		--shade: #ec8fac;
	}
	.row {
		display: flex;
		flex-wrap: wrap;
		justify-content: space-between;
		gap: 0.6rem;
		width: 100%;
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
	}
	.answer.ok {
		background: var(--good-soft);
		color: var(--on-good-soft);
	}
	.answer strong {
		font: 600 1.3rem var(--font-display);
		letter-spacing: 0.12em;
	}
</style>
