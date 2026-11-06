<!--
	A question played as one of the subject games: loads the game (once per game, then it is cached) and
	hands it the question. While it loads, a soft placeholder keeps its room. A game that cannot be loaded
	(an old copy of the app, a dropped connection) falls back to the plain way of answering.
-->
<script lang="ts">
	import type { Snippet } from 'svelte';
	import { gameOf, loaderOf } from './games';
	import type { GameProps } from './kit.svelte';
	import Sticker from '$ui/Sticker.svelte';

	let { plain, ...props }: GameProps & { plain: Snippet } = $props();

	const info = $derived(gameOf(props.question.game));
	const loading = $derived(info ? loaderOf(info.key)?.() : undefined);
</script>

{#if info && loading}
	{#await loading}
		<div class="loading" aria-busy="true">
			<Sticker key={info.icon} size={56} alt="" eager />
			<span>Menyediakan {info.title}…</span>
		</div>
	{:then mod}
		{@const Game = mod.default}
		<div class="game-wrap" data-game={info.key}>
			<Game {...props} />
		</div>
	{:catch}
		{@render plain()}
	{/await}
{:else}
	{@render plain()}
{/if}

<style>
	.loading {
		display: grid;
		justify-items: center;
		gap: 0.4rem;
		min-height: 14rem;
		align-content: center;
		color: var(--ink-2);
		font-weight: 800;
	}
	.loading :global(img) {
		animation: bob 1.2s ease-in-out infinite;
	}
	.game-wrap {
		display: grid;
		gap: 0.8rem;
	}
	@keyframes bob {
		50% {
			transform: translateY(-6px);
		}
	}
</style>
