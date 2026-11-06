<!--
	Art sheet for the subject games: every game with a made-up question, played for real in the page.
	"Semak" shows the answer the way a child sees it after answering. Not linked from the app.
-->
<script lang="ts">
	import Answer from '$lib/questions/Answer.svelte';
	import QuestionCard from '$lib/questions/QuestionCard.svelte';
	import { GAMES, SUBJECTS } from '$lib/subjects/games';
	import { EXAMPLES } from './examples';
	import { mock } from './mock';

	let subject = $state<string>('sains');
	let only = $state<string>('');
	// eslint-disable-next-line @typescript-eslint/no-explicit-any
	let answers = $state<Record<string, any>>({});
	const mocks = Object.fromEntries(Object.entries(EXAMPLES).map(([k, raw]) => [k, mock(raw)]));
	const shown = $derived(GAMES.filter((g) => g.subject === subject && (!only || g.key === only)));
</script>

<svelte:head><title>Gaya subjek · DIDIK Main Bersama</title></svelte:head>

<main class="wrap sheet">
	<nav class="tabs">
		{#each SUBJECTS as s (s.key)}
			<button type="button" class="btn" class:btn--sun={subject === s.key} onclick={() => ((subject = s.key), (only = ''))}>{s.name}</button>
		{/each}
	</nav>
	{#each shown as g (g.key)}
		{@const m = mocks[g.key]}
		<section id={g.key}>
			<h2>{g.title} <small>({g.types.join(', ')})</small> <button type="button" class="btn btn--plain" onclick={() => (only = only ? '' : g.key)}>{only ? 'Semua' : 'Fokus'}</button></h2>
			{#if m}
				<div class="card">
					<QuestionCard question={m.question} />
					{#if answers[g.key] === undefined}
						<Answer question={m.question} onanswer={(a) => (answers = { ...answers, [g.key]: a })} />
					{:else}
						<Answer question={m.question} disabled mine={answers[g.key]} reveal={m.reveal} onanswer={() => {}} />
						<button type="button" class="btn" onclick={() => (answers = { ...answers, [g.key]: undefined })}>Main semula</button>
					{/if}
				</div>
			{:else}
				<p>Tiada contoh.</p>
			{/if}
		</section>
	{/each}
</main>

<style>
	.sheet {
		display: grid;
		gap: 2rem;
		padding-block: 1.5rem 4rem;
		max-width: 46rem;
	}
	.tabs {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
	}
	h2 small {
		color: var(--ink-3);
		font-size: 0.8rem;
	}
	.card {
		display: grid;
		gap: 1rem;
		padding: 1rem;
		border-radius: var(--r-lg);
		background: var(--card);
		box-shadow: var(--card-shadow);
	}
</style>
