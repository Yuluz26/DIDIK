<!--
	A child's own island: twelve patches of sand. A right answer earns a shovel; tap a patch to dig
	it. What is found is decided on the server at the moment of digging.
-->
<script lang="ts">
	import { play } from '$lib/sound';
	import { confetti } from '$lib/confetti';
	import Loot from './Loot.svelte';
	import { LOOT_NAMES } from './loot';

	interface Found {
		found: string;
		amount: number;
		from?: string | null;
		tile?: number;
	}

	let {
		world,
		ondig
	}: {
		world: { island: number; tiles: { i: number; dug: Found | null }[]; last: Found | null; canDig: boolean };
		ondig: (tile: number) => void;
	} = $props();

	let digging = $state<number | null>(null);
	let fresh = $state<number | null>(null);

	function dig(tile: number) {
		if (!world.canDig || digging !== null) return;
		digging = tile;
		play('dig');
		ondig(tile);
	}

	$effect(() => {
		const last = world.last;
		if (!last || last.tile === undefined || last.tile !== digging) return;
		fresh = last.tile;
		digging = null;
		if (last.found === 'gem' || last.found === 'map' || last.found === 'chest') confetti({ count: 60 });
		play(last.amount < 0 ? 'almost' : last.found === 'parrot' ? 'steal' : 'coin');
		const timer = setTimeout(() => (fresh = null), 1600);
		return () => clearTimeout(timer);
	});
</script>

<figure class="island" class:dig-now={world.canDig}>
	<svg class="sea" viewBox="0 0 400 300" preserveAspectRatio="none" aria-hidden="true">
		<rect width="400" height="300" fill="#3ba7d9" />
		<path d="M20 40 q12 -6 24 0 M300 30 q12 -6 24 0 M340 260 q12 -6 24 0 M40 270 q12 -6 24 0" stroke="#9fd8f0" stroke-width="4" fill="none" stroke-linecap="round" />
		<path d="M60 70 Q200 10 340 60 Q400 150 340 240 Q200 300 60 240 Q0 150 60 70z" fill="#f6d58e" />
		<path d="M60 70 Q200 10 340 60 Q400 150 340 240 Q200 300 60 240 Q0 150 60 70z" fill="none" stroke="#fff" stroke-width="6" opacity=".6" />
		<path d="M352 70 q-4 -30 8 -52" stroke="#8e5a2e" stroke-width="6" fill="none" />
		<path d="M360 18 q-18 -4 -28 10 q14 -6 28 -10 q-2 -16 -18 -18 q12 6 18 18 q10 -14 26 -8 q-16 0 -26 8 q18 0 20 16 q-6 -12 -20 -16" fill="#4fa35b" />
	</svg>

	<div class="patches" role="group" aria-label="Petak pasir pulau {world.island}">
		{#each world.tiles as tile (tile.i)}
			<button
				type="button"
				class="patch"
				class:dug={!!tile.dug}
				class:fresh={fresh === tile.i}
				class:digging={digging === tile.i}
				style:--i={tile.i}
				disabled={!!tile.dug || !world.canDig}
				onclick={() => dig(tile.i)}
				aria-label={tile.dug ? `${LOOT_NAMES[tile.dug.found]} ${tile.dug.amount >= 0 ? '+' : ''}${tile.dug.amount}` : `Gali petak ${tile.i + 1}`}
			>
				{#if tile.dug}
					<span class="loot"><Loot kind={tile.dug.found} size={38} /></span>
					{#if tile.dug.amount}<span class="amount" class:minus={tile.dug.amount < 0}>{tile.dug.amount > 0 ? '+' : ''}{tile.dug.amount}</span>{/if}
				{:else}
					<svg viewBox="0 0 60 40" class="mound" aria-hidden="true">
						<ellipse cx="30" cy="30" rx="26" ry="9" fill="#e5c07a" />
						<ellipse cx="30" cy="26" rx="18" ry="9" fill="#f2d49b" />
						<path d="M24 16l12 12M36 16l-12 12" stroke="#c0503a" stroke-width="3.5" stroke-linecap="round" opacity=".75" />
					</svg>
				{/if}
			</button>
		{/each}
	</div>

	<figcaption class="tip">
		{#if world.canDig}
			<strong>Kamu dapat penyodok!</strong> Ketik satu tempat untuk menggali.
		{:else}
			Pulau {world.island} · jawab betul untuk dapat penyodok
		{/if}
	</figcaption>
</figure>

<style>
	.island {
		position: relative;
		margin: 0;
		border-radius: var(--r-lg);
		overflow: hidden;
		box-shadow: var(--card-shadow);
		aspect-ratio: 4 / 3;
		max-height: 70vh;
	}
	.sea {
		position: absolute;
		inset: 0;
		width: 100%;
		height: 100%;
	}
	.patches {
		position: absolute;
		inset: 20% 14% 18% 12%;
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		grid-template-rows: repeat(3, 1fr);
		gap: 4%;
	}
	.patch {
		position: relative;
		display: grid;
		place-items: center;
		padding: 0;
		border: 0;
		border-radius: 50%;
		background: transparent;
		cursor: pointer;
		transition: transform var(--t-state) var(--spring);
	}
	.patch:disabled {
		cursor: default;
	}
	.mound {
		width: 100%;
		height: auto;
		max-width: 5rem;
	}
	.dig-now .patch:not(.dug) {
		animation: bob 1.4s ease-in-out infinite;
		animation-delay: calc(var(--i) * 90ms);
	}
	.dig-now .patch:not(.dug):hover {
		transform: scale(1.15) rotate(-6deg);
	}
	.patch.digging {
		animation: wiggle 0.3s ease-in-out infinite;
	}
	.loot {
		display: grid;
		place-items: center;
	}
	.fresh .loot {
		animation: pop-in 600ms var(--spring);
	}
	.amount {
		position: absolute;
		top: -0.3rem;
		right: -0.2rem;
		padding: 0 0.35rem;
		border-radius: var(--r-pill);
		background: #fff;
		color: var(--good);
		font: 600 0.85rem var(--font-display);
	}
	.amount.minus {
		color: var(--almost);
	}
	.fresh .amount {
		animation: rise-in 500ms var(--spring);
	}
	.tip {
		position: absolute;
		left: 50%;
		bottom: 3%;
		translate: -50% 0;
		max-width: 92%;
		padding: 0.35rem 0.9rem;
		border-radius: var(--r-pill);
		background: rgb(255 255 255 / 0.92);
		font-weight: 700;
		font-size: 0.92rem;
		text-align: center;
		width: max-content;
		line-height: 1.25;
	}
	.dig-now .tip {
		background: var(--sun);
	}
</style>
