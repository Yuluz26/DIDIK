<!--
	Pasukan Warna's island of hexagons. Orange is Pasukan Harimau, teal is Pasukan Penyu. When a child
	has flags, the hexagons they can take glow and show what they cost.
-->
<script lang="ts">
	import { TEAM_COLOURS } from '$lib/names';

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
		oncapture
	}: {
		cells: Cell[];
		targets?: string[];
		costs?: Record<string, number | null>;
		fresh?: string | null;
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

	function fill(owner: string | null) {
		return owner ? TEAM_COLOURS[owner]?.colour : '#cfe8a8';
	}
	function edge(owner: string | null) {
		return owner ? TEAM_COLOURS[owner]?.deep : '#9fc77a';
	}
</script>

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
			{#if target}
				<polygon class="ring" points={corners(c.x, c.y, S * 0.8)} fill="none" stroke="#fff" stroke-width="1.2" />
				<text x={c.x} y={c.y + 1.6} text-anchor="middle" class="cost">{costs[cell.key] === 2 ? '2' : '1'}</text>
			{/if}
		</g>
	{/each}
</svg>

<style>
	.hexes {
		display: block;
		width: 100%;
		height: auto;
		border-radius: var(--r-lg);
		box-shadow: var(--card-shadow);
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
