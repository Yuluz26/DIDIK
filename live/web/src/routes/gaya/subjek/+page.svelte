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

	import { page } from '$app/state';
	import { gameOf } from '$lib/subjects/games';
	import type { PublicQuestion, Reveal } from '$lib/types';

	// ?g=teropong shows one game alone; &state=right | wrong | host shows it answered (rightly, wrongly)
	// or as the host sees the answer. Used for the screenshots in docs/interactive-revamp.
	const asked = page.url.searchParams.get('g') ?? '';
	const stateAsked = page.url.searchParams.get('state') ?? '';
	let subject = $state<string>(gameOf(asked)?.subject ?? 'sains');
	const first = gameOf(asked) ? asked : '';
	let only = $state<string>(first);
	const mocks = Object.fromEntries(Object.entries(EXAMPLES).map(([k, raw]) => [k, mock(raw)]));

	/** An answer that is certainly wrong, of the shape the question's type sends. */
	// eslint-disable-next-line @typescript-eslint/no-explicit-any
	function wrongOf(q: PublicQuestion, reveal: Reveal): any {
		// eslint-disable-next-line @typescript-eslint/no-explicit-any
		const c = reveal.correct as any;
		const rotate = (map: Record<string, string>) => {
			const keys = Object.keys(map);
			return Object.fromEntries(keys.map((k, i) => [k, map[keys[(i + 1) % keys.length]]]));
		};
		switch (q.type) {
			case 'single':
				return q.choices?.find((x) => !c.includes(x.id))?.id;
			case 'multiple':
				return [q.choices?.find((x) => !c.includes(x.id))?.id, c[0]].filter(Boolean);
			case 'truefalse':
				return !c;
			case 'text':
				return 'entah';
			case 'number':
				return Number(c) + (q.unit === 'ml' ? 100 : 3);
			case 'order':
				return [...c].reverse();
			case 'blank':
				return [...c].reverse().map((w: string, i: number) => (c.length === 1 ? (q.bank?.find((b) => b !== w) ?? 'x') : w));
			case 'money':
				return { '100': 1 };
			default:
				return rotate(c);
		}
	}
	/** The right answer in the shape the type sends (money is paid in notes and coins, not as a number). */
	function rightOf(q: PublicQuestion, reveal: Reveal): unknown {
		// one choice is sent as its id alone, not as a list
		if (q.type === 'single') return (reveal.correct as string[])[0];
		if (q.type !== 'money') return reveal.correct;
		let left = Number(reveal.correct);
		const pay: Record<string, number> = {};
		for (const m of [...(q.money ?? [])].sort((x, y) => y - x)) {
			const n = Math.floor(left / m);
			if (n) pay[String(m)] = n;
			left -= n * m;
		}
		return pay;
	}
	// eslint-disable-next-line @typescript-eslint/no-explicit-any
	let answers = $state<Record<string, any>>(
		first && (stateAsked === 'right' || stateAsked === 'wrong') && mocks[first]
			? { [first]: stateAsked === 'right' ? rightOf(mocks[first].question, mocks[first].reveal) : wrongOf(mocks[first].question, mocks[first].reveal) }
			: {}
	);
	const shown = $derived(GAMES.filter((g) => g.subject === subject && (!only || g.key === only)));
</script>

<svelte:head><title>Gaya subjek · DIDIK Main Bersama</title></svelte:head>

<main class="wrap sheet">
	{#if !asked}
		<nav class="tabs">
			{#each SUBJECTS as s (s.key)}
				<button type="button" class="btn" class:btn--sun={subject === s.key} onclick={() => ((subject = s.key), (only = ''))}>{s.name}</button>
			{/each}
		</nav>
	{/if}
	{#each shown as g (g.key)}
		{@const m = mocks[g.key]}
		<section id={g.key}>
			<h2>{g.title} <small>({g.types.join(', ')})</small> <button type="button" class="btn btn--plain" onclick={() => (only = only ? '' : g.key)}>{only ? 'Semua' : 'Fokus'}</button></h2>
			{#if m}
				<div class="card">
					<QuestionCard question={m.question} />
					{#if stateAsked === 'host' && only}
						<Answer question={m.question} disabled reveal={m.reveal} onanswer={() => {}} />
					{:else if answers[g.key] === undefined}
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
