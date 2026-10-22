<!-- A child's game screen, chosen by the room's game. -->
<script lang="ts">
	import type { RoomClient } from '$lib/room.svelte';
	import type { Me, Person, View } from '$lib/types';
	import SelfPlayer from './SelfPlayer.svelte';
	import SyncPlayer from './SyncPlayer.svelte';
	import ForestPlayer from './forest/ForestPlayer.svelte';
	import JumpPlayer from './jump/JumpPlayer.svelte';
	import RaceRiver from './race/RaceRiver.svelte';
	import TeamsWorld from './teams/TeamsWorld.svelte';
	import TreasureIsland from './treasure/TreasureIsland.svelte';
	import { lootLine } from './treasure/loot';
	import VillageWorld from './village/VillageWorld.svelte';
	import GardenPlayer from './garden/GardenPlayer.svelte';
	import PictureGuess from './picture/PictureGuess.svelte';
	import KartStage from './kart/KartStage.svelte';
	import PenaltyStage from './penalty/PenaltyStage.svelte';
	import PirateDeck from './pirate/PirateDeck.svelte';
	import { rewardLine } from './pirate/lines';
	import TowerStage from './tower/TowerStage.svelte';

	let { client, view, me, people }: { client: RoomClient; view: View; me: Me; people: Map<string, Person> } = $props();

	const game = $derived(view.game);
	const mode = $derived(view.room.mode);
	const minutes = $derived(view.game?.length ?? 300);
</script>

{#if mode.key === 'lumba'}
	<SyncPlayer {client} {game} {me} {people} title={mode.title} unit={mode.unit}>
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
		unit={mode.unit}
		total={minutes}
		rewardText={(r) => (r.kind === 'dug' ? lootLine(r) : r.kind === 'shovel' ? 'Kamu dapat penyodok!' : '')}
	>
		{#snippet world()}
			{#if game.world?.tiles}
				<TreasureIsland world={game.world} {me} ondig={(tile) => client.send({ t: 'dig', tile })} />
			{/if}
		{/snippet}
	</SelfPlayer>
{:else if mode.key === 'hutan'}
	<ForestPlayer {client} {game} {me} {people} />
{:else if mode.key === 'pasukan'}
	<SelfPlayer {client} {game} {me} title={mode.title} unit={mode.unit} total={minutes} rewardText={(r) => (r.flags ? `Dapat ${r.flags} bendera!` : '')}>
		{#snippet world()}
			{#if game.world?.cells}<TeamsWorld {client} world={game.world} step={game.seat?.step ?? null} people={[...people.values()]} me={me.id} />{/if}
		{/snippet}
	</SelfPlayer>
{:else if mode.key === 'kampung'}
	<SelfPlayer
		{client}
		{game}
		{me}
		title={mode.title}
		unit={mode.unit}
		total={minutes}
		ranked={false}
		rewardText={(r) => (r.materials ? `+${r.materials} bahan binaan${r.decoration ? ', dan satu hiasan untuk padang!' : ''}` : '')}
	>
		{#snippet world()}
			{#if game.world?.buildings}<VillageWorld {client} world={game.world} {people} me={me.id} />{/if}
		{/snippet}
	</SelfPlayer>
{:else if mode.key === 'kebun'}
	<SelfPlayer
		{client}
		{game}
		{me}
		title={mode.title}
		unit={mode.unit}
		total={minutes}
		rewardText={(r) => (r.water ? `+${r.water} titisan air untuk kebun!` : '')}
	>
		{#snippet world()}
			{#if game.world?.plots}<GardenPlayer {client} world={game.world} {me} />{/if}
		{/snippet}
	</SelfPlayer>
{:else if mode.key === 'teka'}
	<SyncPlayer {client} {game} {me} {people} title={mode.title}>
		{#snippet scene()}
			{#if game.picture}<PictureGuess {client} frame={game.picture} {me} {people} />{/if}
		{/snippet}
	</SyncPlayer>
{:else if mode.key === 'litar'}
	<SyncPlayer {client} {game} {me} {people} title={mode.title} unit={mode.unit}>
		{#snippet scene()}
			{#if game.circuit}<KartStage circuit={game.circuit} {people} me={me.id} view="phone" />{/if}
		{/snippet}
	</SyncPlayer>
{:else if mode.key === 'penalti'}
	<SyncPlayer {client} {game} {me} {people} title={mode.title} unit={mode.unit}>
		{#snippet scene()}
			{#if game.match}<PenaltyStage match={game.match} stage={game.stage} index={game.index} view="phone" />{/if}
		{/snippet}
	</SyncPlayer>
{:else if mode.key === 'lanun'}
	<SelfPlayer {client} {game} {me} title={mode.title} unit={mode.unit} total={minutes} rewardText={(r) => rewardLine(r, people)}>
		{#snippet world()}
			<PirateDeck {client} world={game.world ?? {}} step={game.seat?.step ?? 'question'} {people} />
		{/snippet}
	</SelfPlayer>
{:else if mode.key === 'menara'}
	<SelfPlayer
		{client}
		{game}
		{me}
		title={mode.title}
		unit={mode.unit}
		total={minutes}
		ranked={false}
		rewardText={(r) =>
			r.kind === 'dropped' ? (r.perfect ? `Tepat di tengah! Menara naik ${r.metres} m.` : `Menara naik ${r.metres} m.`) : r.kind === 'block' ? 'Kamu dapat satu blok!' : ''}
	>
		{#snippet world()}
			{#if game.world?.landmarks}
				<TowerStage {client} world={game.world} {people} view="phone" step={game.seat?.step ?? null} me={{ id: me.id, colour: me.colour }} reward={game.seat?.result?.reward ?? null} />
			{/if}
		{/snippet}
	</SelfPlayer>
{:else}
	<p class="wrap">Permainan ini sedang disiapkan.</p>
{/if}
