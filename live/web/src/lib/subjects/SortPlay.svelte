<!--
	Sorting things into groups, for the games that are an "Isih kumpulan" question: the things in a pile,
	the groups on the game's own board (`board`: a magnet and a tray, glass jars, museum cases, the pans of
	a scale). Tap a thing to pick it up and then tap its group, or drag it straight in; tap a thing in a
	group to take it back out. Semak once nothing is left over.
-->
<script lang="ts" module>
	export interface SortThing {
		id: string;
		text: string;
		sticker?: string | null;
	}
	export interface SortView {
		groups: { id: string; name: string; sticker: string | null }[];
		/** The things in a group (the child's, or once answered, theirs or the right ones). */
		inside: (group: string) => SortThing[];
		ok: (item: string) => boolean | null;
		/** The right group's name for a thing put in the wrong one, once shown. */
		should: (item: string) => string | null;
		locked: boolean;
		picked: string | null;
		zone: (group: string) => string;
		/** Tapping a group: puts the picked-up thing in it. */
		tapGroup: (group: string) => void;
		/** The attachment that makes a thing in a group movable. */
		grab: (item: string, group: string) => (node: HTMLElement) => void;
		allRight: boolean;
		sticker: (item: SortThing) => string | undefined;
	}
</script>

<script lang="ts">
	import type { Snippet } from 'svelte';
	import { crossfade } from 'svelte/transition';
	import { backOut } from 'svelte/easing';
	import { dragTap, still } from '$lib/questions/drag';
	import Sticker from '$ui/Sticker.svelte';
	import Checks from './Checks.svelte';
	import { type GameProps, Pairs, isLocked, rightOf, shown, stickerFor } from './kit.svelte';

	let {
		p,
		board,
		pool = 'Isih ini',
		tip,
		card
	}: { p: GameProps; board: Snippet<[SortView]>; pool?: string; tip?: string; card?: Snippet<[SortThing]> } = $props();

	const groups = $derived(p.question.groups ?? []);
	const items = $derived((p.question.items ?? []) as SortThing[]);
	const pairs = new Pairs(false);
	const locked = $derived(isLocked(p));
	const map = $derived(shown<Record<string, string>>(p, pairs.map));
	const right = $derived(rightOf<Record<string, string>>(p));
	const names = $derived(new Map(groups.map((g) => [g.id, g.name])));
	const left = $derived(items.filter((i) => !map[i.id]));
	const sticker = (item: SortThing) => item.sticker ?? stickerFor(item.text);

	function drop(item: string, zone: string) {
		if (zone.startsWith('g-')) pairs.set(item, zone.slice(2));
		else if (zone === 'pool' && pairs.map[item]) pairs.unset(item);
	}

	const view: SortView = $derived({
		groups,
		inside: (g) => items.filter((i) => map[i.id] === g),
		ok: (item) => (right ? right[item] === map[item] : null),
		should: (item) => (right && right[item] !== map[item] ? (names.get(right[item]) ?? null) : null),
		locked,
		picked: pairs.picked,
		zone: (g) => `g-${g}`,
		tapGroup: (g) => {
			if (!locked && pairs.picked) pairs.set(pairs.picked, g);
		},
		grab: (item, g) => dragTap({ enabled: () => !locked, home: () => `g-${g}`, tap: () => pairs.unset(item), drop: (zone) => drop(item, zone) }),
		allRight: !!right && items.every((i) => right[i.id] === map[i.id]),
		sticker
	});

	const [send, receive] = crossfade({ duration: () => (still() ? 0 : 320), easing: backOut });
</script>

<div class="sort-play" class:picking={!!pairs.picked}>
	{@render board(view)}

	{#if !locked}
		<section class="pool" data-zone="pool" aria-label={pool}>
			<h3>{pool}</h3>
			<ul>
				{#each left as item (item.id)}
					{@const pic = sticker(item)}
					<li in:receive={{ key: item.id }} out:send={{ key: item.id }}>
						<button
							type="button"
							class="thing"
							class:picked={pairs.picked === item.id}
							aria-pressed={pairs.picked === item.id}
							{@attach dragTap({ enabled: () => !locked, home: () => 'pool', tap: () => pairs.pick(item.id), drop: (zone) => drop(item.id, zone) })}
						>
							{#if card}{@render card(item)}{:else}
								{#if pic}<Sticker key={pic} size={40} alt="" />{/if}
								<span>{item.text}</span>
							{/if}
						</button>
					</li>
				{:else}
					<li class="done">Semua sudah diisih. Semak bila sedia.</li>
				{/each}
			</ul>
		</section>
		<Checks
			tip={pairs.picked ? 'Sekarang ketik tempatnya.' : (tip ?? 'Ketik satu, kemudian ketik tempatnya. Atau seret terus.')}
			ready={left.length === 0}
			dirty={pairs.count() > 0}
			onreset={() => pairs.clear()}
			oncheck={() => p.onanswer?.(pairs.map)}
		/>
	{/if}
</div>

<style>
	.sort-play {
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
		max-width: 15rem;
		padding: 0.35rem 0.8rem;
		border: 0;
		border-radius: var(--r-md);
		background: #fff;
		color: var(--ink);
		font: 700 0.98rem/1.15 var(--font-body);
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
	.thing.picked {
		transform: translateY(-5px) rotate(-2deg) scale(1.05);
		outline: 3px solid var(--berry, #e0457b);
		outline-offset: 2px;
	}
	.thing:global(.dragging) {
		z-index: 50;
		cursor: grabbing;
	}
	.done {
		color: var(--ink-2);
		font-weight: 800;
	}
	.picking :global([data-zone^='g-']) {
		cursor: pointer;
	}
</style>
