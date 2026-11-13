<!--
	Putting things in order, for the games that are a "Susun turutan" question: the things to place in a
	pile, numbered places on the game's own board (`board`, which lays them out as orbits, a wheel, a
	palace, a rope, a map...). Tap a thing to put it in the next empty place, or drag it onto any place;
	tap a placed thing to take it back, or drag it to another place to swap. Semak once every place is filled.

	The board gets one `OrderView` to draw with: what is in each place, and the means to make a place a
	drop zone and its thing movable.
-->
<script lang="ts" module>
	export interface OrderView {
		/** The thing in each place (the child's, or once answered, theirs or the right one). */
		slots: (string | null)[];
		text: (id: string | null) => string;
		sticker: (id: string | null) => string | undefined;
		/** Right or wrong once the answer is shown; null before. */
		ok: (i: number) => boolean | null;
		/** What should be in a wrongly filled place, once shown. */
		should: (i: number) => string | null;
		locked: boolean;
		/** The drop zone a place is. */
		zone: (i: number) => string;
		/** The attachment that makes the thing in place i movable (tap to take back, drag to move). */
		grab: (i: number) => (node: HTMLElement) => void;
		/** All right, once shown. */
		allRight: boolean;
	}
</script>

<script lang="ts">
	import { type Snippet, untrack } from 'svelte';
	import { crossfade } from 'svelte/transition';
	import { backOut } from 'svelte/easing';
	import { dragTap, still } from '$lib/questions/drag';
	import Sticker from '$ui/Sticker.svelte';
	import Checks from './Checks.svelte';
	import { type GameProps, Slots, isLocked, rightOf, shown, stickerFor } from './kit.svelte';

	let {
		p,
		board,
		tip = 'Ketik untuk letak di tempat kosong seterusnya, atau seret ke tempatnya.',
		pool = 'Susun ini',
		tone = '',
		pic,
		thing
	}: {
		p: GameProps;
		board: Snippet<[OrderView]>;
		tip?: string;
		pool?: string;
		tone?: string;
		/** The game's own picture for a thing, by its words (else its sticker, or one its name suggests). */
		pic?: (text: string) => string | undefined;
		/** The game's own way of drawing a thing in the pile (a real picture with its name), instead of a sticker. */
		thing?: Snippet<[{ id: string; text: string }]>;
	} = $props();

	const items = $derived(p.question.items ?? []);
	const byId = $derived(new Map(items.map((i) => [i.id, i])));
	const play = new Slots(untrack(() => p.question.items?.length ?? 0));
	const locked = $derived(isLocked(p));
	const slots = $derived(shown<(string | null)[]>(p, play.slots));
	const right = $derived(rightOf<string[]>(p));
	const left = $derived(items.filter((i) => !slots.includes(i.id)));

	const text = (id: string | null) => (id ? (byId.get(id)?.text ?? '') : '');
	const sticker = (id: string | null) => {
		if (!id) return undefined;
		const item = byId.get(id);
		if (pic) return pic(item?.text ?? '');
		return item?.sticker ?? stickerFor(item?.text ?? '');
	};

	function drop(item: string, zone: string) {
		if (zone.startsWith('o-')) play.put(item, Number(zone.slice(2)));
		else if (zone === 'pool') {
			const at = play.slots.indexOf(item);
			if (at >= 0) play.take(at);
		}
	}

	const view: OrderView = $derived({
		slots,
		text,
		sticker,
		ok: (i) => (right ? slots[i] === right[i] : null),
		should: (i) => (right && slots[i] !== right[i] ? text(right[i]) : null),
		locked,
		zone: (i) => `o-${i}`,
		grab: (i) =>
			dragTap({
				enabled: () => !locked && !!play.slots[i],
				home: () => `o-${i}`,
				tap: () => play.take(i),
				drop: (zone) => {
					const item = play.slots[i];
					if (item) drop(item, zone);
				}
			}),
		allRight: !!right && slots.every((s, i) => s === right[i])
	});

	const [send, receive] = crossfade({ duration: () => (still() ? 0 : 320), easing: backOut });
</script>

<div class="order-play {tone}">
	{@render board(view)}

	{#if !locked}
		<section class="pool" data-zone="pool" aria-label={pool}>
			<h3>{pool}</h3>
			<ul>
				{#each left as item (item.id)}
					{@const pic = sticker(item.id)}
					<li in:receive={{ key: item.id }} out:send={{ key: item.id }}>
						<button
							type="button"
							class="thing"
							{@attach dragTap({ enabled: () => !locked, home: () => 'pool', tap: () => play.add(item.id), drop: (zone) => drop(item.id, zone) })}
						>
							{#if thing}{@render thing(item)}{:else}
								{#if pic}<Sticker key={pic} size={34} alt="" />{/if}
								<span>{item.text}</span>
							{/if}
						</button>
					</li>
				{:else}
					<li class="done">Semua sudah diletak. Semak bila sedia.</li>
				{/each}
			</ul>
		</section>
		<Checks {tip} ready={play.full} dirty={play.slots.some(Boolean)} onreset={() => play.clear()} oncheck={() => p.onanswer?.(play.slots)} />
	{/if}
</div>

<style>
	.order-play {
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
	.thing {
		display: inline-flex;
		align-items: center;
		gap: 0.4rem;
		min-height: 2.9rem;
		max-width: 16rem;
		padding: 0.35rem 0.8rem;
		border: 0;
		border-radius: var(--r-md);
		background: #fff;
		color: var(--ink);
		font: 700 0.98rem/1.15 var(--font-body);
		text-align: left;
		box-shadow:
			0 4px 0 #e2d6c4,
			0 6px 12px rgb(31 45 39 / 0.08);
		cursor: grab;
		touch-action: none;
		transition: transform var(--t-state) var(--spring);
	}
	.thing:hover {
		transform: translateY(-2px);
	}
	.thing:global(.dragging) {
		z-index: 50;
		cursor: grabbing;
	}
	.done {
		color: var(--ink-2);
		font-weight: 800;
	}
</style>
