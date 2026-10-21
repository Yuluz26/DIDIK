<!--
	A walkable 3/4 world: a flat ground drawing, then props and characters sorted by how far down the
	screen they stand, so a child walking behind a tree is hidden by it and walks in front of it below.
	With `follow`, the view keeps the child's own character in the middle. The `overlay` snippet is
	drawn above everything, in the world's own coordinates (multiply tiles by the tile size).
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
	}
</script>

<script lang="ts">
	import type { Snippet } from 'svelte';
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
		names = true,
		step = 110,
		art,
		overlay
	}: {
		width: number;
		height: number;
		tile?: number;
		ground: Snippet;
		props?: WorldProp[];
		actors?: WorldActor[];
		me?: string | null;
		follow?: boolean;
		/** Name tags over the characters: everyone's, only the child's own ('me'), or none. */
		names?: boolean | 'me';
		/** How long characters take to move to a new position, in milliseconds. */
		step?: number;
		art?: Snippet<[WorldProp, number]>;
		overlay?: Snippet<[number]>;
	} = $props();

	let vw = $state(0);
	let vh = $state(0);
	const chibi = $derived(Math.round(tile * 1.05));
	const mine = $derived(me ? actors.find((a) => a.id === me) : undefined);

	const camera = $derived.by(() => {
		const mapW = W * tile;
		const mapH = H * tile;
		if (!follow || !mine) return { x: mapW < vw ? (vw - mapW) / 2 : 0, y: 0 };
		const x = mapW < vw ? (vw - mapW) / 2 : Math.min(0, Math.max(vw - mapW, vw / 2 - mine.x * tile));
		const y = mapH < vh ? (vh - mapH) / 2 : Math.min(0, Math.max(vh - mapH, vh / 2 - mine.y * tile));
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

<div class="viewport" class:follow bind:clientWidth={vw} bind:clientHeight={vh} style:--step="{step}ms">
	<div class="world" style:width="{W * tile}px" style:height="{H * tile}px" style:transform="translate3d({camera.x}px, {camera.y}px, 0)">
		<svg class="ground" viewBox="0 0 {W} {H}" width={W * tile} height={H * tile} aria-hidden="true" focusable="false">
			{@render ground()}
		</svg>

		{#each props as prop (prop.id)}
			<div class="place" style:left="{prop.x * tile}px" style:top="{prop.y * tile}px" style:z-index={Math.round(prop.y * 10)}>
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
				style:left="{actor.x * tile}px"
				style:top="{actor.y * tile}px"
				style:z-index={Math.round(actor.y * 10) + 1}
			>
				<Chibi
					animal={actor.animal}
					colour={actor.colour}
					skin={actor.skin}
					size={chibi}
					walking={actor.walking}
					facing={actor.facing}
					mood={actor.mood}
				/>
			</div>
		{/each}

		<!-- Name tags float above everything, so a tree or an easel never hides who is who. -->
		{#each actors as actor (actor.id)}
			{#if actor.id === me ? names : names === true && actor.name}
				<span
					class="tag"
					class:me={actor.id === me}
					style:left="{Math.min(W - 0.9, Math.max(0.9, actor.x)) * tile}px"
					style:top="{actor.y * tile - chibi * 1.25}px">{actor.id === me ? 'Kamu' : actor.name}</span
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
		overflow: hidden;
		border-radius: var(--r-lg);
		background: #2e6e43;
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
	/* Near the right edge an absolutely placed box would shrink; drawings keep their own size. */
	.place :global(svg) {
		max-width: none;
	}
	.hit {
		display: block;
		padding: 0;
		border: 0;
		background: none;
		cursor: pointer;
		transition: transform var(--t-state) var(--spring);
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
	.actor {
		translate: -50% calc(-100% + 0.75rem);
	}
	.tag {
		position: absolute;
		z-index: 900;
		translate: -50% calc(-100% + 0.95rem);
		padding: 0 0.4rem;
		border-radius: var(--r-pill);
		background: rgb(255 255 255 / 0.92);
		font-size: 0.68rem;
		font-weight: 800;
		line-height: 1.5;
		white-space: nowrap;
		box-shadow: 0 1px 0 rgb(0 0 0 / 0.12);
	}
	.tag.me {
		background: var(--sun);
	}
</style>
