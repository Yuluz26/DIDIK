<!-- A child's Pasukan Warna world: their team, their flags, and the island to claim. -->
<script lang="ts">
	import type { RoomClient } from '$lib/room.svelte';
	import { TEAM_COLOURS } from '$lib/names';
	import { play } from '$lib/sound';
	import Icon from '$ui/Icon.svelte';
	import HexMap from './HexMap.svelte';
	import TeamBar from './TeamBar.svelte';

	let {
		client,
		world,
		step,
		big = false
	}: {
		client: RoomClient;
		// eslint-disable-next-line @typescript-eslint/no-explicit-any
		world: any;
		step: string | null;
		big?: boolean;
	} = $props();

	let fresh = $state<string | null>(null);
	const team = $derived(world.myTeam ? TEAM_COLOURS[world.myTeam] : null);

	$effect(() =>
		client.onFx((fx) => {
			if (fx.kind !== 'captured') return;
			fresh = fx.cell;
			if (fx.player === client.youId || big) play('capture');
			setTimeout(() => (fresh = null), 700);
		})
	);
</script>

<div class="teams" class:big>
	{#if team}
		<p class="mine" style:--team={team.colour} style:--soft={team.soft}>
			Kamu dalam <strong>{team.name}</strong>
			<span class="flags"><Icon name="flag" size={18} /> {world.flags} bendera</span>
		</p>
	{/if}
	<TeamBar teams={world.teams} mine={world.myTeam} />
	<HexMap cells={world.cells} targets={world.targets ?? []} costs={world.costs ?? {}} {fresh} oncapture={(cell) => client.send({ t: 'capture', cell })} />
	{#if step === 'capture'}
		<div class="capture">
			<p><strong>Tawan satu petak!</strong> Ketik petak bercahaya. Petak kosong perlukan 1 bendera, petak lawan 2.</p>
			<button type="button" class="btn btn--plain" onclick={() => client.send({ t: 'keep' })}>Simpan bendera</button>
		</div>
	{/if}
</div>

<style>
	.teams {
		display: grid;
		gap: 0.8rem;
	}
	.mine {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		flex-wrap: wrap;
		padding: 0.6rem 0.9rem;
		border-radius: var(--r-md);
		background: var(--soft);
		font-weight: 700;
	}
	.mine strong {
		color: var(--team);
		filter: brightness(0.75);
	}
	.flags {
		display: inline-flex;
		align-items: center;
		gap: 0.25rem;
		margin-left: auto;
		padding: 0.15rem 0.6rem;
		border-radius: var(--r-pill);
		background: #fff;
		font-weight: 800;
	}
	.capture {
		display: flex;
		align-items: center;
		gap: 0.8rem;
		flex-wrap: wrap;
		padding: 0.8rem 1rem;
		border-radius: var(--r-md);
		background: var(--sun);
		animation: pop-in 400ms var(--spring);
	}
	.capture p {
		flex: 1 1 14rem;
		font-weight: 700;
	}
</style>
