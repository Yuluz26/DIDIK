<!-- The shared classroom lobby. Children arrive at a free chair, can tap desks to sit or walk
	between them, and appear in the same place on every screen. Furniture collision and seat
	coordinates match didik_live/game/plaza.py. -->
<script lang="ts" module>
	export const PLAZA = {
		W: 16,
		H: 9,
		left: 0.7,
		top: 3.4,
		right: 15.3,
		bottom: 8.6,
		arch: { x: 1.2, y: 3.6 },
		seats: [
			{ x: 2.45, y: 5.25 }, { x: 6.15, y: 5.25 }, { x: 9.85, y: 5.25 }, { x: 13.55, y: 5.25 },
			{ x: 2.45, y: 7.25 }, { x: 6.15, y: 7.25 }, { x: 9.85, y: 7.25 }, { x: 13.55, y: 7.25 }
		],
		// Furniture footprints must match plaza.py OBSTACLES in this order.
		obstacles: [
			{ x: 8, y: 4.15, rx: 1.55, ry: 0.4 },
			{ x: 2.45, y: 5.95, rx: 0.95, ry: 0.34 }, { x: 6.15, y: 5.95, rx: 0.95, ry: 0.34 },
			{ x: 9.85, y: 5.95, rx: 0.95, ry: 0.34 }, { x: 13.55, y: 5.95, rx: 0.95, ry: 0.34 },
			{ x: 2.45, y: 7.95, rx: 0.95, ry: 0.34 }, { x: 6.15, y: 7.95, rx: 0.95, ry: 0.34 },
			{ x: 9.85, y: 7.95, rx: 0.95, ry: 0.34 }, { x: 13.55, y: 7.95, rx: 0.95, ry: 0.34 },
			{ x: 2.45, y: 5.25, rx: 0.38, ry: 0.34 }, { x: 6.15, y: 5.25, rx: 0.38, ry: 0.34 },
			{ x: 9.85, y: 5.25, rx: 0.38, ry: 0.34 }, { x: 13.55, y: 5.25, rx: 0.38, ry: 0.34 },
			{ x: 2.45, y: 7.25, rx: 0.38, ry: 0.34 }, { x: 6.15, y: 7.25, rx: 0.38, ry: 0.34 },
			{ x: 9.85, y: 7.25, rx: 0.38, ry: 0.34 }, { x: 13.55, y: 7.25, rx: 0.38, ry: 0.34 },
			{ x: 14.7, y: 3.55, rx: 0.55, ry: 0.32 },
			{ x: 0.6, y: 5.2, rx: 0.5, ry: 0.38 }
		]
	};

	const box = (x: number, y: number): [number, number] => [Math.min(PLAZA.right, Math.max(PLAZA.left, x)), Math.min(PLAZA.bottom, Math.max(PLAZA.top, y))];
	const free = (x: number, y: number) => PLAZA.obstacles.every((o) => ((x - o.x) / o.rx) ** 2 + ((y - o.y) / o.ry) ** 2 >= 1);
	const r2 = (v: number) => Math.round(v * 100) / 100;

	/** The nearest place a child can stand; the server does the same before it accepts a step. */
	export function clampToPlaza(x: number, y: number): { x: number; y: number } {
		[x, y] = box(x, y);
		for (let pass = 0; pass < 4; pass++) {
			let moved = false;
			for (const o of PLAZA.obstacles) {
				let dx = (x - o.x) / o.rx;
				let dy = (y - o.y) / o.ry;
				let reach = Math.hypot(dx, dy);
				if (reach < 1) {
					if (reach < 1e-6) [dx, dy, reach] = [0, 1, 1];
					[x, y] = box(o.x + (dx / reach) * o.rx * 1.04, o.y + (dy / reach) * o.ry * 1.04);
					moved = true;
				}
			}
			if (!moved) break;
		}
		[x, y] = [r2(x), r2(y)];
		if (!free(x, y)) {
			// between two things that touch (the cat by its bench): the nearest free spot round about
			for (let step = 1; step < 40; step++) {
				const ring = Array.from({ length: 16 }, (_, i) => box(r2(x + step * 0.1 * Math.cos((i * Math.PI) / 8)), r2(y + step * 0.1 * Math.sin((i * Math.PI) / 8))));
				const spot = ring.filter(([sx, sy]) => free(sx, sy)).sort((p, q) => Math.hypot(p[0] - x, p[1] - y) - Math.hypot(q[0] - x, q[1] - y))[0];
				if (spot) return { x: spot[0], y: spot[1] };
			}
		}
		return { x, y };
	}
</script>

<script lang="ts">
	import { untrack } from 'svelte';
	import type { RoomClient } from '$lib/room.svelte';
	import type { Person } from '$lib/types';
	import { fitTile, TILE } from '$lib/pixel/cache';
	import Sprite from '$lib/pixel/Sprite.svelte';
	import Stickers from '$lib/play/Stickers.svelte';
	import World, { type WorldActor, type WorldProp } from './World.svelte';
	import { CHAIR_COLOURS, classroomArt, classroomGround } from './classroom';
	import { route } from './route';

	let {
		people,
		spots,
		client,
		me = null,
		fill = false,
		onwalk,
		onsit
	}: {
		people: Person[];
		spots: [string, number, number, number][];
		client: RoomClient;
		/** On a child's phone: their own id. They can walk, and the view follows them. */
		me?: string | null;
		/** The student's classroom occupies the space between its header and sticker dock. */
		fill?: boolean;
		onwalk?: (x: number, y: number) => void;
		onsit?: (seat: number) => void;
	} = $props();

	const { W, H } = PLAZA;

	const ground = classroomGround();
	const SPEED = 3; // tiles a second, about a child's stroll
	let selectedSeat = $state<number | null>(null);
	function chooseSeat(index: number) { selectedSeat = index; }
	function occupied(index: number) {
		const seat = PLAZA.seats[index];
		return spots.some(([id, x, y]) => id !== me && ((x - seat.x) / 0.85) ** 2 + ((y - seat.y) / 0.5) ** 2 < 1);
	}
	function sit() {
		if (selectedSeat === null || occupied(selectedSeat) || !me || !onsit) return;
		const now = performance.now();
		if (now - lastStep < 300) return;
		lastStep = now;
		const seat = PLAZA.seats[selectedSeat];
		const from = shown[me];
		walkTo(me, seat.x, seat.y, from && Math.abs(seat.x - from.x) > 0.05 ? Math.sign(seat.x - from.x) : (from?.facing ?? 1));
		target = { ...seat, n: (target?.n ?? 0) + 1 };
		walked = true;
		onsit(selectedSeat);
		selectedSeat = null;
	}

	const PROPS: WorldProp[] = [
		{ id: 'teacher', kind: 'teacher', x: 8, y: 4.28, custom: true },
		{ id: 'shelf', kind: 'bookcase', x: 14.7, y: 3.55, custom: true },
		{ id: 'plant', kind: 'plant', x: 0.6, y: 5.2, custom: true },
		...PLAZA.seats.flatMap((seat, i) => [
			{ id: `chair${i}`, kind: 'chair', x: seat.x, y: seat.y - 0.16, variant: i, custom: true, action: me ? () => chooseSeat(i) : undefined, label: `Pilih kerusi ${CHAIR_COLOURS[i].name}` },
			{ id: `desk${i}`, kind: 'desk', x: seat.x, y: seat.y + 0.74, variant: i, custom: true, action: me ? () => chooseSeat(i) : undefined, label: `Pilih meja dengan kerusi ${CHAIR_COLOURS[i].name}` }
		])
	];

	let el = $state<HTMLElement>();
	let world = $state<ReturnType<typeof World>>();
	let width = $state(0);
	let height = $state(0);
	// The host sees the whole classroom; a phone follows the child's own place.
	const tile = $derived(me && fill && height
		? width / height < W / H
			? fitTile(height, H, { min: 2 })
			: fitTile(width, W, { availH: height, rows: H, min: 2 })
		: me ? fitTile(width, W, { min: 2 }) : fitTile(width, W));
	const follow = $derived(!!me && (fill || tile * W > width + 1));

	interface Shown {
		x: number;
		y: number;
		facing: number;
		ms: number;
		walking: boolean;
	}

	let shown = $state<Record<string, Shown>>({});
	let primed = false;
	const timers = new Map<string, ReturnType<typeof setTimeout>>();
	const still = typeof matchMedia === 'function' && matchMedia('(prefers-reduced-motion: reduce)').matches;

	/** Walks a child to (x, y), round whatever is in the way, leg by leg at a stroll. */
	function walkTo(id: string, x: number, y: number, facing: number) {
		const from = shown[id];
		if (!from) return;
		clearTimeout(timers.get(id));
		if (still) {
			shown[id] = { x, y, facing, ms: 0, walking: false };
			return;
		}
		const path = route([from.x, from.y], [x, y], PLAZA.obstacles, PLAZA);
		const leg = (i: number) => {
			if (i >= path.length) {
				const at = shown[id];
				if (at) shown[id] = { ...at, facing, walking: false };
				return;
			}
			const [ax, ay] = path[i - 1];
			const [bx, by] = path[i];
			const ms = Math.round(Math.min(3200, Math.max(250, (Math.hypot(bx - ax, by - ay) / SPEED) * 1000)));
			// facing the way of each leg, then the way the server says once there
			const way = Math.abs(bx - ax) > 0.05 ? (bx < ax ? -1 : 1) : facing;
			shown[id] = { x: bx, y: by, facing: i === path.length - 1 ? facing : way, ms, walking: true };
			timers.set(id, setTimeout(() => leg(i + 1), ms));
		};
		leg(1);
	}

	function place(list: [string, number, number, number][]) {
		const present = new Set<string>();
		for (const [id, x, y, facing] of list) {
			present.add(id);
			const now = shown[id];
			if (!now) {
				if (!primed || still) {
					shown[id] = { x, y, facing, ms: 0, walking: false };
				} else {
					// A new arrival enters through the side door, then walks to the free chair.
					shown[id] = { x: PLAZA.arch.x, y: PLAZA.arch.y, facing, ms: 0, walking: false };
					requestAnimationFrame(() => requestAnimationFrame(() => walkTo(id, x, y, facing)));
				}
			} else if (Math.abs(now.x - x) > 0.01 || Math.abs(now.y - y) > 0.01) {
				walkTo(id, x, y, facing);
			}
		}
		for (const id of Object.keys(shown)) {
			if (!present.has(id)) {
				clearTimeout(timers.get(id));
				delete shown[id];
			}
		}
		primed = true;
	}

	$effect(() => {
		const list = spots;
		untrack(() => place(list));
	});

	$effect(() => () => timers.forEach(clearTimeout));

	const byId = $derived(new Map(people.map((p) => [p.id, p])));
	const actors = $derived<WorldActor[]>(
		Object.entries(shown).flatMap(([id, at]) => {
			const person = byId.get(id);
			if (!person) return [];
			return [
				{
					id,
					x: at.x,
					y: at.y,
					facing: at.facing,
					walking: at.walking,
					seated: !at.walking && PLAZA.seats.some((seat) => Math.hypot(at.x - seat.x, at.y - seat.y) < 0.28),
					ms: at.ms,
					animal: person.avatar,
					colour: person.colour,
					skin: person.skin,
					name: person.name,
					mood: person.online ? 'happy' : 'sleep'
				}
			];
		})
	);

	// ------------------------------------------------------------ walking (phones)

	let target = $state<{ x: number; y: number; n: number } | null>(null);
	let lastStep = 0;
	let walked = $state(false);

	function step(x: number, y: number): boolean {
		if (!me || !onwalk) return false;
		const now = performance.now();
		// The server takes a new spot four times a second at most; stay just under that.
		if (now - lastStep < 300) return false;
		lastStep = now;
		const to = clampToPlaza(x, y);
		const from = shown[me];
		walkTo(me, to.x, to.y, from && Math.abs(to.x - from.x) > 0.05 ? Math.sign(to.x - from.x) : (from?.facing ?? 1));
		target = { ...to, n: (target?.n ?? 0) + 1 };
		walked = true;
		onwalk(to.x, to.y);
		return true;
	}

	function tap(event: MouseEvent) {
		if ((event.target as HTMLElement).closest('button, .seat-choice')) return;
		const at = world?.toTiles(event.clientX, event.clientY);
		if (at) step(at.x, at.y);
	}

	function key(event: KeyboardEvent) {
		const moves: Record<string, [number, number]> = { ArrowLeft: [-1.4, 0], ArrowRight: [1.4, 0], ArrowUp: [0, -1], ArrowDown: [0, 1] };
		const move = moves[event.key];
		const at = me ? shown[me] : undefined;
		if (!move || !at) return;
		event.preventDefault();
		step(at.x + move[0], at.y + move[1]);
	}
</script>

{#snippet marker(tile: number)}
	{#if target}
		{#key target.n}
			<span class="target" style:left="{target.x * tile}px" style:top="{target.y * tile}px"></span>
		{/key}
	{/if}
{/snippet}

{#snippet furniture(prop: WorldProp, tile: number)}
	<Sprite sheet={classroomArt(prop.kind, prop.variant ?? 0)} s={tile / TILE} />
{/snippet}

{#snippet classroomLabels(tile: number)}
	<span class="board-word" style:left="{128 * tile / TILE}px" style:top="{23 * tile / TILE}px" style:font-size="{Math.max(7, tile * 0.28)}px">DIDIK</span>
{/snippet}

{#snippet square()}
	<div class="stage" style:width={follow ? undefined : `${W * tile}px`} style:height={follow ? undefined : `${H * tile}px`}>
		<World bind:this={world} width={W} height={H} {tile} {ground} props={PROPS} {actors} {me} {follow} step={600} art={furniture} under={classroomLabels} overlay={marker} />
	</div>
	{#if me && selectedSeat !== null}
		<div class="seat-choice" role="group" aria-label="Pilih tempat duduk">
			<span class="seat-swatch" style:background={CHAIR_COLOURS[selectedSeat].seat} aria-hidden="true"></span>
			<div class="seat-copy"><strong>Kerusi {CHAIR_COLOURS[selectedSeat].name}</strong><span>{occupied(selectedSeat) ? 'Kerusi ini sudah ada kawan. Pilih kerusi lain ya!' : 'Nak duduk di sini?'}</span></div>
			<button type="button" class="seat-sit" disabled={occupied(selectedSeat)} onclick={sit}>Duduk</button>
			<button type="button" class="seat-cancel" onclick={() => (selectedSeat = null)} aria-label="Batal pilih kerusi">×</button>
		</div>
	{/if}
	{#if me && !walked}
		<p class="hint" aria-hidden="true">Ketik kerusi berwarna untuk pilih tempat duduk</p>
	{/if}
	<Stickers {client} within={el} />
{/snippet}

{#if me}
	<!-- The classroom handles its own keys (arrows walk), which is what the application role is for. -->
	<!-- svelte-ignore a11y_no_noninteractive_tabindex, a11y_no_noninteractive_element_interactions -->
	<div
		class="plaza walkable"
		class:follow
		class:fill
		bind:this={el}
		bind:clientWidth={width}
		bind:clientHeight={height}
		style:--plaza-h="{H * tile}px"
		role="application"
		aria-label="Kelas. Ketik kerusi berwarna dan pilih Duduk, atau tekan anak panah untuk berjalan."
		tabindex="0"
		onclick={tap}
		onkeydown={key}
	>
		{@render square()}
	</div>
{:else}
	<div class="plaza" bind:this={el} bind:clientWidth={width}>
		{@render square()}
	</div>
{/if}

<style>
	.plaza {
		position: relative;
		width: 100%;
	}
	.plaza.fill { height: 100%; min-height: 0; }
	.plaza.fill .stage { width: 100%; height: 100%; }
	/* The square is drawn at a whole step of the pixel size, so it can be a little narrower than its box. */
	.stage {
		margin-inline: auto;
	}
	.plaza :global(.viewport) { background: #c99061; }
	.board-word {
		position: absolute;
		translate: -50% -50%;
		color: #583e38;
		font-family: var(--font-pixel);
		font-weight: 800;
		letter-spacing: 0.12em;
		text-shadow: 1px 1px #fff6da;
	}
	.seat-choice {
		position: absolute;
		z-index: 5;
		left: 50%;
		bottom: 0.65rem;
		translate: -50% 0;
		width: min(29rem, calc(100% - 1rem));
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.55rem;
		border: 2px solid #6a483c;
		border-radius: var(--r-md);
		background: #fff5dd;
		box-shadow: 0 0.45rem 1.2rem rgb(55 32 28 / 0.25);
	}
	.fill .seat-choice { bottom: 4.2rem; }
	.seat-swatch { flex: none; width: 1.7rem; height: 1.7rem; border: 2px solid #6a483c; border-radius: 0.35rem; }
	.seat-copy { display: grid; gap: 0.1rem; min-width: 0; flex: 1; font-size: 0.8rem; line-height: 1.15; }
	.seat-copy strong { font-size: 0.92rem; }
	.seat-sit, .seat-cancel { flex: none; min-height: 2.5rem; border: 0; border-radius: 0.5rem; font: 800 0.9rem var(--font-display); cursor: pointer; }
	.seat-sit { padding-inline: 0.85rem; background: var(--sun); color: var(--ink); }
	.seat-sit:disabled { opacity: 0.5; cursor: not-allowed; }
	.seat-cancel { width: 2.5rem; background: #ead6b6; color: #513e35; font-size: 1.35rem; }
	.seat-sit:focus-visible, .seat-cancel:focus-visible { outline: 3px solid #295b9b; outline-offset: 2px; }
	/* A phone shows a window onto the square that follows the child. */
	.follow .stage {
		height: min(var(--plaza-h), 60dvh);
	}
	.fill.follow .stage { height: 100%; }
	.walkable {
		cursor: pointer;
		touch-action: manipulation;
		-webkit-user-select: none;
		user-select: none;
	}
	.walkable:focus-visible {
		outline: 3px solid var(--sun);
		outline-offset: 3px;
	}
	.target {
		position: absolute;
		width: 2.2rem;
		height: 1.1rem;
		translate: -50% -50%;
		border: 3px solid #fff;
		border-radius: 50%;
		animation: ring 900ms steps(6) forwards;
	}
	@keyframes ring {
		from {
			opacity: 1;
			transform: scale(0.4);
		}
		to {
			opacity: 0;
			transform: scale(1.4);
		}
	}
	.hint {
		position: absolute;
		z-index: 2;
		left: 50%;
		bottom: 0.7rem;
		pointer-events: none;
		translate: -50% 0;
		padding: 0.25rem 0.8rem;
		border-radius: var(--r-pill);
		background: rgb(31 45 39 / 0.78);
		color: #fff;
		font-size: 0.85rem;
		font-weight: 800;
		white-space: nowrap;
		animation: bob 2.4s ease-in-out infinite;
	}
	.fill .hint { bottom: 4.2rem; }
</style>
