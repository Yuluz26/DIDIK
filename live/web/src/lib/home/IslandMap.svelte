<!--
	The eight games as islands on one sea. On a wide screen they lie in two rows with a channel
	between them; pointing at an island sails a sampan along the channel to it, and the card beside
	the map tells you about that island. On a phone and a tablet the islands follow one another down
	the page, each with its own words. The section's heading is passed in as `head`.
-->
<script lang="ts">
	import type { Snippet } from 'svelte';
	import { GAMES } from './islands';
	import GameIsland from './GameIsland.svelte';
	import Sampan from '$lib/worlds/Sampan.svelte';

	let { head }: { head: Snippet } = $props();

	// Island centres in % of the map: the top row left to right, then the bottom row back again.
	const SPOTS = [
		{ x: 13, y: 21 },
		{ x: 38, y: 15 },
		{ x: 63, y: 22 },
		{ x: 87, y: 16 },
		{ x: 87, y: 81 },
		{ x: 62, y: 87 },
		{ x: 37, y: 80 },
		{ x: 12, y: 86 }
	];
	// Where the sampan waits for each island: in the channel between the rows.
	const DOCKS = SPOTS.map((s, i) => ({ x: s.x + (i < 4 ? 3 : -3), y: i < 4 ? 46 : 58 }));
	const HOP = 360;

	let width = $state(typeof window === 'undefined' ? 0 : Math.min(window.innerWidth, 1216) - 32);
	let mapWidth = $state(0);
	const wide = $derived(width >= 960);

	let selected = $state(0);
	let at = $state(0);
	let facing = $state(1);
	let moving = $state(false);
	let hopTimer: ReturnType<typeof setTimeout> | undefined;
	let hoverTimer: ReturnType<typeof setTimeout> | undefined;
	const still = typeof matchMedia === 'function' && matchMedia('(prefers-reduced-motion: reduce)').matches;

	function sailTo(target: number) {
		selected = target;
		clearTimeout(hopTimer);
		if (still) {
			at = target;
			return;
		}
		const n = GAMES.length;
		const hop = () => {
			if (at === target) {
				moving = false;
				return;
			}
			const ahead = (target - at + n) % n;
			const next = (at + (ahead <= n / 2 ? 1 : -1) + n) % n;
			if (Math.abs(DOCKS[next].x - DOCKS[at].x) > 1) facing = DOCKS[next].x > DOCKS[at].x ? 1 : -1;
			at = next;
			moving = true;
			hopTimer = setTimeout(hop, HOP);
		};
		hop();
	}

	// Resting on an island for a moment picks it; passing over it on the way elsewhere does not.
	function hover(i: number) {
		clearTimeout(hoverTimer);
		hoverTimer = setTimeout(() => i !== selected && sailTo(i), 140);
	}

	$effect(() => () => {
		clearTimeout(hopTimer);
		clearTimeout(hoverTimer);
	});

	// The sampan's route: a smooth loop through the docks, in the map's own % units.
	const route = (() => {
		const p = DOCKS;
		const n = p.length;
		let d = `M${p[0].x} ${p[0].y}`;
		for (let i = 0; i < n; i++) {
			const [a, b, c, e] = [p[(i - 1 + n) % n], p[i], p[(i + 1) % n], p[(i + 2) % n]];
			d += ` C${b.x + (c.x - a.x) / 6} ${b.y + (c.y - a.y) / 6} ${c.x - (e.x - b.x) / 6} ${c.y - (e.y - b.y) / 6} ${c.x} ${c.y}`;
		}
		return `${d}Z`;
	})();

	const game = $derived(GAMES[selected]);
</script>

<div class="islands-map" class:wide bind:clientWidth={width}>
	<div class="side">
		{@render head()}
		{#if wide}
			<section id="pulau-kad" class="info" aria-live="polite" style:--tint={game.tint}>
				<p class="pace">{game.pace}</p>
				<h3>{game.title}</h3>
				<p class="line">{game.line}</p>
			</section>
		{/if}
	</div>

	{#if wide}
		<div class="map" bind:clientWidth={mapWidth}>
			<svg class="route" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true" focusable="false">
				<path d={route} />
			</svg>

			{#each GAMES as g, i (g.key)}
				<button
					type="button"
					class="isle"
					class:picked={selected === i}
					style:left="{SPOTS[i].x}%"
					style:top="{SPOTS[i].y}%"
					style:--tint={g.tint}
					aria-pressed={selected === i}
					aria-controls="pulau-kad"
					onclick={() => sailTo(i)}
					onfocus={() => sailTo(i)}
					onpointerenter={() => hover(i)}
					onpointerleave={() => clearTimeout(hoverTimer)}
				>
					<span class="art" data-ui><GameIsland game={g.key} width={mapWidth * 0.215} active={selected === i} /></span>
					<span class="name">{g.title}</span>
				</button>
			{/each}

			<div class="boat" class:moving style:left="{DOCKS[at].x}%" style:top="{DOCKS[at].y}%" style:--hop="{HOP}ms" aria-hidden="true">
				<Sampan tile={mapWidth * 0.03} animal="kancil" colour="hijau" skin="s2" {facing} rowing={moving} />
			</div>
		</div>
	{:else}
		<ol class="list">
			{#each GAMES as g, i (g.key)}
				<li class:flip={i % 2 === 1} style:--tint={g.tint}>
					<div class="art" data-ui><GameIsland game={g.key} width={Math.min(320, width * (width >= 600 ? 0.4 : 0.78))} /></div>
					<div class="words">
						<h3>{g.title}</h3>
						<p class="pace">{g.pace}</p>
						<p class="line">{g.line}</p>
					</div>
				</li>
			{/each}
		</ol>
	{/if}
</div>

<style>
	.islands-map {
		display: grid;
		gap: 2.4rem;
	}
	.wide {
		grid-template-columns: minmax(0, 0.62fr) minmax(0, 1.38fr);
		align-items: center;
		gap: 3rem;
	}
	.side {
		display: grid;
		gap: 1.6rem;
		align-content: center;
	}
	.info {
		display: grid;
		gap: 0.4rem;
		min-height: 13rem;
		align-content: start;
		padding: 1.4rem 1.5rem 1.5rem;
		border-radius: var(--r-lg);
		background: var(--paper);
		color: var(--ink);
	}
	.info h3 {
		font-size: 2rem;
	}
	.pace {
		color: var(--tint);
		font-weight: 800;
	}
	.map {
		position: relative;
		aspect-ratio: 1.42;
	}
	.route {
		position: absolute;
		inset: 0;
		width: 100%;
		height: 100%;
		overflow: visible;
	}
	.route path {
		fill: none;
		stroke: #8fd3f0;
		stroke-width: 5;
		stroke-dasharray: 0 15;
		stroke-linecap: round;
		vector-effect: non-scaling-stroke;
		opacity: 0.7;
	}
	.isle {
		position: absolute;
		display: grid;
		justify-items: center;
		gap: 0.15rem;
		width: 24%;
		padding: 0;
		border: 0;
		background: none;
		color: var(--ink);
		font: inherit;
		cursor: pointer;
		translate: -50% -55%;
	}
	.isle .art {
		display: block;
		width: 100%;
		transition: transform 420ms var(--spring);
	}
	/* A ring spreads on the water under the island you point at. */
	.isle::before {
		content: '';
		position: absolute;
		left: 10%;
		right: 10%;
		top: 36%;
		height: 44%;
		border-radius: 50%;
		border: 3px solid rgb(232 246 252 / 0.85);
		opacity: 0;
		pointer-events: none;
	}
	.isle:hover::before {
		animation: ripple 1.1s var(--ease-out);
	}
	.isle:hover .art,
	.isle.picked .art {
		transform: translateY(-8px);
	}
	.isle:active .art {
		transform: translateY(-2px) scale(0.97);
	}
	.isle:focus-visible {
		outline: none;
	}
	.isle:focus-visible .name {
		outline: 3px solid var(--sun);
		outline-offset: 3px;
	}
	.name {
		position: relative;
		z-index: 1;
		padding: 0.12rem 0.7rem;
		border-radius: var(--r-pill);
		background: var(--paper);
		font: 600 1.0625rem / 1.35 var(--font-display);
		white-space: nowrap;
		transition:
			background-color var(--t-state),
			color var(--t-state),
			transform 420ms var(--spring);
	}
	.isle:hover .name {
		transform: translateY(-3px) rotate(-2deg);
	}
	.picked .name {
		background: var(--tint);
		color: #fff;
	}
	.boat {
		position: absolute;
		z-index: 2;
		translate: -50% -70%;
		transition:
			left var(--hop) linear,
			top var(--hop) linear;
		pointer-events: none;
	}
	/* Phones and tablets: one island after another, the words with each. */
	.list {
		display: grid;
		grid-template-columns: minmax(0, 1fr);
		gap: 2.6rem;
		margin: 0;
		padding: 0;
		list-style: none;
	}
	.list li {
		display: grid;
		gap: 0.6rem;
	}
	.list .art {
		justify-self: start;
		width: min(320px, 78%);
	}
	.list .flip .art {
		justify-self: end;
	}
	.list h3 {
		font-size: 1.6rem;
	}
	.list .pace {
		color: var(--on-sea);
	}
	@media (min-width: 600px) {
		.list {
			grid-template-columns: repeat(2, minmax(0, 1fr));
			gap: 2.4rem 2rem;
		}
		.list .art,
		.list .flip .art {
			justify-self: center;
			width: 82%;
		}
	}
	@keyframes ripple {
		from {
			opacity: 1;
			transform: scale(0.7);
		}
		to {
			opacity: 0;
			transform: scale(1.25);
		}
	}
</style>
