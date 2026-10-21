<!--
	The big screen for games played at each child's own pace: the clock, the leaders and what just
	happened, beside the game's shared world when it has one.
-->
<script lang="ts">
	import type { Snippet } from 'svelte';
	import type { RoomClient } from '$lib/room.svelte';
	import type { FeedItem, Person } from '$lib/types';
	import Countdown from '$ui/Countdown.svelte';
	import Feed from '$ui/Feed.svelte';
	import Leaderboard from '$ui/Leaderboard.svelte';
	import Timer from '$ui/Timer.svelte';

	let {
		client,
		game,
		people,
		feed,
		title,
		unit = 'mata',
		total = 300,
		world,
		board = true
	}: {
		client: RoomClient;
		// eslint-disable-next-line @typescript-eslint/no-explicit-any
		game: any;
		people: Map<string, Person>;
		feed: FeedItem[];
		title: string;
		unit?: string;
		total?: number;
		world?: Snippet;
		board?: boolean;
	} = $props();
</script>

{#if game.stage === 'intro'}
	<Countdown clock={game.clock} offset={client.offset} {title} />
{:else}
	<div class="self-host" class:with-world={!!world}>
		<div class="clock"><Timer clock={game.clock} offset={client.offset} {total} /></div>
		{#if world}<section class="world">{@render world()}</section>{/if}
		<aside class="side">
			{#if board}
				<h2>Kedudukan</h2>
				<Leaderboard rows={game.leaders} {people} {unit} limit={8} compact={!!world} />
			{/if}
			<Feed items={feed} {people} />
		</aside>
	</div>
{/if}

<style>
	.self-host {
		display: grid;
		gap: 1.2rem;
		grid-template-columns: minmax(0, 1fr);
	}
	.self-host.with-world {
		grid-template-columns: minmax(0, 1fr) minmax(16rem, 22rem);
		align-items: start;
	}
	.clock {
		grid-column: 1 / -1;
	}
	.world {
		min-width: 0;
	}
	.side {
		display: grid;
		gap: 0.8rem;
		align-content: start;
	}
	.side h2 {
		font-size: 1.4rem;
	}
	@media (max-width: 980px) {
		.self-host.with-world {
			grid-template-columns: minmax(0, 1fr);
		}
	}
</style>
