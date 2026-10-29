<!--
	The question inside the game: a popup over the game's world, never a panel beside it.

	`modal` (the default): a dimmed scene and a card in the middle, shrunk to fit the screen so the whole
	question shows without scrolling (the scroll bar is hidden; a very small screen can still scroll).
	With `minimisable`, a button folds it into a small pill at the bottom, so the child can look at the
	world (or guess the picture) and open the question again; a new question opens it again.
	`float`: no dimming and no blocking, a compact card pinned to the top of the scene, for games where
	the answer is given in the world itself (Lompat!: tap a pad).
	`dock`: a compact card fixed to the bottom of the screen, with no dimming, for the result of a
	self-paced game: the world above stays playable, so what the answer earned can be spent there.
	The HUD at the top stays above it.
-->
<script lang="ts">
	import { tick, type Snippet } from 'svelte';
	import Icon from '$ui/Icon.svelte';

	let {
		label = 'Soalan',
		mode = 'modal',
		minimisable = false,
		key = '',
		height = $bindable(0),
		head,
		children
	}: {
		label?: string;
		mode?: 'modal' | 'float' | 'dock';
		minimisable?: boolean;
		/** Changes with every question, so a folded popup opens again for the next one. */
		key?: string | number;
		/** `float` only: the card's height, so the scene can keep its top clear. */
		height?: number;
		head?: Snippet;
		children: Snippet;
	} = $props();

	let folded = $state(false);
	let scrim = $state<HTMLElement>();
	let card = $state<HTMLElement>();
	let lastKey: string | number | undefined;

	$effect(() => {
		if (key !== lastKey) {
			lastKey = key;
			folded = false;
		}
	});

	/** Shrinks the card to fit the room it has (it is measured at full size first). */
	function fit() {
		if (!card || !scrim || mode !== 'modal') return;
		card.style.zoom = '1';
		const box = getComputedStyle(scrim);
		const roomH = scrim.clientHeight - parseFloat(box.paddingTop) - parseFloat(box.paddingBottom);
		const roomW = scrim.clientWidth - parseFloat(box.paddingLeft) - parseFloat(box.paddingRight);
		const k = Math.min(1, roomH / card.scrollHeight, roomW / card.offsetWidth);
		card.style.zoom = k < 1 ? String(Math.max(0.55, k)) : '';
	}
	const refit = () => requestAnimationFrame(() => requestAnimationFrame(fit));

	$effect(() => {
		if (!card) return;
		void tick().then(refit);
		// what the card holds changes as the child answers and the result comes in
		const watch = new ResizeObserver(refit);
		for (const child of card.children) watch.observe(child);
		const changes = new MutationObserver(refit);
		changes.observe(card, { childList: true, subtree: true });
		return () => {
			watch.disconnect();
			changes.disconnect();
		};
	});
</script>

<svelte:window onresize={refit} />

{#if mode === 'dock'}
	<section class="dock" aria-label={label} aria-live="polite">
		{#if head}<div class="head">{@render head()}</div>{/if}
		{@render children()}
	</section>
{:else if mode === 'float'}
	<section class="float" aria-label={label} aria-live="polite" bind:clientHeight={height}>
		{#if head}<div class="head">{@render head()}</div>{/if}
		{@render children()}
	</section>
{:else if folded}
	<button type="button" class="pill" onclick={() => (folded = false)}>
		<Icon name="next" /> Buka soalan
	</button>
{:else}
	<div class="scrim" bind:this={scrim}>
		<div class="card" role="dialog" aria-modal="false" aria-label={label} tabindex="-1" bind:this={card}>
			{#if head || minimisable}
				<div class="head">
					{@render head?.()}
					{#if minimisable}
						<button type="button" class="fold" onclick={() => (folded = true)}>Lihat permainan</button>
					{/if}
				</div>
			{/if}
			{@render children()}
		</div>
	</div>
{/if}

<style>
	.scrim {
		position: fixed;
		inset: 0;
		z-index: 15;
		display: grid;
		place-items: center;
		padding: calc(env(safe-area-inset-top, 0px) + 4.6rem) var(--gutter-r, 1rem) max(1rem, env(safe-area-inset-bottom, 0px)) var(--gutter, 1rem);
		background: rgb(12 24 30 / 0.42);
		overflow: auto;
		scrollbar-width: none;
		animation: fade-in 220ms ease-out both;
	}
	.scrim::-webkit-scrollbar {
		display: none;
	}
	.card {
		display: grid;
		gap: 0.9rem;
		width: min(46rem, 100%);
		padding: 1.1rem;
		border-radius: var(--r-lg);
		background: var(--paper, #fff);
		box-shadow:
			var(--card-shadow),
			0 1.4rem 3rem rgb(0 0 0 / 0.28);
		animation: pop-up 320ms var(--spring, cubic-bezier(0.2, 0.9, 0.3, 1.2)) both;
	}
	.card:focus {
		outline: none;
	}
	.head {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: 0.6rem;
	}
	.head > :global(:first-child) {
		flex: 1 1 12rem;
	}
	.fold {
		margin-left: auto;
		padding: 0.35rem 0.8rem;
		border: 2px solid var(--edge, transparent);
		border-radius: var(--r-pill);
		background: var(--card, #fff);
		color: var(--ink);
		font: 700 0.85rem var(--font-display);
		cursor: pointer;
	}
	.pill {
		position: fixed;
		left: 50%;
		bottom: max(1rem, env(safe-area-inset-bottom, 0px));
		z-index: 15;
		display: inline-flex;
		align-items: center;
		gap: 0.4rem;
		translate: -50% 0;
		padding: 0.75rem 1.3rem;
		border: 2px solid var(--edge, transparent);
		border-radius: var(--r-pill);
		background: var(--sun, #ffc23d);
		color: var(--ink);
		font: 700 1.05rem var(--font-display);
		box-shadow: 0 0.6rem 1.4rem rgb(0 0 0 / 0.3);
		cursor: pointer;
		animation: pop-up 320ms var(--spring, ease-out) both;
	}
	.dock {
		position: fixed;
		left: 50%;
		bottom: max(0.6rem, env(safe-area-inset-bottom, 0px));
		z-index: 15;
		display: grid;
		gap: 0.6rem;
		width: min(40rem, calc(100% - 1.2rem));
		max-height: 40dvh;
		overflow: auto;
		scrollbar-width: none;
		translate: -50% 0;
		padding: 0.8rem 0.9rem;
		border-radius: var(--r-lg);
		background: var(--paper, #fff);
		box-shadow:
			var(--card-shadow),
			0 -0.4rem 1.6rem rgb(0 0 0 / 0.22);
		animation: pop-up 320ms var(--spring, ease-out) both;
	}
	.dock::-webkit-scrollbar {
		display: none;
	}
	/* a smaller mascot and tighter words in the dock, so it stays a strip at the bottom */
	.dock :global(.feedback) {
		padding-block: 0.4rem;
	}
	.dock :global(.feedback .didi),
	.dock :global(.feedback > :first-child) {
		width: 52px;
		height: auto;
	}
	.float {
		position: absolute;
		left: 50%;
		top: 0.6rem;
		z-index: 6;
		display: grid;
		gap: 0.5rem;
		width: min(40rem, calc(100% - 1.2rem));
		translate: -50% 0;
		padding: 0.7rem 0.9rem;
		border-radius: var(--r-lg);
		background: color-mix(in srgb, var(--paper, #fff) 94%, transparent);
		box-shadow:
			var(--card-shadow),
			0 0.8rem 1.8rem rgb(0 0 0 / 0.25);
		pointer-events: none;
		animation: pop-up 320ms var(--spring, ease-out) both;
	}
	@keyframes fade-in {
		from {
			opacity: 0;
		}
	}
	@keyframes pop-up {
		from {
			opacity: 0;
			transform: translateY(0.8rem) scale(0.97);
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.scrim,
		.card,
		.pill,
		.dock,
		.float {
			animation: none;
		}
	}
</style>
