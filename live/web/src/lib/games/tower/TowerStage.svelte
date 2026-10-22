<!--
	Menara 118. On a phone: the top of the class's tower; after a right answer the player's block
	slides above it until they press Letak. On the big screen: the whole tower inside the outline of
	Merdeka 118, beside Komtar, Menara Kuala Lumpur and Petronas at their real heights.
-->
<script lang="ts">
	import type { RoomClient } from '$lib/room.svelte';
	import type { Person } from '$lib/types';
	import { COLOURS } from '$lib/names';
	import { play } from '$lib/sound';
	import Icon from '$ui/Icon.svelte';
	import Stage3D from '$lib/three/Stage3D.svelte';
	import type { Block, Landmark, SkylineWorld } from './skyline';

	interface Seen {
		height: number;
		goal: number;
		count: number;
		landmarks: Landmark[];
		blocks?: [string, number, number][];
		top?: [string, number, number, number][];
		block?: number;
		mine?: number;
	}

	let {
		client = null,
		world: seen,
		people,
		view,
		step = null,
		me = null,
		reward = null
	}: {
		client?: RoomClient | null;
		world: Seen;
		people: Map<string, Person>;
		view: 'host' | 'phone';
		step?: string | null;
		me?: { id: string; colour: string } | null;
		// eslint-disable-next-line @typescript-eslint/no-explicit-any
		reward?: any;
	} = $props();

	let world = $state<SkylineWorld | null>(null);

	const create = () => import('./skyline').then(({ SkylineWorld }) => new SkylineWorld(view));

	// The big screen gets every block from the ground up; a phone gets the top few with their bases.
	const blocks = $derived.by((): Block[] => {
		if (seen.top) return seen.top.map(([who, m, x, base]) => ({ who, m, x, base }));
		let base = 0;
		return (seen.blocks ?? []).map(([who, m, x]) => {
			const block = { who, m, x, base };
			base += m;
			return block;
		});
	});

	$effect(() => {
		const colours = new Map([...people.values()].map((p) => [p.id, COLOURS[p.colour]]));
		world?.update({ height: seen.height, blocks, block: seen.block, landmarks: seen.landmarks }, colours);
	});

	$effect(() => {
		world?.slide(step === 'drop', me ? COLOURS[me.colour] : undefined);
	});

	let flashed = '';
	$effect(() => {
		const key = reward ? JSON.stringify(reward) : '';
		if (!world || !reward || reward.kind !== 'dropped' || key === flashed) return;
		flashed = key;
		if (reward.perfect) world.perfect();
	});

	function drop() {
		if (!client) return;
		play('build');
		// Without the 3D view there is nothing to aim, so the block lands a little off-centre.
		const x = world ? world.drop() : (Math.random() - 0.5) * 0.3;
		client.send({ t: 'drop', x: Number(x.toFixed(3)) });
	}

	const next = $derived(seen.landmarks.find((l) => !l.passed));
	const share = $derived(Math.min(1, seen.height / seen.goal));
	const label = $derived(
		`Menara kelas setinggi ${Math.round(seen.height)} meter daripada ${seen.goal}.${next ? ` Seterusnya: ${next.name}, ${next.m} meter.` : ' Setinggi Merdeka 118!'}`
	);
	const short = (name: string) => name.replace('Menara Berkembar ', '').replace('Menara Kuala Lumpur', 'Menara KL');
</script>

<div class="tower tower--{view}">
	<div class="stage">
		<Stage3D {create} bind:world {label}>
			{#snippet fallback()}
				<p class="plain">{Math.round(seen.height)} m daripada {seen.goal} m</p>
			{/snippet}
			{#if world && view === 'host'}
				<span class="tag ours" {@attach world.tags.attach('kita')}>Menara kita · {Math.round(seen.height)} m</span>
				{#each seen.landmarks.filter((l) => l.key !== 'merdeka') as mark (mark.key)}
					<span class="tag" class:passed={mark.passed} {@attach world.tags.attach(mark.key)}>
						{#if mark.passed}<Icon name="check" size={14} />{/if}{short(mark.name)} · {mark.m} m
					</span>
				{/each}
			{/if}
			<div class="meter">
				<strong>{Math.round(seen.height)}</strong> / {seen.goal} m
				<span class="bar"><span style:transform="scaleX({share})"></span></span>
				{#if next && next.key !== 'merdeka'}<small>Seterusnya: {short(next.name)} ({next.m} m)</small>{:else if next}<small>Puncak: Merdeka 118</small>{/if}
			</div>
		</Stage3D>
	</div>
	{#if view === 'phone' && step === 'drop'}
		<button type="button" class="btn btn--sun btn--big drop" onclick={drop}>Letak blok <Icon name="next" /></button>
		<p class="hint">Tekan bila blok berada tepat di atas menara.</p>
	{:else if view === 'phone' && seen.mine}
		<p class="hint">Kamu sudah menambah {seen.mine} m pada menara.</p>
	{/if}
</div>

<style>
	.tower {
		display: grid;
		gap: 0.7rem;
	}
	.stage {
		position: relative;
		border-radius: var(--r-lg);
		overflow: hidden;
		--stage-bg: #3c4f72;
	}
	.tower--phone .stage {
		height: clamp(15rem, 44svh, 24rem);
	}
	.tower--host .stage {
		height: clamp(22rem, calc(100dvh - 12rem), 40rem);
	}
	.meter {
		position: absolute;
		top: 0.7rem;
		left: 0.7rem;
		display: grid;
		gap: 0.25rem;
		padding: 0.45rem 0.75rem;
		border-radius: var(--r-md);
		background: rgb(15 31 36 / 0.84);
		color: #fff;
		font-weight: 700;
		min-width: 11rem;
	}
	.meter strong {
		font: 600 1.5rem/1 var(--font-display);
		font-variant-numeric: tabular-nums;
	}
	.tower--host .meter strong {
		font-size: 2.2rem;
	}
	.tower--phone .meter {
		min-width: 0;
		padding: 0.35rem 0.6rem;
		font-size: 0.9rem;
	}
	.tower--phone .meter strong {
		font-size: 1.25rem;
	}
	.meter small {
		color: #c9d6d3;
		font-size: 0.85rem;
	}
	.bar {
		display: block;
		height: 6px;
		border-radius: 3px;
		background: rgb(255 255 255 / 0.18);
		overflow: hidden;
	}
	.bar span {
		display: block;
		height: 100%;
		background: var(--sun);
		transform-origin: left;
		transition: transform 600ms var(--ease-out);
	}
	.tag {
		position: absolute;
		top: 0;
		left: 0;
		display: inline-flex;
		align-items: center;
		gap: 0.25rem;
		visibility: hidden;
		padding: 0.15rem 0.55rem;
		border-radius: var(--r-pill);
		background: rgb(15 31 36 / 0.8);
		color: #fff;
		font: 600 0.9rem var(--font-display);
		white-space: nowrap;
	}
	.tag.passed {
		background: var(--sun);
		color: var(--on-bright);
	}
	.tag.ours {
		background: var(--sea);
		font-size: 1rem;
	}
	.drop {
		width: 100%;
	}
	.hint {
		color: var(--ink-2);
		font-weight: 700;
		text-align: center;
	}
	.plain {
		padding: 3rem 1rem;
		font: 600 1.4rem var(--font-display);
		text-align: center;
	}
</style>
