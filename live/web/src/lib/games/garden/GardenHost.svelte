<!--
	Kebun Ajaib on the big screen: the three gardens that have harvested the most, each with its
	gardener, so the room can see what a good garden looks like.
-->
<script lang="ts">
	import type { Person } from '$lib/types';
	import GardenWorld, { type CropInfo, type Plot } from './GardenWorld.svelte';

	let {
		world,
		people
	}: {
		world: { top: { id: string; plots: (Plot | null)[]; earned: number }[]; crops: Record<string, CropInfo>; maxPlots: number };
		people: Map<string, Person>;
	} = $props();

	const gardens = $derived(world.top.filter((g) => people.has(g.id)));
</script>

<section class="tops" aria-label="Kebun paling subur">
	<h2>Kebun paling subur</h2>
	{#if gardens.length}
		<ol class="gardens" class:solo={gardens.length === 1}>
			{#each gardens as garden, i (garden.id)}
				{@const owner = people.get(garden.id)!}
				<li class:first={i === 0}>
					<GardenWorld plots={garden.plots} crops={world.crops} maxPlots={world.maxPlots} {owner} maxTile={40} />
					<p><span class="place">{i + 1}</span> <strong>{owner.name}</strong> <span class="earned">{garden.earned} mata</span></p>
				</li>
			{/each}
		</ol>
	{:else}
		<p class="empty">Kebun pertama akan muncul di sini sebaik sahaja seseorang menuai.</p>
	{/if}
</section>

<style>
	.tops {
		display: grid;
		gap: 0.8rem;
	}
	.tops h2 {
		font-size: 1.4rem;
	}
	/* The leading garden large on the left, the next two stacked beside it. */
	.gardens {
		display: grid;
		grid-template-columns: minmax(0, 2fr) minmax(0, 1fr);
		align-items: start;
		gap: 0.9rem;
		margin: 0;
		padding: 0;
		list-style: none;
	}
	.gardens li {
		display: grid;
		gap: 0.4rem;
		min-width: 0;
	}
	.gardens .first {
		grid-row: span 2;
	}
	.gardens.solo {
		grid-template-columns: minmax(0, 1fr);
	}
	@media (max-width: 700px) {
		.gardens {
			grid-template-columns: minmax(0, 1fr);
		}
		.gardens .first {
			grid-row: auto;
		}
	}
	.gardens p {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		font-weight: 700;
	}
	.place {
		display: grid;
		place-items: center;
		width: 1.8rem;
		height: 1.8rem;
		border-radius: 50%;
		background: var(--sun);
		font: 600 1rem var(--font-display);
	}
	.earned {
		margin-left: auto;
		color: var(--ink-2);
	}
	.empty {
		padding: 1rem;
		border-radius: var(--r-md);
		background: var(--card);
		font-weight: 700;
	}
</style>
