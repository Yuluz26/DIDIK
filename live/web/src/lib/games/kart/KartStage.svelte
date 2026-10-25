<!--
	Litar Kart's 3D circuit, on the big screen (the whole circuit, the leaders named) or on a phone
	(a chase view behind the player's kart). three.js loads only when this mounts. Without WebGL the
	race is shown as a short list, and the game is still a full quiz.
-->
<script lang="ts">
	import type { Person } from '$lib/types';
	import { COLOURS } from '$lib/names';
	import Stage3D from '$lib/three/Stage3D.svelte';
	import type { CircuitState, CircuitWorld } from './circuit';

	let {
		circuit,
		people,
		me = null,
		view
	}: { circuit: CircuitState; people: Map<string, Person>; me?: string | null; view: 'host' | 'phone' } = $props();

	let world = $state<CircuitWorld | null>(null);

	const create = () => import('./circuit').then(({ CircuitWorld }) => new CircuitWorld(view, me));

	$effect(() => {
		const colours = new Map([...people.values()].map((p) => [p.id, COLOURS[p.colour]]));
		world?.update(circuit, colours);
	});

	const order = $derived([...circuit.karts].sort((a, b) => b.m - a.m));
	const place = $derived(me ? order.findIndex((k) => k.id === me) + 1 : 0);
	const lapOf = (m: number) => Math.min(circuit.laps, Math.floor((Math.min(m, circuit.length) / Math.max(1, circuit.length)) * circuit.laps) + 1);
	const done = (m: number) => m >= circuit.length;
	const mineKart = $derived(order.find((k) => k.id === me));
	// Name tags: the leaders on the big screen; on a phone, the kart just ahead (the one to catch).
	const ahead = $derived(place > 1 ? order[place - 2] : null);
	const tagged = $derived(view === 'host' ? order.slice(0, 6) : ahead && mineKart && ahead.m > mineKart.m ? [ahead] : []);
	const nameOf = (id: string) => (id === me ? 'Kamu' : (people.get(id)?.name ?? 'Pemain'));
	const label = $derived(
		view === 'phone' && mineKart
			? `Litar: kamu di tempat ke-${place}, pusingan ${lapOf(mineKart.m)} daripada ${circuit.laps}.`
			: order.length
				? `Litar: ${nameOf(order[0].id)} mendahului, pusingan ${lapOf(order[0].m)} daripada ${circuit.laps}.`
				: 'Litar kart.'
	);
</script>

<div class="kart kart--{view}">
	<Stage3D {create} bind:world {label}>
		{#snippet fallback()}
			<ol class="plain">
				{#each order.slice(0, 5) as kart, i (kart.id)}
					<li class:mine={kart.id === me}>{i + 1}. {nameOf(kart.id)}: {kart.m} m, pusingan {lapOf(kart.m)}/{circuit.laps}</li>
				{/each}
			</ol>
		{/snippet}
		{#if world}
			{#each tagged as kart (kart.id)}
				<span class="tag" class:mine={kart.id === me} {@attach world.tags.attach(kart.id)}>
					{nameOf(kart.id)}{#if view === 'phone' && mineKart}<small class="gap">+{kart.m - mineKart.m} m</small>{/if}
				</span>
			{/each}
		{/if}
		{#if view === 'phone' && mineKart}
			<p class="chip-row">
				<span class="pill">{done(mineKart.m) ? 'Selesai!' : `Pusingan ${lapOf(mineKart.m)}/${circuit.laps}`}</span>
				{#if circuit.nitro.includes(mineKart.id)}<span class="pill nitro">Nitro!</span>{/if}
			</p>
		{:else if view === 'host'}
			<ol class="leaders" aria-label="Lima teratas">
				{#each order.slice(0, 5) as kart, i (kart.id)}
					<li>
						<span class="pos">{i + 1}</span>
						<span class="swatch" style:background={COLOURS[people.get(kart.id)?.colour ?? ''] ?? 'var(--sun)'}></span>
						<span class="who">{nameOf(kart.id)}</span>
						<span class="lap">{done(kart.m) ? 'Selesai' : `P${lapOf(kart.m)}`}</span>
						{#if circuit.nitro.includes(kart.id)}<span class="boost">Nitro</span>{/if}
					</li>
				{/each}
			</ol>
		{/if}
	</Stage3D>
</div>

<style>
	.kart {
		position: relative;
		height: 100%;
		border-radius: inherit;
		--stage-bg: #5f7fa0;
	}
	.kart--phone {
		height: clamp(11rem, 30svh, 16rem);
		border-radius: var(--r-lg);
		overflow: hidden;
	}
	.tag {
		position: absolute;
		top: 0;
		left: 0;
		visibility: hidden;
		padding: 0.15rem 0.5rem;
		border-radius: var(--r-pill);
		border: 2px solid #071418;
		background: #0f1f24;
		color: #fff;
		font: 700 0.8rem/1.2 var(--font-body);
		white-space: nowrap;
		will-change: transform;
	}
	.gap {
		margin-left: 0.35em;
		color: var(--sun);
	}
	.tag.mine {
		background: var(--sun);
		color: var(--on-bright);
	}
	.kart--host .tag {
		font-size: 0.95rem;
	}
	.chip-row {
		position: absolute;
		top: 0.6rem;
		left: 0.6rem;
		display: flex;
		gap: 0.4rem;
	}
	.pill {
		padding: 0.2rem 0.65rem;
		border-radius: var(--r-pill);
		border: 2px solid #071418;
		background: #0f1f24;
		color: #fff;
		font: 600 0.95rem var(--font-display);
	}
	.pill.nitro {
		background: var(--sun);
		color: var(--on-bright);
	}
	.leaders {
		position: absolute;
		top: 0.9rem;
		left: 0.9rem;
		display: grid;
		gap: 0.3rem;
		margin: 0;
		padding: 0.7rem 0.8rem;
		border-radius: var(--r-md);
		border: 2px solid #071418;
		background: #0f1f24;
		color: #fff;
		list-style: none;
		min-width: 15rem;
	}
	.leaders li {
		display: flex;
		align-items: center;
		gap: 0.55rem;
		font-weight: 700;
	}
	.pos {
		width: 1.2rem;
		font: 600 1.1rem var(--font-display);
		color: var(--sun);
		text-align: center;
	}
	.swatch {
		width: 0.7rem;
		height: 0.7rem;
		border-radius: 3px;
		flex: none;
	}
	.who {
		flex: 1;
		min-width: 0;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}
	.lap {
		color: #c9d6d3;
		font-variant-numeric: tabular-nums;
	}
	.boost {
		padding: 0 0.4rem;
		border-radius: var(--r-pill);
		background: var(--sun);
		color: var(--on-bright);
		font-size: 0.8rem;
	}
	.plain {
		margin: 0;
		padding: 1rem 1.2rem;
		border-radius: var(--r-lg);
		background: var(--card);
		list-style: none;
		font-weight: 700;
	}
	.plain .mine {
		color: var(--brand-ink);
	}
</style>
