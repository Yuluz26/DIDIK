<!--
	Pasukan Warna's island of hexagons, in pixels. Orange is Pasukan Harimau, teal is Pasukan Penyu;
	each team's children stand on the beach below, their own character in front. When a child has
	flags, the hexagons they can take glow and show what they cost. The board always fits its space,
	and on the big screen the screen's height too.
-->
<script lang="ts">
	import { TEAM_COLOURS } from '$lib/names';
	import { prescale, snapScale, urlOf } from '$lib/pixel/cache';
	import { CW } from '$lib/pixel/chibi';
	import Sprite from '$lib/pixel/Sprite.svelte';
	import type { Person } from '$lib/types';
	import Chibi from '$ui/Chibi.svelte';
	import { pondWater, shoreSand } from '../jump/sprites';
	import { CELL, HEX, hexRing, hexTile } from './sprites';

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

	// A tile's top left corner, in sprite pixels from the first tile's.
	const place = (c: Cell) => ({ x: HEX.w * c.q + (HEX.w / 2) * c.r, y: HEX.row * c.r });

	const MARGIN = 8;
	const BEACH = 36;
	const box = $derived.by(() => {
		const at = cells.map(place);
		const x0 = Math.min(...at.map((p) => p.x));
		const y0 = Math.min(...at.map((p) => p.y));
		const x1 = Math.max(...at.map((p) => p.x)) + CELL.w;
		const y1 = Math.max(...at.map((p) => p.y)) + CELL.h;
		return { x: x0 - MARGIN, y: y0 - MARGIN, w: x1 - x0 + MARGIN * 2, h: y1 - y0 + MARGIN * 2, board: y1 - y0 + MARGIN * 2 };
	});
	const total = $derived(box.h + BEACH);
	const can = $derived(new Set(targets));

	let width = $state(0);
	// One pixel size for everything on the board, the largest that fits its space.
	const s = $derived(snapScale(Math.min(width / box.w, maxHeight / total), 1));
	const k = $derived(prescale(s));
	const sea = $derived(urlOf(pondWater(), k));
	const sand = $derived(urlOf(shoreSand(), k));
	const palette = (owner: string | null) => (owner ? (TEAM_COLOURS[owner]?.colour ?? '#cfe8a8') : '#cfe8a8');

	// Each team's children stand on the beach, the child's own character at the front; past four a
	// count stands for the rest.
	const crowds = $derived(
		Object.keys(TEAM_COLOURS).map((team, i) => {
			const members = people.filter((p) => p.team === team).sort((a, b) => Number(b.id === me) - Number(a.id === me));
			return { team, right: i === 1, members: members.slice(0, 4), more: Math.max(0, members.length - 4) };
		})
	);
</script>

<div class="map" bind:clientWidth={width}>
	<div class="frame" style:width="{box.w * s}px" style:height="{total * s}px" style:--s="{s}px">
		<div class="sea" style:height="{box.h * s}px" style:background-image="url({sea})" style:background-size="{48 * s}px {48 * s}px"></div>
		<div class="beach" style:top="{box.h * s}px" style:height="{BEACH * s}px" style:background-image="url({sand})" style:background-size="{32 * s}px {32 * s}px"></div>
		<div class="hexes" role="group" aria-label="Peta pulau">
			{#each cells as cell (cell.key)}
				{@const at = place(cell)}
				{@const target = can.has(cell.key)}
				{@const sheet = hexTile(cell.owner, palette(cell.owner), cell.base, !!cell.owner)}
				{#snippet face()}
					<Sprite {sheet} {s} />
					{#if target}
						<span class="ring"><Sprite sheet={hexRing()} {s} frames={2} ms={500} /></span>
						<span class="cost" style:font-size="{Math.max(9, 8 * s)}px">{costs[cell.key] === 2 ? '2' : '1'}</span>
					{/if}
				{/snippet}
				{#if target}
					<button
						type="button"
						class="cell target"
						class:fresh={fresh === cell.key}
						style:left="{(at.x - box.x) * s}px"
						style:top="{(at.y - box.y) * s}px"
						style:width="{CELL.w * s}px"
						style:height="{CELL.h * s}px"
						aria-label="Tawan petak ({costs[cell.key]} bendera)"
						onclick={() => oncapture?.(cell.key)}
					>
						{@render face()}
					</button>
				{:else}
					<span
						class="cell"
						class:fresh={fresh === cell.key}
						style:left="{(at.x - box.x) * s}px"
						style:top="{(at.y - box.y) * s}px"
						style:width="{CELL.w * s}px"
						style:height="{CELL.h * s}px"
					>
						{@render face()}
					</span>
				{/if}
			{/each}
		</div>
		{#each crowds as crowd (crowd.team)}
			<div class="crowd" class:right={crowd.right} style:bottom="{3 * s}px" style:--overlap="{-CW * 0.4 * s}px" aria-hidden="true">
				{#each crowd.members as person (person.id)}
					<span class="member" class:me={person.id === me}>
						<Chibi animal={person.avatar} colour={person.colour} skin={person.skin} {s} />
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
		overflow: hidden;
		border-radius: var(--r-md);
		box-shadow: var(--card-shadow);
	}
	.sea,
	.beach {
		position: absolute;
		left: 0;
		right: 0;
		background-color: #2a88a6;
	}
	.beach {
		background-color: #e9c78d;
		box-shadow: inset 0 calc(var(--s) * 2) 0 #fff0cc;
	}
	.hexes {
		position: absolute;
		inset: 0;
	}
	.cell {
		position: absolute;
		display: block;
		padding: 0;
		border: 0;
		background: none;
		line-height: 0;
	}
	.ring {
		position: absolute;
		inset: 0;
		pointer-events: none;
	}
	.cost {
		position: absolute;
		left: 50%;
		top: 38%;
		translate: -50% -50%;
		color: #2a1f2d;
		font-family: var(--font-pixel);
		font-weight: 700;
		line-height: 1;
		text-shadow: 1px 0 #fff, -1px 0 #fff, 0 1px #fff, 0 -1px #fff;
	}
	.crowd {
		position: absolute;
		left: calc(var(--s) * 4);
		display: flex;
		align-items: flex-end;
		line-height: 0;
		pointer-events: none;
	}
	.crowd.right {
		left: auto;
		right: calc(var(--s) * 4);
		flex-direction: row-reverse;
	}
	.more {
		align-self: center;
		margin-inline: 0.2rem;
		padding: 0 0.35rem;
		border: 2px solid #2a1f2d;
		border-radius: 4px;
		background: #fff6e6;
		color: #2a1f2d;
		font: 700 0.8rem/1.4 var(--font-pixel);
	}
	.member + .member {
		margin-left: var(--overlap);
	}
	.right .member + .member {
		margin-left: 0;
		margin-right: var(--overlap);
	}
	.member.me {
		position: relative;
		z-index: 1;
		filter: drop-shadow(var(--s) 0 0 #fff) drop-shadow(calc(var(--s) * -1) 0 0 #fff) drop-shadow(0 var(--s) 0 #fff) drop-shadow(0 calc(var(--s) * -1) 0 #fff);
	}
	.cell.target {
		cursor: pointer;
		transition: transform 160ms steps(2);
	}
	.cell.target:hover,
	.cell.target:focus-visible {
		transform: translateY(calc(var(--s) * -1));
		outline: none;
	}
	.fresh {
		animation: pop-in 600ms var(--spring);
	}
</style>
