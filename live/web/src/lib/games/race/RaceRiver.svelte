<!--
	Lumba Sampan's river in the worlds' 3/4 view: a jetty at the start, a line of buoys and a banner at
	the finish, trees along the far bank, and every child paddling their own boat in their own lane.
	Distance is drawn to scale. On a phone the view follows the child's boat and shows the boats
	nearest to it; on the big screen the whole river fits.
-->
<script lang="ts">
	import type { Person } from '$lib/types';
	import { COLOURS } from '$lib/names';
	import Chibi from '$ui/Chibi.svelte';
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
	const LANE = 1.45;
	const TOP = 2.2; // where the water begins, below the far bank

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
	// five lanes around the child's own boat.
	const lanes = $derived.by(() => {
		const boats = race.boats.filter((b) => people.has(b.id));
		if (!compact || !me) return boats;
		const at = boats.findIndex((b) => b.id === me);
		if (at < 0) return boats.slice(0, 5);
		const from = Math.max(0, Math.min(at - 2, boats.length - 5));
		return boats.slice(from, from + 5);
	});

	const H = $derived(TOP + Math.max(lanes.length, 3) * LANE + 1.9);
	const bottom = $derived(TOP + Math.max(lanes.length, 3) * LANE + 0.35);
	const laneY = (i: number) => TOP + 0.95 + i * LANE;
	const boatX = (m: number) => START + Math.min(1, m / Math.max(1, race.length)) * (FINISH - START + 0.6);

	let width = $state(0);
	let innerHeight = $state(800);
	// A phone shows ten tiles of river around the child's boat; the big screen fits the whole river
	// into about a third of its height, so the question above stays in view.
	const tile = $derived(
		compact ? Math.max(28, Math.min(40, width / 10)) : Math.max(16, Math.min(width / W, (innerHeight * 0.36) / H, 52))
	);

	const scenery = $derived<WorldProp[]>([
		...[1.2, 4.6, 7.4, 10.9, 13.6, 16.8, 21.2].map((x, i) => ({
			id: `far${i}`,
			kind: i % 3 === 1 ? 'palm' : 'tree',
			x,
			y: 1.25 + (i % 2) * 0.15,
			variant: i % 3
		})),
		{ id: 'pondok', kind: 'pondok', x: 6.0, y: 1.9 },
		...[3.2, 9.2, 15.0].map((x, i) => ({ id: `reeds${i}`, kind: 'reeds', x, y: TOP + 0.25 })),
		{ id: 'start', kind: 'banner', x: 1.3, y: 2.05, state: 'MULA', variant: 1 },
		{ id: 'finish', kind: 'banner', x: FINISH + 0.7, y: 2.05, state: 'PENAMAT', variant: 0 },
		...[2.0, 8.0, 12.5, 18.0].map((x, i) => ({ id: `near${i}`, kind: i % 2 ? 'flowers' : 'reeds', x, y: bottom + 0.55, variant: i % 2 })),
		{ id: 'bench', kind: 'bench', x: 14.6, y: bottom + 1.25 },
		{ id: 'near-bush', kind: 'bush', x: 5.4, y: bottom + 1.35, variant: 0 }
	]);

	const boats = $derived<WorldProp[]>(
		lanes.map((boat, i) => ({ id: boat.id, kind: 'boat', custom: true, glide: true, x: boatX(boat.m), y: laneY(i) + 0.32 }))
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
		<div
			class="boat"
			class:mine={prop.id === me}
			class:rowing={rowing.has(prop.id)}
			class:ahead={prop.x > W / 2}
			style:--t="{tile}px"
			style:--flag={COLOURS[person.colour] ?? COLOURS.hijau}
		>
			{#if !compact || prop.id === me}<span class="name">{prop.id === me ? 'Kamu' : person.name}</span>{/if}
			<svg class="hull back" viewBox="0 0 120 50" aria-hidden="true">
				<ellipse cx="60" cy="46" rx="56" ry="5" fill="#bfe6f6" opacity=".8" />
				<path class="wake" d="M-6 40 q8 -6 16 0 M-20 44 q8 -6 16 0" stroke="#fff" stroke-width="3" fill="none" stroke-linecap="round" />
				<rect x="11" y="-16" width="3" height="32" fill="#8e5a2e" />
				<path d="M14 -16 l18 6 -18 6z" fill="var(--flag)" />
				<ellipse cx="60" cy="16" rx="57" ry="12" fill="#c9572e" />
				<ellipse cx="60" cy="16.5" rx="51" ry="8.5" fill="#6b3a20" />
			</svg>
			<span class="rider">
				<Chibi animal={person.avatar} colour={person.colour} skin={person.skin} size={Math.round(tile * 0.95)} mood={finished(boat.m) ? 'cheer' : 'happy'} walking={false} />
			</span>
			<svg class="hull front" viewBox="0 0 120 50" aria-hidden="true">
				<path class="paddle" d="M78 2 L96 44" stroke="#8e5a2e" stroke-width="4" stroke-linecap="round" />
				<ellipse class="paddle blade" cx="97" cy="45" rx="5" ry="8" fill="#a46a37" transform="rotate(-24 97 45)" />
				<path d="M3 16 Q8 44 60 46 Q112 44 117 16 Q60 31 3 16z" fill="#c9572e" />
				<path d="M12 27 Q60 41 108 27" stroke="#f7c948" stroke-width="3.5" fill="none" stroke-linecap="round" />
				<path d="M3 16 Q60 31 117 16" stroke="#e8774c" stroke-width="3" fill="none" />
			</svg>
		</div>
	{/if}
{/snippet}

<figure class="river" class:compact class:rapids={race.rapids} bind:clientWidth={width}>
	<div class="frame" style:height={compact ? `${H * tile}px` : undefined} style:max-width={compact ? undefined : `${W * tile}px`}>
		<World width={W} height={H} {tile} props={[...scenery, ...boats]} actors={[]} {me} follow={compact} {focus} {art}>
			{#snippet ground()}
				<rect width={W} height={H} fill="#8fd05e" />
				<!-- The river, its sandy near bank and the jetty at the start. -->
				<rect y={TOP} width={W} height={bottom - TOP} fill="#3ba7d9" />
				<rect y={TOP} width={W} height="0.14" fill="#bfe6f6" />
				<rect y={bottom} width={W} height="0.5" fill="#e9cf98" />
				<!-- Ripples every 3.7 tiles in each band, so moving them by 3.7 loops without a seam. -->
				<g class="flow">
					{#each Array.from({ length: Math.max(lanes.length, 3) + 1 }, (_, row) => row) as row (row)}
						{#each Array.from({ length: 8 }, (_, k) => k) as k (k)}
							<path d="M{k * 3.7 - 3.7 + (row % 2) * 1.85} {TOP + 0.45 + row * LANE} q0.5 -0.22 1 0 t1 0" stroke="#9fd8f0" stroke-width="0.07" fill="none" stroke-linecap="round" />
						{/each}
					{/each}
				</g>
				<rect x="-0.1" y={TOP - 0.15} width="1.9" height={bottom - TOP + 0.3} fill="#c98a54" />
				{#each Array.from({ length: Math.ceil((bottom - TOP) / 0.5) }, (_, i) => i) as i (i)}
					<path d="M-0.1 {TOP + i * 0.5} H1.8" stroke="#a46a37" stroke-width="0.05" />
				{/each}
				<!-- The finish: a line of red and white buoys across the river. -->
				{#each Array.from({ length: Math.ceil((bottom - TOP) / 0.45) }, (_, i) => i) as i (i)}
					<circle cx={FINISH + 0.5} cy={TOP + 0.3 + i * 0.45} r="0.16" fill={i % 2 ? '#fff' : '#e2483d'} />
				{/each}
			{/snippet}
		</World>
		{#if race.rapids}<p class="rapids-banner">Arus deras! Semua sampan meluncur ke depan</p>{/if}
	</div>
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
	.flow {
		animation: flow 7s linear infinite;
	}
	.rapids .flow {
		animation-duration: 1.4s;
	}
	/* In the ground drawing one px is one tile. */
	@keyframes flow {
		to {
			transform: translateX(3.7px);
		}
	}
	.boat {
		position: relative;
		width: calc(var(--t) * 2.4);
		height: calc(var(--t) * 1.75);
		animation: bob-boat 2.8s ease-in-out infinite;
	}
	.hull {
		position: absolute;
		left: 0;
		bottom: 0;
		width: 100%;
		height: calc(var(--t) * 1);
		overflow: visible;
	}
	.rider {
		position: absolute;
		left: 50%;
		bottom: calc(var(--t) * 0.45);
		translate: -46% 0;
		line-height: 0;
	}
	.wake {
		opacity: 0;
	}
	.rowing .wake {
		animation: wake 0.7s ease-out 2;
	}
	.paddle {
		transform-box: view-box;
		transform-origin: 78px 2px;
	}
	.rowing .paddle {
		animation: row 0.45s ease-in-out 3;
	}
	/* Name tags trail behind a boat once it is past halfway, and lead it before that, so a tag never
	   runs off either end of the river. */
	.name {
		position: absolute;
		left: calc(100% - var(--t) * 0.1);
		bottom: calc(var(--t) * 0.35);
		padding: 0 0.45rem;
		border-radius: var(--r-pill);
		background: rgb(255 255 255 / 0.9);
		font-size: 0.72rem;
		font-weight: 800;
		line-height: 1.6;
		white-space: nowrap;
	}
	.ahead .name {
		left: auto;
		right: calc(100% - var(--t) * 0.1);
	}
	.mine .name {
		background: var(--sun);
	}
	.rapids-banner {
		position: absolute;
		top: 0.6rem;
		left: 50%;
		z-index: 1001;
		translate: -50% 0;
		padding: 0.35rem 1rem;
		border-radius: var(--r-pill);
		background: #fff;
		color: var(--sky-deep);
		font: 600 1.05rem var(--font-display);
		white-space: nowrap;
		box-shadow: var(--lift-low);
		animation: pop-in 500ms var(--spring);
	}
	@keyframes bob-boat {
		0%,
		100% {
			transform: translateY(0) rotate(-1deg);
		}
		50% {
			transform: translateY(-2px) rotate(1deg);
		}
	}
	@keyframes row {
		50% {
			transform: rotate(28deg);
		}
	}
	@keyframes wake {
		from {
			opacity: 1;
			transform: translateX(0);
		}
		to {
			opacity: 0;
			transform: translateX(-10px);
		}
	}
</style>
