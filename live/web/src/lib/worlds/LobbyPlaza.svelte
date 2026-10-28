<!--
	The waiting room's town square, on the host's screen and on every phone. Children come in under
	the arch when they join; on a phone, tapping the square (or the arrow keys) walks your character
	there and everyone sees it. Positions come from the server; this only animates the walking.
	The walkable box, fountain and arch match didik_live/game/plaza.py.
-->
<script lang="ts" module>
	export const PLAZA = {
		W: 16,
		H: 9,
		left: 0.8,
		top: 3.4,
		right: 15.2,
		bottom: 8.6,
		fountain: { x: 8, y: 5.6, rx: 1.8, ry: 1.35 },
		arch: { x: 8, y: 3.5 }
	};

	/** The nearest place a child can stand; the server does the same before it accepts a step. */
	export function clampToPlaza(x: number, y: number): { x: number; y: number } {
		x = Math.min(PLAZA.right, Math.max(PLAZA.left, x));
		y = Math.min(PLAZA.bottom, Math.max(PLAZA.top, y));
		const f = PLAZA.fountain;
		let dx = (x - f.x) / f.rx;
		let dy = (y - f.y) / f.ry;
		let reach = Math.hypot(dx, dy);
		if (reach < 1) {
			if (reach < 1e-6) [dx, dy, reach] = [0, 1, 1];
			x = f.x + (dx / reach) * f.rx * 1.02;
			y = f.y + (dy / reach) * f.ry * 1.02;
		}
		return { x: Math.round(x * 100) / 100, y: Math.round(y * 100) / 100 };
	}
</script>

<script lang="ts">
	import { untrack } from 'svelte';
	import type { RoomClient } from '$lib/room.svelte';
	import type { Person } from '$lib/types';
	import { fitTile, memo } from '$lib/pixel/cache';
	import { landMap, paintGround } from '$lib/pixel/ground';
	import Stickers from '$lib/play/Stickers.svelte';
	import World, { type WorldActor, type WorldProp } from './World.svelte';
	import { route } from './route';

	let {
		people,
		spots,
		client,
		me = null,
		onwalk
	}: {
		people: Person[];
		spots: [string, number, number, number][];
		client: RoomClient;
		/** On a child's phone: their own id. They can walk, and the view follows them. */
		me?: string | null;
		onwalk?: (x: number, y: number) => void;
	} = $props();

	const { W, H } = PLAZA;

	// Grass with a hedge row along the back, a dirt path in from the arch and out to each side, and a
	// paved oval square in the middle, in pixels (a tile is 16).
	const ground = memo('ground:plaza', () => {
		const map = landMap(Array.from({ length: H }, () => 'g'.repeat(W)), { g: 'grass' });
		const oval = (cx: number, cy: number, rx: number, ry: number) => (x: number, y: number) => ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 <= 1;
		return paintGround(map, {
			seed: 4,
			meadow: 0.35,
			shapes: [
				{ land: 'moss', test: (x, y) => y < 40 + Math.sin(x / 8) * 3 },
				{ land: 'dirt', test: (x, y) => x >= 113 && x < 143 && y >= 43 && y < 62 },
				{ land: 'dirt', test: (x, y) => y >= 86 && y < 106 && (x < 54 || x >= 202) },
				{ land: 'dirt', test: (x, y) => x >= 118 && x < 138 && y >= 130 },
				{ land: 'stone', test: oval(128, 95, 102, 43) }
			]
		});
	});
	const SPEED = 3; // tiles a second, about a child's stroll

	const PROPS: WorldProp[] = [
		{ id: 't1', kind: 'tree', x: 0.9, y: 2.7, variant: 0 },
		{ id: 't2', kind: 'palm', x: 2.4, y: 2.2, variant: 1 },
		{ id: 't3', kind: 'pine', x: 3.8, y: 2.8, variant: 2 },
		{ id: 't4', kind: 'tree', x: 5.3, y: 2.3, variant: 2 },
		{ id: 'arch', kind: 'arch', x: 8, y: 3.35 },
		{ id: 't5', kind: 'tree', x: 10.7, y: 2.3, variant: 1 },
		{ id: 't6', kind: 'pine', x: 12.2, y: 2.8, variant: 0 },
		{ id: 't7', kind: 'palm', x: 13.7, y: 2.2, variant: 0 },
		{ id: 'wau', kind: 'wau', x: 15.25, y: 3.1 },
		{ id: 'lamp1', kind: 'lamp', x: 5.6, y: 4.2 },
		{ id: 'lamp2', kind: 'lamp', x: 10.4, y: 4.2 },
		{ id: 'fountain', kind: 'fountain', x: 8, y: 5.95 },
		{ id: 'bench1', kind: 'bench', x: 2.6, y: 4.5 },
		{ id: 'bench2', kind: 'bench', x: 13.4, y: 4.5 },
		{ id: 'cat', kind: 'cat', x: 14.4, y: 4.8 },
		{ id: 'hen', kind: 'hen', x: 1.5, y: 7.3 },
		{ id: 'hibiscus', kind: 'hibiscus', x: 0.6, y: 9 },
		{ id: 'flowers1', kind: 'flowers', x: 4.4, y: 8.95 },
		{ id: 'flowers2', kind: 'flowers', x: 11.9, y: 8.95, variant: 1 },
		{ id: 'bush', kind: 'bush', x: 15.5, y: 9.05 }
	];

	let el = $state<HTMLElement>();
	let world = $state<ReturnType<typeof World>>();
	let width = $state(0);
	// The host's screen shows the whole square; a phone shows a closer view that follows the child.
	const tile = $derived(me ? fitTile(width, W, { min: 2 }) : fitTile(width, W));
	const follow = $derived(!!me && tile * W > width + 1);

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

	/** Walks a child to (x, y), round the fountain if it is in the way, leg by leg at a stroll. */
	function walkTo(id: string, x: number, y: number, facing: number) {
		const from = shown[id];
		if (!from) return;
		clearTimeout(timers.get(id));
		if (still) {
			shown[id] = { x, y, facing, ms: 0, walking: false };
			return;
		}
		const path = route([from.x, from.y], [x, y], PLAZA.fountain);
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
					// A new arrival: stand under the arch first, then walk in once that has been drawn.
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

	function step(x: number, y: number) {
		if (!me || !onwalk) return;
		const now = performance.now();
		// The server takes a new spot four times a second at most; stay just under that.
		if (now - lastStep < 300) return;
		lastStep = now;
		const to = clampToPlaza(x, y);
		const from = shown[me];
		walkTo(me, to.x, to.y, from && Math.abs(to.x - from.x) > 0.05 ? Math.sign(to.x - from.x) : (from?.facing ?? 1));
		target = { ...to, n: (target?.n ?? 0) + 1 };
		walked = true;
		onwalk(to.x, to.y);
	}

	function tap(event: MouseEvent) {
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

{#snippet square()}
	<div class="stage" style:width={follow ? undefined : `${W * tile}px`} style:height={follow ? undefined : `${H * tile}px`}>
		<World bind:this={world} width={W} height={H} {tile} {ground} props={PROPS} {actors} {me} {follow} step={600} overlay={marker} />
	</div>
	{#if me && !walked}
		<p class="hint" aria-hidden="true">Ketik di mana-mana untuk berjalan</p>
	{/if}
	<Stickers {client} within={el} />
{/snippet}

{#if me}
	<!-- The square handles its own keys (arrows walk), which is what the application role is for. -->
	<!-- svelte-ignore a11y_no_noninteractive_tabindex, a11y_no_noninteractive_element_interactions -->
	<div
		class="plaza walkable"
		class:follow
		bind:this={el}
		bind:clientWidth={width}
		style:--plaza-h="{H * tile}px"
		role="application"
		aria-label="Dataran. Ketik di mana-mana, atau tekan anak panah, untuk berjalan."
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
	/* The square is drawn at a whole step of the pixel size, so it can be a little narrower than its box. */
	.stage {
		margin-inline: auto;
	}
	/* A phone shows a window onto the square that follows the child. */
	.follow .stage {
		height: min(var(--plaza-h), 60dvh);
	}
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
</style>
