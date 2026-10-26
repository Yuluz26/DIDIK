<!-- The host's big screen during a game, chosen by the room's game. -->
<script lang="ts">
	import type { RoomClient } from '$lib/room.svelte';
	import type { Person, View } from '$lib/types';
	import ForestHost from '$lib/games/forest/ForestHost.svelte';
	import JumpHost from '$lib/games/jump/JumpHost.svelte';
	import TeamsWorld from '$lib/games/teams/TeamsWorld.svelte';
	import RaceRiver from '$lib/games/race/RaceRiver.svelte';
	import VillageWorld from '$lib/games/village/VillageWorld.svelte';
	import GardenHost from '$lib/games/garden/GardenHost.svelte';
	import PictureHost from '$lib/games/picture/PictureHost.svelte';
import StoryHost from '$lib/games/story/StoryHost.svelte';
	import ScoreTowers from '$ui/ScoreTowers.svelte';
						import SelfHost from './SelfHost.svelte';
	import SyncHost from './SyncHost.svelte';

	let { client, view, people }: { client: RoomClient; view: View; people: Map<string, Person> } = $props();

	const game = $derived(view.game);
	const mode = $derived(view.room.mode);
	const minutes = $derived(view.game?.length ?? 300);
</script>

{#if mode.key === 'lumba'}
	<SyncHost {client} {game} {people} title={mode.title} unit={mode.unit}>
		{#snippet scene()}
			{#if game.race}<RaceRiver race={game.race} {people} />{/if}
		{/snippet}
	</SyncHost>
{:else if mode.key === 'lompat'}
	<JumpHost {client} {game} {people} />
{:else if mode.key === 'harta'}
	<SelfHost {client} {game} {people} feed={view.feed} title={mode.title} unit={mode.unit} total={minutes} board={false}>
		{#snippet world()}
			<ScoreTowers rows={game.leaders} {people} />
		{/snippet}
	</SelfHost>
{:else if mode.key === 'hutan'}
	<ForestHost {client} {game} {people} feed={view.feed} />
{:else if mode.key === 'pasukan'}
	<SelfHost {client} {game} {people} feed={view.feed} title={mode.title} unit={mode.unit} total={minutes}>
		{#snippet world()}
			{#if game.world?.cells}<TeamsWorld {client} world={game.world} step={null} people={[...people.values()]} big />{/if}
		{/snippet}
	</SelfHost>
{:else if mode.key === 'kampung'}
	<SelfHost {client} {game} {people} feed={view.feed} title={mode.title} unit={mode.unit} total={minutes} boardTitle="Paling banyak membantu">
		{#snippet world()}
			{#if game.world?.buildings}<VillageWorld {client} world={game.world} {people} big />{/if}
		{/snippet}
	</SelfHost>
{:else if mode.key === 'teka'}
	<SyncHost {client} {game} {people} title={mode.title} wideSide>
		{#snippet side()}
			{#if game.picture}<PictureHost {client} frame={game.picture} {people} />{/if}
		{/snippet}
	</SyncHost>
{:else if mode.key === 'kebun'}
	<SelfHost {client} {game} {people} feed={view.feed} title={mode.title} unit={mode.unit} total={minutes}>
		{#snippet world()}
			{#if game.world?.top}<GardenHost world={game.world} {people} unit={mode.unit} />{/if}
		{/snippet}
	</SelfHost>
{:else if mode.key === 'legenda'}
	<StoryHost {client} {game} {people} />
{:else}
	<SelfHost {client} {game} {people} feed={view.feed} title={mode.title} total={minutes} />
{/if}
