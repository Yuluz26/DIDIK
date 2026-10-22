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
		fountain: { x: 8, y: 5.25, rx: 1.45, ry: 0.8 },
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
	import Stickers from '$lib/play/Stickers.svelte';
	import World, { type WorldActor, type WorldProp } from './World.svelte';

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
	const tile = $derived(me ? Math.max(34, width / W) : width / W);
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

	function walkTo(id: string, x: number, y: number, facing: number) {
		const from = shown[id];
		if (!from) return;
		const ms = still ? 0 : Math.round(Math.min(3200, Math.max(250, (Math.hypot(x - from.x, y - from.y) / SPEED) * 1000)));
		shown[id] = { x, y, facing, ms, walking: ms > 0 };
		clearTimeout(timers.get(id));
		if (ms) timers.set(id, setTimeout(() => shown[id] && (shown[id] = { ...shown[id], walking: false }), ms));
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
	// On a phone, a crowd of name tags would hide the square; past ten friends only yours stays.
	const names = $derived(!me || actors.length <= 10 ? true : 'me');

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

{#snippet ground()}
	<rect width={W} height={H} fill="#8fd05e" />
	<path d="M0 0 H16 V2.75 C14 3.15 12.5 2.6 10.6 2.95 C9.4 3.2 6.6 3.2 5.4 2.95 C3.5 2.6 2 3.15 0 2.75z" fill="#78bf4f" />
	<!-- Paths in from the arch and out to the sides, then the paved square itself. -->
	<path d="M7.05 2.7 H8.95 L9.1 3.9 H6.9z" fill="#e9cf98" />
	<path d="M-0.2 5.35 C1.5 5.15 2.5 5.5 3.2 5.45 V6.55 C2.5 6.5 1.5 6.85 -0.2 6.65z M16.2 5.35 C14.5 5.15 13.5 5.5 12.8 5.45 V6.55 C13.5 6.5 14.5 6.85 16.2 6.65z" fill="#e9cf98" />
	<ellipse cx="8" cy="5.95" rx="6.3" ry="2.6" fill="#e9cf98" />
	<ellipse cx="8" cy="5.95" rx="6.3" ry="2.6" fill="none" stroke="#d8b77a" stroke-width="0.07" />
	<ellipse cx="8" cy="5.95" rx="4.6" ry="1.85" fill="none" stroke="#d8b77a" stroke-width="0.05" stroke-dasharray="0.3 0.2" />
	<path d="M7.4 8.5 C7.5 8.8 7.4 9 7.5 9.2 H8.5 C8.6 9 8.5 8.8 8.6 8.5z" fill="#e9cf98" />
	{#each [[1.3, 3.9], [14.6, 6.9], [2.9, 8.2], [12.8, 8.4], [10.2, 3.6], [0.6, 5.0], [15.4, 7.8]] as [x, y] (`${x}-${y}`)}
		<path d="M{x} {y} l0.06 -0.16 l0.06 0.16 M{x + 0.3} {y - 0.2} l0.05 -0.13 l0.05 0.13" stroke="#6cb33f" stroke-width="0.05" fill="none" stroke-linecap="round" />
	{/each}
{/snippet}

{#snippet marker(tile: number)}
	{#if target}
		{#key target.n}
			<span class="target" style:left="{target.x * tile}px" style:top="{target.y * tile}px"></span>
		{/key}
	{/if}
{/snippet}

{#snippet square()}
	<World bind:this={world} width={W} height={H} {tile} {ground} props={PROPS} {actors} {me} {follow} {names} step={600} overlay={marker} />
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
		aspect-ratio: 16 / 9;
		border-radius: var(--r-lg);
	}
	.plaza :global(.viewport) {
		background: #78bf4f;
	}
	/* A phone shows a window onto the square that follows the child. */
	.follow {
		aspect-ratio: auto;
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
		animation: ring 900ms var(--ease-out) forwards;
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
