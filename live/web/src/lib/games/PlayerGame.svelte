<!-- A child's game screen, chosen by the room's game. -->
<script lang="ts">
	import type { RoomClient } from '$lib/room.svelte';
	import type { Me, Person, View } from '$lib/types';
	import SelfPlayer from './SelfPlayer.svelte';
	import SyncPlayer from './SyncPlayer.svelte';
	import JumpPlayer from './jump/JumpPlayer.svelte';
	import RaceRiver from './race/RaceRiver.svelte';
	import TreasureIsland from './treasure/TreasureIsland.svelte';
	import { lootLine } from './treasure/loot';

	let { client, view, me, people }: { client: RoomClient; view: View; me: Me; people: Map<string, Person> } = $props();

	const game = $derived(view.game);
	const mode = $derived(view.room.mode);
	const minutes = $derived(view.game?.length ?? 300);
</script>

{#if mode.key === 'lumba'}
	<SyncPlayer {client} {game} {me} {people} title={mode.title} unit="m">
		{#snippet scene()}
			{#if game.race}<RaceRiver race={game.race} {people} me={me.id} compact />{/if}
		{/snippet}
	</SyncPlayer>
{:else if mode.key === 'lompat'}
	<JumpPlayer {client} {game} {me} {people} />
{:else if mode.key === 'harta'}
	<SelfPlayer
		{client}
		{game}
		{me}
		title={mode.title}
		unit="syiling"
		total={minutes}
		rewardText={(r) => (r.kind === 'dug' ? lootLine(r) : r.kind === 'shovel' ? 'Kamu dapat penyodok!' : '')}
	>
		{#snippet world()}
			{#if game.world?.tiles}
				<TreasureIsland world={game.world} ondig={(tile) => client.send({ t: 'dig', tile })} />
			{/if}
		{/snippet}
	</SelfPlayer>
{:else}
	<p class="wrap">Permainan ini sedang disiapkan.</p>
{/if}
