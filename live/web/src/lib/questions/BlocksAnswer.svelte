<!--
	Bina nombor: build a number with base-ten blocks. A place-value mat with a column for each place
	(ratus, puluh, sa); tap a block in the supply to add it to its column (or drag it there), tap a block
	on the mat to take it away. Each column holds up to nine, and shows its digit underneath, as a
	place-value chart does. Semak sends how many of each.
-->
<script lang="ts">
	import { scale } from 'svelte/transition';
	import { backOut } from 'svelte/easing';
	import type { Reveal } from '$lib/types';
	import { play } from '$lib/sound';
	import Icon from '$ui/Icon.svelte';
	import { dragTap, still } from './drag';

	let {
		places,
		disabled = false,
		mine = undefined,
		reveal = null,
		onanswer
	}: {
		places: string[];
		disabled?: boolean;
		mine?: Record<string, number>;
		reveal?: Reveal | null;
		onanswer?: (answer: Record<string, number>) => void;
	} = $props();

	const NAME: Record<string, string> = { ratus: 'Ratus', puluh: 'Puluh', sa: 'Sa' };
	const TINT: Record<string, string> = { ratus: '#ffb3c7', puluh: '#9fd0ff', sa: '#ffe08a' };
	const EDGE: Record<string, string> = { ratus: '#e07a9a', puluh: '#5d8fe0', sa: '#e0a92b' };

	let built = $state<Record<string, number>>({ ratus: 0, puluh: 0, sa: 0 });
	const shown = $derived<Record<string, number>>(mine ?? (reveal ? (reveal.correct as Record<string, number>) : built));
	const locked = $derived(disabled || !!reveal || mine !== undefined);
	const total = $derived(places.reduce((sum, p) => sum + (built[p] ?? 0), 0));
	const right = $derived<Record<string, number>>(reveal ? reveal.correct : {});
	const ok = (p: string) => reveal && (shown[p] ?? 0) === (right[p] ?? 0);

	function add(place: string) {
		if (locked || (built[place] ?? 0) >= 9) return;
		play('pop');
		built = { ...built, [place]: (built[place] ?? 0) + 1 };
	}

	function remove(place: string) {
		if (locked || !(built[place] ?? 0)) return;
		play('tap');
		built = { ...built, [place]: built[place] - 1 };
	}

	const pop = { start: 0.3, duration: still() ? 0 : 320, easing: backOut };
</script>

{#snippet block(place: string)}
	{#if place === 'ratus'}
		<span class="flat" aria-hidden="true">{#each Array.from({ length: 100 }, (_, i) => i) as i (i)}<i></i>{/each}</span>
	{:else if place === 'puluh'}
		<span class="rod" aria-hidden="true">{#each Array.from({ length: 10 }, (_, i) => i) as i (i)}<i></i>{/each}</span>
	{:else}
		<span class="cube" aria-hidden="true"></span>
	{/if}
{/snippet}

<div class="blocks">
	<div class="mat" style:--cols={places.length}>
		{#each places as place (place)}
			<div class="col" data-zone="col-{place}" style:--tint={TINT[place]} style:--edge-c={EDGE[place]} class:ok={reveal && ok(place)} class:off={reveal && mine !== undefined && !ok(place)}>
				<p class="name">{NAME[place]}</p>
				<div class="stack {place}">
					{#each Array.from({ length: shown[place] ?? 0 }, (_, i) => i) as i (i)}
						<button
							type="button"
							class="piece"
							in:scale={pop}
							disabled={locked}
							aria-label="Buang satu blok {NAME[place].toLowerCase()}"
							onclick={() => remove(place)}
						>
							{@render block(place)}
						</button>
					{/each}
				</div>
				<p class="digit" aria-label="{shown[place] ?? 0} {NAME[place].toLowerCase()}">{shown[place] ?? 0}</p>
			</div>
		{/each}
	</div>

	{#if !reveal && mine === undefined}
		<div class="supply" aria-label="Ambil blok">
			{#each places as place (place)}
				<button
					type="button"
					class="take"
					style:--tint={TINT[place]}
					style:--edge-c={EDGE[place]}
					disabled={locked || (built[place] ?? 0) >= 9}
					aria-label="Tambah satu blok {NAME[place].toLowerCase()}"
					{@attach dragTap({ enabled: () => !locked, tap: () => add(place), drop: (zone) => zone === `col-${place}` && add(place) })}
				>
					{@render block(place)}
					<span class="take-name">+1 {NAME[place].toLowerCase()}</span>
				</button>
			{/each}
		</div>
		{#if !locked}
			<div class="row">
				<button type="button" class="btn btn--plain" disabled={!total} onclick={() => ((built = { ratus: 0, puluh: 0, sa: 0 }), play('tap'))}>
					<Icon name="shuffle" /> Kosongkan
				</button>
				<button type="button" class="btn btn--big check" disabled={!total} onclick={() => onanswer?.(Object.fromEntries(places.map((p) => [p, built[p] ?? 0])))}>
					Semak <Icon name="check" />
				</button>
			</div>
		{/if}
	{/if}

	{#if reveal && reveal.number !== undefined}
		<p class="answer" class:ok={places.every((p) => ok(p))}>
			{reveal.number} = {places.map((p) => `${right[p] ?? 0} ${NAME[p].toLowerCase()}`).join(' + ')}
		</p>
	{/if}
</div>

<style>
	.blocks {
		display: grid;
		gap: 0.8rem;
	}
	.mat {
		display: grid;
		grid-template-columns: repeat(var(--cols), minmax(0, 1fr));
		gap: 0.5rem;
	}
	.col {
		display: grid;
		grid-template-rows: auto 1fr auto;
		gap: 0.35rem;
		min-height: 11rem;
		padding: 0.45rem;
		border: 3px dashed var(--edge-c);
		border-radius: var(--r-lg);
		background: color-mix(in srgb, var(--tint) 22%, #fff);
		transition: transform var(--t-state) var(--spring);
	}
	.col:global(.zone-hover) {
		border-style: solid;
		transform: scale(1.03);
	}
	.col.ok {
		border-style: solid;
		border-color: var(--good);
	}
	.col.off {
		border-style: solid;
		border-color: var(--almost);
	}
	.name {
		font: 600 1rem var(--font-display);
		text-align: center;
	}
	.stack {
		display: flex;
		flex-wrap: wrap;
		align-content: flex-end;
		justify-content: center;
		gap: 3px;
	}
	/* tens lie flat, one above the other, like a ladder of ten-rods */
	.stack.puluh {
		flex-direction: column-reverse;
		flex-wrap: nowrap;
		justify-content: flex-start;
	}
	.stack.puluh .piece {
		width: 100%;
	}
	.digit {
		justify-self: center;
		min-width: 2.6rem;
		padding: 0.1rem 0.6rem;
		border-radius: 999px;
		background: #fff;
		font: 600 1.6rem var(--font-display);
		text-align: center;
		box-shadow: 0 3px 0 var(--edge-c);
	}
	.piece,
	.take {
		padding: 0;
		border: 0;
		background: none;
		cursor: pointer;
		touch-action: none;
	}
	.piece:disabled {
		cursor: default;
	}
	.cube {
		display: block;
		width: 1.15rem;
		height: 1.15rem;
		border-radius: 3px;
		background: #ffd36b;
		box-shadow:
			inset 0 -3px 0 #d99a12,
			inset 0 2px 0 rgb(255 255 255 / 0.6);
	}
	.rod {
		display: grid;
		grid-template-columns: repeat(10, 1fr);
		gap: 1px;
		width: 100%;
		min-width: 5rem;
		height: 0.95rem;
		padding: 1px;
		border-radius: 3px;
		background: #5d8fe0;
	}
	.rod i {
		border-radius: 2px;
		background: #9fd0ff;
	}
	.flat {
		display: grid;
		grid-template-columns: repeat(10, 1fr);
		gap: 1px;
		width: 2.6rem;
		height: 2.6rem;
		padding: 1px;
		border-radius: 4px;
		background: #e07a9a;
	}
	.flat i {
		border-radius: 1px;
		background: #ffc2d4;
	}
	.supply {
		display: flex;
		flex-wrap: wrap;
		align-items: flex-end;
		justify-content: center;
		gap: 0.8rem;
		padding: 0.6rem;
		border-radius: var(--r-lg);
		background: #f6f2ff;
	}
	.take {
		display: grid;
		justify-items: center;
		gap: 0.3rem;
		padding: 0.4rem 0.6rem;
		border-radius: var(--r-md);
		background: #fff;
		box-shadow: 0 4px 0 var(--edge-c);
		transition: transform var(--t-state) var(--spring);
	}
	.take .rod {
		width: 6rem;
	}
	.take .flat {
		width: 3.4rem;
		height: 3.4rem;
	}
	.take:not(:disabled):hover {
		transform: translateY(-3px);
	}
	.take:disabled {
		opacity: 0.45;
		cursor: default;
	}
	.take:global(.dragging) {
		z-index: 50;
	}
	.take-name {
		font-size: 0.8rem;
		font-weight: 800;
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
</style>
