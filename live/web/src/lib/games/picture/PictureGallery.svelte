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
	import World, { type WorldActor, type WorldProp } from '$lib/worlds/World.svelte';

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
	const tile = $derived(Math.max(26, Math.min(56, width / W)));
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
	<div class="easel" style:--t="{tile}px">
		<svg class="legs" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">
			<path d="M22 100 L42 8 M78 100 L58 8 M50 100 V40" stroke="#8e5a2e" stroke-width="5" stroke-linecap="round" />
		</svg>
		<div class="canvas">
			<img src={frame.url} alt={frame.name ? `Gambar ${frame.name}` : 'Gambar rahsia, sebahagiannya tertutup'} />
			<div class="cover" aria-hidden="true">
				{#each Array.from({ length: frame.tiles }, (_, i) => i) as i (i)}
					<span class="shutter" class:open={open.has(i)} class:alt={(i + Math.floor(i / 4)) % 2 === 1} style:--n={i % 4}></span>
				{/each}
			</div>
		</div>
		<span class="ledge"></span>
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
		<World width={W} height={H} {tile} props={PROPS} {actors} {me} names={me ? 'me' : true} {art}>
			{#snippet ground()}
				<!-- The back wall with its wainscot, then the wooden floor. -->
				<rect width={W} height="2.3" fill="#fbe9c9" />
				<rect y="1.75" width={W} height="0.55" fill="#efd3a2" />
				<rect y="2.22" width={W} height="0.1" fill="#c98a54" />
				<rect x="0.9" y="0.45" width="1.1" height="0.85" rx="0.06" fill="#8e5a2e" /><rect x="1.0" y="0.55" width="0.9" height="0.65" fill="#bde7f5" />
				<path d="M1.0 1.2 l0.3 -0.32 l0.22 0.2 l0.18 -0.14 l0.2 0.26z" fill="#4fa35b" />
				<rect x="6.0" y="0.5" width="1.0" height="0.8" rx="0.06" fill="#8e5a2e" /><rect x="6.1" y="0.6" width="0.8" height="0.6" fill="#ffe7a3" />
				<circle cx="6.5" cy="0.9" r="0.16" fill="#e8553f" />
				<rect y="2.32" width={W} height={H - 2.32} fill="#d9a066" />
				{#each [2.95, 3.6, 4.25, 4.9, 5.55] as y (y)}<rect y={y} width={W} height="0.04" fill="#c48a52" />{/each}
				<ellipse cx="4" cy="5.25" rx="2.6" ry="0.55" fill="#2bb0a6" opacity=".85" />
				<ellipse cx="4" cy="5.25" rx="2.2" ry="0.4" fill="none" stroke="#fff" stroke-width="0.05" stroke-dasharray="0.15 0.1" />
			{/snippet}
		</World>
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
		font: 600 1.2rem var(--font-display);
	}
	.count {
		margin-left: auto;
		padding: 0.05rem 0.6rem;
		border-radius: var(--r-pill);
		background: var(--sun);
		font-weight: 800;
		font-size: 0.85rem;
	}
	.fit {
		width: 100%;
		margin-inline: auto;
	}
	.easel {
		position: relative;
		width: calc(var(--t) * 4.6);
		height: calc(var(--t) * 5.2);
	}
	.legs {
		position: absolute;
		inset: calc(var(--t) * 0.6) 0 0;
		width: 100%;
		height: calc(100% - var(--t) * 0.6);
	}
	.canvas {
		position: absolute;
		top: 0;
		left: 50%;
		width: calc(var(--t) * 4.1);
		aspect-ratio: 1;
		translate: -50% 0;
		overflow: hidden;
		border: calc(var(--t) * 0.14) solid #8e5a2e;
		border-radius: 6px;
		background: #fff;
		box-shadow: 0 4px 0 #6b4220;
		perspective: 600px;
	}
	.canvas img {
		display: block;
		width: 100%;
		height: 100%;
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
		box-shadow: inset 0 0 0 1px rgb(255 255 255 / 0.22);
		transition:
			transform 480ms var(--spring),
			opacity 380ms var(--ease-out);
		transition-delay: calc(var(--n) * 70ms);
	}
	.shutter.alt {
		background: #239a91;
	}
	.shutter::after {
		content: '?';
		color: rgb(255 255 255 / 0.45);
		font: 600 calc(var(--t) * 0.45) var(--font-display);
	}
	.shutter.open {
		opacity: 0;
		transform: rotateY(90deg) scale(0.7);
	}
	.ledge {
		position: absolute;
		top: calc(var(--t) * 4.05);
		left: 50%;
		width: calc(var(--t) * 4.5);
		height: calc(var(--t) * 0.22);
		translate: -50% 0;
		border-radius: 4px;
		background: #a46a37;
	}
</style>
