<!--
	Isih kumpulan: things to put into two or three baskets (Darat and Laut, Buah and Sayur). Tap a thing to
	pick it up, then tap a basket; or drag it straight in. Tap a thing in a basket to take it back out.
	Semak sends where everything went once nothing is left over.
-->
<script lang="ts">
	import { crossfade } from 'svelte/transition';
	import { backOut } from 'svelte/easing';
	import type { Reveal } from '$lib/types';
	import { play } from '$lib/sound';
	import Icon from '$ui/Icon.svelte';
	import Sticker from '$ui/Sticker.svelte';
	import { dragTap, still } from './drag';

	interface Group {
		id: string;
		name: string;
		sticker?: string | null;
	}
	interface Thing {
		id: string;
		text: string;
		sticker?: string | null;
	}

	let {
		groups,
		items,
		disabled = false,
		mine = undefined,
		reveal = null,
		onanswer
	}: {
		groups: Group[];
		items: Thing[];
		disabled?: boolean;
		mine?: Record<string, string>;
		reveal?: Reveal | null;
		onanswer?: (answer: Record<string, string>) => void;
	} = $props();

	let placed = $state<Record<string, string>>({});
	let picked = $state<string | null>(null);
	const locked = $derived(disabled || !!reveal || mine !== undefined);
	const correct = $derived<Record<string, string>>(reveal ? reveal.correct : {});
	// on the host's screen the answer shows as everything in its right basket
	const shown = $derived<Record<string, string>>(mine ?? (reveal ? correct : placed));
	const pool = $derived(items.filter((i) => !shown[i.id]));
	const done = $derived(items.every((i) => placed[i.id]));
	const groupName = $derived(new Map(groups.map((g) => [g.id, g.name])));

	const [send, receive] = crossfade({
		duration: (d) => (still() ? 0 : Math.min(440, 200 + Math.sqrt(d) * 10)),
		easing: backOut,
		fallback: (node) => ({ duration: still() ? 0 : 200, css: (t) => `opacity: ${t}; transform: scale(${0.6 + 0.4 * t})` })
	});

	function place(item: string, group: string) {
		if (locked) return;
		play('pop');
		placed = { ...placed, [item]: group };
		picked = null;
	}

	function unplace(item: string) {
		if (locked) return;
		play('tap');
		const { [item]: _, ...rest } = placed;
		placed = rest;
	}

	function pick(item: string) {
		if (locked) return;
		play('tap');
		picked = picked === item ? null : item;
	}

	function dropTo(item: string, zone: string) {
		if (zone === 'pool') unplace(item);
		else if (zone.startsWith('g-')) place(item, zone.slice(2));
	}

	const TINTS = ['#ffe3ec', '#dff4ff', '#e6f8d8'];
	const EDGES = ['#f2a7bf', '#8fc8ec', '#9fd27a'];
</script>

{#snippet card(item: Thing, small: boolean)}
	{#if item.sticker}<Sticker key={item.sticker} size={small ? 34 : 50} alt="" />{/if}
	<span class="label">{item.text}</span>
{/snippet}

<div class="sort" class:picking={!!picked}>
	<div class="baskets" style:--n={groups.length}>
		{#each groups as group, g (group.id)}
			<!-- svelte-ignore a11y_click_events_have_key_events, a11y_no_static_element_interactions -->
			<div
				class="basket"
				data-zone="g-{group.id}"
				style:--tint={TINTS[g % 3]}
				style:--edge-c={EDGES[g % 3]}
				onclick={(event) => picked && !(event.target as HTMLElement).closest('.thing') && place(picked, group.id)}
			>
				<button type="button" class="head" disabled={locked || !picked} onclick={() => picked && place(picked, group.id)} aria-label={picked ? `Masukkan ke ${group.name}` : group.name}>
					{#if group.sticker}<Sticker key={group.sticker} size={40} alt="" />{/if}
					<span>{group.name}</span>
				</button>
				<ul class="inside">
					{#each items.filter((i) => shown[i.id] === group.id) as item (item.id)}
						{@const ok = reveal && correct[item.id] === group.id}
						<li in:receive={{ key: item.id }} out:send={{ key: item.id }}>
							<button
								type="button"
								class="thing small"
								class:ok
								class:off={reveal && !ok}
								disabled={locked}
								aria-label="{item.text} dalam {group.name}. Ketik untuk keluarkan"
								{@attach dragTap({ enabled: () => !locked, home: () => `g-${group.id}`, tap: () => unplace(item.id), drop: (zone) => dropTo(item.id, zone) })}
							>
								{@render card(item, true)}
								{#if reveal}
									<span class="mark"><Icon name={ok ? 'check' : 'close'} size={14} /></span>
								{/if}
							</button>
							{#if reveal && !ok}<span class="should">→ {groupName.get(correct[item.id])}</span>{/if}
						</li>
					{/each}
				</ul>
			</div>
		{/each}
	</div>

	{#if !reveal && mine === undefined}
		{#if !locked}<p class="tip" aria-live="polite">{picked ? 'Sekarang ketik bakul yang betul.' : pool.length ? 'Ketik satu benda, kemudian ketik bakulnya. Atau seret terus.' : 'Semua sudah diisih!'}</p>{/if}
		<ul class="pool" data-zone="pool" aria-label="Benda untuk diisih">
			{#each pool as item, i (item.id)}
				<li in:receive={{ key: item.id }} out:send={{ key: item.id }} style:--i={i}>
					<button
						type="button"
						class="thing"
						disabled={locked}
						class:picked={picked === item.id}
						aria-pressed={picked === item.id}
						{@attach dragTap({ enabled: () => !locked, home: () => 'pool', tap: () => pick(item.id), drop: (zone) => dropTo(item.id, zone) })}
					>
						{@render card(item, false)}
					</button>
				</li>
			{/each}
		</ul>
		{#if !locked}
		<div class="row">
			<button type="button" class="btn btn--plain" disabled={!Object.keys(placed).length} onclick={() => ((placed = {}), (picked = null), play('tap'))}>
				<Icon name="shuffle" /> Mula semula
			</button>
			<button type="button" class="btn btn--big check" disabled={!done} onclick={() => onanswer?.(placed)}>
				Semak <Icon name="check" />
			</button>
		</div>
		{/if}
	{/if}
</div>

<style>
	.sort {
		display: grid;
		gap: 0.8rem;
	}
	.baskets {
		display: grid;
		grid-template-columns: repeat(var(--n), minmax(0, 1fr));
		gap: 0.55rem;
	}
	.basket {
		display: grid;
		grid-template-rows: auto 1fr;
		gap: 0.4rem;
		min-width: 0;
		min-height: 9rem;
		padding: 0.45rem;
		border: 3px dashed var(--edge-c);
		border-radius: var(--r-lg);
		background: var(--tint);
		transition:
			transform var(--t-state) var(--spring),
			border-color var(--t-state),
			box-shadow var(--t-state);
	}
	.picking .basket {
		border-style: solid;
		cursor: pointer;
		animation: wiggle-soft 1.4s ease-in-out infinite;
	}
	.basket:global(.zone-hover) {
		border-style: solid;
		transform: scale(1.03);
		box-shadow: 0 0 0 4px color-mix(in srgb, var(--edge-c) 45%, transparent);
	}
	.head {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 0.15rem;
		min-height: 2.75rem;
		padding: 0.3rem;
		border: 0;
		border-radius: var(--r-md);
		background: rgb(255 255 255 / 0.7);
		color: var(--ink);
		font: 600 clamp(0.95rem, 0.85rem + 0.5vw, 1.15rem) / 1.1 var(--font-display);
		text-align: center;
		overflow-wrap: anywhere;
	}
	.head:disabled {
		cursor: inherit;
	}
	.inside,
	.pool {
		display: flex;
		flex-wrap: wrap;
		align-content: flex-start;
		justify-content: center;
		gap: 0.35rem;
		margin: 0;
		padding: 0;
		list-style: none;
	}
	.inside li {
		display: grid;
		justify-items: center;
	}
	.pool {
		gap: 0.5rem;
		min-height: 4.5rem;
		padding: 0.5rem;
		border-radius: var(--r-lg);
	}
	.pool:global(.zone-hover) {
		outline: 3px dashed var(--sky);
		outline-offset: -3px;
	}
	.thing {
		position: relative;
		display: grid;
		justify-items: center;
		gap: 0.2rem;
		min-width: 5rem;
		max-width: 8rem;
		padding: 0.45rem 0.55rem 0.4rem;
		border: 0;
		border-radius: var(--r-md);
		background: var(--card);
		color: var(--ink);
		font: 700 0.95rem/1.15 var(--font-body);
		text-align: center;
		box-shadow:
			0 4px 0 #e2d6c4,
			0 6px 12px rgb(31 45 39 / 0.08);
		cursor: grab;
		touch-action: none;
		transition:
			transform var(--t-state) var(--spring),
			box-shadow var(--t-press);
	}
	.thing.small {
		min-width: 0;
		max-width: 100%;
		padding: 0.3rem 0.4rem;
		font-size: 0.8rem;
		box-shadow: 0 3px 0 #e2d6c4;
	}
	.thing:not(:disabled):hover {
		transform: translateY(-3px);
	}
	.thing:disabled {
		cursor: default;
	}
	.thing.picked {
		transform: translateY(-6px) rotate(-3deg) scale(1.06);
		outline: 4px solid var(--berry);
		outline-offset: 2px;
		box-shadow: 0 12px 16px rgb(31 45 39 / 0.18);
	}
	.thing:focus-visible {
		outline: 3px solid var(--sky);
		outline-offset: 2px;
	}
	.thing:global(.dragging) {
		z-index: 50;
		cursor: grabbing;
	}
	.thing.ok {
		box-shadow: 0 0 0 3px var(--good);
	}
	.thing.off {
		box-shadow: 0 0 0 3px var(--almost);
	}
	.label {
		overflow-wrap: anywhere;
	}
	.mark {
		position: absolute;
		top: -0.45rem;
		right: -0.45rem;
		display: grid;
		place-items: center;
		width: 1.4rem;
		height: 1.4rem;
		border-radius: 50%;
		background: var(--good);
		color: #fff;
	}
	.thing.off .mark {
		background: var(--almost);
	}
	.should {
		color: var(--on-almost-soft);
		font-size: 0.78rem;
		font-weight: 800;
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
	}
	.check {
		flex: 1;
		max-width: 16rem;
		margin-left: auto;
	}
	@keyframes wiggle-soft {
		25% {
			transform: rotate(-0.8deg);
		}
		75% {
			transform: rotate(0.8deg);
		}
	}
	@media (max-width: 420px) {
		.thing {
			min-width: 4.4rem;
			font-size: 0.88rem;
		}
	}
</style>
