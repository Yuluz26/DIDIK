<!-- How much of the island each team holds, as a tug of war. -->
<script lang="ts">
	import { TEAM_COLOURS } from '$lib/names';

	let { teams, mine = null }: { teams: { key: string; name: string; cells: number; players: number }[]; mine?: string | null } = $props();

	const total = $derived(Math.max(1, teams.reduce((n, t) => n + t.cells, 0)));
</script>

<div class="bar" role="img" aria-label={teams.map((t) => `${t.name} ${t.cells} petak`).join(', ')}>
	{#each teams as team (team.key)}
		<span
			class="side"
			class:mine={team.key === mine}
			style:background={TEAM_COLOURS[team.key]?.colour}
			style:flex-grow={team.cells / total}
		>
			<strong>{team.cells}</strong> {team.name.replace('Pasukan ', '')}
		</span>
	{/each}
</div>

<style>
	.bar {
		display: flex;
		gap: 3px;
		min-height: 2.6rem;
		padding: 3px;
		border-radius: var(--r-pill);
		background: #fff;
		box-shadow: 0 3px 0 var(--line);
	}
	.side {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 0.35rem;
		min-width: 6.5rem;
		padding: 0 0.9rem;
		border-radius: var(--r-pill);
		color: #fff;
		font-weight: 800;
		white-space: nowrap;
		transition: flex-grow 700ms var(--spring);
	}
	.side strong {
		font: 600 1.3rem var(--font-display);
	}
	.side.mine {
		outline: 3px solid var(--ink);
		outline-offset: -3px;
	}
</style>
