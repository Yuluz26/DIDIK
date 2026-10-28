<!--
	A child's screen in the games played at their own pace. Each answer earns something for the
	game's world (a shovel, a flag, water, building material); the world is the `world` snippet.

	The world fills the screen. The question is a popup inside the game, over the world; after
	answering, the same popup shows the result, the right answer and the Next button, and closes when
	the child goes back to the world to spend what was earned.
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
	import QuestionPopup from './QuestionPopup.svelte';

	let {
		client,
		game,
		me,
		title,
		unit = 'mata',
		rewardText,
		nextLabel = 'Soalan seterusnya',
		world,
		total = 300,
		ranked = true
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
		ranked?: boolean;
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

<Hud {me} score={game.score} rank={ranked ? game.rank : null} {unit} streak={seat.streak ?? 0} />

{#if game.stage === 'intro'}
	<main class="wrap"><Countdown clock={game.clock} offset={client.offset} {title} /></main>
{:else}
	<div class="clock wrap"><Timer clock={game.clock} offset={client.offset} {total} compact /></div>
	<main class="self wrap">
		<section class="world" aria-label="Dunia permainan">
			{@render world()}
		</section>
	</main>

	{#if (step === 'question' || step === 'result') && seat.question}
		<QuestionPopup label="Soalan" key={seat.answered ?? 0}>
			{#snippet head()}
				<Timer clock={game.clock} offset={client.offset} {total} compact />
			{/snippet}
			<QuestionCard question={seat.question} />
			{#if step === 'result' && seat.result}
				<Feedback
					correct={seat.result.correct}
					fraction={seat.result.fraction}
					extra={seat.result.reward && rewardText ? rewardText(seat.result.reward) : ''}
				/>
			{/if}
			<Answer
				question={seat.question}
				disabled={step !== 'question'}
				mine={step === 'result' ? seat.result?.answer : undefined}
				reveal={step === 'result' ? seat.result?.reveal : null}
				allRight={seat.result?.correct}
				onanswer={(a) => client.send({ t: 'answer', a })}
			/>
			{#if step === 'result'}
				<button type="button" class="btn btn--sun btn--big next" onclick={() => client.send({ t: 'next' })}>
					{nextLabel} <Icon name="next" />
				</button>
			{/if}
		</QuestionPopup>
	{/if}
{/if}

<style>
	.clock {
		padding-top: 0.6rem;
	}
	.self {
		padding-block: 0.8rem 3rem;
	}
	.world {
		min-width: 0;
	}
	.next {
		width: 100%;
	}
</style>
