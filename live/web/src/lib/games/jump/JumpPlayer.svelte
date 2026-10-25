<!-- A child's Lompat! screen: the statement, the pond to hop across, hearts, and the splash. -->
<script lang="ts">
	import type { RoomClient } from '$lib/room.svelte';
	import type { Me, Person } from '$lib/types';
	import { play } from '$lib/sound';
	import { confetti } from '$lib/confetti';
	import Feedback from '$lib/questions/Feedback.svelte';
	import QuestionCard from '$lib/questions/QuestionCard.svelte';
	import { heart } from '$lib/pixel/icons';
	import Sprite from '$lib/pixel/Sprite.svelte';
	import Countdown from '$ui/Countdown.svelte';
	import Timer from '$ui/Timer.svelte';
	import Hud from '../Hud.svelte';
	import JumpPond from './JumpPond.svelte';

	// eslint-disable-next-line @typescript-eslint/no-explicit-any
	let { client, game, me, people }: { client: RoomClient; game: any; me: Me; people: Map<string, Person> } = $props();

	const hearts = $derived(game.pond?.hearts?.[me.id] ?? 3);
	let lastReveal = -1;

	$effect(() => {
		if (game.stage !== 'reveal' || game.index === lastReveal) return;
		lastReveal = game.index;
		if (game.result?.correct) {
			play('correct');
			confetti({ count: 50 });
		} else {
			play('splash');
		}
	});

	function pick(pad: string) {
		play('pop');
		client.send({ t: 'pick', pad });
	}
</script>

<Hud {me} score={game.score} rank={game.rank} streak={game.streak}>
	<span class="hearts" aria-label="{hearts} hati tinggal">
		{#if hearts > 0}
			{#each [0, 1, 2] as i (i)}
				<Sprite sheet={heart(i < hearts)} s={1.5} />
			{/each}
		{:else}
			<span class="fish-tag">Ikan</span>
		{/if}
	</span>
</Hud>

<main class="jump wrap">
	{#if game.stage === 'intro'}
		<Countdown clock={game.clock} offset={client.offset} title="Lompat!" />
	{:else if game.question && game.pond}
		{#if game.stage === 'question'}
			<Timer clock={game.clock} offset={client.offset} total={game.question.timeLimit} ticks={!game.myPick} />
		{/if}
		<QuestionCard question={game.question} index={game.index} total={game.total} />
		{#if game.stage === 'reveal' && game.result}
			<Feedback
				correct={game.result.correct}
				missed={game.result.missed}
				points={game.result.points}
				extra={hearts === 0 ? 'Kamu ikan sekarang. Jawab betul dua kali untuk naik semula ke darat.' : ''}
			/>
		{:else if hearts === 0}
			<p class="note">Kamu ikan sekarang, tapi masih boleh menjawab! Dua jawapan betul berturut-turut dan kamu naik semula ke darat.</p>
		{/if}
		<JumpPond pond={game.pond} {people} me={me.id} stage={game.stage} interactive={game.stage === 'question'} onpick={pick} />
		{#if game.stage === 'question'}
			<p class="tip">{game.myPick ? 'Boleh tukar pulau sebelum masa tamat.' : 'Ketik pulau jawapan kamu!'}</p>
		{/if}
	{/if}
</main>

<style>
	.jump {
		display: grid;
		gap: 0.9rem;
		padding-block: 0.9rem 3rem;
		max-width: 52rem;
	}
	.hearts {
		display: inline-flex;
		gap: 0.2rem;
		line-height: 0;
	}
	.fish-tag {
		padding: 0.1rem 0.6rem;
		border: 2px solid var(--edge, transparent);
		border-radius: var(--r-pill);
		background: #c9eef5;
		color: #0b5866;
		font-weight: 800;
		font-size: 0.85rem;
	}
	.note {
		padding: 0.7rem 1rem;
		border-radius: var(--r-md);
		background: #c9eef5;
		color: #0b5866;
		font-weight: 800;
	}
	.tip {
		text-align: center;
		font-weight: 800;
		color: var(--ink-2);
	}
</style>
