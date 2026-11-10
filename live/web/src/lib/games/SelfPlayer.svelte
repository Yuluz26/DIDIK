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
	import { nextMove, showNextMove } from './nextMove';

	let {
		client,
		game,
		me,
		title,
		modeKey,
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
		modeKey: string;
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
	const move = $derived(nextMove(modeKey, game));
	let dismissedFor = $state(-1);
	const resultStep = $derived(step === 'result' || step === 'capture');
	const guideOpen = $derived(resultStep && !!seat.result && dismissedFor !== seat.answered);
	let lastAnswered = -1;

	function goPlay() {
		dismissedFor = seat.answered;
		showNextMove(move.target);
	}

	function next() {
		dismissedFor = seat.answered;
		client.send({ t: 'next' });
	}

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
	<main class="self wrap" class:docked={resultStep && !guideOpen}>
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
	{:else if resultStep && seat.result && guideOpen}
		<QuestionPopup label="Keputusan dan langkah seterusnya" key={seat.answered ?? 0}>
			<Feedback
				correct={seat.result.correct}
				fraction={seat.result.fraction}
				extra={seat.result.reward && rewardText ? rewardText(seat.result.reward) : ''}
				explain={seat.result.reveal?.explain ?? ''}
			/>
			{#if !seat.result.correct && seat.question}
				<details class="reveal">
					<summary>Lihat jawapan betul</summary>
					<Answer question={seat.question} disabled mine={seat.result.answer} reveal={seat.result.reveal} allRight={false} onanswer={() => {}} />
				</details>
			{/if}
			<div class="move" aria-live="polite">
				<span class="move-icon" aria-hidden="true">✦</span>
				<div><h2>{move.title}</h2><p>{move.detail}</p></div>
			</div>
			<div class="choices">
				<button type="button" class="btn btn--sun btn--big" onclick={goPlay}>{move.button} <Icon name="next" /></button>
				{#if step === 'capture'}
					<button type="button" class="btn btn--plain btn--big" onclick={() => { dismissedFor = seat.answered; client.send({ t: 'keep' }); }}>Simpan bendera</button>
				{:else}
					<button type="button" class="btn btn--plain btn--big" onclick={next}>{nextLabel}</button>
				{/if}
			</div>
		</QuestionPopup>
	{:else if resultStep && seat.result}
		<QuestionPopup mode="dock" label="Pilihan permainan">
			<div class="dock-actions">
				<button type="button" class="btn btn--plain" onclick={() => (dismissedFor = -1)}>Lihat panduan</button>
				{#if step === 'capture'}
					<button type="button" class="btn btn--sun" onclick={() => client.send({ t: 'keep' })}>Simpan bendera</button>
				{:else}
					<button type="button" class="btn btn--sun" onclick={next}>{nextLabel} <Icon name="next" /></button>
				{/if}
			</div>
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
	.move {
		display: flex;
		align-items: flex-start;
		gap: 0.8rem;
		padding: 0.85rem 1rem;
		border: 2px solid var(--sun);
		border-radius: var(--r-md);
		background: #fff8dd;
	}
	.move-icon { font-size: 1.8rem; line-height: 1; color: #c78600; }
	.move h2 { font-size: 1.15rem; line-height: 1.2; }
	.move p { margin-top: 0.25rem; line-height: 1.4; }
	.choices, .dock-actions { display: flex; flex-wrap: wrap; gap: 0.55rem; }
	.choices > button, .dock-actions > button { flex: 1 1 11rem; }
	@media (max-width: 36rem) {
		.choices > button { flex-basis: 100%; }
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
