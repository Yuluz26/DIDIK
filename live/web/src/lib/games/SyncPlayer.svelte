<!--
	A child's screen in the games everyone answers together (Lumba Sampan, Teka Gambar).
	Stages from the server: intro → question → reveal → standings → … The game's own world (the
	`scene` snippet) fills the screen and the question is a popup inside it, which also shows the
	result. With `minimisable` the popup folds away so the child can play in the scene (Teka Gambar:
	guess the picture at any moment).
-->
<script lang="ts">
	import type { Snippet } from 'svelte';
	import type { Me, Person } from '$lib/types';
	import type { RoomClient } from '$lib/room.svelte';
	import { play } from '$lib/sound';
	import { confetti } from '$lib/confetti';
	import Answer from '$lib/questions/Answer.svelte';
	import Feedback from '$lib/questions/Feedback.svelte';
	import QuestionCard from '$lib/questions/QuestionCard.svelte';
	import Countdown from '$ui/Countdown.svelte';
	import Leaderboard from '$ui/Leaderboard.svelte';
	import Timer from '$ui/Timer.svelte';
	import Avatar from '$ui/Avatar.svelte';
	import Hud from './Hud.svelte';
	import QuestionPopup from './QuestionPopup.svelte';

	let {
		client,
		game,
		me,
		people,
		title,
		unit = 'mata',
		scene,
		extra,
		minimisable = false
	}: {
		client: RoomClient;
		// eslint-disable-next-line @typescript-eslint/no-explicit-any
		game: any;
		me: Me;
		people: Map<string, Person>;
		title: string;
		unit?: string;
		scene?: Snippet;
		extra?: Snippet;
		minimisable?: boolean;
	} = $props();

	let lastReveal = '';

	// Sound and confetti once per reveal.
	$effect(() => {
		if (game.stage !== 'reveal' || !game.result) return;
		const key = `${game.index}`;
		if (key === lastReveal) return;
		lastReveal = key;
		if (game.result.correct) {
			play('correct');
			confetti({ count: 70 });
		} else {
			play('almost');
		}
	});

	function answer(value: unknown) {
		client.send({ t: 'answer', a: value });
	}
</script>

<Hud {me} score={game.score} rank={game.rank} {unit} streak={game.streak} />

<main class="play wrap">
	{#if game.stage === 'intro'}
		<Countdown clock={game.clock} offset={client.offset} title={title} />
	{:else if game.stage === 'standings'}
		<section class="standings">
			<h2>Kedudukan</h2>
			<Leaderboard rows={game.standings} {people} me={me.id} {unit} limit={5} />
			{#if game.rank > 5}
				<p class="mine"><Avatar animal={me.avatar} colour={me.colour} skin={me.skin} size={34} /> Kamu di tempat ke-{game.rank}. Teruskan!</p>
			{/if}
		</section>
	{:else if game.question}
		{@render scene?.()}
		{@render extra?.()}

		<QuestionPopup label="Soalan {game.index + 1} daripada {game.total}" {minimisable} key={game.index}>
			{#snippet head()}
				{#if game.stage === 'question'}
					<Timer clock={game.clock} offset={client.offset} total={game.question.timeLimit} ticks={!game.answered} />
				{/if}
			{/snippet}
			<QuestionCard question={game.question} index={game.index} total={game.total} />

			{#if game.stage === 'reveal' && game.result}
				<Feedback correct={game.result.correct} fraction={game.result.fraction} missed={game.result.missed} points={game.result.points} {unit} />
			{/if}

			<Answer
				question={game.question}
				disabled={game.answered || game.stage !== 'question'}
				mine={game.myAnswer}
				reveal={game.stage === 'reveal' ? game.reveal : null}
				allRight={game.result?.correct}
				onanswer={answer}
			/>

			{#if game.stage === 'question' && game.answered}
				<p class="waiting" aria-live="polite">
					Jawapan dihantar! Menunggu kawan-kawan… <strong>{game.answeredCount}/{game.playerCount}</strong>
				</p>
			{/if}
		</QuestionPopup>
	{/if}
</main>

<style>
	.play {
		display: grid;
		gap: 1rem;
		padding-block: 1rem 3rem;
		max-width: 52rem;
	}
	.waiting {
		padding: 0.8rem 1rem;
		border-radius: var(--r-md);
		background: var(--brand-soft);
		color: var(--on-brand-soft);
		font-weight: 800;
		text-align: center;
		animation: rise-in var(--t-enter) var(--ease-out);
	}
	.standings {
		display: grid;
		gap: 1rem;
		padding-top: 1rem;
	}
	.standings h2 {
		font-size: var(--fs-h1);
		text-align: center;
	}
	.mine {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 0.6rem;
		font-weight: 800;
	}
</style>
