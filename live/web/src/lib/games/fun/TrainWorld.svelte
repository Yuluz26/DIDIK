<!--
	A child's Kereta Api Kampung (and, without a client, a train on the host's board), as one pixel
	scene: the steam engine and its carriages, passengers at the windows, standing with their wheels
	on the rail at a station whose name is on its board. A run sets the wheels turning and the steam
	puffing while hills, trees, kampung houses and telegraph poles slide past at their own speeds, until
	the next station comes in and the train stops at it. For the child, their coal and what it buys.
-->
<script lang="ts">
	import type { RoomClient } from '$lib/room.svelte';
	import { play } from '$lib/sound';
	import Scene from '$lib/pixel/Scene.svelte';
	import { type G, ease, put, sagLine, stillWanted, hex } from '$lib/pixel/scene';
	import Icon from '$ui/Icon.svelte';
	import { BOARD, RAIL, STATION, coach, locomotive, pole, puff, railHills, railNear, railSky, railTrees, station } from './rail';
	import { cloud } from './scenery';

	interface Train {
		coal?: number;
		cars: number;
		station: number;
		stations: string[];
		carCost?: number;
		runCost?: number;
		kmPerCar?: number;
		maxCars?: number;
	}
	let { client = null, world }: { client?: RoomClient | null; world: Train; s?: number } = $props();

	const { w: W, h: H, top: TOP } = RAIL;
	const ENGINE_X = 124;
	const STATION_X = 22;
	const RUN = 2800;
	const TRIP = W * 3; // how far the countryside slides past on one run
	const still = stillWanted();

	let run = $state<{ at: number; from: number } | null>(null);
	let travelled = 0;
	let gained = $state<{ key: number; km: number } | null>(null);
	let n = 0;
	$effect(() => {
		if (!client) return;
		return client.onFx((fx) => {
			if (fx.kind !== 'arrive') return;
			const key = ++n;
			const from = (fx.station - 1 + world.stations.length) % world.stations.length;
			if (!still) run = { at: performance.now(), from };
			play('go');
			setTimeout(() => {
				gained = { key, km: fx.km };
				play('coin');
			}, still ? 0 : RUN - 200);
			setTimeout(() => gained?.key === key && (gained = null), (still ? 0 : RUN) + 1800);
		});
	});

	// the name on the board: the station left behind until the train is halfway, then the next one
	let half = $state(false);
	const shown = $derived(run && !half ? run.from : world.station);
	const here = $derived(world.stations[shown] ?? '');
	const next = $derived(world.stations[(world.station + 1) % world.stations.length] ?? '');

	function tile(g: G, pix: Parameters<typeof put>[1], offset: number, y = 0) {
		const x = -(((offset % W) + W) % W);
		put(g, pix, x, y);
		put(g, pix, x + W, y);
	}

	function paint(g: G, t: number) {
		const now = still ? 0 : t;
		let cam = 0;
		let moving = false;
		if (run) {
			const u = (now - run.at) / RUN;
			if (u >= 1) {
				travelled += TRIP;
				run = null;
				half = false;
			} else {
				cam = TRIP * ease(u);
				moving = true;
				if (u > 0.5 !== half) half = u > 0.5;
			}
		}
		const go = travelled + cam;

		put(g, railSky(), 0, 0);
		put(g, cloud(0), ((now * 0.002 - go * 0.05) % (W + 60) + W + 60) % (W + 60) - 40, 6);
		tile(g, railHills(), go * 0.12);
		tile(g, railTrees(), go * 0.35);

		// the station going out, and the next one coming in
		put(g, station(), STATION_X - cam, TOP - STATION.h);
		if (run) put(g, station(), STATION_X - cam + TRIP, TOP - STATION.h);

		tile(g, railNear(), go);

		// telegraph poles behind the track, wires slung between them
		const gap = 88;
		const first = -(((go % gap) + gap) % gap);
		const tops: [number, number][] = [];
		for (let x = first - gap; x < W + gap; x += gap) {
			put(g, pole(), x, RAIL.ground - 30);
			tops.push([x + 4, RAIL.ground - 27]);
		}
		for (let i = 0; i + 1 < tops.length; i++) sagLine(g, tops[i], tops[i + 1], 2, hex('#3a3346', 200));

		// the train: wheels on the rail, a little jolt at every rail joint while it runs
		const frame = moving ? ((now / 110) | 0) % 2 : 0;
		const jolt = moving && ((now / 170) | 0) % 2 ? 1 : 0;
		for (let i = 0; i < world.cars; i++) {
			const x = ENGINE_X - (i + 1) * 31;
			if (x < -32) break;
			put(g, coach(i, frame), x, TOP - 21 - 1 + (i % 2 ? jolt : 0));
		}
		put(g, locomotive(frame), ENGINE_X, TOP - 25 - 1 + jolt);

		// steam from the chimney: a stream of puffs blown back while running, a lazy one at a stop
		const every = moving ? 110 : 700;
		const life = moving ? 1100 : 2200;
		const cx = ENGINE_X + 29;
		const cy = TOP - 26 - 3;
		for (let k = 0; k < Math.ceil(life / every); k++) {
			const born = Math.floor(now / every) * every - k * every;
			const age = now - born;
			if (age < 0 || age > life) continue;
			const a = age / 1000;
			const x = cx - a * (moving ? 70 : 6) + Math.sin(born) * 2;
			const y = cy - a * (moving ? 10 : 9);
			const size = age < life * 0.3 ? 0 : age < life * 0.65 ? 1 : 2;
			g.globalAlpha = Math.max(0, 1 - age / life) * 0.95;
			put(g, puff(size), x - 6, y - 5);
			g.globalAlpha = 1;
		}
	}

	const label = $derived(`Kereta api dengan ${world.cars} gerabak di stesen ${here}.`);
	const boardStyle = `left:${((STATION_X + BOARD.x) / W) * 100}%;top:${((TOP - STATION.h + BOARD.y) / H) * 100}%;width:${(BOARD.w / W) * 100}%;height:${(BOARD.h / H) * 100}%`;
</script>

<div class="fun keretapi">
	{#if client}
		<ul class="stats" aria-label="Simpanan kamu">
			<li><Icon name="coin" size={20} /><strong>{world.coal}</strong> arang</li>
			<li><strong>{world.cars}</strong> gerabak</li>
		</ul>
	{/if}

	<div class="frame">
		<Scene w={W} h={H} {paint} fps={20} {label}>
			{#if !run}<p class="board" style={boardStyle}>{here}</p>{/if}
			{#if gained}{#key gained.key}<p class="km" role="status">+{gained.km} km</p>{/key}{/if}
		</Scene>
	</div>

	{#if client && world.carCost !== undefined}
		<div class="acts">
			<button type="button" class="btn btn--sun btn--big" disabled={(world.coal ?? 0) < (world.runCost ?? 2) || !!run} onclick={() => client?.send({ t: 'go' })}>
				Jalan ke {next} · {world.runCost} arang
			</button>
			<button type="button" class="btn btn--sea" disabled={(world.coal ?? 0) < world.carCost || world.cars >= (world.maxCars ?? 8) || !!run} onclick={() => (client?.send({ t: 'car' }), play('build'))}>
				Tambah gerabak · {world.carCost} arang
			</button>
		</div>
		<p class="hint" aria-live="polite">Setiap gerabak menambah {world.kmPerCar} km bagi setiap perjalanan.</p>
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
	.frame {
		overflow: hidden;
		border: 3px solid #2a1f2d;
		border-radius: 6px;
		box-shadow: 0 4px 0 #2a1f2d;
		background: #8fcdee;
	}
	.board {
		position: absolute;
		display: grid;
		place-items: center;
		overflow: hidden;
		color: #2a1f2d;
		font: 700 clamp(0.5rem, 3.3cqw, 1.3rem) / 1 var(--font-pixel);
		letter-spacing: -0.01em;
		text-align: center;
		white-space: nowrap;
	}
	.km {
		position: absolute;
		right: 4%;
		top: 6%;
		padding: 0.3rem 0.8rem;
		border: 2px solid #2a1f2d;
		border-radius: 4px;
		background: #ffcf5a;
		box-shadow: 0 3px 0 #2a1f2d;
		font: 700 1.1rem/1.2 var(--font-display);
		animation: rise 1.8s steps(10) both;
	}
	.acts {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
	}
	.acts .btn {
		flex: 1 1 12rem;
	}
	.hint {
		color: var(--ink-2);
		font-weight: 800;
		text-align: center;
	}
	@keyframes rise {
		from {
			opacity: 0;
			transform: translateY(0.8rem);
		}
		80% {
			opacity: 1;
		}
		to {
			opacity: 0;
			transform: translateY(-0.8rem);
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.km {
			animation: none;
		}
	}
</style>
