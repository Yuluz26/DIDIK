<!--
	Matching, for the games that are a "Padankan" question: the left-hand things stay put on the game's own
	board (`board`: element tiles, ships at their berths, sky panels, lanterns) and the right-hand ones are
	cards in a pile. Drag a card onto its partner, or tap a card and then its partner; tap a placed card to
	take it back. Semak once every left-hand thing has its card.
-->
<script lang="ts" module>
	export interface MatchView {
		left: { id: string; text: string; sticker?: string | null }[];
		/** The card placed on a left-hand thing (the child's, or once answered, theirs or the right one). */
		placed: (left: string) => { id: string; text: string } | undefined;
		ok: (left: string) => boolean | null;
		should: (left: string) => string | null;
		locked: boolean;
		picked: string | null;
		zone: (left: string) => string;
		tapLeft: (left: string) => void;
		grab: (left: string) => (node: HTMLElement) => void;
		allRight: boolean;
	}
</script>

<script lang="ts">
	import type { Snippet } from 'svelte';
	import { crossfade } from 'svelte/transition';
	import { backOut } from 'svelte/easing';
	import { dragTap, still } from '$lib/questions/drag';
	import Checks from './Checks.svelte';
	import { type GameProps, Pairs, isLocked, rightOf, shown } from './kit.svelte';

	let { p, board, pool = 'Padankan', tone = '' }: { p: GameProps; board: Snippet<[MatchView]>; pool?: string; tone?: string } = $props();

	const left = $derived(p.question.left ?? []);
	const rights = $derived(p.question.right ?? []);
	const byId = $derived(new Map(rights.map((r) => [r.id, r])));
	const pairs = new Pairs(true);
	const locked = $derived(isLocked(p));
	const map = $derived(shown<Record<string, string>>(p, pairs.map));
	const right = $derived(rightOf<Record<string, string>>(p));
	const free = $derived(rights.filter((r) => !Object.values(map).includes(r.id)));

	function drop(card: string, zone: string) {
		if (zone.startsWith('m-')) pairs.set(zone.slice(2), card);
		else if (zone === 'pool') {
			const at = pairs.keyOf(card);
			if (at) pairs.unset(at);
		}
	}

	const view: MatchView = $derived({
		left,
		placed: (l) => (map[l] ? byId.get(map[l]) : undefined),
		ok: (l) => (right ? right[l] === map[l] : null),
		should: (l) => (right && right[l] !== map[l] ? (byId.get(right[l])?.text ?? null) : null),
		locked,
		picked: pairs.picked,
		zone: (l) => `m-${l}`,
		tapLeft: (l) => {
			if (!locked && pairs.picked) pairs.set(l, pairs.picked);
		},
		grab: (l) =>
			dragTap({
				enabled: () => !locked && !!pairs.map[l],
				home: () => `m-${l}`,
				tap: () => pairs.unset(l),
				drop: (zone) => {
					const card = pairs.map[l];
					if (card) drop(card, zone);
				}
			}),
		allRight: !!right && left.every((l) => right[l.id] === map[l.id])
	});

	const [send, receive] = crossfade({ duration: () => (still() ? 0 : 320), easing: backOut });
</script>

<div class="match-play {tone}" class:picking={!!pairs.picked}>
	{@render board(view)}
	{#if !locked}
		<section class="pool" data-zone="pool" aria-label={pool}>
			<h3>{pool}</h3>
			<ul>
				{#each free as card (card.id)}
					<li in:receive={{ key: card.id }} out:send={{ key: card.id }}>
						<button
							type="button"
							class="card"
							class:picked={pairs.picked === card.id}
							aria-pressed={pairs.picked === card.id}
							{@attach dragTap({ enabled: () => !locked, home: () => 'pool', tap: () => pairs.pick(card.id), drop: (zone) => drop(card.id, zone) })}
						>
							{card.text}
						</button>
					</li>
				{:else}
					<li class="done">Semua sudah dipadankan. Semak bila sedia.</li>
				{/each}
			</ul>
		</section>
		<Checks
			tip={pairs.picked ? 'Sekarang ketik pasangannya.' : 'Seret setiap kad ke pasangannya, atau ketik kad kemudian pasangannya.'}
			ready={pairs.count() === left.length}
			dirty={pairs.count() > 0}
			onreset={() => pairs.clear()}
			oncheck={() => p.onanswer?.(pairs.map)}
		/>
	{/if}
</div>

<style>
	.match-play {
		display: grid;
		gap: 0.8rem;
	}
	.pool {
		display: grid;
		gap: 0.4rem;
		padding: 0.6rem;
		border-radius: var(--r-lg);
		background: var(--paper-2, #f6efe3);
	}
	.pool:global(.zone-hover) {
		outline: 3px dashed var(--sky);
	}
	h3 {
		font-size: 0.85rem;
		color: var(--ink-2);
		text-transform: uppercase;
		letter-spacing: 0.06em;
	}
	ul {
		display: flex;
		flex-wrap: wrap;
		justify-content: center;
		gap: 0.5rem;
		margin: 0;
		padding: 0;
		list-style: none;
	}
	.card {
		min-height: 2.8rem;
		max-width: 16rem;
		padding: 0.35rem 0.85rem;
		border: 0;
		border-radius: var(--r-md);
		background: #fff;
		color: var(--ink);
		font: 700 0.95rem/1.15 var(--font-body);
		box-shadow:
			0 4px 0 #e2d6c4,
			0 6px 12px rgb(31 45 39 / 0.08);
		cursor: grab;
		touch-action: none;
		transition: transform var(--t-state) var(--spring);
	}
	.card:hover {
		transform: translateY(-2px);
	}
	.card.picked {
		transform: translateY(-5px) rotate(-2deg) scale(1.05);
		outline: 3px solid var(--berry, #e0457b);
		outline-offset: 2px;
	}
	.card:global(.dragging) {
		z-index: 50;
		cursor: grabbing;
	}
	.done {
		color: var(--ink-2);
		font-weight: 800;
	}
	.picking :global([data-zone^='m-']) {
		cursor: pointer;
	}
</style>
