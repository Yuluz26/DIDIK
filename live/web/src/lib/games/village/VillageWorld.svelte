<!--
	Kampung Kita: the village the whole room builds. Seven lots along a kampung road, each building
	rising as answers bring material, the biggest helpers at work beside the one going up, and a
	padang in front where children put the decorations they have earned.
-->
<script lang="ts">
	import { untrack } from 'svelte';
	import type { RoomClient } from '$lib/room.svelte';
	import type { Person } from '$lib/types';
	import { confetti } from '$lib/confetti';
	import { play } from '$lib/sound';
	import Prop from '$lib/worlds/Prop.svelte';
	import World, { type WorldActor, type WorldProp } from '$lib/worlds/World.svelte';

	interface Building {
		key: string;
		name: string;
		cost: number;
		done: boolean;
		progress: number;
	}

	interface Site {
		buildings: Building[];
		built: number;
		decor: { id: number; kind: string; x: number; y: number; by: string }[];
		helpers?: { id: string; n: number }[];
		tokens?: number;
		mine?: number;
	}

	let {
		client,
		world,
		people,
		me = null,
		big = false
	}: { client: RoomClient; world: Site; people: Map<string, Person>; me?: string | null; big?: boolean } = $props();

	const W = 16;
	const H = 12;
	// Each building's lot (the middle of its front edge): four behind the road, three before the padang.
	const LOTS: Record<string, [number, number]> = {
		rumah: [2.2, 4.4],
		sekolah: [6.1, 4.4],
		masjid: [9.9, 4.4],
		balai: [13.8, 4.4],
		kedai: [3.0, 9.0],
		rumahpanjang: [8.0, 9.0],
		jeti: [13.0, 9.0]
	};
	// The padang in tiles. The server keeps decorations inside the same field (PADANG_X, PADANG_Y).
	const PADANG = { x0: 0.04 * W, x1: 0.96 * W, y0: 0.8 * H, y1: 0.97 * H };
	const DECOR = [
		{ key: 'kelapa', prop: 'palm', name: 'Kelapa' },
		{ key: 'bunga', prop: 'hibiscus', name: 'Bunga raya' },
		{ key: 'pelita', prop: 'pelita', name: 'Pelita' },
		{ key: 'wau', prop: 'wau', name: 'Wau' },
		{ key: 'kucing', prop: 'cat', name: 'Kucing' },
		{ key: 'ayam', prop: 'hen', name: 'Ayam' }
	];
	const PROP_OF: Record<string, string> = Object.fromEntries(DECOR.map((d) => [d.key, d.prop]));

	// What was always there: trees along the back, lamps by the road, palms between the houses.
	const SCENERY: WorldProp[] = [
		...[0.5, 1.8, 3.9, 5.2, 7.9, 9.1, 11.8, 13.1, 15.4].map((x, i) => ({
			id: `back${i}`,
			kind: i % 3 === 1 ? 'palm' : 'tree',
			x,
			y: 1.0 + (i % 2) * 0.15,
			variant: i % 3
		})),
		...[4.15, 8.0, 11.85].map((x, i) => ({ id: `lamp${i}`, kind: 'lamp', x, y: 4.62 })),
		{ id: 'gap-palm', kind: 'palm', x: 5.45, y: 8.8 },
		{ id: 'gap-flowers-l', kind: 'flowers', x: 9.75, y: 9.0 },
		{ id: 'gap-flowers-r', kind: 'flowers', x: 11.25, y: 9.0, variant: 1 },
		{ id: 'edge-bush', kind: 'bush', x: 0.7, y: 8.9, variant: 2 },
		{ id: 'edge-palm', kind: 'palm', x: 15.3, y: 8.95 }
	];
	const hash = (x: number, y: number) => ((x * 73856093) ^ (y * 19349663)) >>> 0;
	const TUFTS: [number, number][] = [];
	for (let y = 0; y < 9; y++) for (let x = 0; x < W; x++) if (hash(x, y) % 5 === 0 && (y < 4 || y > 5)) TUFTS.push([x, y]);
	// Where helpers stand around the building going up, relative to its lot: rows far enough apart
	// that name tags do not run into each other.
	const SPOTS: [number, number][] = [
		[-1.2, 0.45], [1.2, 0.45],
		[0, 1.0], [-2.4, 1.0], [2.4, 1.0],
		[-1.2, 1.55], [1.2, 1.55], [-3.6, 1.55], [3.6, 1.55],
		[0, 2.1], [-2.4, 2.1], [2.4, 2.1]
	];

	let width = $state(0);
	let innerHeight = $state(800);
	// The whole village always fits: by width on a phone, by width and height on the big screen.
	const tile = $derived(Math.max(14, Math.min(width / W, big ? (innerHeight * 0.66) / H : 64)));

	const current = $derived(world.buildings.find((b) => !b.done) ?? null);
	const tokens = $derived(world.tokens ?? 0);

	// ------------------------------------------------------------ who is at work

	let carried = $state<Record<string, { n: number; key: number }>>({});
	let cheering = $state(false);
	let before = new Map<string, number>();
	let counter = 0;

	$effect(() => {
		const helpers = world.helpers ?? [];
		const fresh: Record<string, { n: number; key: number }> = {};
		for (const h of helpers) {
			const was = before.get(h.id);
			if (was !== undefined && h.n > was) fresh[h.id] = { n: h.n - was, key: ++counter };
		}
		before = new Map(helpers.map((h) => [h.id, h.n]));
		if (!Object.keys(fresh).length) return;
		untrack(() => (carried = { ...carried, ...fresh }));
		setTimeout(() => {
			const left = { ...carried };
			for (const [id, c] of Object.entries(fresh)) if (left[id]?.key === c.key) delete left[id];
			carried = left;
		}, 1400);
	});

	$effect(() =>
		client.onFx((fx) => {
			if (fx.kind === 'built') {
				cheering = true;
				play('build');
				if (big) confetti({ count: 90 });
				setTimeout(() => (cheering = false), 2400);
			} else if (fx.kind === 'placed' && big) {
				play('pop');
			}
		})
	);

	const crew = $derived.by(() => {
		const ids = (world.helpers ?? []).map((h) => h.id).filter((id) => people.has(id) && id !== me);
		if (me && people.has(me)) ids.unshift(me);
		return ids.slice(0, big ? 12 : 6);
	});

	const actors = $derived<WorldActor[]>(
		crew.map((id, i) => {
			const person = people.get(id)!;
			const [sx, sy] = current ? LOTS[current.key] : [8, 9.4];
			const [dx, dy] = SPOTS[i % SPOTS.length];
			const x = Math.min(W - 0.5, Math.max(0.5, sx + dx * (current ? 1 : 1.6)));
			return {
				id,
				x,
				y: sy + dy,
				facing: x < sx ? 1 : -1,
				walking: !!carried[id],
				animal: person.avatar,
				colour: person.colour,
				skin: person.skin,
				// Only the first few carry a name tag, so a crowd at the site stays readable.
				name: i < 5 ? person.name : '',
				mood: cheering || !current ? 'cheer' : 'happy'
			};
		})
	);

	const items = $derived<WorldProp[]>([
		...SCENERY,
		...world.buildings.map((b) => {
			const [x, y] = LOTS[b.key] ?? [8, 9];
			return {
				id: `lot-${b.key}`,
				kind: b.key,
				x,
				y,
				state: b.done ? 'done' : b === current ? 'building' : 'plot',
				progress: b.cost ? b.progress / b.cost : 0
			};
		}),
		...world.decor.map((d) => ({ id: `decor${d.id}`, kind: PROP_OF[d.kind] ?? 'flowers', x: d.x * W, y: d.y * H, variant: d.id % 3 }))
	]);

	// ------------------------------------------------------------ placing a decoration

	let picked = $state<string | null>(null);
	const pickedName = $derived(DECOR.find((d) => d.key === picked)?.name ?? '');

	$effect(() => {
		if (tokens < 1) picked = null;
	});

	function place(event: MouseEvent) {
		if (!picked) return;
		const box = (event.currentTarget as HTMLElement).getBoundingClientRect();
		// A keyboard press has no position: anywhere on the padang will do.
		const fx = event.detail === 0 ? Math.random() : (event.clientX - box.left) / box.width;
		const fy = event.detail === 0 ? Math.random() : (event.clientY - box.top) / box.height;
		const x = PADANG.x0 + Math.min(1, Math.max(0, fx)) * (PADANG.x1 - PADANG.x0);
		const y = PADANG.y0 + Math.min(1, Math.max(0, fy)) * (PADANG.y1 - PADANG.y0);
		client.send({ t: 'place', kind: picked, x: x / W, y: y / H });
		play('pop');
		picked = null;
	}
</script>

<svelte:window bind:innerHeight />

{#snippet overlay(tile: number)}
	{#if current}
		{@const [lx, ly] = LOTS[current.key]}
		<span class="marker" style:left="{lx * tile}px" style:top="{(ly - 3.3) * tile}px" style:--s="{tile}px"></span>
	{/if}
	{#each actors as actor (actor.id)}
		{#if carried[actor.id]}
			{#key carried[actor.id].key}
				<span class="carried" style:left="{actor.x * tile}px" style:top="{(actor.y - 1.25) * tile}px">+{carried[actor.id].n}</span>
			{/key}
		{/if}
	{/each}
	{#if picked}
		<button
			type="button"
			class="padang"
			style:left="{PADANG.x0 * tile}px"
			style:top="{PADANG.y0 * tile}px"
			style:width="{(PADANG.x1 - PADANG.x0) * tile}px"
			style:height="{(PADANG.y1 - PADANG.y0) * tile}px"
			aria-label="Letak {pickedName} di padang"
			onclick={place}
		>
			<span>Ketik di sini</span>
		</button>
	{/if}
{/snippet}

<div class="stage" bind:clientWidth={width}>
	<div class="village" class:big style:max-width="{W * tile}px">
		<header class="status">
			{#if current}
				<p class="now"><small>Sedang dibina</small> <strong>{current.name}</strong></p>
				<div
					class="bar"
					role="progressbar"
					aria-label="Bahan untuk {current.name}"
					aria-valuemin={0}
					aria-valuemax={current.cost}
					aria-valuenow={current.progress}
				>
					<span style:width="{Math.min(100, (current.progress / current.cost) * 100)}%"></span>
				</div>
				<p class="amount">{current.progress}/{current.cost} bahan</p>
			{:else}
				<p class="now"><strong>Kampung siap!</strong></p>
			{/if}
			<p class="built"><strong>{world.built}</strong>/{world.buildings.length} siap</p>
		</header>

		<div class="map">
			<World width={W} height={H} {tile} props={items} {actors} {me} names={big ? true : 'me'} {overlay}>
				{#snippet ground()}
					<rect width={W} height={H} fill="#8fd05e" />
					{#each TUFTS as [x, y] (`${x}-${y}`)}
						<path d="M{x + 0.3} {y + 0.6} l0.06 -0.16 l0.06 0.16 M{x + 0.62} {y + 0.36} l0.05 -0.13 l0.05 0.13" stroke="#6cb33f" stroke-width="0.05" fill="none" stroke-linecap="round" />
					{/each}
					<!-- The padang, mown in stripes. -->
					<rect x="0.3" y="9.35" width={W - 0.6} height="3" rx="0.5" fill="#a3dc6f" />
					{#each [0, 1, 2, 3] as i (i)}<rect x={0.3 + (i * 2 + 1) * 1.925} y="9.35" width="1.925" height="3" fill="#98d564" />{/each}
					<rect x="0.3" y="9.35" width={W - 0.6} height="0.08" fill="#c4ea9a" />
					<!-- The road, and the lane down to the padang. -->
					<rect x="-0.1" y="4.7" width={W + 0.2} height="1.2" fill="#e9cf98" />
					<rect x="-0.1" y="4.7" width={W + 0.2} height="0.08" fill="#d8b77a" />
					<rect x="-0.1" y="5.82" width={W + 0.2} height="0.08" fill="#d8b77a" />
					<rect x="10.1" y="5.85" width="0.8" height="3.6" rx="0.2" fill="#e9cf98" />
					{#each [1.2, 3.4, 7.1, 9.6, 12.4, 14.8] as x, i (x)}<circle cx={x} cy={i % 2 ? 5.05 : 5.5} r="0.05" fill="#cfae6c" />{/each}
				{/snippet}
			</World>
		</div>

		{#if !big}
			<div class="tray">
				{#if tokens > 0}
					<p>
						<strong>Kamu ada {tokens} hiasan.</strong>
						{picked ? `Ketik di padang untuk letak ${pickedName.toLowerCase()}.` : 'Pilih satu, kemudian ketik di padang.'}
					</p>
					<div class="choices" role="group" aria-label="Pilih hiasan">
						{#each DECOR as d (d.key)}
							<button type="button" class="choice" aria-pressed={picked === d.key} onclick={() => (picked = picked === d.key ? null : d.key)}>
								<span class="art"><Prop kind={d.prop} tile={30} /></span>
								<span>{d.name}</span>
							</button>
						{/each}
					</div>
				{:else}
					<p class="hint">
						Setiap tiga jawapan betul, kamu dapat satu hiasan untuk padang. Bahan yang kamu bawa: <strong>{world.mine ?? 0}</strong>.
					</p>
				{/if}
			</div>
		{/if}
	</div>
</div>

<style>
	.village {
		display: grid;
		gap: 0.7rem;
		margin-inline: auto;
	}
	.status {
		display: grid;
		grid-template-columns: minmax(0, 1fr) auto;
		grid-template-areas: 'now built' 'bar amount';
		align-items: center;
		gap: 0.35rem 0.8rem;
		padding: 0.7rem 0.9rem;
		border-radius: var(--r-md);
		background: var(--card);
		box-shadow: var(--card-shadow);
	}
	.now {
		grid-area: now;
		display: flex;
		align-items: baseline;
		gap: 0.45rem;
		flex-wrap: wrap;
	}
	.now small {
		color: var(--ink-2);
		font-weight: 700;
	}
	.now strong {
		font: 600 1.15rem/1.2 var(--font-display);
	}
	.built {
		grid-area: built;
		padding: 0.1rem 0.6rem;
		border-radius: var(--r-pill);
		background: var(--brand-soft);
		font-weight: 700;
		white-space: nowrap;
	}
	.built strong {
		font: 600 1.05rem var(--font-display);
	}
	.bar {
		grid-area: bar;
		height: 0.8rem;
		overflow: hidden;
		border-radius: var(--r-pill);
		background: #efe6d2;
	}
	.bar span {
		display: block;
		height: 100%;
		border-radius: inherit;
		background: var(--sun);
		transition: width 600ms var(--ease-out);
	}
	.amount {
		grid-area: amount;
		font-size: var(--fs-small);
		font-weight: 700;
		white-space: nowrap;
	}
	.map {
		min-width: 0;
	}
	.marker {
		position: absolute;
		width: calc(var(--s) * 0.5);
		height: calc(var(--s) * 0.42);
		translate: -50% -100%;
		background: var(--sun);
		clip-path: polygon(0 0, 100% 0, 50% 100%);
		filter: drop-shadow(0 2px 0 var(--sun-deep));
		animation: hover-down 1s ease-in-out infinite alternate;
	}
	.carried {
		position: absolute;
		translate: -50% 0;
		padding: 0 0.4rem;
		border-radius: var(--r-pill);
		background: var(--sun);
		font: 600 0.8rem/1.5 var(--font-display);
		animation: gain 1.3s var(--ease-out) forwards;
	}
	.padang {
		position: absolute;
		display: grid;
		place-items: center;
		padding: 0;
		border: 3px dashed #fff;
		border-radius: 14px;
		background: rgb(255 255 255 / 0.22);
		cursor: copy;
		pointer-events: auto;
		animation: glow 1.1s ease-in-out infinite alternate;
	}
	.padang span {
		padding: 0.15rem 0.7rem;
		border-radius: var(--r-pill);
		background: #fff;
		font-weight: 800;
		font-size: 0.85rem;
	}
	.tray {
		display: grid;
		gap: 0.6rem;
		padding: 0.8rem 0.9rem;
		border-radius: var(--r-md);
		background: var(--card);
		box-shadow: var(--card-shadow);
	}
	.tray:has(.choices) {
		background: #fff3d6;
		animation: pop-in 400ms var(--spring);
	}
	.hint {
		font-size: var(--fs-small);
	}
	.choices {
		display: grid;
		grid-template-columns: repeat(3, minmax(0, 1fr));
		gap: 0.5rem;
	}
	.choice {
		display: grid;
		justify-items: center;
		gap: 0.2rem;
		min-height: 5.6rem;
		padding: 0.45rem 0.3rem;
		border: 2px solid transparent;
		border-radius: var(--r-sm);
		background: #fff;
		font-weight: 800;
		font-size: 0.85rem;
		box-shadow: 0 3px 0 var(--line);
		cursor: pointer;
		transition:
			transform var(--t-press) var(--ease-out),
			border-color var(--t-state);
	}
	.choice:hover {
		transform: translateY(-2px);
	}
	.choice:active {
		transform: translateY(1px);
	}
	.choice[aria-pressed='true'] {
		border-color: var(--sun-deep);
		background: var(--sun);
	}
	.art {
		display: grid;
		place-items: end center;
	}
	.art :global(svg) {
		width: auto;
		height: 3.2rem;
		max-width: 100%;
	}
	.big .status {
		padding: 0.9rem 1.2rem;
	}
	.big .now strong {
		font-size: 1.5rem;
	}
	.big .bar {
		height: 1.1rem;
	}
	@media (min-width: 560px) {
		.choices {
			grid-template-columns: repeat(6, minmax(0, 1fr));
		}
	}
	@keyframes hover-down {
		to {
			transform: translateY(30%);
		}
	}
	@keyframes glow {
		to {
			background: rgb(255 255 255 / 0.4);
		}
	}
</style>
