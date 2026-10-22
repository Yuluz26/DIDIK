<!-- Lompat! on the big screen: the statement, the pond with everyone's choice, and who is still dry. -->
<script lang="ts">
	import type { RoomClient } from '$lib/room.svelte';
	import type { Person } from '$lib/types';
	import { play } from '$lib/sound';
	import QuestionCard from '$lib/questions/QuestionCard.svelte';
	import Countdown from '$ui/Countdown.svelte';
	import Leaderboard from '$ui/Leaderboard.svelte';
	import Timer from '$ui/Timer.svelte';
	import JumpPond from './JumpPond.svelte';

	// eslint-disable-next-line @typescript-eslint/no-explicit-any
	let { client, game, people }: { client: RoomClient; game: any; people: Map<string, Person> } = $props();

	let lastReveal = -1;
	$effect(() => {
		if (game.stage === 'reveal' && game.index !== lastReveal) {
			lastReveal = game.index;
			play('splash');
		}
	});

	const dry = $derived(game.pond ? Object.values(game.pond.hearts as Record<string, number>).filter((h) => h > 0).length : 0);
</script>

{#if game.stage === 'intro'}
	<Countdown clock={game.clock} offset={client.offset} title="Lompat!" />
{:else if game.question && game.pond}
	<div class="jump-host">
		<div class="main">
			<div class="top">
				{#if game.stage === 'question'}<Timer clock={game.clock} offset={client.offset} total={game.question.timeLimit} ticks />{/if}
				<span class="count">{Object.keys(game.pond.picks).length}/{game.playerCount} sudah melompat</span>
			</div>
			<QuestionCard question={game.question} index={game.index} total={game.total} big />
			<JumpPond pond={game.pond} {people} stage={game.stage} big />
		</div>
		<aside class="side">
			<p class="dry"><strong>{dry}</strong> masih di darat</p>
			<Leaderboard rows={game.leaders} {people} limit={8} compact />
		</aside>
	</div>
{/if}

<style>
	.jump-host {
		display: grid;
		grid-template-columns: minmax(0, 1fr) minmax(15rem, 20rem);
		gap: 1.2rem;
		align-items: start;
	}
	.main {
		display: grid;
		gap: 0.8rem;
		min-width: 0;
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
		margin-left: auto;
		padding: 0.3rem 0.9rem;
		border-radius: var(--r-pill);
		background: var(--brand-soft);
		color: var(--on-brand-soft);
		font-weight: 800;
		white-space: nowrap;
	}
	.side {
		display: grid;
		gap: 0.8rem;
	}
	.dry {
		padding: 0.7rem 1rem;
		border-radius: var(--r-md);
		background: #c9eef5;
		color: #0b5866;
		font-weight: 800;
	}
	.dry strong {
		font: 600 1.6rem var(--font-display);
	}
	@media (max-width: 980px) {
		.jump-host {
			grid-template-columns: minmax(0, 1fr);
		}
	}
</style>
