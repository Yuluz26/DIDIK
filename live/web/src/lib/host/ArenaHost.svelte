<!--
	The big screen for the 3D games everyone answers together (Litar Kart, Sepakan Penalti): the
	world fills most of the screen like a broadcast, and the question sits beside it, large enough to
	read across a classroom. On a narrower screen the question goes under the world.

	`scene` is the 3D world; `board` floats over its corner (the order, the score).
-->
<script lang="ts">
	import type { Snippet } from 'svelte';
	import type { RoomClient } from '$lib/room.svelte';
	import { play } from '$lib/sound';
	import Answer from '$lib/questions/Answer.svelte';
	import QuestionCard from '$lib/questions/QuestionCard.svelte';
	import Countdown from '$ui/Countdown.svelte';
	import Timer from '$ui/Timer.svelte';

	let {
		client,
		game,
		title,
		scene,
		board
	}: {
		client: RoomClient;
		// eslint-disable-next-line @typescript-eslint/no-explicit-any
		game: any;
		title: string;
		scene: Snippet;
		board?: Snippet;
	} = $props();

	const typed = $derived(game.question && !['single', 'multiple', 'truefalse'].includes(game.question.type));
	let lastStage = '';

	$effect(() => {
		const key = `${game.stage}:${game.index}`;
		if (key === lastStage) return;
		lastStage = key;
		if (game.stage === 'reveal') play('tiles');
		if (game.stage === 'question') play('pop');
	});
</script>

<div class="arena" class:revealing={game.stage === 'reveal'}>
	<section class="screen" aria-label="Dunia permainan">
		{@render scene()}
		{#if board}<div class="board">{@render board()}</div>{/if}
	</section>

	<div class="panel">
		{#if game.stage === 'intro'}
			<Countdown clock={game.clock} offset={client.offset} {title} />
		{:else if game.question}
			<div class="top">
				{#if game.stage === 'question'}
					<Timer clock={game.clock} offset={client.offset} total={game.question.timeLimit} ticks />
				{/if}
				<span class="count">{game.answeredCount}/{game.playerCount} sudah menjawab</span>
			</div>
			<QuestionCard question={game.question} index={game.index} total={game.total} big />
			{#if typed && game.stage === 'question'}
				<p class="device">Jawab di peranti kamu.</p>
			{:else}
				<div class="answers">
					<Answer question={game.question} disabled reveal={game.stage === 'reveal' ? game.reveal : null} stats={game.stage === 'reveal' ? game.stats : null} />
				</div>
			{/if}
			{#if game.stage === 'reveal'}
				<p class="tally">{game.correctCount} daripada {game.playerCount} menjawab betul.</p>
			{/if}
		{/if}
	</div>
</div>

<style>
	.arena {
		display: grid;
		gap: 1.2rem;
		grid-template-columns: minmax(0, 1fr);
	}
	.screen {
		position: relative;
		height: clamp(18rem, 52vh, 34rem);
		border-radius: var(--r-lg);
		overflow: hidden;
		background: var(--stage-bg, #13303d);
	}
	.board {
		position: absolute;
		top: 0.8rem;
		left: 0.8rem;
		pointer-events: none;
	}
	.panel {
		display: grid;
		gap: 0.8rem;
		align-content: start;
		min-width: 0;
	}
	.panel :global(.tile) {
		min-height: 3.4rem;
		padding-block: 0.5rem;
	}
	.panel :global(.tf .tile) {
		min-height: 4.6rem;
	}
	.top {
		display: flex;
		align-items: center;
		gap: 1rem;
	}
	.top :global(.timer) {
		flex: 1;
	}
	.count {
		flex: none;
		margin-left: auto;
		padding: 0.3rem 0.9rem;
		border-radius: var(--r-pill);
		background: var(--brand-soft);
		color: var(--on-brand-soft);
		font-weight: 800;
	}
	.device {
		padding: 1.2rem;
		border-radius: var(--r-lg);
		background: var(--card);
		box-shadow: var(--card-shadow);
		font: 600 1.5rem var(--font-display);
		text-align: center;
		color: var(--ink-2);
	}
	.tally {
		font: 600 1.3rem var(--font-display);
		text-align: center;
	}
	/* A laptop or projector: the world on the left, filling the height, the question on the right. */
	@media (min-width: 1100px) {
		.arena {
			grid-template-columns: minmax(0, 1.6fr) minmax(22rem, 1fr);
			align-items: start;
		}
		.screen {
			height: clamp(24rem, calc(100dvh - 9.5rem), 46rem);
			position: sticky;
			top: 5.2rem;
		}
	}
</style>
