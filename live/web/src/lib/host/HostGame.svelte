<!-- The host's big screen during a game, chosen by the room's game. -->
<script lang="ts">
	import type { RoomClient } from '$lib/room.svelte';
	import type { Person, View } from '$lib/types';
	import ForestHost from '$lib/games/forest/ForestHost.svelte';
	import JumpHost from '$lib/games/jump/JumpHost.svelte';
	import TeamsWorld from '$lib/games/teams/TeamsWorld.svelte';
	import RaceRiver from '$lib/games/race/RaceRiver.svelte';
	import ScoreTowers from '$ui/ScoreTowers.svelte';
	import SelfHost from './SelfHost.svelte';
	import SyncHost from './SyncHost.svelte';

	let { client, view, people }: { client: RoomClient; view: View; people: Map<string, Person> } = $props();

	const game = $derived(view.game);
	const mode = $derived(view.room.mode);
	const minutes = $derived(view.game?.length ?? 300);
</script>

{#if mode.key === 'lumba'}
	<SyncHost {client} {game} {people} title={mode.title} unit="m">
		{#snippet scene()}
			{#if game.race}<RaceRiver race={game.race} {people} />{/if}
		{/snippet}
	</SyncHost>
{:else if mode.key === 'lompat'}
	<JumpHost {client} {game} {people} />
{:else if mode.key === 'harta'}
	<SelfHost {client} {game} {people} feed={view.feed} title={mode.title} unit="syiling" total={minutes} board={false}>
		{#snippet world()}
			<ScoreTowers rows={game.leaders} {people} />
		{/snippet}
	</SelfHost>
{:else if mode.key === 'hutan'}
	<ForestHost {client} {game} {people} feed={view.feed} />
{:else if mode.key === 'pasukan'}
	<SelfHost {client} {game} {people} feed={view.feed} title={mode.title} unit="petak" total={minutes}>
		{#snippet world()}
			{#if game.world?.cells}<TeamsWorld {client} world={game.world} step={null} big />{/if}
		{/snippet}
	</SelfHost>
{:else}
	<SelfHost {client} {game} {people} feed={view.feed} title={mode.title} total={minutes} />
{/if}
