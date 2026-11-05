<!--
	Kira dan masukkan: a pile of objects and a basket (a box, a bus, a plate). Tap an object, or drag it,
	to put it in; tap one in the basket, or drag it out, to take it back. Semak sends how many are in.
	The number is never shown while answering: counting them is the point. Each object flies from where
	it was to where it lands.
-->
<script lang="ts">
	import { crossfade } from 'svelte/transition';
	import { backOut } from 'svelte/easing';
	import type { Reveal } from '$lib/types';
	import { play } from '$lib/sound';
	import { placeOf, stickerOf } from '$lib/stickers';
	import Icon from '$ui/Icon.svelte';
	import Sticker from '$ui/Sticker.svelte';
	import { dragTap, still } from './drag';

	let {
		sticker,
		place,
		supply,
		disabled = false,
		mine = undefined,
		reveal = null,
		onanswer
	}: {
		sticker: string;
		place: string;
		supply: number;
		disabled?: boolean;
		mine?: number;
		reveal?: Reveal | null;
		onanswer?: (answer: number) => void;
	} = $props();

	const ids = $derived(Array.from({ length: supply }, (_, i) => i));
	let inside = $state<number[]>([]);
	// once answered, the basket shows the answer that was given; on the host's screen at the reveal, the right number
	const shown = $derived(mine !== undefined ? ids.slice(0, Number(mine)) : reveal ? ids.slice(0, Number(reveal.correct)) : inside);
	const pile = $derived(ids.filter((id) => !shown.includes(id)));
	const locked = $derived(disabled || !!reveal || mine !== undefined);
	const what = $derived(stickerOf(sticker));
	const name = $derived(what?.name.toLowerCase() ?? 'objek');
	const where = $derived(placeOf(place));
	const right = $derived(reveal ? Number(reveal.correct) : null);
	const ok = $derived(right !== null && mine !== undefined && Number(mine) === right);

	const [send, receive] = crossfade({
		duration: (d) => (still() ? 0 : Math.min(460, 180 + Math.sqrt(d) * 14)),
		easing: backOut,
		fallback: (node) => ({ duration: still() ? 0 : 220, css: (t) => `opacity: ${t}; transform: scale(${0.6 + 0.4 * t})` })
	});

	function put(id: number) {
		// a quick second tap on the same spot lands on the object still flying away: take the next one
		if (inside.includes(id)) id = pile[0] ?? -1;
		if (locked || id < 0 || inside.includes(id)) return;
		play('pop');
		inside = [...inside, id];
	}

	function takeOut(id: number) {
		if (locked) return;
		play('tap');
		inside = inside.filter((x) => x !== id);
	}

	// a little tilt for each object, the same every time, so the pile looks tipped out by hand
	const tilt = (id: number) => `${((id * 37) % 13) - 6}deg`;
</script>

<div class="count">
	<div class="place" data-zone="in" class:ok={reveal && (ok || mine === undefined)} class:off={reveal && mine !== undefined && !ok}>
		<span class="place-art" aria-hidden="true"><Sticker key={place} size={76} alt="" /></span>
		<p class="place-label">
			<strong>{where.name}</strong>
			{#if !locked}<span>{shown.length ? 'Ketik untuk keluarkan' : 'Ketik atau seret ke sini'}</span>{/if}
		</p>
		<ul class="inside" aria-label="Dalam {where.name.toLowerCase()}">
			{#each shown as id (id)}
				<li in:receive={{ key: id }} out:send={{ key: id }}>
					<button
						type="button"
						class="obj"
						style:--tilt={tilt(id)}
						disabled={locked}
						aria-label="Keluarkan satu {name}"
						{@attach dragTap({ enabled: () => !locked, home: () => 'in', tap: () => takeOut(id), drop: (zone) => zone === 'pile' && takeOut(id) })}
					>
						<Sticker key={sticker} size={46} alt="" />
					</button>
				</li>
			{/each}
		</ul>
	</div>

	{#if !reveal && mine === undefined}
		<ul class="pile" data-zone="pile" aria-label="Ketik untuk masukkan">
			{#each pile as id (id)}
				<li in:receive={{ key: id }} out:send={{ key: id }}>
					<button
						type="button"
						class="obj"
						style:--tilt={tilt(id)}
						disabled={locked}
						aria-label="Masukkan satu {name}"
						{@attach dragTap({ enabled: () => !locked, home: () => 'pile', tap: () => put(id), drop: (zone) => zone === 'in' && put(id) })}
					>
						<Sticker key={sticker} size={52} alt="" />
					</button>
				</li>
			{/each}
		</ul>
		{#if !locked}
		<div class="row">
			<button type="button" class="btn btn--plain" disabled={!inside.length} onclick={() => ((inside = []), play('tap'))}>
				<Icon name="shuffle" /> Kosongkan
			</button>
			<button type="button" class="btn btn--big check" disabled={!inside.length} onclick={() => onanswer?.(inside.length)}>
				Semak <Icon name="check" />
			</button>
		</div>
		{/if}
	{/if}

	{#if right !== null}
		<div class="answer" class:ok={ok || mine === undefined}>
			<p>
				Jawapan betul: <strong>{right} {what?.unit ?? ''} {name}</strong>
				{#if mine !== undefined && !ok}<span class="mine">Kamu masukkan {mine}.</span>{/if}
			</p>
			<span class="row-of" aria-hidden="true">
				{#each Array.from({ length: right }, (_, i) => i) as i (i)}<span style:--i={i}><Sticker key={sticker} size={30} alt="" /></span>{/each}
			</span>
		</div>
	{/if}
</div>

<style>
	.count {
		display: grid;
		gap: 0.9rem;
	}
	.place {
		--tray: #fff4d9;
		position: relative;
		display: grid;
		grid-template-columns: auto minmax(0, 1fr);
		grid-template-areas: 'art label' 'items items';
		align-items: center;
		gap: 0.4rem 0.7rem;
		min-height: 9.5rem;
		padding: 0.7rem 0.8rem 0.9rem;
		border: 3px dashed #e9c77d;
		border-radius: var(--r-lg);
		background: var(--tray);
		transition:
			border-color var(--t-state),
			background-color var(--t-state),
			transform var(--t-state) var(--spring);
	}
	.place:global(.zone-hover) {
		border-style: solid;
		border-color: var(--sun-deep);
		background: #ffe9b0;
		transform: scale(1.02);
	}
	.place.ok {
		border-style: solid;
		border-color: var(--good);
		background: var(--good-soft);
	}
	.place.off {
		border-style: solid;
		border-color: var(--almost);
		background: var(--almost-soft);
	}
	.place-art {
		grid-area: art;
		filter: drop-shadow(0 4px 4px rgb(120 80 0 / 0.18));
	}
	.place-label {
		grid-area: label;
		display: grid;
		line-height: 1.2;
	}
	.place-label strong {
		font: 600 1.15rem var(--font-display);
	}
	.place-label span {
		color: var(--ink-2);
		font-size: 0.88rem;
		font-weight: 800;
	}
	.inside,
	.pile {
		display: flex;
		flex-wrap: wrap;
		justify-content: center;
		gap: 0.25rem;
		margin: 0;
		padding: 0;
		list-style: none;
	}
	.inside {
		grid-area: items;
		min-height: 3.2rem;
	}
	.pile {
		gap: 0.35rem;
		padding: 0.6rem;
		border-radius: var(--r-lg);
		background: color-mix(in srgb, var(--card) 70%, #e9f4ff);
		box-shadow: inset 0 2px 0 rgb(0 0 0 / 0.04);
	}
	.pile:global(.zone-hover) {
		outline: 3px dashed var(--sky);
		outline-offset: -3px;
	}
	.obj {
		display: grid;
		place-items: center;
		min-width: 2.9rem;
		min-height: 2.9rem;
		padding: 0.1rem;
		border: 0;
		border-radius: 0.9rem;
		background: none;
		cursor: grab;
		transform: rotate(var(--tilt));
		touch-action: none;
		transition: transform var(--t-state) var(--spring);
		filter: drop-shadow(0 3px 2px rgb(31 45 39 / 0.18));
	}
	.obj:not(:disabled):hover {
		transform: rotate(0deg) translateY(-3px) scale(1.08);
	}
	.obj:not(:disabled):active {
		transform: scale(0.92);
	}
	.obj:disabled {
		cursor: default;
	}
	.obj:global(.dragging) {
		position: relative;
		z-index: 50;
		cursor: grabbing;
		filter: drop-shadow(0 12px 10px rgb(31 45 39 / 0.3));
	}
	.obj:focus-visible {
		outline: 3px solid var(--sky);
		outline-offset: 2px;
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
	.answer {
		display: grid;
		gap: 0.4rem;
		padding: 0.7rem 0.9rem;
		border-radius: var(--r-md);
		background: var(--almost-soft);
		color: var(--on-almost-soft);
		font-weight: 800;
	}
	.answer.ok {
		background: var(--good-soft);
		color: var(--on-good-soft);
	}
	.mine {
		display: block;
		font-weight: 700;
	}
	.row-of {
		display: flex;
		flex-wrap: wrap;
		gap: 0.15rem;
	}
	.row-of span {
		animation: pop-in 360ms var(--spring) both;
		animation-delay: calc(var(--i) * 45ms);
	}
</style>
