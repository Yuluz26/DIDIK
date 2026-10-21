<!--
	The big screen for games everyone answers together: the question large enough to read across a
	room, how many have answered, and after the reveal how many chose each option.
-->
<script lang="ts">
	import type { Snippet } from 'svelte';
	import type { RoomClient } from '$lib/room.svelte';
	import type { Person } from '$lib/types';
	import { play } from '$lib/sound';
	import Answer from '$lib/questions/Answer.svelte';
	import QuestionCard from '$lib/questions/QuestionCard.svelte';
	import Countdown from '$ui/Countdown.svelte';
	import Leaderboard from '$ui/Leaderboard.svelte';
	import Timer from '$ui/Timer.svelte';

	let {
		client,
		game,
		people,
		title,
		unit = 'mata',
		scene,
		side
	}: {
		client: RoomClient;
		// eslint-disable-next-line @typescript-eslint/no-explicit-any
		game: any;
		people: Map<string, Person>;
		title: string;
		unit?: string;
		scene?: Snippet;
		side?: Snippet;
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

<div class="stage">
	{#if game.stage === 'intro'}
		<Countdown clock={game.clock} offset={client.offset} title={title} />
	{:else if game.stage === 'standings'}
		<section class="standings">
			<h2>Kedudukan selepas soalan {game.index + 1}</h2>
			<Leaderboard rows={game.standings} {people} {unit} limit={5} />
		</section>
	{:else if game.question}
		<div class="layout" class:with-side={!!side}>
			<div class="q">
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
					<Answer question={game.question} disabled reveal={game.stage === 'reveal' ? game.reveal : null} stats={game.stage === 'reveal' ? game.stats : null} />
				{/if}
				{#if game.stage === 'reveal'}
					<p class="tally">{game.correctCount} daripada {game.playerCount} menjawab betul.</p>
				{/if}
			</div>
			{#if side}<div class="side">{@render side()}</div>{/if}
		</div>
		{@render scene?.()}
	{/if}
</div>

<style>
	.stage {
		display: grid;
		gap: 1.2rem;
	}
	.layout {
		display: grid;
		gap: 1.4rem;
	}
	.layout.with-side {
		grid-template-columns: minmax(0, 1fr) minmax(16rem, 22rem);
		align-items: start;
	}
	.q {
		display: grid;
		gap: 0.8rem;
		min-width: 0;
	}
	/* Shorter tiles on the big screen so the game's world stays in view on a laptop. */
	.q :global(.tile) {
		min-height: 3.5rem;
		padding-block: 0.55rem;
	}
	.q :global(.tf .tile) {
		min-height: 5rem;
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
		color: var(--brand-deep);
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
	.standings {
		display: grid;
		gap: 1rem;
		max-width: 40rem;
		width: 100%;
		margin: 1rem auto;
	}
	.standings h2 {
		font-size: var(--fs-h1);
		text-align: center;
	}
	@media (max-width: 980px) {
		.layout.with-side {
			grid-template-columns: minmax(0, 1fr);
		}
	}
</style>
