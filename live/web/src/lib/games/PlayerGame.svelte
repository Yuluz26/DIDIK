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
	import LegendaPlayer from './legenda/LegendaPlayer.svelte';
	import FishingWorld from './fun/FishingWorld.svelte';
	import SkyKites from './fun/SkyKites.svelte';
	import CastleWorld from './fun/CastleWorld.svelte';
	import TrainWorld from './fun/TrainWorld.svelte';
	import MarketWorld from './fun/MarketWorld.svelte';
	import StarSky from './fun/StarSky.svelte';

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
	<SyncPlayer {client} {game} {me} {people} title={mode.title} minimisable>
		{#snippet scene()}
			{#if game.picture}<PictureGuess {client} frame={game.picture} {me} {people} />{/if}
		{/snippet}
	</SyncPlayer>
{:else if mode.key === 'pancing'}
	<SelfPlayer {client} {game} {me} title={mode.title} unit={mode.unit} total={minutes} rewardText={(r) => (r.gold ? 'Kamu dapat umpan emas!' : r.bait ? 'Kamu dapat satu umpan!' : '')}>
		{#snippet world()}
			{#if game.world?.fish}<FishingWorld {client} world={game.world} {me} />{/if}
		{/snippet}
	</SelfPlayer>
{:else if mode.key === 'wau'}
	<SyncPlayer {client} {game} {me} {people} title={mode.title} unit={mode.unit}>
		{#snippet scene()}
			{#if game.race}<SkyKites race={game.race} {people} me={me.id} compact />{/if}
		{/snippet}
	</SyncPlayer>
{:else if mode.key === 'kubu'}
	<SelfPlayer {client} {game} {me} title={mode.title} unit={mode.unit} total={minutes} rewardText={(r) => (r.sand ? `+${r.sand} baldi pasir!` : '')}>
		{#snippet world()}
			{#if game.world?.costs}<CastleWorld {client} world={game.world} offset={client.offset} />{/if}
		{/snippet}
	</SelfPlayer>
{:else if mode.key === 'keretapi'}
	<SelfPlayer {client} {game} {me} title={mode.title} unit={mode.unit} total={minutes} rewardText={(r) => (r.coal ? `+${r.coal} arang untuk kereta api!` : '')}>
		{#snippet world()}
			{#if game.world?.stations}<TrainWorld {client} world={game.world} />{/if}
		{/snippet}
	</SelfPlayer>
{:else if mode.key === 'pasar'}
	<SelfPlayer {client} {game} {me} title={mode.title} unit={mode.unit} total={minutes} rewardText={(r) => (r.stock ? `+${r.stock} barang untuk dijual!` : '')}>
		{#snippet world()}
			{#if game.world?.upgrades}<MarketWorld {client} world={game.world} />{/if}
		{/snippet}
	</SelfPlayer>
{:else if mode.key === 'bintang'}
	<SelfPlayer {client} {game} {me} title={mode.title} unit={mode.unit} total={minutes} rewardText={(r) => (r.stars ? `Kamu menangkap ${r.stars} bintang!` : '')}>
		{#snippet world()}
			{#if game.world?.teams}<StarSky {client} world={game.world} />{/if}
		{/snippet}
	</SelfPlayer>
{:else if mode.key === 'legenda'}
	<LegendaPlayer {client} {game} {me} {people} />
{:else}
	<p class="wrap">Permainan ini sedang disiapkan.</p>
{/if}
