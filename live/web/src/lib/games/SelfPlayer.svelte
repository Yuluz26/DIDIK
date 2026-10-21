<!--
	A child's screen in the games played at their own pace. Each answer earns something for the
	game's world (a shovel, a flag, water, building material); the world is the `world` snippet.

	Phone: while answering, the question comes first. After answering, the result and the Next button
	come first, then the world (to spend what was earned), then the question again with the right
	answer shown. Wide screens put the world on the left and the question on the right.
-->
<script lang="ts">
	import type { Snippet } from 'svelte';
	import type { Me } from '$lib/types';
	import type { RoomClient } from '$lib/room.svelte';
	import { play } from '$lib/sound';
	import { confetti } from '$lib/confetti';
	import Answer from '$lib/questions/Answer.svelte';
	import Feedback from '$lib/questions/Feedback.svelte';
	import QuestionCard from '$lib/questions/QuestionCard.svelte';
	import Countdown from '$ui/Countdown.svelte';
	import Icon from '$ui/Icon.svelte';
	import Timer from '$ui/Timer.svelte';
	import Hud from './Hud.svelte';

	let {
		client,
		game,
		me,
		title,
		unit = 'mata',
		rewardText,
		nextLabel = 'Soalan seterusnya',
		world,
		total = 300
	}: {
		client: RoomClient;
		// eslint-disable-next-line @typescript-eslint/no-explicit-any
		game: any;
		me: Me;
		title: string;
		unit?: string;
		// eslint-disable-next-line @typescript-eslint/no-explicit-any
		rewardText?: (reward: any) => string;
		nextLabel?: string;
		world: Snippet;
		total?: number;
	} = $props();

	const seat = $derived(game.seat ?? {});
	const step = $derived(seat.step as string);
	let lastAnswered = -1;

	$effect(() => {
		if (!seat.result || seat.answered === lastAnswered || step === 'question') return;
		lastAnswered = seat.answered;
		if (seat.result.correct) {
			play('correct');
			confetti({ count: 40 });
		} else {
			play('almost');
		}
	});
</script>

<Hud {me} score={game.score} rank={game.rank} {unit} streak={seat.streak ?? 0} />

{#if game.stage === 'intro'}
	<main class="wrap"><Countdown clock={game.clock} offset={client.offset} {title} /></main>
{:else}
	<div class="clock wrap"><Timer clock={game.clock} offset={client.offset} {total} compact /></div>
	<main class="self wrap step-{step}">
		{#if step === 'result' && seat.result}
			<section class="result">
				<Feedback
					correct={seat.result.correct}
					fraction={seat.result.fraction}
					extra={seat.result.reward && rewardText ? rewardText(seat.result.reward) : ''}
				/>
				<button type="button" class="btn btn--sun btn--big next" onclick={() => client.send({ t: 'next' })}>
					{nextLabel} <Icon name="next" />
				</button>
			</section>
		{/if}

		<section class="world" aria-label="Dunia permainan">
			{@render world()}
		</section>

		{#if (step === 'question' || step === 'result') && seat.question}
			<section class="question" aria-label="Soalan">
				<QuestionCard question={seat.question} />
				<Answer
					question={seat.question}
					disabled={step !== 'question'}
					mine={step === 'result' ? seat.result?.answer : undefined}
					reveal={step === 'result' ? seat.result?.reveal : null}
					allRight={seat.result?.correct}
					onanswer={(a) => client.send({ t: 'answer', a })}
				/>
			</section>
		{/if}
	</main>
{/if}

<style>
	.clock {
		padding-top: 0.6rem;
	}
	.self {
		display: grid;
		gap: 1rem;
		padding-block: 0.8rem 3rem;
		align-items: start;
		grid-template-columns: minmax(0, 1fr);
		grid-template-areas: 'question' 'world';
	}
	.self.step-result {
		grid-template-areas: 'result' 'world' 'question';
	}
	.self:not(.step-question):not(.step-result) {
		grid-template-areas: 'world';
	}
	.result {
		grid-area: result;
		display: grid;
		gap: 0.7rem;
	}
	.world {
		grid-area: world;
		min-width: 0;
	}
	.question {
		grid-area: question;
		display: grid;
		gap: 0.9rem;
		min-width: 0;
		padding: 1.1rem;
		border-radius: var(--r-lg);
		background: var(--card);
		box-shadow: var(--card-shadow);
		animation: rise-in var(--t-enter) var(--ease-out);
	}
	.next {
		width: 100%;
	}
	@media (min-width: 900px) {
		.self.step-question {
			grid-template-columns: minmax(0, 1fr) minmax(0, 1.05fr);
			grid-template-areas: 'world question';
		}
		.self.step-result {
			grid-template-columns: minmax(0, 1fr) minmax(0, 1.05fr);
			grid-template-areas: 'world result' 'world question';
			align-content: start;
		}
		.self.step-result .world {
			grid-row: 1 / span 2;
		}
	}
</style>
