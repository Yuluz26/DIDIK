<!--
	Susun huruf: letter tiles to put back in order under the picture. A tap puts a letter in the first
	empty box; dragging puts it in the box it is dropped on (a letter already there goes back). A tap on a
	filled box takes its letter out. Semak sends the tiles in order once every box is filled.
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

	interface Tile {
		id: string;
		ch: string;
	}

	let {
		tiles,
		length,
		sticker = null,
		disabled = false,
		mine = undefined,
		reveal = null,
		onanswer
	}: {
		tiles: Tile[];
		length: number;
		sticker?: string | null;
		disabled?: boolean;
		mine?: string[];
		reveal?: (Reveal & { word?: string }) | null;
		onanswer?: (answer: string[]) => void;
	} = $props();

	// the question is shown afresh (keyed by its id), so its length never changes under it
	let slots = $state<(string | null)[]>(Array.from({ length: untrack(() => length) }, () => null));

	// once answered, the boxes hold the answer given; on the host's screen at the reveal, the right word
	const shown = $derived<(string | null)[]>(mine ?? (reveal ? (reveal.correct as string[]) : slots));
	const byId = $derived(new Map(tiles.map((t) => [t.id, t])));
	const pool = $derived(tiles.filter((t) => !shown.includes(t.id)));
	const locked = $derived(disabled || !!reveal || mine !== undefined);
	const full = $derived(slots.length === length && slots.every(Boolean));
	const word = $derived<string>(reveal?.word ?? '');
	const correctTiles = $derived<string[]>(reveal ? reveal.correct : []);

	const [send, receive] = crossfade({
		duration: () => (still() ? 0 : 300),
		easing: backOut,
		fallback: (node) => ({ duration: still() ? 0 : 200, css: (t) => `opacity: ${t}; transform: scale(${0.6 + 0.4 * t})` })
	});

	function put(id: string, at = slots.indexOf(null)) {
		if (locked || at < 0) return;
		play('pop');
		const next = slots.map((s) => (s === id ? null : s));
		next[at] = id;
		slots = next;
	}

	function takeOut(at: number) {
		if (locked || !slots[at]) return;
		play('tap');
		slots = slots.map((s, i) => (i === at ? null : s));
	}

	const zoneSlot = (zone: string) => (zone.startsWith('slot-') ? Number(zone.slice(5)) : -1);
	// right letter in this box, compared without minding capitals
	const rightAt = (i: number) => !!word && !!shown[i] && byId.get(shown[i]!)?.ch.toLowerCase() === word[i]?.toLowerCase();
</script>

<div class="spell">
	{#if sticker}
		<div class="hint" aria-hidden="true"><Sticker key={sticker} size={108} alt="" eager /></div>
	{/if}

	<ol class="slots" aria-label="Kotak huruf">
		{#each shown as id, i (i)}
			<li class="slot" data-zone="slot-{i}" class:filled={!!id} class:ok={reveal && rightAt(i)} class:off={reveal && id && !rightAt(i)}>
				{#if id}
					{#key id}
						<button
							type="button"
							class="letter in-slot"
							in:receive|global={{ key: id }}
							out:send|global={{ key: id }}
							disabled={locked}
							aria-label="Huruf {byId.get(id)?.ch}, kotak {i + 1}. Ketik untuk keluarkan"
							{@attach dragTap({
								enabled: () => !locked,
								home: () => `slot-${i}`,
								tap: () => takeOut(i),
								drop: (zone) => (zone === 'pool' ? takeOut(i) : zoneSlot(zone) >= 0 && put(id, zoneSlot(zone)))
							})}
						>
							{byId.get(id)?.ch}
						</button>
					{/key}
				{:else}
					<span class="blank" aria-label="Kotak {i + 1} kosong"></span>
				{/if}
			</li>
		{/each}
	</ol>

	{#if !reveal && mine === undefined}
		<div class="pool" data-zone="pool" aria-label="Huruf untuk disusun">
			{#each pool as tile, i (tile.id)}
				<button
					type="button"
					class="letter t{i % 6}"
					disabled={locked}
					in:receive={{ key: tile.id }}
					out:send={{ key: tile.id }}
					aria-label="Huruf {tile.ch}"
					{@attach dragTap({
						enabled: () => !locked,
						home: () => 'pool',
						tap: () => put(tile.id),
						drop: (zone) => zoneSlot(zone) >= 0 && put(tile.id, zoneSlot(zone))
					})}
				>
					{tile.ch}
				</button>
			{/each}
		</div>
		{#if !locked}
		<div class="row">
			<button type="button" class="btn btn--plain" disabled={!slots.some(Boolean)} onclick={() => ((slots = slots.map(() => null)), play('tap'))}>
				<Icon name="shuffle" /> Susun semula
			</button>
			<button type="button" class="btn btn--big check" disabled={!full} onclick={() => onanswer?.(slots as string[])}>
				Semak <Icon name="check" />
			</button>
		</div>
		{/if}
	{/if}

	{#if reveal && word}
		<p class="answer" class:ok={shown.every((_, i) => rightAt(i))}>
			Ejaan betul:
			<strong>{#each word.split('') as ch, i (i)}<span style:--i={i}>{ch}</span>{/each}</strong>
		</p>
	{/if}
	{#if reveal && !word && correctTiles.length}
		<p class="answer">Ejaan betul: <strong>{correctTiles.map((id) => byId.get(id)?.ch).join('')}</strong></p>
	{/if}
</div>

<style>
	.spell {
		display: grid;
		justify-items: center;
		gap: 0.9rem;
	}
	.hint {
		display: grid;
		place-items: center;
		width: 8.2rem;
		height: 8.2rem;
		border-radius: 50%;
		background: radial-gradient(circle at 50% 40%, #fff 0 40%, #ffeef7 70%, #ffe1ef);
		box-shadow:
			inset 0 -6px 0 rgb(211 50 141 / 0.1),
			0 6px 14px rgb(211 50 141 / 0.12);
		animation: float-soft 3.2s ease-in-out infinite;
	}
	.slots {
		display: flex;
		flex-wrap: wrap;
		justify-content: center;
		gap: 0.4rem;
		margin: 0;
		padding: 0;
		list-style: none;
	}
	.slot {
		--size: clamp(2.6rem, 11vw, 3.4rem);
		display: grid;
		place-items: center;
		width: var(--size);
		height: calc(var(--size) * 1.12);
		border: 3px dashed #d9c4ec;
		border-radius: var(--r-md);
		background: #fbf6ff;
		transition:
			border-color var(--t-state),
			transform var(--t-state) var(--spring),
			background-color var(--t-state);
	}
	.slot.filled {
		border-style: solid;
		border-color: transparent;
		background: none;
	}
	.slot:global(.zone-hover) {
		border-style: solid;
		border-color: var(--berry);
		background: #ffe6f3;
		transform: translateY(-3px);
	}
	.slot.ok :global(.letter) {
		--c: var(--good);
		--shade: #13723c;
		color: #fff;
	}
	.slot.off :global(.letter) {
		--c: var(--almost);
		--shade: #a5550f;
		color: #fff;
	}
	.blank {
		width: 40%;
		height: 3px;
		margin-top: 40%;
		border-radius: 3px;
		background: #d9c4ec;
	}
	.pool {
		display: flex;
		flex-wrap: wrap;
		justify-content: center;
		gap: 0.55rem;
		min-height: 3.6rem;
		padding: 0.6rem;
		border-radius: var(--r-lg);
	}
	.pool:global(.zone-hover) {
		outline: 3px dashed var(--sky);
		outline-offset: -3px;
	}
	.letter {
		--c: #ffd36b;
		--shade: #d99a12;
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
		transition:
			transform var(--t-state) var(--spring),
			box-shadow var(--t-press);
	}
	.letter.in-slot {
		width: 100%;
		height: 100%;
	}
	.letter:not(:disabled):hover {
		transform: translateY(-3px) rotate(-2deg);
		box-shadow:
			0 8px 0 var(--shade),
			inset 0 3px 0 rgb(255 255 255 / 0.45);
	}
	.letter:not(:disabled):active {
		transform: translateY(4px);
		box-shadow:
			0 1px 0 var(--shade),
			inset 0 3px 0 rgb(255 255 255 / 0.45);
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
		cursor: grabbing;
	}
	.letter.t1 {
		--c: #9fe3d4;
		--shade: #3fae97;
	}
	.letter.t2 {
		--c: #ffb3c9;
		--shade: #df6f92;
	}
	.letter.t3 {
		--c: #b8d4ff;
		--shade: #5d8fe0;
	}
	.letter.t4 {
		--c: #c8ef9d;
		--shade: #79b941;
	}
	.letter.t5 {
		--c: #dcc6ff;
		--shade: #9a73e0;
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
		text-align: center;
	}
	.answer.ok {
		background: var(--good-soft);
		color: var(--on-good-soft);
	}
	.answer strong {
		font: 600 1.3rem var(--font-display);
		letter-spacing: 0.12em;
	}
	.answer strong span {
		display: inline-block;
		animation: pop-in 360ms var(--spring) both;
		animation-delay: calc(var(--i) * 70ms);
	}
	@keyframes float-soft {
		50% {
			transform: translateY(-5px) rotate(-2deg);
		}
	}
</style>
