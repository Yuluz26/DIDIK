<!--
	Cantum gambar: a picture (a 3D sticker on a colourful backdrop, or the question's own picture) cut into
	4 or 9 pieces. The board shows a faint copy as a guide. Tap a piece and then a square, or drag it there;
	tap a placed piece to send it back. Semak once every square is filled.
-->
<script lang="ts">
	import { untrack } from 'svelte';
	import { crossfade } from 'svelte/transition';
	import { backOut } from 'svelte/easing';
	import type { Reveal } from '$lib/types';
	import { play } from '$lib/sound';
	import { stickerUrl } from '$lib/stickers';
	import Icon from '$ui/Icon.svelte';
	import { dragTap, still } from './drag';

	let {
		pieces,
		grid,
		sticker = null,
		image = null,
		disabled = false,
		mine = undefined,
		reveal = null,
		onanswer
	}: {
		pieces: { id: string; cut: number }[];
		grid: number;
		sticker?: string | null;
		image?: string | null;
		disabled?: boolean;
		mine?: string[];
		reveal?: Reveal | null;
		onanswer?: (answer: string[]) => void;
	} = $props();

	const n = $derived(grid * grid);
	let board = $state<(string | null)[]>(Array.from({ length: untrack(() => grid * grid) }, () => null));
	let picked = $state<string | null>(null);
	const shown = $derived<(string | null)[]>(mine ?? (reveal ? (reveal.correct as string[]) : board));
	const cutOf = $derived(new Map(pieces.map((p) => [p.id, p.cut])));
	const tray = $derived(pieces.filter((p) => !shown.includes(p.id)));
	const locked = $derived(disabled || !!reveal || mine !== undefined);

	// An uploaded picture keeps its own shape; a sticker sits on a square, colourful backdrop, so every
	// piece (even a corner with no sticker on it) has colours of its own to place it by.
	let ratio = $state(1);
	$effect(() => {
		if (!image || sticker) return;
		const probe = new Image();
		probe.onload = () => probe.naturalHeight && (ratio = probe.naturalWidth / probe.naturalHeight);
		probe.src = image;
	});
	const layers = $derived(
		sticker
			? `url(${stickerUrl(sticker)}), conic-gradient(from 45deg, #ffd1e3, #ffe9a8, #c9f2d8, #c8e2ff, #e3d2ff, #ffd1e3)`
			: `url(${image})`
	);
	const pos = (cut: number) => {
		const x = grid > 1 ? ((cut % grid) / (grid - 1)) * 100 : 0;
		const y = grid > 1 ? (Math.floor(cut / grid) / (grid - 1)) * 100 : 0;
		return `${x}% ${y}%`;
	};

	const [send, receive] = crossfade({
		duration: (d) => (still() ? 0 : Math.min(420, 180 + Math.sqrt(d) * 12)),
		easing: backOut,
		fallback: (node) => ({ duration: still() ? 0 : 200, css: (t) => `opacity: ${t}; transform: scale(${0.7 + 0.3 * t})` })
	});

	function place(id: string, at: number) {
		if (locked || at < 0) return;
		play('pop');
		const next = board.map((b) => (b === id ? null : b));
		next[at] = id;
		board = next;
		picked = null;
	}

	function takeOut(at: number) {
		if (locked || !board[at]) return;
		play('tap');
		board = board.map((b, i) => (i === at ? null : b));
	}

	function tapSlot(at: number) {
		if (locked) return;
		if (picked) place(picked, at);
		else if (board[at]) takeOut(at);
	}

	const zoneSlot = (zone: string) => (zone.startsWith('sq-') ? Number(zone.slice(3)) : -1);
	const rightAt = (i: number) => shown[i] !== null && cutOf.get(shown[i]!) === i;
</script>

{#snippet piece(id: string, size: string)}
	<span class="art" style:--size={size} style:background-image={layers} style:background-size="{grid * 100}% {grid * 100}%" style:background-position={pos(cutOf.get(id) ?? 0)}></span>
{/snippet}

<div class="puzzle" style:--grid={grid} style:--ratio={ratio}>
	<div class="board" style:--ghost={layers} role="group" aria-label="Papan cantuman, {n} petak">
		{#each Array.from({ length: n }, (_, i) => i) as i (i)}
			{@const id = shown[i]}
			<!-- svelte-ignore a11y_click_events_have_key_events, a11y_no_static_element_interactions -->
			<div class="sq" data-zone="sq-{i}" class:empty={!id} class:ok={reveal && rightAt(i)} class:off={reveal && id && !rightAt(i)} onclick={() => !id && tapSlot(i)}>
				{#if id}
					{#key id}
						<button
							type="button"
							class="placed"
							in:receive|global={{ key: id }}
							out:send|global={{ key: id }}
							disabled={locked}
							aria-label="Kepingan di petak {i + 1}. Ketik untuk keluarkan"
							{@attach dragTap({
								enabled: () => !locked,
								home: () => `sq-${i}`,
								tap: () => (picked ? place(picked, i) : takeOut(i)),
								drop: (zone) => (zone === 'tray' ? takeOut(i) : zoneSlot(zone) >= 0 && place(id, zoneSlot(zone)))
							})}>{@render piece(id, '100%')}</button
						>
					{/key}
				{:else if picked}
					<span class="drop-here" aria-hidden="true"></span>
				{/if}
			</div>
		{/each}
	</div>

	{#if !reveal && mine === undefined}
		<p class="tip">{picked ? 'Sekarang ketik petak untuknya.' : 'Ketik satu kepingan, kemudian petaknya. Atau seret terus.'}</p>
		<div class="tray" data-zone="tray" aria-label="Kepingan gambar">
			{#each tray as p (p.id)}
				<button
					type="button"
					class="loose"
					class:picked={picked === p.id}
					in:receive={{ key: p.id }}
					out:send={{ key: p.id }}
					disabled={locked}
					aria-pressed={picked === p.id}
					aria-label="Kepingan gambar"
					{@attach dragTap({
						enabled: () => !locked,
						home: () => 'tray',
						tap: () => ((picked = picked === p.id ? null : p.id), play('tap')),
						drop: (zone) => zoneSlot(zone) >= 0 && place(p.id, zoneSlot(zone))
					})}>{@render piece(p.id, '100%')}</button
				>
			{/each}
		</div>
		{#if !locked}
			<div class="row">
				<button type="button" class="btn btn--plain" disabled={!board.some(Boolean)} onclick={() => ((board = board.map(() => null)), (picked = null), play('tap'))}>
					<Icon name="shuffle" /> Mula semula
				</button>
				<button type="button" class="btn btn--big check" disabled={!board.every(Boolean)} onclick={() => onanswer?.(board as string[])}>
					Semak <Icon name="check" />
				</button>
			</div>
		{/if}
	{/if}
</div>

<style>
	.puzzle {
		display: grid;
		justify-items: center;
		gap: 0.8rem;
	}
	.board {
		position: relative;
		display: grid;
		grid-template-columns: repeat(var(--grid), minmax(0, 1fr));
		grid-template-rows: repeat(var(--grid), minmax(0, 1fr));
		gap: 3px;
		width: min(100%, 20rem);
		aspect-ratio: var(--ratio);
		padding: 6px;
		border-radius: var(--r-lg);
		background: #fff;
		box-shadow:
			0 6px 0 #e6dbf6,
			0 14px 30px rgb(110 80 160 / 0.15);
	}
	/* the faint guide under the squares */
	.board::before {
		content: '';
		position: absolute;
		inset: 6px;
		border-radius: calc(var(--r-lg) - 4px);
		background-image: var(--ghost);
		background-size: 100% 100%;
		opacity: 0.18;
		filter: grayscale(0.4);
		pointer-events: none;
	}
	.sq {
		position: relative;
		display: grid;
		border-radius: 8px;
		outline: 2px dashed rgb(150 120 200 / 0.35);
		outline-offset: -2px;
		transition: outline-color var(--t-state);
	}
	.sq.empty {
		cursor: pointer;
	}
	.sq:global(.zone-hover) {
		outline: 3px solid var(--berry);
		background: rgb(211 50 141 / 0.08);
	}
	.sq.ok {
		outline: 3px solid var(--good);
	}
	.sq.off {
		outline: 3px solid var(--almost);
	}
	.drop-here {
		margin: auto;
		width: 30%;
		aspect-ratio: 1;
		border-radius: 50%;
		background: rgb(211 50 141 / 0.18);
		animation: pulse-drop 1.2s ease-in-out infinite;
	}
	.placed,
	.loose {
		display: block;
		padding: 0;
		border: 0;
		background: none;
		cursor: grab;
		touch-action: none;
	}
	.placed {
		width: 100%;
		height: 100%;
	}
	.placed:disabled,
	.loose:disabled {
		cursor: default;
	}
	.art {
		display: block;
		width: var(--size);
		height: 100%;
		border-radius: 8px;
		background-repeat: no-repeat;
	}
	.tray {
		display: flex;
		flex-wrap: wrap;
		justify-content: center;
		gap: 0.5rem;
		min-height: 4.5rem;
		padding: 0.5rem;
		border-radius: var(--r-lg);
	}
	.loose {
		width: calc(min(20rem, 92vw) / var(--grid) * 0.8);
		aspect-ratio: var(--ratio);
		border-radius: 10px;
		box-shadow:
			0 4px 0 #e2d6c4,
			0 8px 14px rgb(31 45 39 / 0.12);
		transition: transform var(--t-state) var(--spring);
	}
	.loose:not(:disabled):hover {
		transform: translateY(-3px) rotate(-2deg);
	}
	.loose.picked {
		outline: 4px solid var(--berry);
		outline-offset: 2px;
		transform: translateY(-5px) scale(1.05);
	}
	.loose:global(.dragging) {
		z-index: 50;
	}
	.placed:focus-visible,
	.loose:focus-visible {
		outline: 3px solid var(--sky);
		outline-offset: 2px;
	}
	.tip {
		color: var(--ink-2);
		font-weight: 800;
		text-align: center;
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
	@keyframes pulse-drop {
		50% {
			transform: scale(1.4);
			opacity: 0.6;
		}
	}
</style>
