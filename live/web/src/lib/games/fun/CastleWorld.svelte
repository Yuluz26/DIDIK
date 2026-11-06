<!--
	A child's Kubu Pasir (and, without a client, a castle on the host's board), as one pixel scene: the
	sea behind, the waves washing up the wet sand, the sea walls as mounds between the sea and the
	castle, and the castle itself in tiers that narrow as they rise, flags on top. As the next wave
	nears, a swell can be seen rolling in; when it comes, it surges up the beach and breaks on the wall,
	or, with no wall, washes over the castle and takes its top tier. For the child, the sand in their
	bucket and what it builds.
-->
<script lang="ts">
	import type { RoomClient } from '$lib/room.svelte';
	import { play } from '$lib/sound';
	import Scene from '$lib/pixel/Scene.svelte';
	import { type G, dot, hash, hex, put, stillWanted } from '$lib/pixel/scene';
	import Icon from '$ui/Icon.svelte';
	import { BEACH, FOAM, beachBack, beachHeight, castle, spade, wallMound } from './beach';
	import { bird, cloud } from './scenery';

	interface Castle {
		sand?: number;
		floors: number;
		walls: number;
		flags: number;
		costs?: Record<string, number>;
		maxFloors?: number;
		maxWalls?: number;
		maxFlags?: number;
		waveAt?: number;
		paused?: boolean;
	}
	let { client = null, world, offset = 0 }: { client?: RoomClient | null; world: Castle; s?: number; offset?: number } = $props();

	const { w: W, horizon: HORIZON, surf: SURF } = BEACH;
	const H = $derived(beachHeight(world.floors));
	const FOOT = $derived(H - 12);
	const still = stillWanted();

	let now = $state(Date.now());
	$effect(() => {
		const timer = setInterval(() => (now = Date.now()), 500);
		return () => clearInterval(timer);
	});
	const left = $derived(world.waveAt ? Math.max(0, Math.ceil((world.waveAt - (now + offset)) / 1000)) : null);

	// When a wave comes: whether a wall was there to take it (the room may already show it gone).
	let wallsBefore = -1;
	let wallGoneAt = 0;
	$effect(() => {
		const walls = world.walls;
		if (wallsBefore >= 0 && walls < wallsBefore) wallGoneAt = Date.now();
		wallsBefore = walls;
	});
	let surge = $state<{ at: number; wall: boolean; top: number } | null>(null);
	$effect(() => {
		if (!client) return;
		return client.onFx((fx) => {
			if (fx.kind !== 'wave') return;
			const wall = world.walls > 0 || Date.now() - wallGoneAt < 1500;
			surge = { at: performance.now(), wall, top: castle(world.floors, world.flags).top };
			play('splash');
		});
	});

	function build(part: 'floor' | 'wall' | 'flag') {
		if (!client || !world.costs || (world.sand ?? 0) < world.costs[part]) return;
		client.send({ t: 'build', part });
		play('build');
	}
	const can = (part: string) => !!world.costs && (world.sand ?? 0) >= world.costs[part];

	// ------------------------------------------------------------------ the picture

	const SEA_LIGHT = hex('#7cc8da', 235);
	const SEA_DEEP = hex('#3fa2c0', 245);
	const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

	/** Water washing up the sand from the sea to `edge`, with a line of foam at its front. */
	function wash(g: G, edge: number, t: number) {
		for (let x = 0; x < W; x++) {
			const e = Math.round(edge + Math.sin(x * 0.11 + t / 900) * 1.5 + (hash(x >> 2, 9) - 0.5) * 2);
			if (e <= SURF) continue;
			g.fillStyle = 'rgba(124,200,218,0.85)';
			g.fillRect(x, SURF, 1, e - SURF);
			dot(g, x, e, FOAM);
			if (hash(x, (t / 300) | 0) < 0.4) dot(g, x, e - 1, FOAM);
		}
	}

	function paint(g: G, t: number) {
		const now = still ? 0 : t;
		put(g, beachBack(H), 0, 0);
		put(g, cloud(0), ((now * 0.0025) % (W + 60)) - 40, 4);
		for (let i = 0; i < 2; i++) put(g, bird(((now / 240 + i) | 0) % 2), W - (((now * 0.01 + i * 40) % (W + 30)) - 10), 14 + i * 6);

		// the swell of the coming wave, rolling in from far out
		if (left !== null && !world.paused && left <= 12 && !surge) {
			const u = 1 - left / 12;
			const y = Math.round(lerp(HORIZON + 4, SURF - 3, u));
			for (let x = 0; x < W; x++) {
				const yy = y + Math.round(Math.sin(x * 0.09 + now / 500));
				dot(g, x, yy, FOAM);
				dot(g, x, yy + 1, SEA_LIGHT);
				dot(g, x, yy + 2, SEA_DEEP);
				if (hash(x, (now / 200) | 0) < 0.3) dot(g, x, yy - 1, FOAM);
			}
		}

		// the tide line going in and out, or a wave surging up the beach
		const wallFoot = BEACH.wall + (world.walls > 1 ? BEACH.wallGap : 0);
		let edge = SURF + 2 + Math.round(Math.sin(now / 1400) * 2);
		let surgeU = -1;
		if (surge) {
			surgeU = (now - surge.at) / 1900;
			if (still || surgeU > 1) surge = null;
			else {
				const reach = surge.wall ? BEACH.wall - 3 : FOOT - 2;
				edge = Math.round(lerp(SURF, reach, Math.sin(Math.PI * Math.min(1, surgeU * 1.25))));
			}
		}
		wash(g, edge, now);

		// sea walls: the first nearest the sea, a second one closer in, in front of it
		for (let i = 0; i < Math.min(world.walls, 2); i++) put(g, wallMound(), (W - 104) / 2, BEACH.wall + i * BEACH.wallGap - 9);

		// the castle, with a spade and a bucket beside it
		const built = castle(world.floors, world.flags);
		put(g, built.pix, (W - built.pix.w) / 2, FOOT - built.pix.h + 1);
		if (world.floors || client) put(g, spade(), W / 2 + 30, FOOT - 13);

		if (surge && surgeU >= 0) {
			// spray where the wave meets the wall, or sand tumbling off the castle's top
			const s = surgeU * 1.9;
			if (surge.wall) {
				for (let k = 0; k < 26; k++) {
					const x = 40 + hash(k, 1) * 96;
					const v = 30 + hash(k, 2) * 40;
					const y = BEACH.wall - 6 - v * s + 70 * s * s;
					if (s > 0.15 && y < BEACH.wall) dot(g, x, y, k % 3 ? FOAM : hex('#9fe6ea'));
				}
			} else if (surge.top) {
				for (let k = 0; k < 10; k++) {
					const x = W / 2 + (hash(k, 3) - 0.5) * 24;
					const y = FOOT - surge.top + 6 + (s * 60) ** 1.4 * (0.4 + hash(k, 4));
					if (y < FOOT) g.fillStyle = k % 2 ? '#e9c78d' : '#d1a974';
					if (y < FOOT) g.fillRect(Math.round(x), Math.round(y), 2, 2);
				}
			}
		}
	}

	const label = $derived(`Pantai. Istana ${world.floors} tingkat, ${world.flags} bendera, ${world.walls} tembok menghadap laut.`);
</script>

<div class="fun kubu">
	{#if client}
		<ul class="stats" aria-label="Simpanan kamu">
			<li><Icon name="coin" size={20} /><strong>{world.sand}</strong> baldi pasir</li>
			<li><strong>{world.floors}</strong> tingkat</li>
			{#if left !== null && !world.paused}<li class="wave" class:soon={left <= 10}>Ombak dalam <strong>{left}</strong> s</li>{/if}
		</ul>
	{/if}

	<div class="frame">
		<Scene w={W} h={H} {paint} fps={15} {label}>
			{#if world.floors === 0}<p class="empty">Belum ada istana</p>{/if}
		</Scene>
	</div>

	{#if client && world.costs}
		<div class="acts">
			<button type="button" class="btn btn--sun" disabled={!can('floor') || world.floors >= (world.maxFloors ?? 12)} onclick={() => build('floor')}>Tambah tingkat · {world.costs.floor}</button>
			<button type="button" class="btn btn--sea" disabled={!can('wall') || world.walls >= (world.maxWalls ?? 2)} onclick={() => build('wall')}>Bina tembok · {world.costs.wall}</button>
			<button type="button" class="btn" disabled={!can('flag') || world.floors === 0 || world.flags >= (world.maxFlags ?? 3)} onclick={() => build('flag')}>Pacak bendera · {world.costs.flag}</button>
		</div>
		<p class="hint" aria-live="polite">
			{world.walls ? 'Tembok kamu akan menahan ombak seterusnya.' : 'Tiada tembok: ombak akan meruntuhkan satu tingkat!'}
		</p>
	{/if}
</div>

<style>
	.fun {
		display: grid;
		gap: 0.7rem;
	}
	.stats {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
		margin: 0;
		padding: 0;
		list-style: none;
	}
	.stats li {
		display: inline-flex;
		align-items: center;
		gap: 0.35rem;
		padding: 0.35rem 0.8rem;
		border-radius: var(--r-pill);
		background: var(--card);
		box-shadow: var(--card-shadow);
		font-weight: 800;
	}
	.stats .wave {
		background: #c9eef5;
	}
	.stats .soon {
		background: #ffe3d6;
		animation: pulse 1s ease-in-out infinite;
	}
	.frame {
		overflow: hidden;
		border: 3px solid #2a1f2d;
		border-radius: 6px;
		box-shadow: 0 4px 0 #2a1f2d;
		background: #e9c78d;
	}
	.empty {
		position: absolute;
		left: 50%;
		bottom: 14%;
		translate: -50% 0;
		padding: 0.3rem 0.8rem;
		border: 2px solid #2a1f2d;
		border-radius: 4px;
		background: #fff6e6;
		color: #6a4a2a;
		font-weight: 800;
		line-height: 1.3;
		white-space: nowrap;
	}
	.acts {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
	}
	.acts .btn {
		flex: 1 1 10rem;
	}
	.hint {
		color: var(--ink-2);
		font-weight: 800;
		text-align: center;
	}
	@keyframes pulse {
		50% {
			transform: scale(1.05);
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.stats .soon {
			animation: none;
		}
	}
</style>
