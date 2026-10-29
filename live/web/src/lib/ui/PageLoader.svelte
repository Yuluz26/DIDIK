<!--
	A small loader for a page change that takes a moment (the parents' pages, the front page): Didi's head
	hopping in a pill at the top of the screen, over a run of the brand's colours. It waits a quarter of a
	second before showing, so quick changes show nothing, and it never shows on the way into a game.
-->
<script lang="ts">
	import { navigating } from '$app/state';
	import { isGamePath } from './preloader';

	const DELAY = 250;
	let shown = $state(false);

	$effect(() => {
		const to = navigating.to?.url.pathname;
		if (!to || isGamePath(to)) {
			shown = false;
			return;
		}
		const timer = setTimeout(() => (shown = true), DELAY);
		return () => clearTimeout(timer);
	});
</script>

{#if shown}
	<div class="page-loader" role="status" aria-live="polite">
		<svg class="head" viewBox="0 0 64 64" width="30" height="30" aria-hidden="true" focusable="false">
			<path d="M15 27 C8 13 9 6 13 4 C18 3 24 12 27 20 Z" class="fur" />
			<path d="M49 27 C56 13 55 6 51 4 C46 3 40 12 37 20 Z" class="fur" />
			<ellipse cx="32" cy="35" rx="21" ry="19" class="fur" />
			<ellipse cx="32" cy="44" rx="11" ry="8" class="muzzle" />
			<ellipse cx="23.5" cy="33" rx="4.2" ry="4.8" class="eye" />
			<ellipse cx="40.5" cy="33" rx="4.2" ry="4.8" class="eye" />
			<ellipse cx="32" cy="40.5" rx="2.6" ry="1.9" class="eye" />
			<ellipse cx="16.5" cy="40" rx="3.4" ry="2.1" class="blush" />
			<ellipse cx="47.5" cy="40" rx="3.4" ry="2.1" class="blush" />
		</svg>
		<span class="words">Sebentar…</span>
		<span class="track" aria-hidden="true"><span></span></span>
	</div>
{/if}

<style>
	.page-loader {
		position: fixed;
		left: 50%;
		top: max(0.8rem, env(safe-area-inset-top));
		z-index: 9000;
		display: inline-flex;
		align-items: center;
		gap: 0.55rem;
		padding: 0.4rem 0.9rem 0.4rem 0.5rem;
		border: 2px solid var(--edge, #e4d8c2);
		border-radius: 999px;
		background: var(--paper);
		box-shadow: 0 0.5rem 1.2rem rgb(31 45 39 / 0.16);
		color: var(--ink);
		font: 600 0.95rem/1 var(--font-display);
		translate: -50% 0;
		animation: drop 300ms cubic-bezier(0.2, 0.9, 0.3, 1.2) both;
		pointer-events: none;
	}
	.head {
		overflow: visible;
		transform-origin: 50% 100%;
		animation: hop 0.8s cubic-bezier(0.3, 0, 0.3, 1) infinite;
	}
	.fur {
		fill: var(--didi-fur);
		stroke: #6b4a2e;
		stroke-width: 2;
		stroke-linejoin: round;
	}
	.muzzle {
		fill: var(--didi-belly);
	}
	.eye {
		fill: #2b2133;
	}
	.blush {
		fill: #f59aa5;
		opacity: 0.75;
	}
	.track {
		position: relative;
		width: 3.4rem;
		height: 0.45rem;
		overflow: hidden;
		border-radius: 999px;
		background: #efe3cb;
	}
	.track span {
		position: absolute;
		inset: 0 auto 0 0;
		width: 45%;
		border-radius: inherit;
		background: linear-gradient(90deg, var(--sun), var(--coral), var(--berry), var(--sea), var(--leaf));
		animation: run 1.2s cubic-bezier(0.6, 0, 0.4, 1) infinite;
	}
	@keyframes drop {
		from {
			opacity: 0;
			transform: translateY(-0.6rem);
		}
	}
	@keyframes hop {
		0%,
		100% {
			transform: translateY(0) scale(1.06, 0.92);
		}
		50% {
			transform: translateY(-0.35rem) scale(0.97, 1.04);
		}
	}
	@keyframes run {
		from {
			transform: translateX(-100%);
		}
		to {
			transform: translateX(230%);
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.page-loader,
		.head,
		.track span {
			animation: none;
		}
	}
</style>
