<!--
	A child's screen in the games played at their own pace. Each answer earns something for the
	game's world (a shovel, a flag, water, building material); the world is the `world` snippet.

	The world fills the screen. The question is a popup inside the game, over the world; after
	answering, the result (and the right answer, when it was wrong) docks at the bottom with the Next
	button, and the world above stays playable, so what the answer earned can be spent there.
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
	<main class="self wrap" class:docked={step === 'result'}>
		<section class="world" aria-label="Dunia permainan">
			{@render world()}
		</section>
	</main>

	{#if step === 'question' && seat.question}
		<QuestionPopup label="Soalan" key={seat.answered ?? 0}>
			{#snippet head()}
				<Timer clock={game.clock} offset={client.offset} {total} compact />
			{/snippet}
			<QuestionCard question={seat.question} />
			<Answer question={seat.question} onanswer={(a) => client.send({ t: 'answer', a })} />
		</QuestionPopup>
	{:else if step === 'result' && seat.result}
		<!-- the result docks at the bottom, so what the answer earned can be spent in the world above -->
		<QuestionPopup mode="dock" label="Keputusan">
			<Feedback
				correct={seat.result.correct}
				fraction={seat.result.fraction}
				extra={seat.result.reward && rewardText ? rewardText(seat.result.reward) : ''}
			/>
			{#if !seat.result.correct && seat.question}
				<!-- the right answer folds away, so the dock leaves the world in view -->
				<details class="reveal">
					<summary>Lihat jawapan betul</summary>
					<Answer question={seat.question} disabled mine={seat.result.answer} reveal={seat.result.reveal} allRight={false} onanswer={() => {}} />
				</details>
			{/if}
			<button type="button" class="btn btn--sun btn--big next" onclick={() => client.send({ t: 'next' })}>
				{nextLabel} <Icon name="next" />
			</button>
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
	/* room under the world, so none of it stays hidden behind the docked result */
	.self.docked {
		padding-bottom: 36dvh;
	}
	.world {
		min-width: 0;
	}
	.next {
		width: 100%;
	}
	.reveal summary {
		cursor: pointer;
		color: var(--brand-ink);
		font-weight: 800;
		min-height: 2.75rem;
		display: flex;
		align-items: center;
	}
	.reveal[open] summary {
		margin-bottom: 0.5rem;
	}
</style>
