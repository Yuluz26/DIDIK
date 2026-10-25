<!--
	Lumba Sampan's river in pixel art: a jetty at the start, a chain of floats and a banner at the
	finish, trees along the far bank, lane ropes between the lanes, and every child paddling their own
	boat in their own lane. Distance is drawn to scale. On a phone the view follows the child's boat and
	shows the boats nearest to it; on the big screen the whole river fits, with ten lanes at most.
-->
<script lang="ts">
	import { RIPPLE, riverGround, ripples } from '$lib/games/race/sprites';
	import { TILE, fitTile, prescale, urlOf } from '$lib/pixel/cache';
	import type { Person } from '$lib/types';
	import Sampan from '$lib/worlds/Sampan.svelte';
	import World, { type WorldProp } from '$lib/worlds/World.svelte';

	interface Race {
		length: number;
		rapids: boolean;
		boats: { id: string; m: number }[];
	}

	let {
		race,
		people,
		me = null,
		compact = false
	}: { race: Race; people: Map<string, Person>; me?: string | null; compact?: boolean } = $props();

	const W = 22;
	const START = 2.6;
	const FINISH = 19.6;
	const TOP = 2.4; // where the water begins, below the far bank
	const MAX_LANES = 10;

	// Remember who moved, so their paddle swings for a moment.
	let previous = new Map<string, number>();
	let rowing = $state(new Set<string>());

	$effect(() => {
		const moved = new Set<string>();
		for (const boat of race.boats) {
			if ((previous.get(boat.id) ?? 0) !== boat.m) moved.add(boat.id);
		}
		previous = new Map(race.boats.map((b) => [b.id, b.m]));
		if (!moved.size) return;
		rowing = moved;
		const timer = setTimeout(() => (rowing = new Set()), 1400);
		return () => clearTimeout(timer);
	});

	// Lanes keep the order children joined in, so a boat never jumps lanes; on a phone, only the
	// five lanes around the child's own boat. A class bigger than the big screen's ten lanes sees the
	// ten boats in front instead, in order, changing lanes as they overtake.
	const racing = $derived(race.boats.filter((b) => people.has(b.id)));
	const lanes = $derived.by(() => {
		const boats = racing;
		if (!compact || !me) return boats.length <= room ? boats : [...boats].sort((a, b) => b.m - a.m).slice(0, room);
		const at = boats.findIndex((b) => b.id === me);
		if (at < 0) return boats.slice(0, 5);
		const from = Math.max(0, Math.min(at - 2, boats.length - 5));
		return boats.slice(from, from + 5);
	});
	const behind = $derived(compact ? 0 : racing.length - lanes.length);

	let width = $state(0);
	let innerHeight = $state(800);

	// The big screen gives the river about half its height, below the question. The pixels are drawn
	// at least one and a half times their size, so the river holds as many lanes as fit that way (ten
	// at most); a bigger class sees the boats in front.
	const avail = $derived(innerHeight * 0.46);
	const room = $derived(compact ? 5 : Math.max(3, Math.min(MAX_LANES, Math.floor((avail / (TILE * 1.5) - TOP - 1.9) / 1.45))));

	// A boat and its child are taller than a lane is wide when many share the screen; fewer boats get
	// roomier lanes.
	const count = $derived(Math.max(lanes.length, 3));
	const LANE = $derived(compact ? 2.1 : count > 6 ? 1.45 : count > 4 ? 1.8 : 2.1);
	const H = $derived(TOP + count * LANE + 1.9);
	const bottom = $derived(TOP + count * LANE + 0.35);
	const laneY = (i: number) => TOP + 0.95 + i * LANE;
	const boatX = (m: number) => START + Math.min(1, m / Math.max(1, race.length)) * (FINISH - START + 0.6);

	// A phone shows ten tiles of river around the child's boat.
	const tile = $derived(compact ? fitTile(width, 10, { min: 2, max: 48 }) : fitTile(width, W, { availH: avail, rows: H, min: 1.5, max: 64 }));
	const s = $derived(tile / TILE);

	const ground = $derived(riverGround({ W, TOP, LANE, lanes: count, finish: FINISH }));
	const ripple = $derived(urlOf(ripples(), prescale(s)));

	const scenery = $derived<WorldProp[]>([
		...[1.2, 4.6, 7.4, 10.9, 13.6, 16.8, 21.2].map((x, i) => ({
			id: `far${i}`,
			kind: i % 3 === 1 ? 'palm' : 'tree',
			x,
			y: 1.6 + (i % 2) * 0.15,
			variant: i % 3
		})),
		{ id: 'pondok', kind: 'pondok', x: 6.0, y: 2.1 },
		...[3.2, 9.2, 15.0].map((x, i) => ({ id: `reeds${i}`, kind: 'reeds', x, y: TOP + 0.3 })),
		{ id: 'start', kind: 'banner', x: 1.3, y: 2.3, state: 'MULA', variant: 1 },
		{ id: 'finish', kind: 'banner', x: FINISH + 0.7, y: 2.3, state: 'PENAMAT', variant: 0 },
		...[2.0, 8.0, 12.5, 18.0].map((x, i) => ({ id: `near${i}`, kind: i % 2 ? 'flowers' : 'reeds', x, y: bottom + 0.75, variant: i % 2 })),
		{ id: 'bench', kind: 'bench', x: 14.6, y: bottom + 1.45 },
		{ id: 'near-bush', kind: 'bush', x: 5.4, y: bottom + 1.5, variant: 0 }
	]);

	// A boat's foot is the waterline at the middle of its lane.
	const boats = $derived<WorldProp[]>(
		lanes.map((boat, i) => ({ id: boat.id, kind: 'boat', custom: true, glide: true, x: boatX(boat.m), y: laneY(i) + 0.55 }))
	);

	const mine = $derived(boats.find((b) => b.id === me));
	const focus = $derived(mine ? { x: Math.max(mine.x, 4), y: H / 2 } : null);
	const finished = (m: number) => m >= race.length;
</script>

<svelte:window bind:innerHeight />

{#snippet art(prop: WorldProp, tile: number)}
	{@const boat = race.boats.find((b) => b.id === prop.id)}
	{@const person = people.get(prop.id)}
	{#if boat && person}
		<div class="lane-boat" class:mine={prop.id === me} class:ahead={prop.x > W / 2}>
			<Sampan {tile} animal={person.avatar} colour={person.colour} skin={person.skin} mood={finished(boat.m) ? 'cheer' : 'happy'} rowing={rowing.has(prop.id)}>
				{#if !compact || prop.id === me}<span class="name">{prop.id === me ? 'Kamu' : person.name}</span>{/if}
			</Sampan>
		</div>
	{/if}
{/snippet}

{#snippet under(t: number)}
	<div class="water" style:top="{TOP * t}px" style:height="{(bottom - TOP) * t}px">
		<span class="drift" style:--period="{RIPPLE.w * s}px" style:background-image="url({ripple})" style:background-size="{RIPPLE.w * s}px {RIPPLE.h * s}px"></span>
	</div>
{/snippet}

<figure class="river" class:compact class:rapids={race.rapids} bind:clientWidth={width}>
	<div class="frame" style:height={compact ? `${H * tile}px` : undefined} style:max-width={compact ? undefined : `${W * tile}px`}>
		<World width={W} height={H} {tile} {ground} {under} props={[...scenery, ...boats]} actors={[]} {me} follow={compact} {focus} {art} />
		{#if race.rapids}<p class="rapids-banner">Arus deras! Semua sampan meluncur ke depan</p>{/if}
	</div>
	{#if behind > 0}<figcaption class="behind">{lanes.length} sampan terdepan. {behind} lagi sedang mengejar.</figcaption>{/if}
</figure>

<style>
	.river {
		position: relative;
		margin: 0;
		min-width: 0;
	}
	.frame {
		position: relative;
		width: 100%;
		margin-inline: auto;
	}
	.compact .frame :global(.viewport) {
		height: 100%;
	}
	/* The view follows the child's boat as smoothly as the boat glides. */
	.compact .frame :global(.world) {
		transition-duration: 1.1s;
		transition-timing-function: var(--ease-out);
	}
	/* The water drifts to the right, one sprite pixel at a time. */
	.water {
		position: absolute;
		left: 0;
		width: 100%;
		overflow: hidden;
	}
	.drift {
		position: absolute;
		inset: 0 0 0 calc(var(--period) * -1);
		background-repeat: repeat;
		animation: drift 8s steps(64) infinite;
	}
	.rapids .drift {
		animation-duration: 1.6s;
	}
	@keyframes drift {
		to {
			transform: translateX(var(--period));
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.drift {
			animation: none;
		}
	}
	/* Name tags trail behind a boat once it is past halfway, and lead it before that, so a tag never
	   runs off either end of the river. */
	.name {
		position: absolute;
		left: calc(100% - var(--t) * 0.1);
		bottom: calc(var(--t) * 0.35);
		padding: 0 0.4rem;
		border: 2px solid #2a1f2d;
		border-radius: 4px;
		background: #fff6e6;
		color: #2a1f2d;
		font: 600 0.72rem/1.35 var(--font-pixel);
		white-space: nowrap;
	}
	.ahead .name {
		left: auto;
		right: calc(100% - var(--t) * 0.1);
	}
	.mine .name {
		background: var(--sun);
	}
	.behind {
		margin-top: 0.4rem;
		color: var(--ink-2);
		font-weight: 700;
		font-size: 0.92rem;
		text-align: center;
	}
	.rapids-banner {
		position: absolute;
		top: 0.6rem;
		left: 50%;
		z-index: 1001;
		translate: -50% 0;
		padding: 0.35rem 1rem;
		border: 2px solid #2a1f2d;
		border-radius: 4px;
		background: #fff6e6;
		color: var(--sky-deep);
		font: 600 1.05rem var(--font-pixel);
		white-space: nowrap;
		animation: pop-in 500ms var(--spring);
	}
</style>
