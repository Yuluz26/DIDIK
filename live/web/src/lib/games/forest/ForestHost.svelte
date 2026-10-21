<!-- Hutan Misteri on the big screen: the whole forest with every child walking, and who got out. -->
<script lang="ts">
	import type { RoomClient } from '$lib/room.svelte';
	import type { FeedItem, Person } from '$lib/types';
	import Avatar from '$ui/Avatar.svelte';
	import Countdown from '$ui/Countdown.svelte';
	import Feed from '$ui/Feed.svelte';
	import Leaderboard from '$ui/Leaderboard.svelte';
	import Timer from '$ui/Timer.svelte';
	import ForestMap from './ForestMap.svelte';
	import { livePositions } from './positions.svelte';

	let {
		client,
		game,
		people,
		feed
	}: {
		client: RoomClient;
		// eslint-disable-next-line @typescript-eslint/no-explicit-any
		game: any;
		people: Map<string, Person>;
		feed: FeedItem[];
	} = $props();

	const world = $derived(game.world);
	// The room connection never changes for the life of this screen.
	// svelte-ignore state_referenced_locally
	const positions = livePositions(client);
	let width = $state(900);
	const tile = $derived(Math.max(14, Math.floor(width / (world?.map?.[0]?.length ?? 32))));
</script>

{#if game.stage === 'intro'}
	<Countdown clock={game.clock} offset={client.offset} title="Hutan Misteri" />
{:else if world}
	<div class="forest-host">
		<div class="clock"><Timer clock={game.clock} offset={client.offset} total={game.length ?? 300} /></div>
		<div class="map" bind:clientWidth={width}>
			<ForestMap map={world.map} chests={world.chests} gate={world.gate} positions={positions.all} moving={positions.moving} {people} escaped={world.escaped} {tile} />
		</div>
		<aside class="side">
			{#if world.escaped.length}
				<section class="out">
					<h2>Sudah keluar</h2>
					<ol>
						{#each world.escaped as id, i (id)}
							{@const person = people.get(id)}
							<li><span class="n">{i + 1}</span><Avatar animal={person?.avatar} colour={person?.colour} skin={person?.skin} size={30} /> {person?.name}</li>
						{/each}
					</ol>
				</section>
			{/if}
			<h2>Kedudukan</h2>
			<Leaderboard rows={game.leaders} {people} limit={8} compact />
			<Feed items={feed} {people} limit={4} />
		</aside>
	</div>
{/if}

<style>
	.forest-host {
		display: grid;
		grid-template-columns: minmax(0, 1fr) minmax(15rem, 20rem);
		gap: 1rem;
		align-items: start;
	}
	.clock {
		grid-column: 1 / -1;
	}
	.map {
		min-width: 0;
	}
	.side {
		display: grid;
		gap: 0.7rem;
	}
	.side h2 {
		font-size: 1.25rem;
	}
	.out {
		display: grid;
		gap: 0.5rem;
		padding: 0.8rem 1rem;
		border-radius: var(--r-lg);
		background: var(--sun);
	}
	.out ol {
		display: grid;
		gap: 0.3rem;
		margin: 0;
		padding: 0;
		list-style: none;
		font-weight: 800;
	}
	.out li {
		display: flex;
		align-items: center;
		gap: 0.45rem;
	}
	.n {
		width: 1.4rem;
		font: 600 1rem var(--font-display);
	}
	@media (max-width: 980px) {
		.forest-host {
			grid-template-columns: minmax(0, 1fr);
		}
	}
</style>
