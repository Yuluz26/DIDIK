<!--
	Pasukan Warna's island of hexagons. Orange is Pasukan Harimau, teal is Pasukan Penyu; each team's
	children stand by their base. When a child has flags, the hexagons they can take glow and show
	what they cost. The island always fits its space, and on the big screen the screen's height too.
-->
<script lang="ts">
	import type { Person } from '$lib/types';
	import { TEAM_COLOURS } from '$lib/names';
	import Chibi from '$ui/Chibi.svelte';

	interface Cell {
		key: string;
		q: number;
		r: number;
		owner: string | null;
		base: boolean;
	}

	let {
		cells,
		targets = [],
		costs = {},
		fresh = null,
		people = [],
		me = null,
		maxHeight = Infinity,
		oncapture
	}: {
		cells: Cell[];
		targets?: string[];
		costs?: Record<string, number | null>;
		fresh?: string | null;
		people?: Person[];
		me?: string | null;
		maxHeight?: number;
		oncapture?: (key: string) => void;
	} = $props();

	const S = 10;
	const SQ3 = Math.sqrt(3);
	const centre = (c: Cell) => ({ x: S * SQ3 * (c.q + c.r / 2), y: S * 1.5 * c.r });
	const corners = (x: number, y: number, size = S * 0.96) =>
		Array.from({ length: 6 }, (_, i) => {
			const a = (Math.PI / 180) * (60 * i - 30);
			return `${(x + size * Math.cos(a)).toFixed(2)},${(y + size * Math.sin(a)).toFixed(2)}`;
		}).join(' ');

	const box = $derived.by(() => {
		const points = cells.map(centre);
		const xs = points.map((p) => p.x);
		const ys = points.map((p) => p.y);
		const pad = S * 1.4;
		return { x: Math.min(...xs) - pad, y: Math.min(...ys) - pad, w: Math.max(...xs) - Math.min(...xs) + pad * 2, h: Math.max(...ys) - Math.min(...ys) + pad * 2 };
	});
	const can = $derived(new Set(targets));

	let width = $state(0);
	const fit = $derived(Math.min(width, maxHeight * (box.w / box.h)));
	const px = (units: number) => (units / box.w) * fit;

	// Each team's children gather by their base, the child's own character at the front. The bases sit
	// at the island's two ends, so each group lines up from its own edge of the map inwards and stays
	// on the map however big the team; past five, a count stands for the rest.
	const crowds = $derived(
		cells
			.filter((c) => c.base && c.owner)
			.map((base) => {
				const at = centre(base);
				const members = people.filter((p) => p.team === base.owner).sort((a, b) => Number(b.id === me) - Number(a.id === me));
				return { key: base.key, y: at.y, right: at.x > box.x + box.w / 2, members: members.slice(0, 5), more: Math.max(0, members.length - 5) };
			})
	);

	function fill(owner: string | null) {
		return owner ? TEAM_COLOURS[owner]?.colour : '#cfe8a8';
	}
	function edge(owner: string | null) {
		return owner ? TEAM_COLOURS[owner]?.deep : '#9fc77a';
	}
</script>

<div class="map" bind:clientWidth={width}>
	<div class="frame" style:width="{fit}px">
		<svg class="hexes" viewBox="{box.x} {box.y} {box.w} {box.h}" role="group" aria-label="Peta pulau">
			<rect x={box.x} y={box.y} width={box.w} height={box.h} fill="#3ba7d9" rx="6" />
			{#each cells as cell (cell.key)}
				{@const c = centre(cell)}
				{@const target = can.has(cell.key)}
				<!-- svelte-ignore a11y_no_noninteractive_tabindex -->
				<g
					class="cell"
					class:target
					class:fresh={fresh === cell.key}
					role={target ? 'button' : undefined}
					tabindex={target ? 0 : undefined}
					aria-label={target ? `Tawan petak (${costs[cell.key]} bendera)` : undefined}
					onclick={() => target && oncapture?.(cell.key)}
					onkeydown={(e) => target && (e.key === 'Enter' || e.key === ' ') && oncapture?.(cell.key)}
					style:transform-origin="{c.x}px {c.y}px"
				>
					<polygon points={corners(c.x, c.y + 1.2)} fill={edge(cell.owner)} />
					<polygon points={corners(c.x, c.y)} fill={fill(cell.owner)} />
					{#if cell.base}
						<path d="M{c.x - 2} {c.y + 4.5} v-9.5" stroke="#6b4a2e" stroke-width="0.9" stroke-linecap="round" />
						<path d="M{c.x - 1.6} {c.y - 5} l6 2.2 -6 2.2z" fill="#fff" />
						<circle cx={c.x + 0.6} cy={c.y - 2.8} r="0.9" fill={edge(cell.owner)} />
					{/if}
					{#if cell.owner && !cell.base}
						<!-- A small flag on every claimed hexagon. -->
						<path d="M{c.x - 0.8} {c.y + 3} v-6.4" stroke="#6b4a2e" stroke-width="0.7" stroke-linecap="round" />
						<path d="M{c.x - 0.5} {c.y - 3.4} l4 1.5 -4 1.5z" fill="#fff" />
					{:else if !cell.owner && (cell.q * 3 + cell.r) % 3 === 0}
						<path d="M{c.x - 3} {c.y + 2} l0.6 -1.6 0.6 1.6 M{c.x + 2} {c.y - 1} l0.5 -1.3 0.5 1.3" stroke="#9fc77a" stroke-width="0.6" fill="none" stroke-linecap="round" />
					{/if}
					{#if target}
						<polygon class="ring" points={corners(c.x, c.y, S * 0.8)} fill="none" stroke="#fff" stroke-width="1.2" />
						<text x={c.x} y={c.y + 1.6} text-anchor="middle" class="cost">{costs[cell.key] === 2 ? '2' : '1'}</text>
					{/if}
				</g>
			{/each}
		</svg>
		{#each crowds as crowd (crowd.key)}
			<div class="crowd" class:right={crowd.right} style:top="{px(crowd.y - box.y + 5)}px" aria-hidden="true">
				{#each crowd.members as person (person.id)}
					<span class="member" class:me={person.id === me}>
						<Chibi animal={person.avatar} colour={person.colour} skin={person.skin} size={Math.max(16, Math.round(px(11)))} />
					</span>
				{/each}
				{#if crowd.more}<span class="more">+{crowd.more}</span>{/if}
			</div>
		{/each}
	</div>
</div>

<style>
	.map {
		min-width: 0;
	}
	.frame {
		position: relative;
		margin-inline: auto;
	}
	.hexes {
		display: block;
		width: 100%;
		height: auto;
		border-radius: var(--r-lg);
		box-shadow: var(--card-shadow);
	}
	.crowd {
		position: absolute;
		left: 0.4rem;
		display: flex;
		align-items: flex-end;
		translate: 0 -100%;
		line-height: 0;
		pointer-events: none;
	}
	.crowd.right {
		left: auto;
		right: 0.4rem;
		flex-direction: row-reverse;
	}
	.more {
		align-self: center;
		margin-inline: 0.2rem;
		padding: 0 0.4rem;
		border-radius: var(--r-pill);
		background: #fff;
		color: var(--ink);
		font-weight: 800;
		font-size: 0.8rem;
		line-height: 1.6;
	}
	.member + .member {
		margin-left: -0.3rem;
	}
	.right .member + .member {
		margin-left: 0;
		margin-right: -0.3rem;
	}
	.member.me {
		position: relative;
		z-index: 1;
		filter: drop-shadow(0 0 2px #fff);
	}
	.cell {
		transition: transform 300ms var(--spring);
	}
	.cell.target {
		cursor: pointer;
	}
	.cell.target:hover,
	.cell.target:focus-visible {
		transform: scale(1.08);
		outline: none;
	}
	.ring {
		stroke-dasharray: 3 2;
		animation: march 1.2s linear infinite;
	}
	.cost {
		font: 600 5px var(--font-display);
		fill: #1f2d27;
		paint-order: stroke;
		stroke: #fff;
		stroke-width: 1.4px;
	}
	.fresh {
		animation: pop-in 600ms var(--spring);
	}
	@keyframes march {
		to {
			stroke-dashoffset: -10;
		}
	}
</style>
