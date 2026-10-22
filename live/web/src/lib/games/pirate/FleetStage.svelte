<!--
	Peti Lanun on the big screen: the eight richest ships in the bay, their gold heaped on deck, each
	named. A raid fires a cannonball from the raider's ship to the other one.
-->
<script lang="ts">
	import type { RoomClient } from '$lib/room.svelte';
	import type { Person } from '$lib/types';
	import { COLOURS } from '$lib/names';
	import { play } from '$lib/sound';
	import Stage3D from '$lib/three/Stage3D.svelte';
	import type { BayWorld } from './bay';

	let { client, leaders, people }: { client: RoomClient; leaders: { id: string; score: number }[]; people: Map<string, Person> } = $props();

	let world = $state<BayWorld | null>(null);

	const create = () => import('./bay').then(({ BayWorld }) => new BayWorld());

	$effect(() => {
		world?.update(leaders.map((row) => ({ id: row.id, gold: row.score, colour: COLOURS[people.get(row.id)?.colour ?? ''] })));
	});

	$effect(() =>
		client.onFx((fx) => {
			if (fx.kind !== 'plunder') return;
			world?.fire(String(fx.by), String(fx.from));
			play('steal');
		})
	);

	const top = $derived(leaders.slice(0, 8));
	const label = $derived(top.length ? `Teluk lanun: ${people.get(top[0].id)?.name ?? 'Pemain'} paling kaya dengan ${top[0].score} emas.` : 'Teluk lanun.');
</script>

<div class="fleet">
	<Stage3D {create} bind:world {label}>
		{#if world}
			{#each top as row, i (row.id)}
				<span class="tag" class:first={i === 0} {@attach world.tags.attach(row.id)}>
					<b>{people.get(row.id)?.name ?? 'Pemain'}</b>
					<span>{row.score.toLocaleString('ms-MY')} emas</span>
				</span>
			{/each}
		{/if}
	</Stage3D>
</div>

<style>
	.fleet {
		height: clamp(22rem, calc(100dvh - 12rem), 40rem);
		border-radius: var(--r-lg);
		overflow: hidden;
		--stage-bg: #7c5f7d;
	}
	.tag {
		position: absolute;
		top: 0;
		left: 0;
		display: grid;
		justify-items: center;
		visibility: hidden;
		padding: 0.2rem 0.6rem;
		border-radius: var(--r-md);
		background: rgb(15 31 36 / 0.82);
		color: #fff;
		line-height: 1.2;
		white-space: nowrap;
	}
	.tag b {
		font: 600 0.95rem var(--font-display);
	}
	.tag span {
		color: var(--sun);
		font-size: 0.85rem;
		font-weight: 800;
	}
	.tag.first {
		background: var(--sun);
		color: var(--on-bright);
	}
	.tag.first span {
		color: var(--on-bright);
	}
</style>
