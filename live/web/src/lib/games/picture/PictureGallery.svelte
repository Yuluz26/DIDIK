<!--
	Teka Gambar's gallery: a hidden picture on an easel under sixteen tiles that open as questions are
	answered, in a small 3/4 room with its visitors standing on the floor. The picture itself is served
	by a token that changes every round, and its name only arrives once it is guessed or finished.
-->
<script lang="ts" module>
	export interface Frame {
		url: string;
		tiles: number;
		opened: number[];
		done: boolean;
		number: number;
		guessedCount: number;
		guessers: string[];
		name?: string;
		guessed?: boolean;
		bonus?: number;
	}
</script>

<script lang="ts">
	import type { Person } from '$lib/types';
	import { TILE, fitTile } from '$lib/pixel/cache';
	import Sprite from '$lib/pixel/Sprite.svelte';
	import World, { type WorldActor, type WorldProp } from '$lib/worlds/World.svelte';
	import { EASEL, easel, galleryGround } from './sprites';

	let {
		frame,
		people,
		visitors = [],
		me = null,
		cheering = []
	}: {
		frame: Frame;
		people: Map<string, Person>;
		/** Who stands in the room, nearest the easel first. */
		visitors?: string[];
		me?: string | null;
		/** Visitors who have guessed the picture cheer. */
		cheering?: string[];
	} = $props();

	const W = 8;
	const H = 6;
	const SPOTS: [number, number][] = [
		[6.5, 4.6], [1.5, 4.7], [6.9, 5.7], [1.1, 5.8], [5.6, 5.85], [2.4, 5.9], [7.4, 4.1], [0.6, 4.2]
	];
	const PROPS: WorldProp[] = [
		{ id: 'easel', kind: 'easel', custom: true, x: 4, y: 5.3 },
		{ id: 'pot-l', kind: 'pot', x: 0.6, y: 2.75 },
		{ id: 'pot-r', kind: 'pot', x: 7.4, y: 2.75 }
	];

	let width = $state(0);
	const tile = $derived(fitTile(width, W, { min: 2, max: 64 }));
	const ground = galleryGround(W, H);
	// A child who has guessed sees the whole picture straight away; everyone else waits for the tiles.
	const open = $derived(new Set(frame.guessed ? Array.from({ length: frame.tiles }, (_, i) => i) : frame.opened));
	const closed = $derived(frame.tiles - frame.opened.length);

	const actors = $derived<WorldActor[]>(
		visitors
			.filter((id) => people.has(id))
			.slice(0, SPOTS.length)
			.map((id, i) => {
				const person = people.get(id)!;
				const [x, y] = SPOTS[i];
				return {
					id,
					x,
					y,
					facing: x < 4 ? 1 : -1,
					animal: person.avatar,
					colour: person.colour,
					skin: person.skin,
					// Name tags only for those who have guessed, so the small room stays readable.
					name: cheering.includes(id) ? person.name : '',
					mood: cheering.includes(id) ? 'cheer' : 'happy'
				};
			})
	);
</script>

{#snippet art(_prop: WorldProp, tile: number)}
	{@const s = tile / TILE}
	<div class="easel" style:--s="{s}px" style:width="{EASEL.w * s}px" style:height="{EASEL.h * s}px">
		<div class="canvas" style:left="{EASEL.pic.x * s}px" style:top="{EASEL.pic.y * s}px" style:width="{EASEL.pic.size * s}px" style:height="{EASEL.pic.size * s}px">
			<img src={frame.url} alt={frame.name ? `Gambar ${frame.name}` : 'Gambar rahsia, sebahagiannya tertutup'} />
			<div class="cover" aria-hidden="true">
				{#each Array.from({ length: frame.tiles }, (_, i) => i) as i (i)}
					<span class="shutter" class:open={open.has(i)} class:alt={(i + Math.floor(i / 4)) % 2 === 1} style:--n={i % 4}></span>
				{/each}
			</div>
		</div>
		<span class="frame"><Sprite sheet={easel()} {s} /></span>
	</div>
{/snippet}

<figure class="gallery" bind:clientWidth={width}>
	<figcaption>
		{#if frame.name && (frame.done || frame.guessed)}
			<span class="label">Gambar {frame.number}</span> <strong>{frame.name}</strong>
		{:else}
			<span class="label">Gambar {frame.number}</span> <strong>{closed} petak tertutup</strong>
		{/if}
		{#if frame.guessedCount}<span class="count">{frame.guessedCount} sudah meneka</span>{/if}
	</figcaption>
	<div class="fit" style:max-width="{W * tile}px">
		<World width={W} height={H} {tile} {ground} props={PROPS} {actors} {me} names={me ? 'me' : true} {art} />
	</div>
</figure>

<style>
	.gallery {
		display: grid;
		gap: 0.5rem;
		margin: 0;
		min-width: 0;
	}
	figcaption {
		display: flex;
		align-items: baseline;
		flex-wrap: wrap;
		gap: 0.2rem 0.5rem;
	}
	.label {
		color: var(--ink-2);
		font-weight: 700;
	}
	figcaption strong {
		font: 600 1.2rem var(--font-pixel);
	}
	.count {
		margin-left: auto;
		padding: 0.05rem 0.6rem;
		border: 2px solid #2a1f2d;
		border-radius: 4px;
		background: var(--sun);
		font: 700 0.85rem var(--font-pixel);
	}
	.fit {
		width: 100%;
		margin-inline: auto;
	}
	.easel {
		position: relative;
	}
	.canvas {
		position: absolute;
		overflow: hidden;
		background: #fff;
	}
	.canvas img {
		display: block;
		width: 100%;
		height: 100%;
		object-fit: cover;
	}
	.frame {
		position: absolute;
		inset: 0;
		pointer-events: none;
		line-height: 0;
	}
	.cover {
		position: absolute;
		inset: 0;
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		grid-template-rows: repeat(4, 1fr);
	}
	/* Not called .tile: that is the answer buttons' shared class. */
	.shutter {
		display: grid;
		place-items: center;
		background: #2bb0a6;
		box-shadow:
			inset var(--s) var(--s) 0 rgb(255 255 255 / 0.28),
			inset calc(var(--s) * -1) calc(var(--s) * -1) 0 rgb(0 0 0 / 0.2);
		transition: opacity 380ms steps(4);
		transition-delay: calc(var(--n) * 70ms);
	}
	.shutter.alt {
		background: #239a91;
	}
	.shutter::after {
		content: '?';
		color: rgb(255 255 255 / 0.5);
		font: 700 calc(var(--s) * 9) var(--font-pixel);
	}
	.shutter.open {
		opacity: 0;
	}
</style>
