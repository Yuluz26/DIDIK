<!--
	A walkable 3/4 world: a flat ground drawing, then props and characters sorted by how far down the
	screen they stand, so a child walking behind a tree is hidden by it and walks in front of it below.
	With `follow`, the view keeps the child's own character in the middle. The `overlay` snippet is
	drawn above everything, in the world's own coordinates (multiply tiles by the tile size).
	`toTiles` turns a point on the screen (a tap) into a place in the world.
-->
<script lang="ts" module>
	export interface WorldProp {
		id: string;
		kind: string;
		x: number;
		y: number;
		variant?: number;
		state?: string;
		progress?: number;
		label?: string;
		badge?: string | number;
		action?: () => void;
		/** Drawn by the world's own `art` snippet instead of the shared props. */
		custom?: boolean;
		/** Moves smoothly to a new position (a boat racing) instead of jumping there. */
		glide?: boolean;
	}

	export interface WorldActor {
		id: string;
		x: number;
		y: number;
		facing?: number;
		walking?: boolean;
		animal: string;
		colour: string;
		skin?: string;
		name: string;
		mood?: 'happy' | 'cheer' | 'oops' | 'sleep';
		/** How long this character's current walk takes, when it differs from the world's `step`. */
		ms?: number;
	}
</script>

<script lang="ts">
	import { type Snippet, untrack } from 'svelte';
	import { TILE } from '$lib/pixel/cache';
	import { CH } from '$lib/pixel/chibi';
	import GroundCanvas from '$lib/pixel/GroundCanvas.svelte';
	import type { Pix } from '$lib/pixel/pix';
	import Chibi from '$ui/Chibi.svelte';
	import Prop from './Prop.svelte';

	let {
		width: W,
		height: H,
		tile = 44,
		ground,
		props = [],
		actors = [],
		me = null,
		follow = false,
		focus = null,
		names = true,
		step = 110,
		art,
		under,
		overlay
	}: {
		width: number;
		height: number;
		/** CSS pixels to a tile; a multiple of half a sprite pixel (see fitTile) keeps the art sharp. */
		tile?: number;
		/** The painted ground (lib/pixel/ground.ts). */
		ground: Pix;
		props?: WorldProp[];
		actors?: WorldActor[];
		me?: string | null;
		follow?: boolean;
		/** With `follow`, the point (in tiles) to keep in the middle instead of the child's character. */
		focus?: { x: number; y: number } | null;
		/** Name tags over the characters: everyone's, only the child's own ('me'), or none. A crowd
		 * keeps fewer (see `tags`). */
		names?: boolean | 'me';
		/** How long characters take to move to a new position, in milliseconds. */
		step?: number;
		art?: Snippet<[WorldProp, number]>;
		/** Drawn on the ground, under every prop and character (moving water). */
		under?: Snippet<[number]>;
		overlay?: Snippet<[number]>;
	} = $props();

	// A crowd of name tags hides the world: past ten children a phone keeps only its own, and past
	// sixteen the big screen shows none (its leaderboard or list names everyone).
	const tags = $derived(names === true && actors.length > (me ? 10 : 16) ? (me ? 'me' : false) : names);

	let vw = $state(0);
	let vh = $state(0);
	let worldEl = $state<HTMLElement>();

	/** The place in the world, in tiles, under a point on the screen. */
	export function toTiles(clientX: number, clientY: number): { x: number; y: number } | null {
		if (!worldEl) return null;
		const box = worldEl.getBoundingClientRect();
		return { x: (clientX - box.left) / tile, y: (clientY - box.top) / tile };
	}
	/** CSS pixels to a sprite pixel: every picture in the world is drawn at this one size. */
	const s = $derived(tile / TILE);
	const mine = $derived(me ? actors.find((a) => a.id === me) : undefined);

	// Which way each character looks follows where it is walking: sideways, away from us, or at us.
	type Look = { dir: 'front' | 'back' | 'side'; facing: number };
	const looks = $state<Record<string, Look>>({});
	const seen = new Map<string, { x: number; y: number }>();
	$effect(() => {
		const here = new Set<string>();
		for (const a of actors) {
			here.add(a.id);
			const was = seen.get(a.id);
			const now = untrack(() => looks[a.id]) ?? { dir: 'front', facing: a.facing ?? 1 };
			let next = now;
			if (was && (was.x !== a.x || was.y !== a.y)) {
				const dx = a.x - was.x;
				const dy = a.y - was.y;
				next = Math.abs(dx) >= Math.abs(dy) * 0.9 ? { dir: 'side', facing: dx < 0 ? -1 : 1 } : { dir: dy < 0 ? 'back' : 'front', facing: now.facing };
			}
			seen.set(a.id, { x: a.x, y: a.y });
			if (next.dir !== now.dir || next.facing !== now.facing || !untrack(() => looks[a.id])) looks[a.id] = next;
		}
		for (const id of seen.keys()) {
			if (!here.has(id)) {
				seen.delete(id);
				delete looks[id];
			}
		}
	});

	const target = $derived(focus ?? (mine ? { x: mine.x, y: mine.y } : null));

	const camera = $derived.by(() => {
		const mapW = W * tile;
		const mapH = H * tile;
		if (!follow || !target) return { x: mapW < vw ? (vw - mapW) / 2 : 0, y: 0 };
		const x = mapW < vw ? (vw - mapW) / 2 : Math.min(0, Math.max(vw - mapW, vw / 2 - target.x * tile));
		const y = mapH < vh ? (vh - mapH) / 2 : Math.min(0, Math.max(vh - mapH, vh / 2 - target.y * tile));
		return { x, y };
	});
</script>

{#snippet drawing(prop: WorldProp)}
	{#if prop.custom && art}
		{@render art(prop, tile)}
	{:else}
		<Prop kind={prop.kind} variant={prop.variant} state={prop.state} progress={prop.progress} {tile} />
	{/if}
{/snippet}

<div
	class="viewport"
	class:follow
	bind:clientWidth={vw}
	bind:clientHeight={vh}
	style:--step="{step}ms"
	style:--tile="{tile}px"
	style:--s="{s}px"
	style:max-width={follow ? undefined : `${W * tile}px`}
>
	<div class="world" bind:this={worldEl} style:width="{W * tile}px" style:height="{H * tile}px" style:transform="translate3d({Math.round(camera.x)}px, {Math.round(camera.y)}px, 0)">
		<div class="ground"><GroundCanvas pix={ground} {tile} /></div>

		{#if under}<div class="under">{@render under(tile)}</div>{/if}

		{#each props as prop (prop.id)}
			<div class="place" class:glide={prop.glide} style:left="{Math.round(prop.x * tile)}px" style:top="{Math.round(prop.y * tile)}px" style:z-index={Math.round(prop.y * 10)}>
				{#if prop.action}
					<button type="button" class="hit" onclick={prop.action} aria-label={prop.label}>{@render drawing(prop)}</button>
				{:else}
					{@render drawing(prop)}
				{/if}
				{#if prop.badge !== undefined}<span class="badge">{prop.badge}</span>{/if}
			</div>
		{/each}

		{#each actors as actor (actor.id)}
			<div
				class="place actor"
				data-player={actor.id}
				style:left="{Math.round(actor.x * tile)}px"
				style:top="{Math.round(actor.y * tile)}px"
				style:z-index={Math.round(actor.y * 10) + 1}
				style:--step={actor.ms === undefined ? undefined : `${actor.ms}ms`}
			>
				<Chibi
					animal={actor.animal}
					colour={actor.colour}
					skin={actor.skin}
					{s}
					walking={actor.walking}
					dir={looks[actor.id]?.dir ?? 'front'}
					facing={looks[actor.id]?.facing ?? actor.facing ?? 1}
					mood={actor.mood}
				/>
			</div>
		{/each}

		<!-- Name tags float above everything, so a tree or an easel never hides who is who. -->
		{#each actors as actor (actor.id)}
			{#if actor.id === me ? tags : tags === true && actor.name}
				<span
					class="tag"
					class:me={actor.id === me}
					style:left="{Math.round(Math.min(W - 0.9, Math.max(0.9, actor.x)) * tile)}px"
					style:top="{Math.round(actor.y * tile - (CH - 6) * s)}px"
					style:--step={actor.ms === undefined ? undefined : `${actor.ms}ms`}>{actor.id === me ? 'Kamu' : actor.name}</span
				>
			{/if}
		{/each}

		{#if overlay}<div class="overlay">{@render overlay(tile)}</div>{/if}
	</div>
</div>

<style>
	.viewport {
		position: relative;
		width: 100%;
		max-width: 100%;
		margin-inline: auto;
		overflow: hidden;
		border-radius: var(--r-lg);
		background: #3c7c3a;
		box-shadow: var(--card-shadow);
	}
	.viewport.follow {
		height: 100%;
	}
	.world {
		position: relative;
		transition: transform 120ms linear;
		will-change: transform;
	}
	.ground {
		position: absolute;
		inset: 0;
		display: block;
	}
	.under {
		position: absolute;
		inset: 0;
		overflow: hidden;
		pointer-events: none;
	}
	/* Overlay content ignores the pointer unless it asks for it (a control sets pointer-events: auto). */
	.overlay {
		position: absolute;
		inset: 0;
		z-index: 1000;
		pointer-events: none;
	}
	.place {
		position: absolute;
		translate: -50% -100%;
		width: max-content;
		line-height: 0;
	}
	.glide {
		transition:
			left 1.1s var(--ease-out),
			top 1.1s var(--ease-out);
	}
	.hit {
		position: relative;
		display: block;
		padding: 0;
		border: 0;
		background: none;
		cursor: pointer;
		transition: transform var(--t-state) var(--spring);
	}
	/* A finger is bigger than a small drawing: the tap area reaches a little past it. */
	.hit::after {
		content: '';
		position: absolute;
		inset: -0.45rem;
	}
	.hit:hover {
		transform: translateY(-4px) scale(1.06);
	}
	.hit:active {
		transform: translateY(0) scale(0.98);
	}
	.hit:focus-visible {
		outline: 3px solid var(--sun);
		outline-offset: 3px;
		border-radius: var(--r-sm);
	}
	.badge {
		position: absolute;
		top: 0;
		right: -0.4rem;
		min-width: 1.3rem;
		padding: 0 0.3rem;
		border-radius: var(--r-pill);
		background: #fff;
		font: 600 0.75rem/1.4 var(--font-display);
		text-align: center;
		box-shadow: 0 2px 0 rgb(0 0 0 / 0.15);
	}
	.actor,
	.tag {
		transition:
			left var(--step) linear,
			top var(--step) linear;
		pointer-events: none;
	}
	/* The feet stand two sprite pixels above the bottom of the picture. */
	.actor {
		translate: -50% calc(-100% + var(--s) * 2);
	}
	.tag {
		position: absolute;
		z-index: 900;
		translate: -50% -100%;
		padding: 0 0.4rem;
		border: 2px solid #2a1f2d;
		border-radius: 4px;
		background: #fff6e6;
		color: #2a1f2d;
		font: 600 clamp(0.68rem, calc(var(--tile) * 0.24), 1.1rem) / 1.35 var(--font-pixel);
		white-space: nowrap;
	}
	.tag.me {
		z-index: 901;
		background: var(--sun);
	}
</style>
